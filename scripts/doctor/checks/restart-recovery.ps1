$restartRecoveryScript = Join-Path $repoRoot "scripts\codex-restart-recovery.ps1"

function Add-RestartRecoveryProblem {
    param([string]$Message)

    $problems.Add("restart recovery: $Message")
}

function New-RestartRecoveryRecord {
    param(
        [string]$Kind,
        [string]$Role,
        [string]$Phase,
        [string]$Text,
        [string]$EventType
    )

    $payload = [ordered]@{}
    if ($Kind -eq "event_msg") {
        $payload["type"] = $EventType
    }
    else {
        $payload["type"] = "message"
        $payload["role"] = $Role
        if ($Phase) {
            $payload["phase"] = $Phase
        }
        $payload["content"] = @([ordered]@{ text = $Text })
    }

    return ([ordered]@{
        timestamp = (Get-Date).ToUniversalTime().ToString("o")
        type = $Kind
        payload = $payload
    } | ConvertTo-Json -Compress -Depth 8)
}

function New-RestartRecoveryFixture {
    param(
        [string]$Root,
        [string[]]$Lines
    )

    $codexHome = Join-Path $Root "codex-home"
    $sessionsRoot = Join-Path $codexHome "sessions"
    New-Item -ItemType Directory -Force -Path $sessionsRoot | Out-Null
    $sessionId = [guid]::NewGuid().ToString()
    $sessionPath = Join-Path $sessionsRoot "$sessionId.jsonl"
    Set-Content -LiteralPath $sessionPath -Value $Lines -Encoding UTF8
    $bootUtc = (Get-CimInstance Win32_OperatingSystem).LastBootUpTime.ToUniversalTime()
    (Get-Item -LiteralPath $sessionPath).LastWriteTimeUtc = $bootUtc.AddMinutes(-5)

    return [pscustomobject]@{
        CodexHome = $codexHome
        SessionId = $sessionId
        StateDir = Join-Path $Root "state"
    }
}

function New-RestartRecoverySessionFile {
    param(
        [string]$CodexHome,
        [string[]]$Lines,
        [int]$SecondsBeforeBoot
    )

    $sessionsRoot = Join-Path $CodexHome "sessions"
    New-Item -ItemType Directory -Force -Path $sessionsRoot | Out-Null
    $sessionId = [guid]::NewGuid().ToString()
    $sessionPath = Join-Path $sessionsRoot "$sessionId.jsonl"
    Set-Content -LiteralPath $sessionPath -Value $Lines -Encoding UTF8
    $bootUtc = (Get-CimInstance Win32_OperatingSystem).LastBootUpTime.ToUniversalTime()
    (Get-Item -LiteralPath $sessionPath).LastWriteTimeUtc = $bootUtc.AddSeconds(-1 * $SecondsBeforeBoot)

    return [pscustomobject]@{
        SessionId = $sessionId
        Path = $sessionPath
    }
}

function Invoke-RestartRecoveryDryRun {
    param($Fixture)

    return @(& $restartRecoveryScript -CodexHome $Fixture.CodexHome -StateDir $Fixture.StateDir -DryRun)
}

function Get-RestartRecoveryComparableEnv {
    param([string]$Value)

    if ([string]::IsNullOrEmpty($Value)) {
        return $null
    }

    return $Value
}

