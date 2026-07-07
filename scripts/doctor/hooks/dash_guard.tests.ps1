$dash = [char]0x2014
$portableHookGuardModules = @("dash_guard")

Test-PortableGuardDeny -Name "git commit dash" -ExpectedReasonPattern "plain hyphen" -Payload @{
    hook_event_name = "PreToolUse"
    tool_name = "Bash"
    tool_input = @{
        command = "git commit -m `"bad $dash msg`""
    }
}

Test-PortableGuardDeny -Name "git global option dash" -ExpectedReasonPattern "plain hyphen" -Payload @{
    hook_event_name = "PreToolUse"
    tool_name = "Bash"
    tool_input = @{
        command = "git -C repo commit -m `"bad $dash msg`""
    }
}

Test-PortableGuardDeny -Name "patch dash" -ExpectedReasonPattern "plain hyphen" -Payload @{
    hook_event_name = "PreToolUse"
    tool_name = "apply_patch"
    tool_input = "*** Begin Patch`n*** Add File: sample.md`n+bad $dash msg`n*** End Patch`n"
}

Test-PortableGuardSilent -Name "clean git command" -Payload @{
    hook_event_name = "PreToolUse"
    tool_name = "Bash"
    tool_input = @{
        command = "git status"
    }
}

Test-PortableGuardSilent -Name "read-only gh pr view dash" -Payload @{
    hook_event_name = "PreToolUse"
    tool_name = "Bash"
    tool_input = @{
        command = "gh pr view 68 $dash note"
    }
}

$oldDashOptOut = [Environment]::GetEnvironmentVariable("CODEX_PORTABLE_DISABLE_DASH_GUARD", "Process")
[Environment]::SetEnvironmentVariable("CODEX_PORTABLE_DISABLE_DASH_GUARD", "1", "Process")
try {
    Test-PortableGuardSilent -Name "dash guard opt-out" -Payload @{
        hook_event_name = "PreToolUse"
        tool_name = "Bash"
        tool_input = @{
            command = "git commit -m `"bad $dash msg`""
        }
    }
}
finally {
    [Environment]::SetEnvironmentVariable("CODEX_PORTABLE_DISABLE_DASH_GUARD", $oldDashOptOut, "Process")
}

if (Test-Path -LiteralPath $portableHookLauncherPath) {
    $launcherResult = Invoke-PortableGuardLauncherCase -Name "dash guard" -Payload @{
        hook_event_name = "PreToolUse"
        tool_name = "Bash"
        tool_input = @{
            command = "git commit -m `"bad $dash msg`""
        }
    }
    if ($launcherResult.ExitCode -eq 0 -and -not ($launcherResult.Output -match '"permissionDecision":"deny"')) {
        $problems.Add("portable hook PowerShell launcher did not run dash guard")
    }
}
