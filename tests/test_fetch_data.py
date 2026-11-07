"""scripts/fetch_data.py: size before hash; a mismatch is deleted and fetched once more; both attempts logged."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import fetch_data  # noqa: E402

GOOD = b"registered bytes"
ENTRY = {"file": "log.xes", "url": "https://example.invalid/log", "size": len(GOOD),
         "sha256": hashlib.sha256(GOOD).hexdigest()}


def _patch(monkeypatch, tmp_path, payloads):
    monkeypatch.setattr(fetch_data, "LOG", tmp_path / "log.txt")
    calls = iter(payloads)

    def download(url, dest, size):
        data = next(calls)
        part = dest.with_suffix(dest.suffix + ".part")
        part.write_bytes(data)
        if len(data) == size:
            part.replace(dest)

    monkeypatch.setattr(fetch_data, "download", download)


def test_a_hash_mismatch_is_retried_once(monkeypatch, tmp_path):
    _patch(monkeypatch, tmp_path, [b"Registered bytes", GOOD])  # same size, other hash, then right
    assert fetch_data.fetch("k", ENTRY, tmp_path / "log.xes")
    log = (tmp_path / "log.txt").read_text()
    assert "attempt 1:" in log and "SHA-256" in log and "deleted" in log and "attempt 2: log.xes size and sha256 ok" in log


def test_two_failures_give_up(monkeypatch, tmp_path):
    _patch(monkeypatch, tmp_path, [b"short", b"also short"])
    assert not fetch_data.fetch("k", ENTRY, tmp_path / "log.xes")
    assert (tmp_path / "log.txt").read_text().count("incomplete") == 2


def test_size_is_checked_before_the_hash(tmp_path):
    f = tmp_path / "log.xes"
    f.write_bytes(GOOD + b"!")
    ok, reason, got = fetch_data.verify(f, ENTRY)
    assert not ok and reason.startswith("size") and got is None