if (-not (Test-Path -LiteralPath $restartRecoveryScript)) {
    Add-RestartRecoveryProblem "missing script"
}
else {
    $restartRecoveryTemp = Join-Path ([System.IO.Path]::GetTempPath()) "compass-restart-recovery-$([guid]::NewGuid())"
    $oldPath = [Environment]::GetEnvironmentVariable("PATH", "Process")
    $oldFakeEnvOut = [Environment]::GetEnvironmentVariable("FAKE_CODEX_ENV_OUT", "Process")
    $oldFakeExit = [Environment]::GetEnvironmentVariable("FAKE_CODEX_EXIT", "Process")
    $oldCodexHome = [Environment]::GetEnvironmentVariable("CODEX_HOME", "Process")

    try {
        New-Item -ItemType Directory -Force -Path $restartRecoveryTemp | Out-Null
        $fakeBin = Join-Path $restartRecoveryTemp "bin"
        New-Item -ItemType Directory -Force -Path $fakeBin | Out-Null
        $fakeCodex = Join-Path $fakeBin "codex.cmd"
        Set-Content -LiteralPath $fakeCodex -Encoding ASCII -Value @(
            "@echo off",
            "echo CODEX_HOME=%CODEX_HOME%> ""%FAKE_CODEX_ENV_OUT%""",
            "exit /b %FAKE_CODEX_EXIT%"
        )
        [Environment]::SetEnvironmentVariable("PATH", "$fakeBin;$oldPath", "Process")

        $completedFixture = New-RestartRecoveryFixture -Root (Join-Path $restartRecoveryTemp "completed") -Lines @(
            New-RestartRecoveryRecord -Kind "response_item" -Role "user" -Text "do work"
            New-RestartRecoveryRecord -Kind "response_item" -Role "assistant" -Phase "final_answer" -Text "done"
        )
        $completedCandidates = @(Invoke-RestartRecoveryDryRun -Fixture $completedFixture)
        if ($completedCandidates.Count -ne 0) {
            Add-RestartRecoveryProblem "final_answer session was treated as unfinished"
        }

        $taskCompleteFixture = New-RestartRecoveryFixture -Root (Join-Path $restartRecoveryTemp "task-complete") -Lines @(
            New-RestartRecoveryRecord -Kind "response_item" -Role "user" -Text "do work"
            New-RestartRecoveryRecord -Kind "event_msg" -EventType "task_complete"
        )
        $taskCompleteCandidates = @(Invoke-RestartRecoveryDryRun -Fixture $taskCompleteFixture)
        if ($taskCompleteCandidates.Count -ne 0) {
            Add-RestartRecoveryProblem "task_complete session was treated as unfinished"
        }

        $restartAfterAbortFixture = New-RestartRecoveryFixture -Root (Join-Path $restartRecoveryTemp "restart-after-abort") -Lines @(
            New-RestartRecoveryRecord -Kind "response_item" -Role "user" -Text "continue work"
            New-RestartRecoveryRecord -Kind "event_msg" -EventType "turn_aborted"
            New-RestartRecoveryRecord -Kind "event_msg" -EventType "task_started"
        )
        $restartAfterAbortCandidates = @(Invoke-RestartRecoveryDryRun -Fixture $restartAfterAbortFixture)
        if ($restartAfterAbortCandidates.SessionId -notcontains $restartAfterAbortFixture.SessionId) {
            Add-RestartRecoveryProblem "task_started after abort was not treated as unfinished"
        }

        $abortedFixture = New-RestartRecoveryFixture -Root (Join-Path $restartRecoveryTemp "aborted") -Lines @(
            New-RestartRecoveryRecord -Kind "response_item" -Role "user" -Text "stop work"
            New-RestartRecoveryRecord -Kind "event_msg" -EventType "task_started"
            New-RestartRecoveryRecord -Kind "event_msg" -EventType "turn_aborted"
        )
        $abortedCandidates = @(Invoke-RestartRecoveryDryRun -Fixture $abortedFixture)
        if ($abortedCandidates.Count -ne 0) {
            Add-RestartRecoveryProblem "aborted latest turn was treated as unfinished"
        }

        $longTurnLines = New-Object System.Collections.Generic.List[string]
        $longTurnLines.Add((New-RestartRecoveryRecord -Kind "response_item" -Role "user" -Text "long running work"))
        for ($index = 0; $index -lt 601; $index++) {
            $longTurnLines.Add((New-RestartRecoveryRecord -Kind "response_item" -Role "assistant" -Phase "analysis" -Text "still working"))
        }
        $longTurnFixture = New-RestartRecoveryFixture -Root (Join-Path $restartRecoveryTemp "long-turn") -Lines $longTurnLines.ToArray()
        $longTurnCandidates = @(Invoke-RestartRecoveryDryRun -Fixture $longTurnFixture)
        if ($longTurnCandidates.SessionId -notcontains $longTurnFixture.SessionId) {
            Add-RestartRecoveryProblem "long unfinished turn was not treated as unfinished"
        }

        $failedPromptFixture = New-RestartRecoveryFixture -Root (Join-Path $restartRecoveryTemp "failed-prompt") -Lines @(
            New-RestartRecoveryRecord -Kind "response_item" -Role "user" -Text "recover this"
            New-RestartRecoveryRecord -Kind "response_item" -Role "user" -Text "continue, the computer restarted for some reason"
        )
        $failedPromptCandidates = @(Invoke-RestartRecoveryDryRun -Fixture $failedPromptFixture)
        if ($failedPromptCandidates.SessionId -notcontains $failedPromptFixture.SessionId) {
            Add-RestartRecoveryProblem "latest recovery prompt without completion was not retryable"
        }

        $manyFilesRoot = Join-Path $restartRecoveryTemp "many-files"
        $manyFilesCodexHome = Join-Path $manyFilesRoot "codex-home"
        $completedLines = @(
            New-RestartRecoveryRecord -Kind "response_item" -Role "user" -Text "finished work"
            New-RestartRecoveryRecord -Kind "response_item" -Role "assistant" -Phase "final_answer" -Text "done"
        )
        for ($index = 0; $index -lt 101; $index++) {
            [void](New-RestartRecoverySessionFile -CodexHome $manyFilesCodexHome -Lines $completedLines -SecondsBeforeBoot (60 + $index))
        }
        $unfinishedFile = New-RestartRecoverySessionFile `
            -CodexHome $manyFilesCodexHome `
            -Lines @(New-RestartRecoveryRecord -Kind "response_item" -Role "user" -Text "older unfinished work") `
            -SecondsBeforeBoot 600
        $manyFilesFixture = [pscustomobject]@{
            CodexHome = $manyFilesCodexHome
            SessionId = $unfinishedFile.SessionId
            StateDir = Join-Path $manyFilesRoot "state"
        }
        $manyFileCandidates = @(Invoke-RestartRecoveryDryRun -Fixture $manyFilesFixture)
        if ($manyFileCandidates.SessionId -notcontains $unfinishedFile.SessionId) {
            Add-RestartRecoveryProblem "older unfinished session was hidden by newer completed files"
        }

        $successFixture = New-RestartRecoveryFixture -Root (Join-Path $restartRecoveryTemp "success") -Lines @(
            New-RestartRecoveryRecord -Kind "response_item" -Role "user" -Text "recover this"
        )
        $envOut = Join-Path $restartRecoveryTemp "codex-home-env.txt"
        [Environment]::SetEnvironmentVariable("FAKE_CODEX_ENV_OUT", $envOut, "Process")
        [Environment]::SetEnvironmentVariable("FAKE_CODEX_EXIT", "0", "Process")
        try {
            & $restartRecoveryScript -CodexHome $successFixture.CodexHome -StateDir $successFixture.StateDir -MaxThreads 1 | Out-Null
        }
        catch {
            Add-RestartRecoveryProblem "successful fake resume failed: $($_.Exception.Message)"
        }
        $childCodexHome = ""
        if (Test-Path -LiteralPath $envOut) {
            $childCodexHome = (Get-Content -LiteralPath $envOut -Raw).Trim()
        }
        if ($childCodexHome -ne "CODEX_HOME=$($successFixture.CodexHome)") {
            Add-RestartRecoveryProblem "custom Codex home was not passed to child resume"
        }
        if (-not (Test-Path -LiteralPath (Join-Path $successFixture.StateDir "last-processed-boot.txt"))) {
            Add-RestartRecoveryProblem "successful fake resume did not mark boot handled"
        }
        $restoredCodexHome = [Environment]::GetEnvironmentVariable("CODEX_HOME", "Process")
        if ((Get-RestartRecoveryComparableEnv -Value $restoredCodexHome) -ne (Get-RestartRecoveryComparableEnv -Value $oldCodexHome)) {
            Add-RestartRecoveryProblem "Codex home environment was not restored after resume"
        }

        $failureFixture = New-RestartRecoveryFixture -Root (Join-Path $restartRecoveryTemp "failure") -Lines @(
            New-RestartRecoveryRecord -Kind "response_item" -Role "user" -Text "recover this"
        )
        [Environment]::SetEnvironmentVariable("FAKE_CODEX_EXIT", "7", "Process")
        $failedAsExpected = $false
        try {
            & $restartRecoveryScript -CodexHome $failureFixture.CodexHome -StateDir $failureFixture.StateDir -MaxThreads 1 | Out-Null
        }
        catch {
            $failedAsExpected = $true
        }
        if (-not $failedAsExpected) {
            Add-RestartRecoveryProblem "failed fake resume exited successfully"
        }
        if (Test-Path -LiteralPath (Join-Path $failureFixture.StateDir "last-processed-boot.txt")) {
            Add-RestartRecoveryProblem "failed fake resume marked boot handled"
        }

        $whatIfFixture = New-RestartRecoveryFixture -Root (Join-Path $restartRecoveryTemp "what-if") -Lines @(
            New-RestartRecoveryRecord -Kind "response_item" -Role "user" -Text "recover this"
        )
        & powershell.exe `
            -NoProfile `
            -ExecutionPolicy Bypass `
            -File $restartRecoveryScript `
            -CodexHome $whatIfFixture.CodexHome `
            -StateDir $whatIfFixture.StateDir `
            -MarkCurrentBootHandled `
            -WhatIf *> $null
        if ($LASTEXITCODE -ne 0) {
            Add-RestartRecoveryProblem "WhatIf mark exited with $LASTEXITCODE"
        }
        if (Test-Path -LiteralPath (Join-Path $whatIfFixture.StateDir "last-processed-boot.txt")) {
            Add-RestartRecoveryProblem "WhatIf mark wrote boot state"
        }
    }
    catch {
        Add-RestartRecoveryProblem "fixture check threw: $($_.Exception.Message)"
    }
    finally {
        [Environment]::SetEnvironmentVariable("PATH", $oldPath, "Process")
        [Environment]::SetEnvironmentVariable("FAKE_CODEX_ENV_OUT", $oldFakeEnvOut, "Process")
        [Environment]::SetEnvironmentVariable("FAKE_CODEX_EXIT", $oldFakeExit, "Process")
        [Environment]::SetEnvironmentVariable("CODEX_HOME", $oldCodexHome, "Process")
        if (Test-Path -LiteralPath $restartRecoveryTemp) {
            Remove-Item -LiteralPath $restartRecoveryTemp -Recurse -Force
        }
    }
}
