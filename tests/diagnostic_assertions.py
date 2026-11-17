"""Check the artifact's effective access rules using the host's permission model."""

import os
import subprocess
from pathlib import Path


def assert_private_file(path):
    if os.name != "nt":
        assert path.stat().st_mode & 0o077 == 0
        return
    script = """
$ErrorActionPreference = 'Stop'
$sid = [System.Security.Principal.WindowsIdentity]::GetCurrent().User
$file = [System.IO.FileInfo]::new($env:ALETHEIA_TEST_DIAGNOSTIC)
$rules = $file.GetAccessControl().GetAccessRules($true, $true, [System.Security.Principal.SecurityIdentifier])
if ($rules.Count -ne 1 -or $rules[0].IdentityReference -ne $sid -or
    $rules[0].AccessControlType -ne 'Allow' -or $rules[0].FileSystemRights -ne 'FullControl') {
    throw 'Diagnostic file is not private to the current user'
}
"""
    executable = Path(os.environ["SystemRoot"]) / "System32/WindowsPowerShell/v1.0/powershell.exe"
    subprocess.run(
        [str(executable), "-NoProfile", "-NonInteractive", "-Command", script],
        env={**os.environ, "ALETHEIA_TEST_DIAGNOSTIC": str(path)},
        capture_output=True,
        check=True,
        timeout=15,
    )
