import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_every_locked_hash_and_doi_is_in_the_registration() -> None:
    lock = tomllib.loads((ROOT / "prereg" / "data.lock").read_text(encoding="utf-8"))
    prereg = (ROOT / "prereg" / "p7-v1.md").read_text(encoding="utf-8")
    decisions = (ROOT / "DECISIONS.md").read_text(encoding="utf-8")
    assert set(lock) == {"bpi2019", "bpi2020_international", "bpi2020_domestic"}
    for entry in lock.values():
        assert len(entry["sha256"]) == 64
        for text in (prereg, decisions):
            assert entry["sha256"] in text
            assert entry["doi"] in text
            assert entry["file"] in text


def test_engines_lock_names_the_three_siblings() -> None:
    lock = tomllib.loads((ROOT / "engines.lock").read_text(encoding="utf-8"))
    assert set(lock) == {"dqSarc", "sarc-authority-derivation", "gigo-jev-probe"}
    for name, entry in lock.items():
        assert entry["path"] == f"../{name}"
        assert len(entry["commit"]) == 40
