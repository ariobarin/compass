[CmdletBinding(DefaultParameterSetName = "Run", SupportsShouldProcess = $true)]
param(
    [string]$CodexHome,
    [string]$StateDir,
    [string]$TaskName = "Codex Restart Recovery",
    [string]$TaskPath = "\Compass\",
    [string]$Prompt = "Resume the interrupted task. Reopen repository guidance and any named goal, plan, ledger, or checkpoint. Verify current state before continuing.",
    [ValidateRange(1, 720)]
    [int]$LookbackHours = 24,
    [ValidateRange(1, 20)]
    [int]$MaxThreads = 1,
    [ValidateRange(1, 60)]
    [int]$DelayMinutes = 2,
    [Parameter(ParameterSetName = "Preview")]
    [switch]$DryRun,
    [Parameter(ParameterSetName = "Install")]
    [switch]$InstallTask,
    [Parameter(ParameterSetName = "Uninstall")]
    [switch]$UninstallTask,
    [Parameter(ParameterSetName = "Mark")]
    [switch]$MarkCurrentBootHandled
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

. "$PSScriptRoot\common.ps1"

$resolvedCodexHome = Get-CodexHome -CodexHome $CodexHome
if (-not $StateDir) {
    $StateDir = Join-Path $resolvedCodexHome "restart-recovery"
}
$resolvedStateDir = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($StateDir)

$logPath = Join-Path $resolvedStateDir "restart-recovery.log"
$stateFile = Join-Path $resolvedStateDir "last-processed-boot.txt"
$sessionsRoot = Join-Path $resolvedCodexHome "sessions"
$sessionIndexPath = Join-Path $resolvedCodexHome "session_index.jsonl"

function Get-NormalizedTaskPath {
    $path = $TaskPath
    if (-not $path.StartsWith("\")) {
        $path = "\$path"
    }
    if (-not $path.EndsWith("\")) {
        $path = "$path\"
    }
    return $path
}

$resolvedTaskPath = Get-NormalizedTaskPath
$qualifiedTaskName = "$resolvedTaskPath$TaskName"

function Write-RecoveryLog {
    param([string]$Message)

    New-Item -ItemType Directory -Force -Path $resolvedStateDir | Out-Null
    $line = "{0} {1}" -f (Get-Date).ToString("o"), $Message
    Add-Content -Path $logPath -Value $line
}

function ConvertTo-TaskArgument {
    param([string]$Value)

    return "`"$($Value -replace '`', '``' -replace '"', '`"')`""
}

function Get-JsonProperty {
    param(
        $Object,
        [string]$Name
    )

    if ($null -eq $Object) {
        return $null
    }

    $property = $Object.PSObject.Properties[$Name]
    if ($property) {
        return $property.Value
    }

    return $null
}

function Get-RecoveryBootKey {
    return (Get-CimInstance Win32_OperatingSystem).LastBootUpTime.ToUniversalTime().ToString("o")
}

function Get-RecoveryBootTimeUtc {
    return (Get-CimInstance Win32_OperatingSystem).LastBootUpTime.ToUniversalTime()
}

function Get-TextFromContent {
    param($Content)

    if ($null -eq $Content) {
        return ""
    }

    $parts = @()
    foreach ($item in @($Content)) {
        $text = Get-JsonProperty -Object $item -Name "text"
        if ($null -ne $text) {
            $parts += [string]$text
        }
    }
    return ($parts -join "`n")
}

function Get-SessionIdFromPath {
    param([string]$Path)

    $match = [regex]::Match($Path, "([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})\.jsonl$")
    if ($match.Success) {
        return $match.Groups[1].Value
    }
    return $null
}

function Get-ThreadNameMap {
    $map = @{}
    if (-not (Test-Path $sessionIndexPath)) {
        return $map
    }

    foreach ($line in Get-Content -Path $sessionIndexPath -Tail 500) {
        if ([string]::IsNullOrWhiteSpace($line)) {
            continue
        }

        try {
            $entry = $line | ConvertFrom-Json
            if ($entry.id -and $entry.thread_name) {
                $map[[string]$entry.id] = [string]$entry.thread_name
            }
        }
        catch {
            continue
        }
    }

    return $map
}

function Test-UnfinishedSession {
    param([System.IO.FileInfo]$File)

    $sessionId = Get-SessionIdFromPath -Path $File.FullName
    if (-not $sessionId) {
        return $null
    }

    $lastUserAt = $null
    $lastUserRecord = -1
    $lastFinalAssistantRecord = -1
    $lastAbortRecord = -1
    $lastTaskStartedRecord = -1
    $lastTaskCompleteRecord = -1
    $recordIndex = 0

    foreach ($line in Get-Content -Path $File.FullName) {
        $recordIndex++
        if ([string]::IsNullOrWhiteSpace($line)) {
            continue
        }

        try {
            $record = $line | ConvertFrom-Json
        }
        catch {
            continue
        }

        $recordType = Get-JsonProperty -Object $record -Name "type"
        $payload = Get-JsonProperty -Object $record -Name "payload"
        $payloadType = Get-JsonProperty -Object $payload -Name "type"
        $payloadRole = Get-JsonProperty -Object $payload -Name "role"
        $payloadPhase = Get-JsonProperty -Object $payload -Name "phase"
        $payloadContent = Get-JsonProperty -Object $payload -Name "content"
        $timestampText = Get-JsonProperty -Object $record -Name "timestamp"

        $timestamp = $null
        if ($timestampText) {
            try {
                $timestamp = ([datetimeoffset]$timestampText).UtcDateTime
            }
            catch {
                $timestamp = $null
            }
        }

        if ($recordType -eq "event_msg") {
            if ($payloadType -eq "turn_aborted") {
                $lastAbortRecord = $recordIndex
            }
            elseif ($payloadType -eq "task_started") {
                $lastTaskStartedRecord = $recordIndex
            }
            elseif ($payloadType -eq "task_complete") {
                $lastTaskCompleteRecord = $recordIndex
            }
            continue
        }

        if ($recordType -ne "response_item" -or $payloadType -ne "message") {
            continue
        }

        if ($payloadRole -eq "user") {
            $lastUserAt = $timestamp
            $lastUserRecord = $recordIndex
            continue
        }

        if ($payloadRole -eq "assistant" -and $payloadPhase -in @("final", "final_answer")) {
            $lastFinalAssistantRecord = $recordIndex
        }
    }

    if (-not $lastUserAt) {
        return $null
    }

    if ($lastTaskCompleteRecord -gt $lastUserRecord) {
        return $null
    }

    if ($lastFinalAssistantRecord -gt $lastUserRecord) {
        return $null
    }

    if ($lastAbortRecord -gt $lastUserRecord -and $lastTaskStartedRecord -lt $lastAbortRecord) {
        return $null
    }

    return [pscustomobject]@{
        SessionId = $sessionId
        Path = $File.FullName
        LastWriteTimeUtc = $File.LastWriteTimeUtc
        LastUserAt = $lastUserAt
    }
}

function Get-RecoveryCandidates {
    $bootUtc = Get-RecoveryBootTimeUtc
    $windowStartUtc = $bootUtc.AddHours(-1 * $LookbackHours)

    if (-not (Test-Path $sessionsRoot)) {
        return @()
    }

    $sessionFiles = Get-ChildItem -Path $sessionsRoot -Recurse -File -Filter "*.jsonl" |
        Where-Object { $_.LastWriteTimeUtc -lt $bootUtc -and $_.LastWriteTimeUtc -ge $windowStartUtc } |
        Sort-Object LastWriteTimeUtc -Descending

    $candidates = @()
    foreach ($file in $sessionFiles) {
        $candidate = Test-UnfinishedSession -File $file
        if ($candidate) {
            $candidates += $candidate
            if ($candidates.Count -ge $MaxThreads) {
                break
            }
        }
    }

    return @($candidates)
}

function Test-RecoveryTaskOwnsScript {
    param($Task)

    $scriptPath = $PSCommandPath
    $matchingAction = @($Task.Actions | Where-Object {
        $_.Execute -ieq "powershell.exe" -and
            ([string]$_.Arguments).IndexOf($scriptPath, [System.StringComparison]::OrdinalIgnoreCase) -ge 0
    })

    return ($matchingAction.Count -gt 0)
}

function Install-RecoveryTask {
    $existingTask = Get-ScheduledTask -TaskName $TaskName -TaskPath $resolvedTaskPath -ErrorAction SilentlyContinue
    if ($existingTask -and -not (Test-RecoveryTaskOwnsScript -Task $existingTask)) {
        throw "refusing to replace existing scheduled task: $qualifiedTaskName"
    }

    $scriptPath = $PSCommandPath
    $args = @(
        "-NoProfile",
        "-ExecutionPolicy Bypass",
        "-WindowStyle Hidden",
        "-File $(ConvertTo-TaskArgument -Value $scriptPath)",
        "-CodexHome $(ConvertTo-TaskArgument -Value $resolvedCodexHome)",
        "-StateDir $(ConvertTo-TaskArgument -Value $resolvedStateDir)",
        "-Prompt $(ConvertTo-TaskArgument -Value $Prompt)",
        "-LookbackHours $LookbackHours",
        "-MaxThreads $MaxThreads",
        "-DelayMinutes $DelayMinutes"
    ) -join " "

    if (-not $PSCmdlet.ShouldProcess($qualifiedTaskName, "register scheduled task")) {
        return
    }

    if ($existingTask) {
        Unregister-ScheduledTask -TaskName $TaskName -TaskPath $resolvedTaskPath -Confirm:$false
    }

    $currentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
    $action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument $args
    $trigger = New-ScheduledTaskTrigger -AtLogOn -User $currentUser
    $trigger.Delay = "PT$($DelayMinutes)M"
    $settings = New-ScheduledTaskSettingsSet `
        -StartWhenAvailable `
        -AllowStartIfOnBatteries `
        -DontStopIfGoingOnBatteries `
        -MultipleInstances IgnoreNew
    $principal = New-ScheduledTaskPrincipal `
        -UserId $currentUser `
        -LogonType Interactive `
        -RunLevel Limited

    Register-ScheduledTask `
        -TaskName $TaskName `
        -TaskPath $resolvedTaskPath `
        -Action $action `
        -Trigger $trigger `
        -Settings $settings `
        -Principal $principal `
        -Description "Once per boot, resume Codex sessions interrupted by restart" | Out-Null

    $bootKey = Get-RecoveryBootKey
    New-Item -ItemType Directory -Force -Path $resolvedStateDir | Out-Null
    Set-Content -Path $stateFile -Value $bootKey
    Write-RecoveryLog "installed task $qualifiedTaskName and marked current boot handled: $bootKey"
    Write-Host "installed task: $qualifiedTaskName"
    Write-Host "marked current boot handled: $bootKey"
}

function Uninstall-RecoveryTask {
    $task = Get-ScheduledTask -TaskName $TaskName -TaskPath $resolvedTaskPath -ErrorAction SilentlyContinue
    if ($task) {
        if (-not (Test-RecoveryTaskOwnsScript -Task $task)) {
            throw "refusing to uninstall unowned scheduled task: $qualifiedTaskName"
        }

        if (-not $PSCmdlet.ShouldProcess($qualifiedTaskName, "unregister scheduled task")) {
            return
        }

        Unregister-ScheduledTask -TaskName $TaskName -TaskPath $resolvedTaskPath -Confirm:$false
        Write-RecoveryLog "uninstalled task $qualifiedTaskName"
        Write-Host "uninstalled task: $qualifiedTaskName"
        return
    }

    Write-Host "task not found: $qualifiedTaskName"
}

if ($InstallTask) {
    Install-RecoveryTask
    return
}

if ($UninstallTask) {
    Uninstall-RecoveryTask
    return
}

$bootKey = Get-RecoveryBootKey

if ($MarkCurrentBootHandled) {
    if (-not $PSCmdlet.ShouldProcess($bootKey, "mark current boot handled")) {
        return
    }

    New-Item -ItemType Directory -Force -Path $resolvedStateDir | Out-Null
    Set-Content -Path $stateFile -Value $bootKey
    Write-RecoveryLog "marked current boot handled: $bootKey"
    Write-Host "marked current boot handled: $bootKey"
    return
}

if (-not $DryRun -and (Test-Path $stateFile)) {
    $lastProcessedBoot = (Get-Content -Path $stateFile -Raw).Trim()
    if ($lastProcessedBoot -eq $bootKey) {
        Write-RecoveryLog "already processed boot $bootKey"
        return
    }
}

if (-not (Get-Command codex -ErrorAction SilentlyContinue)) {
    Write-RecoveryLog "codex command not found"
    throw "codex command not found"
}

$threadNames = Get-ThreadNameMap
$candidates = @(Get-RecoveryCandidates)

if ($DryRun) {
    foreach ($candidate in $candidates) {
        [pscustomobject]@{
            SessionId = $candidate.SessionId
            ThreadName = $threadNames[$candidate.SessionId]
            LastWriteTimeUtc = $candidate.LastWriteTimeUtc
            LastUserAt = $candidate.LastUserAt
        }
    }
    return
}

if (-not $PSCmdlet.ShouldProcess($bootKey, "resume $($candidates.Count) candidate session(s)")) {
    return
}

New-Item -ItemType Directory -Force -Path $resolvedStateDir | Out-Null
Write-RecoveryLog "processing boot $bootKey with $($candidates.Count) candidates"

$bootSafe = ([datetimeoffset]$bootKey).UtcDateTime.ToString("yyyyMMddTHHmmssZ")
$failedSessions = New-Object System.Collections.Generic.List[string]
$oldCodexHome = [Environment]::GetEnvironmentVariable("CODEX_HOME", "Process")
[Environment]::SetEnvironmentVariable("CODEX_HOME", $resolvedCodexHome, "Process")
try {
    foreach ($candidate in $candidates) {
        $name = $threadNames[$candidate.SessionId]
        $safeId = $candidate.SessionId -replace "[^a-zA-Z0-9-]", "_"
        $sessionLog = Join-Path $resolvedStateDir "resume-$bootSafe-$safeId.jsonl"
        Write-RecoveryLog "resuming $($candidate.SessionId) $name"

        & codex exec resume --all --skip-git-repo-check --json $candidate.SessionId $Prompt *> $sessionLog
        $exitCode = $LASTEXITCODE
        Write-RecoveryLog "resume exited $exitCode for $($candidate.SessionId)"
        if ($exitCode -ne 0) {
            $failedSessions.Add($candidate.SessionId)
        }
    }
}
finally {
    if ([string]::IsNullOrEmpty($oldCodexHome)) {
        [Environment]::SetEnvironmentVariable("CODEX_HOME", $null, "Process")
    }
    else {
        [Environment]::SetEnvironmentVariable("CODEX_HOME", $oldCodexHome, "Process")
    }
}

if ($failedSessions.Count -gt 0) {
    Write-RecoveryLog "not marking boot handled because $($failedSessions.Count) resume(s) failed"
    throw "resume failed for $($failedSessions.Count) session(s): $($failedSessions -join ', ')"
}

Set-Content -Path $stateFile -Value $bootKey
Write-RecoveryLog "marked boot handled after successful recovery: $bootKey"
