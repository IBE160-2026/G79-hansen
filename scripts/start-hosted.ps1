[CmdletBinding()]
param(
    [string]$EnvFile = '.env.hosted',
    [switch]$Check
)

# Windows PowerShell 5 compatible. Paths and dotenv contents are always data.
$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$exitCode = 1
Push-Location -LiteralPath $repoRoot
try {
    $envItem = Get-Item -LiteralPath $EnvFile -Force -ErrorAction Stop
    if ($envItem.PSIsContainer) { throw 'invalid' }
    $uv = Get-Command uv -CommandType Application -ErrorAction Stop
    $uvArguments = @('run', '--offline', '--no-sync', '--locked', '--no-env-file',
                     'python', '-m', 'scripts.hosted_server', '--env-file', $envItem.FullName)
    if ($Check) { $uvArguments += '--check' }
    # uv's dotenv/parser diagnostics can quote entire secret-bearing input lines.
    # Suppress stderr and admit only our fixed, value-free stdout messages.
    $ErrorActionPreference = 'Continue'
    & $uv.Source @uvArguments 2>$null | ForEach-Object {
        if ($_ -cmatch '^hosted-startup: (check-passed|email-disabled \(password login available\)|environment-invalid|configuration-invalid|state-invalid|model-state-invalid|save-state-invalid|email-state-invalid|backup-retention-failed|port-busy|arguments-invalid|launch-failed)$') {
            Write-Output $_
        }
    }
    $exitCode = $LASTEXITCODE
    if ($exitCode -ne 0) { Write-Output 'hosted-startup: launch-failed' }
}
catch {
    Write-Output 'hosted-startup: environment-or-launch-invalid'
    $exitCode = 1
}
finally {
    Pop-Location
}
exit $exitCode
