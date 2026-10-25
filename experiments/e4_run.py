"""E4 calls (prereg/p7-v1.1.md section 7; DECISIONS.md D-C-2, D-C-3), as paper 6 jev-v3.

One family per invocation, over the committed sample (results/e4/sample.json) and
views (results/e4/views.jsonl, or views-timeline.jsonl for the exploratory arm), in
the registered sample order.

- Families: `jev` (TypeSafe System One, typesafe-sdk 0.7.2, model alias `jev-latest`,
  endpoint https://api.typesafe.ai/v1/systemone) and `haiku` (Anthropic Messages API,
  `claude-haiku-4-5-20251001`, temperature 0, max_tokens 48, no system prompt,
  assistant prefill "{").
- Request and parser. Haiku: the rendered view as the single user message; the reply
  is prefill + text, fences removed, first JSON object, `decision` in {clear, hold} and
  `p_hold` a number in [0, 1] (jev-v3 section 3b, fields of section 7). Jev: System One
  takes a state and typed questions, not a text reply; the view's task sentence is the
  state context, the ERP record the state record, and one `choice` question with labels
  `clear` and `hold`; decision = the selected label, p_hold = the probability of `hold`.
- SDK retries are off; every retry passes through here (1 s doubling to 60 s, at most 8,
  on 429, 5xx and connection errors). Every raw request and response is appended to
  responses/<arm>/<family>/responses.jsonl from the HTTP hook, before parsing, with the
  hashed line id, timestamps, token counts and cost. Nothing is overwritten; no header,
  key or environment value is written.
- Cap: USD 60 across E4 and the exploratory arm, retries included. Before every attempt,
  committed spend (every responses file under responses/e4 and responses/e4-exploratory)
  plus the attempt's worst-case cost (paper 6's bound: request bytes as input tokens,
  max_tokens as output tokens) must not exceed the cap, or the family stops CAP_TRUNCATED.
- One re-request on an invalid reply, then the line is scored `invalid`.
- Arm health (jev-v3 3c): more than 2 invalid among the first 20 lines, or more than 10
  among the first 200, stops the family ARM_INVALID (final, not resumable).
- MODEL_VERSION_CHANGED: Haiku's returned model differs from the pinned id; Jev's differs
  from the first model it returned. ARM_ENDPOINT: the key or endpoint fails (401, 403,
  404, or the pre-call model check fails). Never another model in its place.

Statuses: COMPLETE, ARM_INVALID, CAP_TRUNCATED, MODEL_VERSION_CHANGED, ARM_ENDPOINT,
RETRY_EXHAUSTED, HTTP_<status>, SDK_ERROR, PAUSED (--limit). A stopped family other
than PAUSED is final.

Keys are read from the process environment only (JEV_API_KEY, JEV_BASE_URL,
ANTHROPIC_API_KEY) and passed to the SDK constructors; they are never printed or written.

Usage: python -m experiments.e4_run --family jev|haiku [--arm e4|e4-exploratory] [--limit N]
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import logging
import math
import os
import platform
import re
import sys
import time
import uuid
from pathlib import Path
from typing import Any, Callable

from p2p_replay.config import REGISTRATION, ROOT

logging.getLogger("typesafe_sdk").setLevel(logging.WARNING)
logging.getLogger("anthropic").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpx2").setLevel(logging.WARNING)

CAP_USD = 60.0
SMOKE_N, SMOKE_MAX_INVALID = 20, 2
HEALTH_N, HEALTH_MAX_INVALID = 200, 10
MAX_RETRIES, BACKOFF_INITIAL_S, BACKOFF_MAX_S, HTTP_TIMEOUT_S = 8, 1.0, 60.0, 60.0

JEV_ENDPOINT = "https://api.typesafe.ai/v1/systemone"
JEV_MODEL = "jev-latest"
JEV_SDK = "0.7.2"
JEV_QID = "Q_clear_or_hold"
JEV_QUESTION = "Decide whether to clear the invoice for payment now or to hold it."
JEV_CRITERIA = {"clear": "Clear the invoice for payment now.", "hold": "Hold the invoice; do not pay it now."}
# Paper 6 (gigo-jev-probe constants_v2): USD 42 per 1e9 input tokens, output free.
JEV_USD_IN, JEV_USD_OUT = 42.0 / 1e9, 0.0

HAIKU_MODEL = "claude-haiku-4-5-20251001"
HAIKU_BASE_URL = "https://api.anthropic.com"
HAIKU_SDK = "1.9.0"
HAIKU_MAX_TOKENS, HAIKU_TEMPERATURE, HAIKU_PREFILL = 48, 0.0, "{"
# Paper 6 (gigo-jev-probe constants_v2): Claude Haiku 4.5 list price, USD 1.00 / 5.00 per 1e6 tokens.
HAIKU_USD_IN, HAIKU_USD_OUT = 1.00 / 1e6, 5.00 / 1e6

FAMILIES = ("jev", "haiku")
ARMS = {"e4": ("responses/e4", "views.jsonl"), "e4-exploratory": ("responses/e4-exploratory", "views-timeline.jsonl")}
SAMPLE_PATH = ROOT / "results" / "e4" / "sample.json"
FENCE_RE = re.compile(r"```[A-Za-z0-9_-]*")
DECISIONS = ("clear", "hold")


class RunStop(Exception):
    def __init__(self, status: str, detail: str = "") -> None:
        super().__init__(f"{status}: {detail}" if detail else status)
        self.status, self.detail = status, detail


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="microseconds")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class Log:
    """Append-only JSONL; each append is flushed and fsynced."""

    def __init__(self, path: Path) -> None:
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, rec: dict[str, Any]) -> None:
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, ensure_ascii=False, separators=(",", ":"), allow_nan=False) + "\n")
            fh.flush()
            os.fsync(fh.fileno())

    def records(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        with self.path.open(encoding="utf-8") as fh:
            return [json.loads(line) for line in fh if line.strip()]


def committed_spend(root: Path = ROOT) -> float:
    """Spend charged by every attempt in every E4 responses file (both arms, both families)."""
    total = 0.0
    for arm_dir, _ in ARMS.values():
        for path in sorted((root / arm_dir).glob("*/responses.jsonl")):
            total += sum(float(r["charged_usd"]) for r in Log(path).records() if r.get("kind") == "attempt")
    return total


def decode(raw: str | None) -> Any:
    if raw is None:
        return None
    try:
        return json.loads(raw)
    except ValueError:
        return None


def usage_tokens(raw: str | None) -> tuple[int | None, int | None]:
    body = decode(raw)
    usage = body.get("usage") if isinstance(body, dict) else None
    if not isinstance(usage, dict):
        return None, None

    def _int(v: Any) -> int | None:
        return v if isinstance(v, int) and not isinstance(v, bool) and v >= 0 else None

    return _int(usage.get("input_tokens")), _int(usage.get("output_tokens"))


def returned_model(raw: str | None) -> str:
    body = decode(raw)
    m = body.get("model") if isinstance(body, dict) else None
    return m if isinstance(m, str) and m else "unreported"


def _probability(v: Any) -> float | None:
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        return None
    v = float(v)
    return v if math.isfinite(v) and 0.0 <= v <= 1.0 else None


def parse_haiku(raw: str | None) -> tuple[str, float] | None:
    body = decode(raw)
    if not isinstance(body, dict) or body.get("stop_reason") == "refusal":
        return None
    blocks = body.get("content")
    if not isinstance(blocks, list):
        return None
    text = HAIKU_PREFILL + "".join(b.get("text", "") for b in blocks if isinstance(b, dict) and b.get("type") == "text")
    text = FENCE_RE.sub("", text)
    dec = json.JSONDecoder()
    obj: Any = None
    for m in re.finditer(r"\{", text):
        try:
            obj, _ = dec.raw_decode(text, m.start())
            break
        except ValueError:
            continue
    if not isinstance(obj, dict) or obj.get("decision") not in DECISIONS:
        return None
    p = _probability(obj.get("p_hold"))
    return None if p is None else (obj["decision"], p)


def parse_jev(raw: str | None) -> tuple[str, float] | None:
    body = decode(raw)
    answers = body.get("answers") if isinstance(body, dict) else None
    ans = answers.get(JEV_QID) if isinstance(answers, dict) else None
    if not isinstance(ans, dict) or ans.get("type") != "choice" or ans.get("choice") not in DECISIONS:
        return None
    probs = ans.get("probabilities")
    p = _probability(probs.get("hold")) if isinstance(probs, dict) else None
    return None if p is None else (ans["choice"], p)


def split_view(view: str) -> tuple[str, str]:
    """Jev state: the task sentences of the view (up to the reply-format sentence) and the record."""
    task, record = view.split("\n\n", 1)
    keep = task.split(" Reply with only a JSON object", 1)[0]
    return keep, record


def jev_state(view: str) -> dict[str, str]:
    context, record = split_view(view)
    return {"context": context, "record": record}


def jev_wire(view: str) -> bytes:
    return json.dumps({"state": jev_state(view), "model": JEV_MODEL,
                       "questions": {JEV_QID: {"type": "choice", "instructions": JEV_QUESTION,
                                               "criteria": JEV_CRITERIA}}}).encode("utf-8")


def haiku_params(view: str) -> dict[str, Any]:
    return {"model": HAIKU_MODEL, "max_tokens": HAIKU_MAX_TOKENS, "temperature": HAIKU_TEMPERATURE,
            "messages": [{"role": "user", "content": view}, {"role": "assistant", "content": HAIKU_PREFILL}]}


def haiku_wire(view: str) -> bytes:
    return json.dumps(haiku_params(view), ensure_ascii=False).encode("utf-8")


def backoff_delay(retry_number: int, retry_after_s: float | None) -> float:
    if retry_after_s is not None:
        return min(retry_after_s, BACKOFF_MAX_S)
    return min(BACKOFF_INITIAL_S * 2 ** (retry_number - 1), BACKOFF_MAX_S)


def is_retryable(status: int) -> bool:
    return status in (429, 529) or 500 <= status <= 599


ENDPOINT_STATUSES = (401, 403, 404)


class Family:
    """Shared attempt loop: cap before every attempt, raw response logged from the hook."""

    name = ""
    usd_in = usd_out = 0.0
    max_out = 0
    requested_model = ""

    def __init__(self, log: Log, *, segment: str, sleep: Callable[[float], None], cap_usd: float,
                 spend: float) -> None:
        self.log, self.segment, self.sleep, self.cap_usd, self.spend = log, segment, sleep, cap_usd, spend
        self._ctx: dict[str, Any] = {}
        self._pending: dict[str, Any] = {}
        self._last: dict[str, Any] | None = None

    def worst_case(self, body_len: int) -> float:
        return body_len * self.usd_in + self.max_out * self.usd_out

    def charge(self, in_tok: int | None, out_tok: int | None, body_len: int) -> float:
        if in_tok is None:
            return self.worst_case(body_len)
        return in_tok * self.usd_in + (out_tok or 0) * self.usd_out

    # hooks
    def _on_request(self, request: Any) -> None:
        self._pending.update({"sent_utc": utc_now(), "t0": time.monotonic(), "body": request.content})

    def _on_response(self, response: Any) -> None:
        response.read()
        retry_after = None
        if response.status_code >= 400:
            try:
                retry_after = float(response.headers.get("retry-after")) if response.headers.get("retry-after") else None
            except ValueError:
                retry_after = None
        self._write(http_status=response.status_code, raw=response.text, retry_after_s=retry_after, error_class=None)

    def _write(self, *, http_status: int | None, raw: str | None, retry_after_s: float | None,
               error_class: str | None) -> None:
        body: bytes = self._pending.get("body") or b""
        in_tok, out_tok = usage_tokens(raw)
        inference = self._ctx.get("kind", "attempt") == "attempt"
        charged = self.charge(in_tok, out_tok, len(body)) if inference else 0.0
        rec = {
            "kind": self._ctx.get("kind", "attempt"), "segment": self.segment, "family": self.name,
            **{k: self._ctx[k] for k in ("order", "line", "request_n", "attempt") if k in self._ctx},
            "request_body": decode(body.decode("utf-8")) if body else None,
            "request_sha256": sha256_hex(body) if body else None, "request_bytes": len(body),
            "sent_utc": self._pending.get("sent_utc"), "received_utc": utc_now(),
            "latency_s": (time.monotonic() - self._pending["t0"]) if "t0" in self._pending else None,
            "http_status": http_status, "error_class": error_class, "retry_after_s": retry_after_s,
            "response_body": raw, "requested_model": self.requested_model,
            "returned_model": returned_model(raw) if raw is not None else "unreported",
            "usage_input_tokens": in_tok, "usage_output_tokens": out_tok, "charged_usd": charged,
        }
        self.log.append(rec)
        if inference:
            self.spend += charged
        self._last = rec

    # subclass interface
    def wire(self, view: str) -> bytes:
        raise NotImplementedError

    def send(self, view: str) -> None:
        raise NotImplementedError

    def classify(self, exc: Exception) -> tuple[str, int | None, str]:
        raise NotImplementedError

    def parse(self, raw: str | None) -> tuple[str, float] | None:
        raise NotImplementedError

    def attempts(self, view: str) -> dict[str, Any] | None:
        bound = len(self.wire(view))
        for attempt in range(1, MAX_RETRIES + 2):
            worst = self.worst_case(bound)
            if self.spend + worst > self.cap_usd:
                raise RunStop("CAP_TRUNCATED", f"USD {self.spend:.6f} + {worst:.6f} > {self.cap_usd}")
            self._ctx["attempt"] = attempt
            self._last = None
            self._pending = {"sent_utc": utc_now(), "t0": time.monotonic(), "body": None}
            status: int | None = None
            error_class = ""
            try:
                self.send(view)
                return self._last
            except Exception as exc:  # noqa: BLE001 - mapped by classify()
                what, status, error_class = self.classify(exc)
                if what == "validation":
                    return self._last
                if what == "invalid":
                    return self._last
                if what == "endpoint":
                    raise RunStop("ARM_ENDPOINT", f"HTTP {status} {error_class}") from None
                if what == "stop":
                    raise RunStop(f"HTTP_{status}" if status else "SDK_ERROR", error_class) from None
                if what == "conn":
                    self._pending.setdefault("body", None)
                    self._write(http_status=None, raw=None, retry_after_s=None, error_class=error_class)
            if attempt > MAX_RETRIES:
                self.log.append({"kind": "retry", "segment": self.segment, "family": self.name,
                                 "order": self._ctx.get("order"), "attempt": attempt, "http_status": status,
                                 "error_class": error_class, "delay_s": None, "exhausted": True})
                raise RunStop("RETRY_EXHAUSTED", f"order {self._ctx.get('order')} after {MAX_RETRIES} retries")
            retry_after = self._last.get("retry_after_s") if self._last else None
            delay = backoff_delay(attempt, retry_after)
            self.log.append({"kind": "retry", "segment": self.segment, "family": self.name,
                             "order": self._ctx.get("order"), "attempt": attempt, "http_status": status,
                             "error_class": error_class, "delay_s": delay, "exhausted": False})
            self.sleep(delay)
        raise AssertionError("unreachable")

    def call(self, order: int, line: str, view: str) -> dict[str, Any]:
        parsed = None
        final: dict[str, Any] | None = None
        n = 0
        for request_n in (1, 2):  # one re-request on an invalid reply
            n = request_n
            self._ctx = {"kind": "attempt", "order": order, "line": line, "request_n": request_n}
            final = self.attempts(view)
            ok = final is not None and final["http_status"] is not None and final["http_status"] < 300
            parsed = self.parse(final["response_body"]) if ok else None
            if parsed is not None:
                break
        rec = {
            "kind": "call", "segment": self.segment, "family": self.name, "order": order, "line": line,
            "n_requests": n, "status": "ok" if parsed else "invalid",
            "decision": parsed[0] if parsed else None, "p_hold": parsed[1] if parsed else None,
            "returned_model": final["returned_model"] if final else "unreported", "done_utc": utc_now(),
        }
        self.log.append(rec)
        return rec


class JevFamily(Family):
    name, usd_in, usd_out, max_out, requested_model = "jev", JEV_USD_IN, JEV_USD_OUT, 0, JEV_MODEL

    def __init__(self, log: Log, *, api_key: str, base_url: str, **kw: Any) -> None:
        import httpx2
        from typesafe_sdk import RetryPolicy, TypeSafeClient

        super().__init__(log, **kw)
        root = resolve_jev_root(base_url)
        self._http = httpx2.Client(timeout=HTTP_TIMEOUT_S,
                                   event_hooks={"request": [self._on_request], "response": [self._on_response]})
        self._client = TypeSafeClient(api_key=api_key, base_url=root, model=JEV_MODEL,
                                      retry=RetryPolicy(max_retries=0), http_client=self._http)

    def wire(self, view: str) -> bytes:
        return jev_wire(view)

    def send(self, view: str) -> None:
        from typesafe_sdk import Choice

        self._client.system_one(state=jev_state(view), model=JEV_MODEL,
                                questions={JEV_QID: Choice(instructions=JEV_QUESTION, criteria=JEV_CRITERIA)})

    def parse(self, raw: str | None) -> tuple[str, float] | None:
        return parse_jev(raw)

    def classify(self, exc: Exception) -> tuple[str, int | None, str]:
        from typesafe_sdk import (TypeSafeAPIConnectionError, TypeSafeAPIError, TypeSafeAPIResponseValidationError,
                                  TypeSafeAPITimeoutError)

        name = type(exc).__name__
        if isinstance(exc, TypeSafeAPIResponseValidationError):
            return "validation", None, name
        if isinstance(exc, TypeSafeAPIError):
            if exc.status == 422:
                return "invalid", 422, name
            if exc.status in ENDPOINT_STATUSES:
                return "endpoint", exc.status, name
            return ("retry" if is_retryable(exc.status) else "stop"), exc.status, name
        if isinstance(exc, TypeSafeAPIConnectionError):
            return "conn", None, "timeout" if isinstance(exc, TypeSafeAPITimeoutError) else "connection"
        return "stop", None, name

    def check(self) -> str:
        self._ctx, self._pending = {"kind": "models_list"}, {}
        return ",".join(m.name for m in self._client.models.list().models)

    def close(self) -> None:
        self._client.close()


class HaikuFamily(Family):
    name, usd_in, usd_out, max_out, requested_model = "haiku", HAIKU_USD_IN, HAIKU_USD_OUT, HAIKU_MAX_TOKENS, HAIKU_MODEL

    def __init__(self, log: Log, *, api_key: str, **kw: Any) -> None:
        import anthropic

        super().__init__(log, **kw)
        self._http = anthropic.DefaultHttpxClient(
            timeout=HTTP_TIMEOUT_S, event_hooks={"request": [self._on_request], "response": [self._on_response]})
        self._client = anthropic.Anthropic(api_key=api_key, base_url=HAIKU_BASE_URL, max_retries=0,
                                           http_client=self._http)

    def wire(self, view: str) -> bytes:
        return haiku_wire(view)

    def send(self, view: str) -> None:
        # anthropic 1.x has no `temperature` keyword; it travels in the JSON via extra_body (as paper 6).
        params = haiku_params(view)
        temperature = params.pop("temperature")
        self._client.messages.create(**params, extra_body={"temperature": temperature})

    def parse(self, raw: str | None) -> tuple[str, float] | None:
        return parse_haiku(raw)

    def classify(self, exc: Exception) -> tuple[str, int | None, str]:
        import anthropic

        name = type(exc).__name__
        if isinstance(exc, anthropic.APIResponseValidationError):
            return "validation", None, name
        if isinstance(exc, anthropic.APIStatusError):
            if exc.status_code in ENDPOINT_STATUSES:
                return "endpoint", exc.status_code, name
            return ("retry" if is_retryable(exc.status_code) else "stop"), exc.status_code, name
        if isinstance(exc, anthropic.APIConnectionError):
            return "conn", None, "timeout" if isinstance(exc, anthropic.APITimeoutError) else "connection"
        return "stop", None, name

    def check(self) -> str:
        self._ctx, self._pending = {"kind": "models_retrieve"}, {}
        return self._client.models.retrieve(HAIKU_MODEL).id

    def close(self) -> None:
        self._client.close()


def resolve_jev_root(base_url: str) -> str:
    """API root for the SDK; the resolved endpoint must be the registered one."""
    root = base_url.strip().rstrip("/")
    for suffix in ("/v1/systemone", "/v1"):
        if root.endswith(suffix):
            root = root[: -len(suffix)]
            break
    if root + "/v1/systemone" != JEV_ENDPOINT:
        raise RunStop("ARM_ENDPOINT", "JEV_BASE_URL does not resolve to the registered endpoint")
    return root


def load_inputs(arm: str, root: Path = ROOT) -> list[tuple[int, str, str]]:
    sample = json.loads((root / "results" / "e4" / "sample.json").read_text(encoding="utf-8"))["lines"]
    views_file = root / "results" / "e4" / ARMS[arm][1]
    views = {r["order"]: r["view"] for r in (json.loads(l) for l in views_file.read_text(encoding="utf-8").splitlines())}
    return [(r["order"], r["case_id"], views[r["order"]]) for r in sorted(sample, key=lambda r: r["order"])]


def manifest_path(root: Path = ROOT) -> Path:
    return root / "responses" / "e4" / "manifest-e4.json"


def update_manifest(arm: str, family: str, entry: dict[str, Any], root: Path = ROOT) -> None:
    path = manifest_path(root)
    data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {
        "registration": REGISTRATION, "cap_usd": CAP_USD, "families": {}}
    data["families"].setdefault(arm, {})[family] = entry
    data["committed_usd_total"] = committed_spend(root)
    data["cap_usd"] = CAP_USD
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run(family: str, arm: str = "e4", *, env: dict[str, str] | None = None, limit: int | None = None,
        root: Path = ROOT, sleep: Callable[[float], None] = time.sleep, cap_usd: float = CAP_USD,
        factory: Callable[..., Family] | None = None, print_: Callable[[str], None] = print) -> str:
    env = dict(os.environ) if env is None else env
    log = Log(root / ARMS[arm][0] / family / "responses.jsonl")
    previous = [r for r in log.records() if r.get("kind") == "run_event"]
    segment = uuid.uuid4().hex[:12]
    done = {r["order"]: r for r in log.records() if r.get("kind") == "call"}
    inputs = load_inputs(arm, root)
    fam: Family | None = None
    entry: dict[str, Any] = {
        "family": family, "arm": arm, "label": "exploratory" if arm != "e4" else "primary",
        "requested_model": JEV_MODEL if family == "jev" else HAIKU_MODEL,
        "endpoint": JEV_ENDPOINT if family == "jev" else HAIKU_BASE_URL,
        "sdk": {"typesafe-sdk": JEV_SDK} if family == "jev" else {"anthropic": HAIKU_SDK},
        "price_usd_per_token": {"input": JEV_USD_IN, "output": JEV_USD_OUT} if family == "jev"
        else {"input": HAIKU_USD_IN, "output": HAIKU_USD_OUT},
        "request": {"max_tokens": HAIKU_MAX_TOKENS, "temperature": HAIKU_TEMPERATURE, "prefill": HAIKU_PREFILL}
        if family == "haiku" else {"question_id": JEV_QID, "question": JEV_QUESTION, "criteria": JEV_CRITERIA},
        "health_rule": {"smoke_n": SMOKE_N, "smoke_max_invalid": SMOKE_MAX_INVALID,
                        "health_n": HEALTH_N, "health_max_invalid": HEALTH_MAX_INVALID},
        "python": platform.python_version(), "lines_in_sample": len(inputs),
    }

    def finish(status: str, detail: str = "") -> str:
        calls = {r["order"]: r for r in log.records() if r.get("kind") == "call"}
        attempts = [r for r in log.records() if r.get("kind") == "attempt"]
        models = sorted({r["returned_model"] for r in calls.values() if r["returned_model"] != "unreported"})
        entry.update({
            "status": status, "detail": detail, "lines_done": len(calls),
            "invalid": sum(1 for r in calls.values() if r["status"] == "invalid"),
            "attempts": len(attempts), "spend_usd": sum(float(r["charged_usd"]) for r in attempts),
            "input_tokens": sum(r["usage_input_tokens"] or 0 for r in attempts),
            "output_tokens": sum(r["usage_output_tokens"] or 0 for r in attempts),
            "returned_models": models, "updated_utc": utc_now(),
        })
        log.append({"kind": "run_event", "segment": segment, "family": family, "utc": utc_now(),
                    "status": status, "detail": detail})
        update_manifest(arm, family, entry, root)
        print_(f"e4_run {arm}/{family}: {status} {detail}".rstrip())
        return status

    final = [r for r in previous if r["status"] not in ("PAUSED",)]
    if final:
        return finish(final[-1]["status"], "a previous segment ended the family; not resumable")
    try:
        spend = committed_spend(root)
        kw = {"segment": segment, "sleep": sleep, "cap_usd": cap_usd, "spend": spend}
        if factory is not None:
            fam = factory(log, **kw)
        elif family == "jev":
            if not env.get("JEV_API_KEY", "").strip() or not env.get("JEV_BASE_URL", "").strip():
                return finish("ARM_ENDPOINT", "JEV_API_KEY or JEV_BASE_URL absent")
            fam = JevFamily(log, api_key=env["JEV_API_KEY"].strip(), base_url=env["JEV_BASE_URL"], **kw)
        else:
            if not env.get("ANTHROPIC_API_KEY", "").strip():
                return finish("ARM_ENDPOINT", "ANTHROPIC_API_KEY absent")
            fam = HaikuFamily(log, api_key=env["ANTHROPIC_API_KEY"].strip(), **kw)
        try:
            entry["model_check"] = fam.check()
        except Exception as exc:  # noqa: BLE001
            return finish("ARM_ENDPOINT", f"model check failed: {type(exc).__name__}")
        first_model = next((r["returned_model"] for r in done.values() if r["returned_model"] != "unreported"), None)
        new = 0
        seen: list[dict[str, Any]] = []
        for order, line, view in inputs:
            if order in done:
                rec = done[order]
            else:
                if limit is not None and new >= limit:
                    return finish("PAUSED", f"limit {limit} reached")
                rec = fam.call(order, line, view)
                new += 1
            seen.append(rec)
            model = rec["returned_model"]
            if model != "unreported":
                expected = HAIKU_MODEL if family == "haiku" else (first_model or model)
                first_model = first_model or model
                if model != expected:
                    return finish("MODEL_VERSION_CHANGED", f"order {order}: {model} != {expected}")
            bad = sum(1 for r in seen if r["status"] == "invalid")
            if len(seen) == SMOKE_N and bad > SMOKE_MAX_INVALID:
                return finish("ARM_INVALID", f"first {SMOKE_N} lines: {bad} invalid (max {SMOKE_MAX_INVALID})")
            if len(seen) == HEALTH_N and bad > HEALTH_MAX_INVALID:
                return finish("ARM_INVALID", f"first {HEALTH_N} lines: {bad} invalid (max {HEALTH_MAX_INVALID})")
            if new and new % 100 == 0:
                print_(f"e4_run {arm}/{family}: {len(seen)} lines, USD {fam.spend:.4f}")
        return finish("COMPLETE")
    except RunStop as stop:
        return finish(stop.status, stop.detail)
    finally:
        if fam is not None and hasattr(fam, "close"):
            fam.close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="experiments.e4_run")
    parser.add_argument("--family", choices=FAMILIES, required=True)
    parser.add_argument("--arm", choices=tuple(ARMS), default="e4")
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args(argv)
    status = run(args.family, args.arm, limit=args.limit)
    return 0 if status in ("COMPLETE", "PAUSED") else 2


if __name__ == "__main__":
    sys.exit(main())
