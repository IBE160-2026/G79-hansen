"""Offline retention installer contracts; every Scheduler entry point is shadowed."""

import json
import os
from pathlib import Path
import shutil
import subprocess

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts/install-backup-retention.ps1'


def ps_literal(value):
    return "'" + str(value).replace("'", "''") + "'"


def run_ps(command):
    executable = shutil.which('powershell.exe')
    if not executable:
        pytest.skip('Windows PowerShell unavailable')
    # Do not pass application credentials/configuration to the child process.
    env = {name: os.environ[name] for name in ('PATH', 'SystemRoot', 'TEMP', 'TMP',
                                              'USERPROFILE', 'LOCALAPPDATA', 'APPDATA')
           if name in os.environ}
    return subprocess.run([executable, '-NoProfile', '-NonInteractive', '-Command', command],
                          capture_output=True, text=True, timeout=20, env=env)


def shadow_scheduler(kind='absent'):
    # Write-Host records observations without adding values to a cmdlet's result pipeline.
    return r'''
function Record([string]$name, $values) {
    Write-Host ('CALL:' + (@{name=$name; values=$values} | ConvertTo-Json -Compress -Depth 8))
}
function Get-Item {
    [CmdletBinding()]param([string]$LiteralPath, [switch]$Force)
    if ($LiteralPath -eq 'C:\StudyBuddy-Backup' -or $LiteralPath -like '*.dpapi') {
        throw 'PRIVATE_ROOT_MUST_NOT_BE_READ'
    }
    Microsoft.PowerShell.Management\Get-Item -LiteralPath $LiteralPath -Force:$Force
}
function Get-CimInstance {
    [CmdletBinding()]param($Namespace, $ClassName, $Filter)
    Record 'query' $PSBoundParameters
    if ($global:RetentionTestKind -eq 'query-error') { throw 'SECRET_SENTINEL' }
    if ($global:RetentionTestKind -eq 'collision') { return [pscustomobject]@{TaskName='existing'} }
}
function New-ScheduledTaskAction {
    [CmdletBinding()]param($Execute, $Argument, $WorkingDirectory)
    Record 'action' $PSBoundParameters
    return [pscustomobject]@{mock='action'}
}
function New-ScheduledTaskTrigger {
    [CmdletBinding()]param([switch]$Daily, [datetime]$At, [switch]$AtLogOn, $User)
    $values = @{} + $PSBoundParameters
    if ($Daily) { $values.At = $At.ToString('HH:mm:ss') }
    Record 'trigger' $values
    return [pscustomobject]@{mock='trigger'}
}
function New-ScheduledTaskPrincipal {
    [CmdletBinding()]param($UserId, $LogonType, $RunLevel)
    Record 'principal' $PSBoundParameters
    return [pscustomobject]@{mock='principal'}
}
function New-ScheduledTaskSettingsSet {
    [CmdletBinding()]param([switch]$StartWhenAvailable, [switch]$AllowStartIfOnBatteries,
        [switch]$DontStopIfGoingOnBatteries, $MultipleInstances, [timespan]$ExecutionTimeLimit,
        [switch]$WakeToRun, [switch]$RunOnlyIfNetworkAvailable)
    $values = @{} + $PSBoundParameters
    $values.ExecutionTimeLimit = $ExecutionTimeLimit.TotalSeconds
    Record 'settings' $values
    return [pscustomobject]@{mock='settings'}
}
function Register-ScheduledTask {
    [CmdletBinding()]param($TaskName, $TaskPath, $Action, $Trigger, $Principal, $Settings,
        [switch]$Force, $Password, $User)
    Record 'register' $PSBoundParameters
    if ($global:RetentionTestKind -eq 'registration-error') { throw 'SECRET_SENTINEL' }
}
function Get-ScheduledTask { throw 'UNEXPECTED_SCHEDULER_CALL' }
function Start-ScheduledTask { throw 'UNEXPECTED_SCHEDULER_CALL' }
function Unregister-ScheduledTask { throw 'UNEXPECTED_SCHEDULER_CALL' }
''' + f'\n$global:RetentionTestKind = {ps_literal(kind)}\n'


def calls(result):
    return [json.loads(line[5:]) for line in result.stdout.splitlines() if line.startswith('CALL:')]


def test_installer_ast_is_ps5_and_has_no_force_registration_or_side_effect_commands():
    command = r'''
$tokens=$null; $errors=$null
$ast=[System.Management.Automation.Language.Parser]::ParseFile(SCRIPT,[ref]$tokens,[ref]$errors)
if ($errors.Count) { exit 1 }
$commands=@($ast.FindAll({param($a) $a -is [System.Management.Automation.Language.CommandAst]},$true))
foreach ($command in $commands) {
    $name=$command.GetCommandName()
    if ($name -in @('Start-ScheduledTask','Unregister-ScheduledTask','Remove-Item','Set-ExecutionPolicy',
                   'Start-Process','Read-Host','Get-Credential')) { exit 2 }
    if ($name -eq 'Register-ScheduledTask' -and
        @($command.CommandElements | Where-Object { $_.ParameterName -eq 'Force' }).Count) { exit 3 }
}
'''.replace('SCRIPT', ps_literal(SCRIPT))
    result = run_ps(command)
    assert result.returncode == 0, result.stdout + result.stderr


