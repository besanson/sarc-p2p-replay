import os
import subprocess
import sys
from pathlib import Path

import pytest

import preflight

SENTINEL = "sk-SENTINEL-must-never-appear-0123456789"


def test_smoke_keys_and_data_absent(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """A0 definition of done: preflight passes with keys and data absent."""
    assert preflight.main([], env={}, data_dir=tmp_path) == 0
    out = capsys.readouterr().out
    assert "JEV_API_KEY: absent" in out
    assert "ANTHROPIC_API_KEY: absent" in out
    assert "BPI_Challenge_2019.xes: absent" in out
    assert "keys incomplete" in out and "data incomplete" in out


def test_smoke_as_a_script_with_empty_environment(tmp_path: Path) -> None:
    env = {"PATH": os.environ.get("PATH", ""), "HOME": str(tmp_path)}
    proc = subprocess.run(
        [sys.executable, str(preflight.ROOT / "preflight.py")],
        env=env, capture_output=True, text=True, check=False,
    )
    assert proc.returncode == 0, proc.stderr
    assert "keys (E4 only" in proc.stdout


def test_key_value_never_printed(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    env = {"JEV_API_KEY": SENTINEL, "JEV_BASE_URL": SENTINEL, "ANTHROPIC_API_KEY": SENTINEL}
    preflight.main(["--require", "keys,data,siblings"], env=env, data_dir=tmp_path)
    out = capsys.readouterr()
    assert SENTINEL not in out.out + out.err


def test_alias_and_blank_keys() -> None:
    keys = preflight.check_keys({"TYPESAFE_API_KEY": "k", "JEV_BASE_URL": "  ", "ANTHROPIC_API_KEY": "k"})
    assert keys == {"JEV_API_KEY": True, "JEV_BASE_URL": False, "ANTHROPIC_API_KEY": True}


def test_require_turns_absence_into_failure(tmp_path: Path) -> None:
    assert preflight.main(["--require", "keys"], env={}, data_dir=tmp_path) == 1
    assert preflight.main(["--require=data"], env={}, data_dir=tmp_path) == 3


def test_missing_sibling_and_broken_lock_never_raise(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    (tmp_path / "prereg").mkdir()
    (tmp_path / "prereg" / "data.lock").write_text("not toml [", encoding="utf-8")
    (tmp_path / "engines.lock").write_text('[x]\nurl = "u"\npath = "missing"\ncommit = "abc"\n', encoding="utf-8")
    assert preflight.main([], env={}, data_dir=tmp_path, lock_dir=tmp_path) == 0
    out = capsys.readouterr().out
    assert "x: absent" in out and "error:" in out
    assert preflight.main(["--require", "siblings"], env={}, data_dir=tmp_path, lock_dir=tmp_path) == 2


def test_data_size_mismatch_is_reported(tmp_path: Path) -> None:
    (tmp_path / "DomesticDeclarations.xes.gz").write_bytes(b"x")
    status = preflight.check_data(tmp_path)
    assert status["DomesticDeclarations.xes.gz"] == "size mismatch"
