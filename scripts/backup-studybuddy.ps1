[CmdletBinding()]
param(
    [ValidateSet('pack', 'rotate', 'restore')]
    [Parameter(Mandatory = $true)][string]$Action,
    [string]$Source,
    [string]$Root = 'C:\StudyBuddy-Backup',
    [string]$Archive,
    [string]$Destination
)

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$exitCode = 1
Push-Location -LiteralPath $repoRoot
try {
    $uv = Get-Command uv -CommandType Application -ErrorAction Stop
    $uvArguments = @('run', '--offline', '--no-sync', '--locked', '--no-env-file',
                     'python', '-m', 'scripts.backup_studybuddy', $Action)
    switch ($Action) {
        'pack' {
            if (-not $Source) { throw 'invalid' }
            $uvArguments += @('--source', $Source, '--root', $Root)
        }
        'rotate' { $uvArguments += @('--root', $Root) }
        'restore' {
            if (-not $Archive -or -not $Destination) { throw 'invalid' }
            $uvArguments += @('--archive', $Archive, '--destination', $Destination)
        }
    }
    $ErrorActionPreference = 'Continue'
    & $uv.Source @uvArguments 2>$null | ForEach-Object {
        if ($_ -cmatch '^studybuddy-backup: (pack-passed|rotate-passed|restore-passed|backup-failed)$') {
            Write-Output $_
        }
    }
    $exitCode = $LASTEXITCODE
    if ($exitCode -ne 0) { Write-Output 'studybuddy-backup: backup-failed' }
}
catch {
    Write-Output 'studybuddy-backup: backup-failed'
    $exitCode = 1
}
finally {
    Pop-Location
}
exit $exitCode
