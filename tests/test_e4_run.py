"""E4 caller: parsers, the attempt loop, cap, health rule and model check, with a fake family (no network)."""

from __future__ import annotations

import json

import pytest

from experiments import e4_run


def _root(tmp_path, n=25):
    (tmp_path / "results" / "e4").mkdir(parents=True)
    lines = [{"order": i + 1, "case_id": f"{i:016x}"} for i in range(n)]
    (tmp_path / "results" / "e4" / "sample.json").write_text(json.dumps({"lines": lines}))
    view = "Task sentence. Reply with only a JSON object of the form {}.\n\nERP record as of 2018-01-01\nX: y"
    for name in ("views.jsonl", "views-timeline.jsonl"):
        (tmp_path / "results" / "e4" / name).write_text(
            "".join(json.dumps({"order": i + 1, "view": view}) + "\n" for i in range(n)))
    return tmp_path


def haiku_body(text, model=e4_run.HAIKU_MODEL, in_tok=100, out_tok=10):
    return json.dumps({"model": model, "content": [{"type": "text", "text": text}], "stop_reason": "end_turn",
                       "usage": {"input_tokens": in_tok, "output_tokens": out_tok}})


class Fake(e4_run.Family):
    name, usd_in, usd_out, max_out, requested_model = "haiku", 1e-6, 5e-6, 48, e4_run.HAIKU_MODEL

    def __init__(self, log, replies, **kw):
        super().__init__(log, **kw)
        self.replies = list(replies)
        self.sent = 0

    def wire(self, view):
        return e4_run.haiku_wire(view)

    def send(self, view):
        self.sent += 1
        self._pending.update({"body": self.wire(view)})
        reply = self.replies.pop(0) if self.replies else haiku_body('"decision": "hold", "p_hold": 0.9}')
        if isinstance(reply, Exception):
            raise reply
        self._write(http_status=200, raw=reply, retry_after_s=None, error_class=None)

    def classify(self, exc):
        return ("retry", 503, "Busy") if isinstance(exc, ConnectionError) else ("stop", None, type(exc).__name__)

    def parse(self, raw):
        return e4_run.parse_haiku(raw)

    def check(self):
        return e4_run.HAIKU_MODEL


def _run(root, replies=(), **kw):
    holder = {}

    def factory(log, **fkw):
        holder["fam"] = Fake(log, replies, **fkw)
        return holder["fam"]

    status = e4_run.run("haiku", root=root, factory=factory, sleep=lambda s: None, print_=lambda s: None, **kw)
    return status, holder.get("fam")


def test_parsers():
    assert e4_run.parse_haiku(haiku_body('"decision": "clear", "p_hold": 0.2}')) == ("clear", 0.2)
    assert e4_run.parse_haiku(haiku_body('```json\n{"decision": "hold", "p_hold": 1}```')) == ("hold", 1.0)
    for bad in ('"decision": "maybe", "p_hold": 0.2}', '"decision": "hold", "p_hold": 1.5}',
                '"decision": "hold", "p_hold": true}', '"decision": "hold"}', "nonsense"):
        assert e4_run.parse_haiku(haiku_body(bad)) is None
    assert e4_run.parse_haiku(json.dumps({"stop_reason": "refusal", "content": []})) is None
    jev = {"answers": {e4_run.JEV_QID: {"type": "choice", "choice": "hold", "confidence": 0.7,
                                         "probabilities": {"clear": 0.3, "hold": 0.7}}}}
    assert e4_run.parse_jev(json.dumps(jev)) == ("hold", 0.7)
    jev["answers"][e4_run.JEV_QID]["choice"] = "pay"
    assert e4_run.parse_jev(json.dumps(jev)) is None
    assert e4_run.parse_jev("{}") is None and e4_run.parse_jev(None) is None


