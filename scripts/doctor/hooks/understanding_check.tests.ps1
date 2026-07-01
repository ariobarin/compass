$understandingContext = "Understanding-check override: make this turn about answering the user's understanding check, not carrying out other requested work. Inspect the repo or search the web if needed to understand the reference. Then state whether you understand, restate the likely meaning, and name any remaining ambiguity."
$portableHookGuardModules = @("understanding_check")

Test-PortableGuardContext -Name "understanding explicit phrase" -ExpectedContext $understandingContext -Payload @{
    hook_event_name = "UserPromptSubmit"
    prompt = "Make the hook narrow, do you understand what i mean?"
}
Test-PortableGuardContext -Name "understanding with trailing request" -ExpectedContext $understandingContext -Payload @{
    hook_event_name = "UserPromptSubmit"
    prompt = "Do you understand what I mean? Also update the PR."
}
Test-PortableGuardContext -Name "understanding tool context allowed" -ExpectedContext $understandingContext -Payload @{
    hook_event_name = "UserPromptSubmit"
    prompt = "Inspect the repo and search the web if needed, do you understand what I mean?"
}
Test-PortableGuardContext -Name "understanding or not" -ExpectedContext $understandingContext -Payload @{
    hook_event_name = "UserPromptSubmit"
    prompt = "Do you understand what I mean or not?"
}
Test-PortableGuardContext -Name "understanding qualified phrase" -ExpectedContext $understandingContext -Payload @{
    hook_event_name = "UserPromptSubmit"
    prompt = "Do you understand what I mean by the retry budget?"
}
Test-PortableGuardContext -Name "understanding qualified phrase no question" -ExpectedContext $understandingContext -Payload @{
    hook_event_name = "UserPromptSubmit"
    prompt = "Do you understand what I mean by the retry budget"
}
Test-PortableGuardContext -Name "understanding qualified shorthand" -ExpectedContext $understandingContext -Payload @{
    hook_event_name = "UserPromptSubmit"
    prompt = "The fix should account for repository state, ykwim about the retry budget?"
}
Test-PortableGuardContext -Name "understanding task preamble" -ExpectedContext $understandingContext -Payload @{
    hook_event_name = "UserPromptSubmit"
    prompt = "Test the hook locally, do you understand what I mean?"
}
Test-PortableGuardContext -Name "understanding detect preamble" -ExpectedContext $understandingContext -Payload @{
    hook_event_name = "UserPromptSubmit"
    prompt = "Detect the root cause, do you understand what I mean?"
}
Test-PortableGuardContext -Name "understanding docs preamble" -ExpectedContext $understandingContext -Payload @{
    hook_event_name = "UserPromptSubmit"
    prompt = "Update the docs, do you understand what I mean?"
}
if (Get-Command cmd.exe -ErrorAction SilentlyContinue) {
    $hooksConfig = Get-Content -Raw -Encoding UTF8 -LiteralPath (Join-Path $repoRoot "codex\hooks.json") | ConvertFrom-Json
    $understandingHook = $hooksConfig.hooks.UserPromptSubmit[0].hooks[0]
    if ($understandingHook.commandWindows -match "\`$home\s*=") {
        $problems.Add("understanding hook Windows command assigns read-only home variable")
    }
    if ($understandingHook.commandWindows -notmatch "\`$codexHome") {
        $problems.Add("understanding hook Windows command does not use codexHome variable")
    }
}
Test-PortableGuardLauncherContext -Name "understanding PowerShell launcher" -ExpectedContext $understandingContext -Payload @{
    hook_event_name = "UserPromptSubmit"
    prompt = "Do you understand what I mean by the retry budget?"
}
Test-PortableGuardContext -Name "understanding contractions" -ExpectedContext $understandingContext -Payload @{
    hook_event_name = "UserPromptSubmit"
    prompt = "I don't think you're following, do you understand what i mean?"
}
Test-PortableGuardContext -Name "understanding dykwim question" -ExpectedContext $understandingContext -Payload @{
    hook_event_name = "UserPromptSubmit"
    prompt = "That should answer the understanding check, DyKwIm?"
}
Test-PortableGuardContext -Name "understanding dywim shorthand" -ExpectedContext $understandingContext -Payload @{
    hook_event_name = "UserPromptSubmit"
    prompt = "That needs more context, dywim?"
}
Test-PortableGuardContext -Name "understanding ykwim trailing" -ExpectedContext $understandingContext -Payload @{
    hook_event_name = "UserPromptSubmit"
    prompt = "Keep it focused on the meaning check, ykwim"
}
Test-PortableGuardSilent -Name "understanding implementation request" -Payload @{
    hook_event_name = "UserPromptSubmit"
    prompt = "add a hook off of ``do you understand what i mean?`` / ``dykwim`` / ``ykwim`` etc."
}
Test-PortableGuardSilent -Name "understanding quoted examples" -Payload @{
    hook_event_name = "UserPromptSubmit"
    prompt = 'Detect "do you understand what i mean?" and "ykwim".'
}
Test-PortableGuardSilent -Name "understanding single quoted examples" -Payload @{
    hook_event_name = "UserPromptSubmit"
    prompt = "Detect 'do you understand what i mean?' and 'ykwim'."
}
Test-PortableGuardSilent -Name "understanding double backtick examples" -Payload @{
    hook_event_name = "UserPromptSubmit"
    prompt = "Add support for ``ykwim``."
}
Test-PortableGuardSilent -Name "understanding code block" -Payload @{
    hook_event_name = "UserPromptSubmit"
    prompt = 'Test this fixture: ```text do you understand what i mean? ```'
}
Test-PortableGuardSilent -Name "understanding fixture text" -Payload @{
    hook_event_name = "UserPromptSubmit"
    prompt = "Example prompt: do you understand what i mean? should be covered."
}
Test-PortableGuardSilent -Name "understanding unquoted phrase discussion" -Payload @{
    hook_event_name = "UserPromptSubmit"
    prompt = "The phrase do you understand what i mean is the one we care about."
}
Test-PortableGuardSilent -Name "understanding unquoted review discussion" -Payload @{
    hook_event_name = "UserPromptSubmit"
    prompt = "Review whether do you understand what i mean should be supported."
}
Test-PortableGuardSilent -Name "understanding identifier text" -Payload @{
    hook_event_name = "UserPromptSubmit"
    prompt = "Enable ykwim_enabled in the test config."
}
Test-PortableGuardSilent -Name "understanding definition query" -Payload @{
    hook_event_name = "UserPromptSubmit"
    prompt = "What does dykwim mean?"
}
Test-PortableGuardSilent -Name "understanding what do you mean definition" -Payload @{
    hook_event_name = "UserPromptSubmit"
    prompt = "What do you mean by ykwim?"
}
Test-PortableGuardSilent -Name "understanding phrase definition query" -Payload @{
    hook_event_name = "UserPromptSubmit"
    prompt = "What do you mean by do you understand what I mean?"
}
Test-PortableGuardSilent -Name "understanding self statement" -Payload @{
    hook_event_name = "UserPromptSubmit"
    prompt = "I don't know what I mean."
}

$oldUnderstandingOptOut = [Environment]::GetEnvironmentVariable("CODEX_PORTABLE_DISABLE_UNDERSTANDING_CHECK", "Process")
[Environment]::SetEnvironmentVariable("CODEX_PORTABLE_DISABLE_UNDERSTANDING_CHECK", "1", "Process")
try {
    Test-PortableGuardSilent -Name "understanding opt-out" -Payload @{
        hook_event_name = "UserPromptSubmit"
        prompt = "Do you understand what I mean?"
    }
}
finally {
    [Environment]::SetEnvironmentVariable("CODEX_PORTABLE_DISABLE_UNDERSTANDING_CHECK", $oldUnderstandingOptOut, "Process")
}
