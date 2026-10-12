"""Preflight for sarc-p2p-replay: reports the environment before any run.

Shape as paper 6 (gigo-jev-probe/preflight.py), changed to report rather than
gate (DECISIONS.md D-A0-4). Three items are checked and each is reported as
present or absent:

- keys: the E4 API keys, read from the process environment only (load .env
  first, e.g. ``set -a; . ./.env; set +a``). A key's value is never printed,
  logged or echoed in any form; only its presence is reported.
- data: each registered log in data/, checked against prereg/data.lock (size,
  then SHA-256).
- siblings: each engine in engines.lock, cloned at its path and at its pin.

By default preflight exits 0 whatever it finds, and never raises.
``--require keys,data,siblings`` (any subset) makes a named item a hard
failure: exit 1 keys, 2 siblings, 3 data (the first failing item, in that order).
"""

from __future__ import annotations

import hashlib
import os
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
# Variable -> accepted alias. Values are never printed.
KEYS = {"JEV_API_KEY": "TYPESAFE_API_KEY", "JEV_BASE_URL": None, "ANTHROPIC_API_KEY": None}
ITEMS = ("keys", "siblings", "data")
EXIT = {"keys": 1, "siblings": 2, "data": 3}


def check_keys(env: dict[str, str]) -> dict[str, bool]:
    """Presence of each E4 variable (blank counts as absent)."""
    out = {}
    for name, alias in KEYS.items():
        out[name] = bool(env.get(name, "").strip()) or bool(alias and env.get(alias, "").strip())
    return out


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def check_data(data_dir: Path = ROOT / "data", lock_path: Path = ROOT / "prereg" / "data.lock") -> dict[str, str]:
    """Status per registered file: ok, absent, size mismatch or sha256 mismatch."""
    entries = tomllib.loads(lock_path.read_text(encoding="utf-8"))
    out = {}
    for entry in entries.values():
        path = data_dir / entry["file"]
        if not path.is_file():
            out[entry["file"]] = "absent"
        elif path.stat().st_size != entry["size"]:
            out[entry["file"]] = "size mismatch"
        elif _sha256(path) != entry["sha256"]:
            out[entry["file"]] = "sha256 mismatch"
        else:
            out[entry["file"]] = "ok"
    return out


def check_siblings(lock_path: Path = ROOT / "engines.lock") -> dict[str, str]:
    """Status per sibling: at pin, absent, or off pin (with the head found)."""
    locks = tomllib.loads(lock_path.read_text(encoding="utf-8"))
    out = {}
    for name, lock in locks.items():
        path = (lock_path.parent / lock["path"]).resolve()
        if not (path / ".git").exists():
            out[name] = f"absent (clone {lock['url']} to {path})"
            continue
        head = subprocess.run(
            ["git", "-C", str(path), "rev-parse", "HEAD"], capture_output=True, text=True, check=False
        ).stdout.strip()
        out[name] = "at pin" if head == lock["commit"] else f"off pin (at {head or 'unknown'}, pinned {lock['commit']})"
    return out


def _safe(check, *args):
    try:
        return check(*args), None
    except Exception as exc:  # preflight reports; it never raises
        return {}, f"{type(exc).__name__}: {exc}"


def parse_require(argv: list[str]) -> set[str]:
    required: set[str] = set()
    for i, arg in enumerate(argv):
        value = None
        if arg == "--require" and i + 1 < len(argv):
            value = argv[i + 1]
        elif arg.startswith("--require="):
            value = arg.split("=", 1)[1]
        if value:
            required |= {v.strip() for v in value.split(",") if v.strip() in ITEMS}
    return required


def main(
    argv: list[str] | None = None,
    env: dict[str, str] | None = None,
    data_dir: Path | None = None,
    lock_dir: Path | None = None,
) -> int:
    argv = sys.argv[1:] if argv is None else argv
    env = dict(os.environ) if env is None else env
    data_dir = ROOT / "data" if data_dir is None else data_dir
    lock_dir = ROOT if lock_dir is None else lock_dir
    required = parse_require(argv)

    keys, keys_err = _safe(check_keys, env)
    sibs, sibs_err = _safe(check_siblings, lock_dir / "engines.lock")
    data, data_err = _safe(check_data, data_dir, lock_dir / "prereg" / "data.lock")

    print("preflight: sarc-p2p-replay")
    print("  keys (E4 only; values never shown):")
    for name, present in keys.items():
        print(f"    {name}: {'present' if present else 'absent'}")
    if keys_err:
        print(f"    error: {keys_err}")
    print("  siblings (engines.lock):")
    for name, status in sibs.items():
        print(f"    {name}: {status}")
    if sibs_err:
        print(f"    error: {sibs_err}")
    print("  data (prereg/data.lock):")
    for name, status in data.items():
        print(f"    {name}: {status}")
    if data_err:
        print(f"    error: {data_err}")

    ok = {
        "keys": not keys_err and bool(keys) and all(keys.values()),
        "siblings": not sibs_err and bool(sibs) and all(s == "at pin" for s in sibs.values()),
        "data": not data_err and bool(data) and all(s == "ok" for s in data.values()),
    }
    print("  summary: " + ", ".join(f"{item} {'complete' if ok[item] else 'incomplete'}" for item in ITEMS))
    for item in ITEMS:
        if item in required and not ok[item]:
            print(f"preflight: required item '{item}' incomplete", file=sys.stderr)
            return EXIT[item]
    return 0


if __name__ == "__main__":
    sys.exit(main())
