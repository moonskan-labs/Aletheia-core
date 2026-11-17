# Create with a protected current-user ACL, or verify an existing directory.
# The path is data in an environment variable, never interpolated into commands.
$ErrorActionPreference = 'Stop'
$path = $env:ALETHEIA_DIAGNOSTIC_DIRECTORY
$sid = [System.Security.Principal.WindowsIdentity]::GetCurrent().User
$security = New-Object System.Security.AccessControl.DirectorySecurity
$security.SetOwner($sid)
$security.SetAccessRuleProtection($true, $false)
$rule = New-Object System.Security.AccessControl.FileSystemAccessRule(
    $sid, 'FullControl', 'ContainerInherit,ObjectInherit', 'None', 'Allow')
$security.AddAccessRule($rule)
$directory = [System.IO.Directory]::CreateDirectory($path, $security)
if (($directory.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) {
    throw 'Reparse point refused'
}
$actual = $directory.GetAccessControl()
if (-not $actual.AreAccessRulesProtected -or $actual.GetOwner([System.Security.Principal.SecurityIdentifier]) -ne $sid) {
    throw 'Unprotected directory refused'
}
$rules = $actual.GetAccessRules($true, $true, [System.Security.Principal.SecurityIdentifier])
if ($rules.Count -ne 1 -or $rules[0].IdentityReference -ne $sid -or
    $rules[0].AccessControlType -ne 'Allow' -or
    $rules[0].FileSystemRights -ne 'FullControl' -or
    $rules[0].InheritanceFlags -ne 'ContainerInherit,ObjectInherit' -or
    $rules[0].PropagationFlags -ne 'None') {
    throw 'Directory permissions refused'
}
