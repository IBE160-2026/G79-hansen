# Run manually in the same Windows account that will check/export the database.
# Parse inside the safe error boundary: PowerShell binding errors can echo values.
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
$exitCode = 1
$secure = $null
$bstr = [IntPtr]::Zero
$characters = $null
$plain = $null
$stream = $null
$owned = $false
$destinationPath = $null
try {
    $destinationPath = 'C:\StudyBuddy-Backup\.database-password.dpapi'
    if ($args.Count -ne 0) {
        if ($args.Count -ne 2 -or $args[0] -ine '-Destination' -or
            $args[1] -isnot [string]) { throw 'invalid' }
        $destinationPath = $args[1]
    }
    # Only canonical absolute local-drive paths; no ADS, traversal or reparse ancestors.
    if ($destinationPath -notmatch '^[A-Za-z]:\\' -or
        $destinationPath.Substring(2).Contains(':') -or
        [IO.Path]::GetFullPath($destinationPath) -ine $destinationPath -or
        [IO.Path]::GetFileName($destinationPath).EndsWith('.') -or
        [IO.Path]::GetFileName($destinationPath).EndsWith(' ')) { throw 'invalid' }
    $fileName = [IO.Path]::GetFileName($destinationPath)
    if (-not $fileName -or $fileName.IndexOfAny([IO.Path]::GetInvalidFileNameChars()) -ge 0 -or
        $fileName -match '^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(\..*)?$') { throw 'invalid' }
    $parent = [IO.DirectoryInfo]::new([IO.Path]::GetDirectoryName($destinationPath))
    while ($null -ne $parent) {
        $item = Get-Item -LiteralPath $parent.FullName -Force
        if (-not $item.PSIsContainer -or
            ($item.Attributes -band [IO.FileAttributes]::ReparsePoint)) { throw 'invalid' }
        $parent = $parent.Parent
    }
    if (Test-Path -LiteralPath $destinationPath) { throw 'invalid' }

    $secure = Read-Host -Prompt 'Database password' -AsSecureString
    if ($null -eq $secure -or $secure.Length -lt 1 -or $secure.Length -gt 1024) { throw 'invalid' }
    $bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
    $characters = New-Object char[] $secure.Length
    for ($index = 0; $index -lt $characters.Length; $index++) {
        $value = [Runtime.InteropServices.Marshal]::ReadInt16($bstr, 2 * $index) -band 65535
        if ($value -eq 0 -or $value -eq 10 -or $value -eq 13) { throw 'invalid' }
        $characters[$index] = [char]$value
    }
    $plain = [Text.UTF8Encoding]::new($false, $true).GetBytes($characters)
    if ($plain.Length -gt 1024) { throw 'invalid' }
    Add-Type -AssemblyName System.Security
    $protected = [Security.Cryptography.ProtectedData]::Protect(
        $plain, $null, [Security.Cryptography.DataProtectionScope]::CurrentUser)
    $stream = [IO.FileStream]::new($destinationPath, [IO.FileMode]::CreateNew,
        [IO.FileAccess]::Write, [IO.FileShare]::None)
    $owned = $true
    $stream.Write($protected, 0, $protected.Length)
    $stream.Flush($true)
    $stream.Dispose()
    $stream = $null
    $exitCode = 0
}
catch {
    # Never emit exception records, values, paths or plaintext.
}
finally {
    if ($null -ne $stream) { $stream.Dispose() }
    if ($null -ne $plain) { [Array]::Clear($plain, 0, $plain.Length) }
    if ($null -ne $characters) { [Array]::Clear($characters, 0, $characters.Length) }
    if ($bstr -ne [IntPtr]::Zero) { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr) }
    if ($null -ne $secure) { $secure.Dispose() }
    if ($exitCode -ne 0 -and $owned) {
        try { [IO.File]::Delete($destinationPath) } catch { }
    }
}
if ($exitCode -eq 0) { Write-Output 'studybuddy-backup: password-saved' }
else { Write-Output 'studybuddy-backup: password-save-failed' }
exit $exitCode
