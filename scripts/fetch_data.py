"""Fetch the registered event logs into data/ and check each SHA-256.

Reads prereg/data.lock. A file already present is hashed, not downloaded again.
A downloaded file whose SHA-256 differs from the lock is deleted. With
``--check`` nothing is downloaded and an absent file is reported.

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


def download(url: str, dest: Path) -> None:
    part = dest.with_suffix(dest.suffix + ".part")
    with urllib.request.urlopen(url, timeout=120) as resp, part.open("wb") as out:
        for block in iter(lambda: resp.read(1 << 20), b""):
            out.write(block)
    part.replace(dest)


def main(argv: list[str]) -> int:
    check_only = "--check" in argv
    entries = tomllib.loads(LOCK.read_text(encoding="utf-8"))
    DATA.mkdir(exist_ok=True)
    ok = True
    rows = []
    for key, entry in entries.items():
        dest = DATA / entry["file"]
        if not dest.exists():
            if check_only:
                print(f"data: {entry['file']} absent")
                ok = False
                continue
            print(f"data: fetching {entry['file']} ({entry['size']:,} bytes)")
            try:
                download(entry["url"], dest)
            except OSError as exc:
                print(f"data: download of {key} failed: {exc}", file=sys.stderr)
                ok = False
                continue
        got = sha256(dest)
        rows.append({"key": key, "file": entry["file"], "url": entry["url"], "size": entry["size"],
                     "sha256_registered": entry["sha256"], "sha256_computed": got, "match": got == entry["sha256"]})
        if got != entry["sha256"]:
            print(f"data: {entry['file']} SHA-256 {got} != registered {entry['sha256']}", file=sys.stderr)
            if not check_only:
                dest.unlink()
                print(f"data: {entry['file']} deleted", file=sys.stderr)
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
