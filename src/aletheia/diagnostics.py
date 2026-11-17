"""Optional diagnostics must not change results, errors, or cancellation."""

import asyncio
import logging
import os
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


async def emit_diagnostic(emit, event, payload):
    task = asyncio.current_task()
    if task is not None and task.cancelling():
        return
    try:
        await emit(event, payload)
    except Exception:
        # Never log exception text, payloads, or tracebacks: they may contain secrets.
        # CancelledError is a BaseException and must continue to propagate.
        logger.warning("Optional research diagnostic could not be saved.")


def private_directory(directory):
    if directory.is_symlink() or directory.is_junction():
        raise OSError("Diagnostic directory is redirected.")
    if os.name == "nt":
        # Windows mode bits do not describe ACLs. Create with a protected ACL and
        # verify it even for preexisting directories; never relax the POSIX guard.
        executable = (
            Path(os.environ["SystemRoot"]) / "System32/WindowsPowerShell/v1.0/powershell.exe"
        )
        script = Path(__file__).with_name("private_directory.ps1").read_text(encoding="utf-8")
        subprocess.run(
            [str(executable), "-NoProfile", "-NonInteractive", "-Command", script],
            env={**os.environ, "ALETHEIA_DIAGNOSTIC_DIRECTORY": str(directory.absolute())},
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
            timeout=15,
        )
    else:
        directory.mkdir(mode=0o700, exist_ok=True)
        if directory.is_symlink() or directory.stat().st_mode & 0o077:
            raise OSError("Diagnostic directory is not restricted.")


async def save_final_check(database_path, record):
    """Local owner-only artifact; deliberately absent from all API and SSE responses."""
    task = asyncio.current_task()
    if task is not None and task.cancelling():
        return
    try:
        directory = database_path.parent / (database_path.name + ".diagnostics")
        await asyncio.to_thread(private_directory, directory)
        path = directory / (record.id + ".json")
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(record.model_dump_json())
    except Exception:
        logger.warning("Optional final-check diagnostic could not be saved.")
