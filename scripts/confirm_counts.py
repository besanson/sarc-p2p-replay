"""Confirm the published case and event counts of a registered XES file.

Counts opening ``<trace`` and ``<event`` tags in a byte stream (plain or gzip).
It reads no attribute, no timestamp and no activity name: this is the only
inspection of the data permitted before the tag ``prereg-p7-v1``.

Usage: python3 -I scripts/confirm_counts.py FILE [FILE ...]
"""

from __future__ import annotations

import gzip
import re
import sys
from pathlib import Path

TRACE = re.compile(rb"<trace[\s>]")
EVENT = re.compile(rb"<event[\s>]")
CHUNK = 1 << 22
CARRY = 16


def count(path: Path) -> tuple[int, int]:
    opener = gzip.open if path.suffix == ".gz" else open
    traces = events = 0
    tail = b""
    with opener(path, "rb") as fh:
        while True:
            block = fh.read(CHUNK)
            if not block:
                break
            buf = tail + block
            # Count only matches that start before the carry region; the carry
            # is re-scanned with the next block so no tag is counted twice.
            limit = len(buf) - CARRY
            traces += sum(1 for m in TRACE.finditer(buf) if m.start() < limit)
            events += sum(1 for m in EVENT.finditer(buf) if m.start() < limit)
            tail = buf[limit:] if limit > 0 else buf
    traces += len(TRACE.findall(tail))
    events += len(EVENT.findall(tail))
    return traces, events


def main(argv: list[str]) -> int:
    for name in argv:
        traces, events = count(Path(name))
        print(f"{Path(name).name}\tcases={traces}\tevents={events}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