def test_pure_plan_returns_deterministic_metadata_without_scheduler_or_private_root():
    result = run_ps(shadow_scheduler('query-error') +
                    f'$a = & {ps_literal(SCRIPT)} -Plan; $b = & {ps_literal(SCRIPT)} -Plan; '
                    'if (($a | ConvertTo-Json -Compress) -cne ($b | ConvertTo-Json -Compress)) { exit 4 }; '
                    '$a | ConvertTo-Json -Compress')
    assert result.returncode == 0, result.stdout + result.stderr
    assert calls(result) == []
    value = json.loads(result.stdout)
    assert value == {
        'TaskName': 'StudyBuddy-Backup-Rotation', 'TaskPath': '\\',
        'Execute': str(ROOT / '.venv/Scripts/pythonw.exe'),
        'Arguments': '-m scripts.backup_studybuddy rotate --root "C:\\StudyBuddy-Backup"',
        'WorkingDirectory': str(ROOT), 'UserId': value['UserId'],
        'LogonType': 'Interactive', 'RunLevel': 'Limited', 'DailyAt': '03:00 local',
        'AtLogOn': value['UserId'], 'StartWhenAvailable': True,
        'AllowStartIfOnBatteries': True, 'DontStopIfGoingOnBatteries': True,
        'MultipleInstances': 'IgnoreNew', 'ExecutionTimeLimit': 'PT5M',
        'WakeToRun': False, 'RunOnlyIfNetworkAvailable': False,
    }
    assert value['UserId'].startswith('S-1-')


def test_installation_registers_only_exact_task_using_current_interactive_user():
    result = run_ps(shadow_scheduler() + f'& {ps_literal(SCRIPT)}')
    assert result.returncode == 0, result.stdout + result.stderr
    observed = calls(result)
    assert [call['name'] for call in observed] == [
        'query', 'action', 'trigger', 'trigger', 'principal', 'settings', 'register']
    values = {call['name']: call['values'] for call in observed}
    assert values['query'] == {
        'Namespace': 'Root/Microsoft/Windows/TaskScheduler', 'ClassName': 'MSFT_ScheduledTask',
        'Filter': "TaskName = 'StudyBuddy-Backup-Rotation' AND TaskPath = '\\\\'",
        'ErrorAction': 1,
    }
    assert values['action'] == {
        'Execute': str(ROOT / '.venv/Scripts/pythonw.exe'),
        'Argument': '-m scripts.backup_studybuddy rotate --root "C:\\StudyBuddy-Backup"',
        'WorkingDirectory': str(ROOT),
    }
    daily, logon = [call['values'] for call in observed if call['name'] == 'trigger']
    assert daily == {'Daily': {'IsPresent': True}, 'At': '03:00:00'}
    assert logon == {'AtLogOn': {'IsPresent': True}, 'User': values['principal']['UserId']}
    assert values['principal'] == {'UserId': logon['User'], 'LogonType': 'Interactive', 'RunLevel': 'Limited'}
    assert values['settings'] == {
        'StartWhenAvailable': {'IsPresent': True}, 'AllowStartIfOnBatteries': {'IsPresent': True},
        'DontStopIfGoingOnBatteries': {'IsPresent': True}, 'MultipleInstances': 'IgnoreNew',
        'ExecutionTimeLimit': 300, 'WakeToRun': {'IsPresent': False},
        'RunOnlyIfNetworkAvailable': {'IsPresent': False},
    }
    assert values['register'] == {
        'TaskName': 'StudyBuddy-Backup-Rotation', 'TaskPath': '\\',
        'Action': {'mock': 'action'}, 'Trigger': [{'mock': 'trigger'}, {'mock': 'trigger'}],
        'Principal': {'mock': 'principal'}, 'Settings': {'mock': 'settings'}, 'ErrorAction': 1,
    }
    assert 'studybuddy-backup: retention-installed' in result.stdout


@pytest.mark.parametrize('kind', ['collision', 'query-error', 'registration-error'])
def test_collision_and_any_scheduler_error_fail_safely_without_replacing(kind):
    result = run_ps(shadow_scheduler(kind) + f'& {ps_literal(SCRIPT)}')
    assert result.returncode == 1
    assert result.stderr == ''
    assert 'SECRET_SENTINEL' not in result.stdout
    assert result.stdout.splitlines()[-1] == 'studybuddy-backup: retention-install-failed'
    observed = calls(result)
    if kind != 'registration-error':
        assert [call['name'] for call in observed] == ['query']
    else:
        assert [call['name'] for call in observed].count('register') == 1
        assert 'Force' not in observed[-1]['values']


@pytest.mark.parametrize('unsafe', ['missing', 'directory', 'reparse'])
def test_invalid_installed_executable_fails_before_scheduler(unsafe):
    command = shadow_scheduler() + r'''
function Get-Item {
    [CmdletBinding()]param([string]$LiteralPath, [switch]$Force)
    if ($LiteralPath -like '*\pythonw.exe') {
        if (KIND -eq 'missing') { throw 'SECRET_SENTINEL' }
        return [pscustomobject]@{PSIsContainer=(KIND -eq 'directory'); Attributes=1024}
    }
    throw 'UNEXPECTED_PATH_READ'
}
& SCRIPT
'''.replace('KIND', ps_literal(unsafe)).replace('SCRIPT', ps_literal(SCRIPT))
    result = run_ps(command)
    assert result.returncode == 1
    assert calls(result) == []
    assert result.stdout.strip() == 'studybuddy-backup: retention-install-failed'
    assert result.stderr == ''
