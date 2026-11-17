"""Private diagnostic artifacts work on POSIX and Windows without exposing failures."""

import json
import os
from types import SimpleNamespace

import pytest

from aletheia.diagnostics import save_final_check


def record(identifier="record"):
    return SimpleNamespace(id=identifier, model_dump_json=lambda: '{"text":"café — checked"}')


async def test_private_diagnostics_are_utf8_reusable_and_never_overwritten(tmp_path):
    database = tmp_path / "research.sqlite3"
    await save_final_check(database, record())
    directory = tmp_path / "research.sqlite3.diagnostics"
    path = directory / "record.json"
    assert json.loads(path.read_text(encoding="utf-8")) == {"text": "café — checked"}
    await save_final_check(database, record("second"))
    assert (directory / "second.json").exists()
    await save_final_check(
        database, SimpleNamespace(id="record", model_dump_json=lambda: "changed")
    )
    assert json.loads(path.read_text(encoding="utf-8"))["text"] == "café — checked"
    if os.name != "nt":
        assert directory.stat().st_mode & 0o077 == 0
        assert path.stat().st_mode & 0o077 == 0


async def test_permissive_existing_directory_is_refused(tmp_path, caplog):
    database = tmp_path / "research.sqlite3"
    directory = tmp_path / "research.sqlite3.diagnostics"
    directory.mkdir()
    if os.name != "nt":
        directory.chmod(0o755)
    # On Windows, this directory inherits its parent's ACL rather than having
    # the explicitly protected current-user-only ACL required by diagnostics.
    await save_final_check(database, record())
    assert not (directory / "record.json").exists()
    assert "Optional final-check diagnostic could not be saved" in caplog.text
    assert str(tmp_path) not in caplog.text


async def test_redirected_directory_is_refused(tmp_path):
    target = tmp_path / "target"
    target.mkdir(mode=0o700)
    directory = tmp_path / "research.sqlite3.diagnostics"
    try:
        directory.symlink_to(target, target_is_directory=True)
    except OSError:
        pytest.skip("Creating symlinks requires privileges on this Windows host")
    await save_final_check(tmp_path / "research.sqlite3", record())
    assert list(target.iterdir()) == []