def test_jev_request_shape_and_endpoint():
    view = "Task. Reply with only a JSON object of the form {}.\n\nERP record\nA: b"
    assert e4_run.jev_state(view) == {"context": "Task.", "record": "ERP record\nA: b"}
    wire = json.loads(e4_run.jev_wire(view))
    assert wire["questions"][e4_run.JEV_QID]["type"] == "choice" and set(wire["questions"][e4_run.JEV_QID]["criteria"]) == {"clear", "hold"}
    for url in ("https://api.typesafe.ai", "https://api.typesafe.ai/v1", "https://api.typesafe.ai/v1/systemone/"):
        assert e4_run.resolve_jev_root(url) == "https://api.typesafe.ai"
    with pytest.raises(e4_run.RunStop):
        e4_run.resolve_jev_root("https://example.com/v1/systemone")
    assert json.loads(e4_run.haiku_wire("v"))["messages"][-1] == {"role": "assistant", "content": "{"}


def test_complete_run_logs_append_only_and_manifest(tmp_path):
    root = _root(tmp_path)
    status, fam = _run(root)
    assert status == "COMPLETE" and fam.sent == 25
    log = e4_run.Log(root / "responses" / "e4" / "haiku" / "responses.jsonl").records()
    calls = [r for r in log if r["kind"] == "call"]
    assert [r["order"] for r in calls] == list(range(1, 26)) and all(r["decision"] == "hold" for r in calls)
    attempts = [r for r in log if r["kind"] == "attempt"]
    assert all(r["charged_usd"] == pytest.approx(100e-6 + 10 * 5e-6) for r in attempts)
    assert all(r["line"] == f"{r['order'] - 1:016x}" for r in attempts)
    man = json.loads((root / "responses" / "e4" / "manifest-e4.json").read_text())
    entry = man["families"]["e4"]["haiku"]
    assert entry["status"] == "COMPLETE" and entry["lines_done"] == 25 and entry["invalid"] == 0
    assert man["committed_usd_total"] == pytest.approx(25 * 150e-6)
    # a finished family is not called again
    status, fam = _run(root)
    assert status == "COMPLETE" and fam is None


def test_rerequest_then_invalid_and_smoke_stop(tmp_path):
    root = _root(tmp_path)
    bad = haiku_body("no json here")
    # line 1: invalid then valid; lines 2-4: invalid twice each -> 3 invalid in the first 20 -> ARM_INVALID
    replies = [bad, haiku_body('"decision": "clear", "p_hold": 0.1}')] + [bad] * 6
    status, _ = _run(root, replies)
    assert status == "ARM_INVALID"
    calls = [r for r in e4_run.Log(root / "responses" / "e4" / "haiku" / "responses.jsonl").records() if r["kind"] == "call"]
    assert calls[0]["n_requests"] == 2 and calls[0]["status"] == "ok" and len(calls) == 20
    assert sum(r["status"] == "invalid" for r in calls) == 3
    status, fam = _run(root)
    assert status == "ARM_INVALID" and fam is None  # final, not resumable


def test_cap_truncates_before_the_attempt(tmp_path):
    root = _root(tmp_path)
    status, fam = _run(root, cap_usd=3 * 150e-6 + 1e-9)
    assert status == "CAP_TRUNCATED"
    calls = [r for r in e4_run.Log(root / "responses" / "e4" / "haiku" / "responses.jsonl").records() if r["kind"] == "call"]
    assert len(calls) <= 3 and e4_run.committed_spend(root) <= 3 * 150e-6 + 1e-9


def test_model_change_stops_and_pause_resumes(tmp_path):
    root = _root(tmp_path)
    status, _ = _run(root, limit=5)
    assert status == "PAUSED"
    status, fam = _run(root, [haiku_body('"decision": "hold", "p_hold": 0.9}', model="claude-other")])
    assert status == "MODEL_VERSION_CHANGED" and fam.sent == 1


def test_retry_then_success(tmp_path):
    root = _root(tmp_path, n=1)
    status, fam = _run(root, [ConnectionError("x"), haiku_body('"decision": "clear", "p_hold": 0.0}')])
    assert status == "COMPLETE" and fam.sent == 2
    log = e4_run.Log(root / "responses" / "e4" / "haiku" / "responses.jsonl").records()
    assert any(r["kind"] == "retry" and r["delay_s"] == 1.0 for r in log)
