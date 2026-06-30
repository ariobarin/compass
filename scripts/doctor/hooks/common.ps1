function Invoke-PortableGuardCase {
    param(
        [string]$Name,
        [hashtable]$Payload
    )

    $moduleArgs = @()
    $moduleVariable = Get-Variable -Name portableHookGuardModules -ErrorAction SilentlyContinue
    if ($moduleVariable) {
        $moduleArgs = @($moduleVariable.Value)
    }
    $payloadText = $Payload | ConvertTo-Json -Compress -Depth 8
    $result = Invoke-DoctorPythonScript -Runner $portableHookPythonRunner -ScriptPath $portableHookGuardPath -InputText $payloadText -Arguments $moduleArgs
    if ($result.ExitCode -ne 0) {
        $problems.Add("portable hook guard failed ${Name}: exit $($result.ExitCode)")
    }
    return $result
}

function Test-PortableGuardSilent {
    param(
        [string]$Name,
        [hashtable]$Payload
    )

    $result = Invoke-PortableGuardCase -Name $Name -Payload $Payload
    if ($result.ExitCode -eq 0 -and $result.Output.Trim()) {
        $problems.Add("portable hook guard emitted output for ${Name}: $($result.Output.Trim())")
    }
}

function Test-PortableGuardDeny {
    param(
        [string]$Name,
        [hashtable]$Payload,
        [string]$ExpectedReasonPattern
    )

    $result = Invoke-PortableGuardCase -Name $Name -Payload $Payload
    if ($result.ExitCode -ne 0) {
        return
    }

    $output = $result.Output.Trim()
    if (-not $output) {
        $problems.Add("portable hook guard did not deny ${Name}")
        return
    }

    try {
        $parsed = $output | ConvertFrom-Json
    }
    catch {
        $problems.Add("portable hook guard emitted invalid deny JSON for ${Name}: $output")
        return
    }

    $hookOutput = $parsed.hookSpecificOutput
    if ($hookOutput.hookEventName -ne "PreToolUse" -or $hookOutput.permissionDecision -ne "deny") {
        $problems.Add("portable hook guard emitted unexpected deny for ${Name}: $output")
    }
    if ($ExpectedReasonPattern -and $hookOutput.permissionDecisionReason -notmatch $ExpectedReasonPattern) {
        $problems.Add("portable hook guard emitted unexpected deny reason for ${Name}: $($hookOutput.permissionDecisionReason)")
    }
}

function Test-PortableGuardBlock {
    param(
        [string]$Name,
        [hashtable]$Payload
    )

    $result = Invoke-PortableGuardCase -Name $Name -Payload $Payload
    if ($result.ExitCode -ne 0) {
        return
    }

    $output = $result.Output.Trim()
    if (-not $output) {
        $problems.Add("portable hook guard did not block ${Name}")
        return
    }

    try {
        $parsed = $output | ConvertFrom-Json
    }
    catch {
        $problems.Add("portable hook guard emitted invalid block JSON for ${Name}: $output")
        return
    }

    if ($parsed.decision -ne "block" -or -not $parsed.reason) {
        $problems.Add("portable hook guard emitted unexpected block for ${Name}: $output")
    }
}

function Test-PortableGuardContext {
    param(
        [string]$Name,
        [hashtable]$Payload,
        [string]$ExpectedContext
    )

    $result = Invoke-PortableGuardCase -Name $Name -Payload $Payload
    if ($result.ExitCode -ne 0) {
        return
    }

    $output = $result.Output.Trim()
    if (-not $output) {
        $problems.Add("portable hook guard emitted no context for ${Name}")
        return
    }

    try {
        $parsed = $output | ConvertFrom-Json
    }
    catch {
        $problems.Add("portable hook emitted invalid context JSON for ${Name}: $output")
        return
    }

    if ($parsed.hookSpecificOutput.hookEventName -ne "UserPromptSubmit") {
        $problems.Add("portable hook unexpected context event for ${Name}: $($parsed.hookSpecificOutput.hookEventName)")
    }
    if ($parsed.hookSpecificOutput.additionalContext -ne $ExpectedContext) {
        $problems.Add("portable hook unexpected context for ${Name}: $($parsed.hookSpecificOutput.additionalContext)")
    }
}

function Invoke-PortableGuardLauncherCase {
    param(
        [string]$Name,
        [hashtable]$Payload
    )

    $payloadText = $Payload | ConvertTo-Json -Compress -Depth 8
    $oldCodexHome = [Environment]::GetEnvironmentVariable("CODEX_HOME", "Process")
    [Environment]::SetEnvironmentVariable("CODEX_HOME", (Join-Path $repoRoot "codex"), "Process")
    try {
        $moduleArgs = @()
        $moduleVariable = Get-Variable -Name portableHookGuardModules -ErrorAction SilentlyContinue
        if ($moduleVariable) {
            $moduleArgs = @($moduleVariable.Value)
        }
        $launcherOutput = $payloadText | & $portableHookLauncherPath @moduleArgs 2>&1
        $exitCode = $LASTEXITCODE
        if ($exitCode -ne 0) {
            $problems.Add("portable hook PowerShell launcher failed ${Name}: exit $exitCode")
        }
        return [pscustomobject]@{
            ExitCode = $exitCode
            Output = ($launcherOutput -join "`n")
        }
    }
    finally {
        [Environment]::SetEnvironmentVariable("CODEX_HOME", $oldCodexHome, "Process")
    }
}

function Test-PortableGuardLauncherSilent {
    param(
        [string]$Name,
        [hashtable]$Payload
    )

    if (-not (Test-Path -LiteralPath $portableHookLauncherPath)) {
        return
    }

    $result = Invoke-PortableGuardLauncherCase -Name $Name -Payload $Payload
    if ($result.ExitCode -eq 0 -and $result.Output.Trim()) {
        $problems.Add("portable hook PowerShell launcher emitted output for ${Name}: $($result.Output.Trim())")
    }
}
