[CmdletBinding()]
param([switch]$Plan)

# Windows PowerShell 5. Plan reads only installed code paths, never the backup root.
$ErrorActionPreference = 'Stop'
try {
    $repoRoot = [IO.Path]::GetFullPath((Split-Path -Parent $PSScriptRoot))
    $pythonw = Join-Path $repoRoot '.venv\Scripts\pythonw.exe'
    $module = Join-Path $repoRoot 'scripts\backup_studybuddy.py'
    $backupRoot = 'C:\StudyBuddy-Backup'
    foreach ($path in @($repoRoot, $pythonw, $module, $backupRoot)) {
        if ($path -notmatch '^[A-Za-z]:\\' -or $path -match '["\x00-\x1f]' -or
            $path -match '(^|\\)\.\.?($|\\)' -or
            [IO.Path]::GetFullPath($path) -cne $path) { throw 'invalid' }
    }
    # Reject reparse ancestors for the executable and module. Do not inspect C:\StudyBuddy-Backup.
    foreach ($file in @($pythonw, $module)) {
        $item = Get-Item -LiteralPath $file -Force -ErrorAction Stop
        if ($item.PSIsContainer) { throw 'invalid' }
        if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'invalid' }
        $item = $item.Directory
        while ($null -ne $item) {
            if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'invalid' }
            $item = $item.Parent
        }
    }
    $operator = [Security.Principal.WindowsIdentity]::GetCurrent().User.Value
    $metadata = [pscustomobject][ordered]@{
        TaskName = 'StudyBuddy-Backup-Rotation'
        TaskPath = '\'
        Execute = $pythonw
        Arguments = '-m scripts.backup_studybuddy rotate --root "C:\StudyBuddy-Backup"'
        WorkingDirectory = $repoRoot
        UserId = $operator
        LogonType = 'Interactive'
        RunLevel = 'Limited'
        DailyAt = '03:00 local'
        AtLogOn = $operator
        StartWhenAvailable = $true
        AllowStartIfOnBatteries = $true
        DontStopIfGoingOnBatteries = $true
        MultipleInstances = 'IgnoreNew'
        ExecutionTimeLimit = 'PT5M'
        WakeToRun = $false
        RunOnlyIfNetworkAvailable = $false
    }
    if ($Plan) { return $metadata }

    # Exact WQL lookup returns no rows for absence; any query/access error refuses installation.
    # Get-ScheduledTask treats absence as an error, so it cannot distinguish that safely here.
    $existing = @(Get-CimInstance -Namespace 'Root/Microsoft/Windows/TaskScheduler' `
        -ClassName 'MSFT_ScheduledTask' `
        -Filter "TaskName = 'StudyBuddy-Backup-Rotation' AND TaskPath = '\\'" -ErrorAction Stop)
    if ($existing.Count -ne 0) { throw 'collision' }
    $action = New-ScheduledTaskAction -Execute $metadata.Execute -Argument $metadata.Arguments `
        -WorkingDirectory $metadata.WorkingDirectory
    $triggers = @(
        New-ScheduledTaskTrigger -Daily -At ([datetime]::Today.AddHours(3))
        New-ScheduledTaskTrigger -AtLogOn -User $operator
    )
    $principal = New-ScheduledTaskPrincipal -UserId $operator -LogonType Interactive -RunLevel Limited
    $settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries `
        -DontStopIfGoingOnBatteries -MultipleInstances IgnoreNew `
        -ExecutionTimeLimit (New-TimeSpan -Minutes 5) -WakeToRun:$false -RunOnlyIfNetworkAvailable:$false
    # No Force: a task created after our lookup must also cause refusal, never replacement.
    Register-ScheduledTask -TaskName $metadata.TaskName -TaskPath $metadata.TaskPath `
        -Action $action -Trigger $triggers -Principal $principal -Settings $settings `
        -ErrorAction Stop | Out-Null
    Write-Output 'studybuddy-backup: retention-installed'
}
catch {
    Write-Output 'studybuddy-backup: retention-install-failed'
    exit 1
}
