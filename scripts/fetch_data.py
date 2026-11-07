"""Fetch the registered event logs into data/ and check each SHA-256.

Reads prereg/data.lock. A file already present is checked (size, then SHA-256), not downloaded
again. A file whose size or SHA-256 differs from the lock is deleted and fetched once more; an
interrupted download is resumed with an HTTP range request where the server allows it. Every attempt
is logged to out/fetch-data/log.txt. With ``--check`` nothing is downloaded and an absent file is
reported.

Exit 0 when every file is present with the registered hash, 1 otherwise.
The script never opens a file's content beyond hashing it. ``--record`` (with ``--check``)
writes results/data-check.json: each file, its registered and computed SHA-256, and the
registered URL it is fetched from (FINAL-AUDIT item 8).
"""

from __future__ import annotations

import hashlib
import json
import sys
import tomllib
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
LOCK = ROOT / "prereg" / "data.lock"
RECORD = ROOT / "results" / "data-check.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


LOG = ROOT / "out" / "fetch-data" / "log.txt"
ATTEMPTS = 2  # a size or hash mismatch is deleted and fetched once more (D-F-1: a transient mismatch)


def log(line: str, err: bool = False) -> None:
    print(line, file=sys.stderr if err else sys.stdout)
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as fh:
        fh.write(line + "\n")


def download(url: str, dest: Path, size: int) -> None:
    """Into dest.part, resuming a shorter .part with an HTTP range request where the server allows it."""
    part = dest.with_suffix(dest.suffix + ".part")
    start = part.stat().st_size if part.exists() else 0
    if start >= size:
        part.unlink()
        start = 0
    req = urllib.request.Request(url, headers={"Range": f"bytes={start}-"} if start else {})
    with urllib.request.urlopen(req, timeout=120) as resp:
        resumed = start and resp.status == 206
        if start and not resumed:
            log(f"data: the server does not resume; fetching {dest.name} from the start")
        with part.open("ab" if resumed else "wb") as out:
            for block in iter(lambda: resp.read(1 << 20), b""):
                out.write(block)
    if part.stat().st_size == size:
        part.replace(dest)


def verify(dest: Path, entry: dict) -> tuple[bool, str, str | None]:
    """Size first (cheap), then SHA-256: (ok, reason, computed hash or None)."""
    got_size = dest.stat().st_size
    if got_size != entry["size"]:
        return False, f"size {got_size:,} != registered {entry['size']:,}", None
    got = sha256(dest)
    if got != entry["sha256"]:
        return False, f"SHA-256 {got} != registered {entry['sha256']}", got
    return True, "ok", got


def fetch(key: str, entry: dict, dest: Path) -> bool:
    for attempt in range(1, ATTEMPTS + 1):
        log(f"data: fetching {entry['file']} ({entry['size']:,} bytes), attempt {attempt} of {ATTEMPTS}")
        try:
            download(entry["url"], dest, entry["size"])
        except OSError as exc:
            log(f"data: attempt {attempt}: download of {key} failed: {exc}", err=True)
            continue
        part = dest.with_suffix(dest.suffix + ".part")
        if not dest.exists():
            log(f"data: attempt {attempt}: {entry['file']} incomplete ({part.stat().st_size:,} of "
                f"{entry['size']:,} bytes); kept to resume", err=True)
            continue
        ok, reason, _ = verify(dest, entry)
        if ok:
            log(f"data: attempt {attempt}: {entry['file']} size and sha256 ok")
            return True
        log(f"data: attempt {attempt}: {entry['file']} {reason}", err=True)
        dest.unlink()
        log(f"data: {entry['file']} deleted", err=True)
    return False


def main(argv: list[str]) -> int:
    check_only = "--check" in argv
    entries = tomllib.loads(LOCK.read_text(encoding="utf-8"))
    DATA.mkdir(exist_ok=True)
    ok = True
    rows = []
    for key, entry in entries.items():
        dest = DATA / entry["file"]
        if dest.exists():
            good, reason, got = verify(dest, entry)
            if not good:
                log(f"data: {entry['file']} {reason}", err=True)
                if not check_only:
                    dest.unlink()
                    log(f"data: {entry['file']} deleted", err=True)
        elif check_only:
            log(f"data: {entry['file']} absent")
            ok = False
            continue
        if not check_only and not dest.exists():
            if not fetch(key, entry, dest):
                ok = False
                continue
            good, reason, got = verify(dest, entry)
        rows.append({"key": key, "file": entry["file"], "url": entry["url"], "size": entry["size"],
                     "sha256_registered": entry["sha256"], "sha256_computed": got, "match": good})
        if not good:
            ok = False
            continue
        print(f"data: {entry['file']} sha256 ok")
    if "--record" in argv and check_only:
        RECORD.write_text(json.dumps({"audit_item": 8, "lock": "prereg/data.lock", "command": "make check-data",
                                      "files": rows, "all_match": ok and len(rows) == len(entries)},
                                     indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
