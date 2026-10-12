"""Clone each sibling in engines.lock beside this repository and check out its pin.

A sibling that exists with uncommitted changes is left alone and reported; a
sibling that exists clean is fetched and checked out at the pinned commit.
Exit 0 when every sibling ends at its pin, 2 otherwise.
"""

from __future__ import annotations

import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def git(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=False)


def main() -> int:
    locks = tomllib.loads((ROOT / "engines.lock").read_text(encoding="utf-8"))
    failed = False
    for name, lock in locks.items():
        path = (ROOT / lock["path"]).resolve()
        if not (path / ".git").exists():
            print(f"siblings: cloning {name} into {path}")
            if git("clone", "-q", lock["url"], str(path)).returncode != 0:
                print(f"siblings: clone of {lock['url']} failed", file=sys.stderr)
                failed = True
                continue
        if git("rev-parse", "HEAD", cwd=path).stdout.strip() == lock["commit"]:
            print(f"siblings: {name} at {lock['commit']}")
            continue
        if git("status", "--porcelain", cwd=path).stdout.strip():
            print(f"siblings: {name} has uncommitted changes; not touched", file=sys.stderr)
            failed = True
            continue
        if git("cat-file", "-e", lock["commit"] + "^{commit}", cwd=path).returncode != 0:
            git("fetch", "-q", "origin", cwd=path)
        if git("checkout", "-q", lock["commit"], cwd=path).returncode != 0:
            print(f"siblings: {name} cannot check out {lock['commit']}", file=sys.stderr)
            failed = True
            continue
        print(f"siblings: {name} at {lock['commit']}")
    return 2 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
