[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$testRoot = Join-Path ([System.IO.Path]::GetTempPath()) "compass-roundtrip-$([guid]::NewGuid().ToString('N'))"
$codexHome = Join-Path $testRoot "codex"
$agentsHome = Join-Path $testRoot "agents"
$claudeHome = Join-Path $testRoot "claude"
$powerShellPath = (Get-Process -Id $PID).Path

function Invoke-TestScript {
    param(
        [string]$Path,
        [string[]]$Arguments,
        [int]$ExpectedExitCode = 0
    )

    $processArguments = @("-NoProfile")
    if ($env:OS -eq "Windows_NT") {
        $processArguments += @("-ExecutionPolicy", "Bypass")
    }
    $processArguments += @("-File", $Path) + $Arguments

    $output = @(& $powerShellPath @processArguments 2>&1 | ForEach-Object { $_.ToString() })
    $exitCode = $LASTEXITCODE
    if ($exitCode -ne $ExpectedExitCode) {
        $output | ForEach-Object { Write-Host $_ }
        $detail = $output -join "`n"
        throw "expected exit code $ExpectedExitCode from $Path, got $exitCode`n$detail"
    }
    return $output
}

function Assert-PathPresent {
    param([string]$Path)

    if (-not (Test-Path -LiteralPath $Path)) {
        throw "expected installed path: $Path"
    }
}

function Assert-TextContains {
    param(
        [string]$Text,
        [string]$Expected
    )

    if (-not $Text.Contains($Expected)) {
        throw "expected text was not preserved: $Expected"
    }
}

try {
    New-Item -ItemType Directory -Force $codexHome, $agentsHome, $claudeHome | Out-Null
    $configPath = Join-Path $codexHome "config.toml"
    $originalConfig = @"
model = "old-model"
service_tier = "flex"
custom_root_value = "keep"

[agents]
max_depth = 1
custom_agent_value = "keep"

[mcp_servers.example]
command = "machine-local-command"

[projects.'C:\work\example']
trust_level = "trusted"

[generated_marketplace]
last_refresh = "machine-local"
"@
    [System.IO.File]::WriteAllText($configPath, $originalConfig, [System.Text.UTF8Encoding]::new($false))

    $homeArguments = @(
        "-CodexHome", $codexHome,
        "-AgentsHome", $agentsHome,
        "-ClaudeHome", $claudeHome,
        "-SkipPluginRetirement",
        "-SkipSkillRuntimeSetup"
    )
    $installPath = Join-Path $PSScriptRoot "install.ps1"
    $verifyPath = Join-Path $PSScriptRoot "verify-live.ps1"

    $preflightSentinel = Join-Path $codexHome "AGENTS.md"
    Set-Content -LiteralPath $preflightSentinel -Encoding utf8NoBOM -Value "preflight sentinel"
    [void](Invoke-TestScript -Path $installPath -Arguments (@(
        "-Apply",
        "-Adopt",
        "-SourceCommit", "not-the-current-head"
    ) + $homeArguments) -ExpectedExitCode 1)
    if ((Get-Content -Raw -LiteralPath $preflightSentinel).Trim() -ne "preflight sentinel") {
        throw "invalid source commit mutated a live target"
    }
    foreach ($unexpectedPath in @(
        (Join-Path $codexHome "portable-backups"),
        (Join-Path $agentsHome "portable-backups"),
        (Join-Path $claudeHome "portable-backups"),
        (Join-Path $codexHome "portable-receipts")
    )) {
        if (Test-Path -LiteralPath $unexpectedPath) {
            throw "invalid source commit created install state: $unexpectedPath"
        }
    }
    Remove-Item -LiteralPath $preflightSentinel -Force

    $reviewOutput = @(Invoke-TestScript -Path $installPath -Arguments $homeArguments)
    if ($reviewOutput -notcontains "planned reviewed config changes:") {
        throw "review mode did not report reviewed config drift"
    }
    if ((Get-Content -Raw -LiteralPath $configPath) -ne $originalConfig) {
        throw "review mode changed live config.toml"
    }
    if (Test-Path -LiteralPath (Join-Path $codexHome "portable-backups")) {
        throw "review mode created a backup"
    }

    $foreignPath = Join-Path (Join-Path (Join-Path $agentsHome "skills") "compass") "SKILL.md"
    New-Item -ItemType Directory -Force (Split-Path -Parent $foreignPath) | Out-Null
    Set-Content -LiteralPath $foreignPath -Encoding utf8NoBOM -Value "foreign skill"
    [void](Invoke-TestScript -Path $installPath -Arguments (@("-Apply") + $homeArguments) -ExpectedExitCode 1)
    if ((Get-Content -Raw -LiteralPath $foreignPath).Trim() -ne "foreign skill") {
        throw "foreign target changed without explicit adoption"
    }

    [void](Invoke-TestScript -Path $installPath -Arguments (@("-Apply", "-Adopt") + $homeArguments))
    [void](Invoke-TestScript -Path $verifyPath -Arguments (@("-SkipCodexCommand", "-SkipPluginCheck", "-RequireInSync") + $homeArguments))

    $installedConfig = Get-Content -Raw -LiteralPath $configPath
    foreach ($preserved in @(
        'service_tier = "flex"',
        'custom_root_value = "keep"',
        'custom_agent_value = "keep"',
        '[mcp_servers.example]',
        'command = "machine-local-command"',
        "[projects.'C:\work\example']",
        '[generated_marketplace]',
        'last_refresh = "machine-local"'
    )) {
        Assert-TextContains -Text $installedConfig -Expected $preserved
    }
    foreach ($managed in @(
        'model = "gpt-5.6-sol"',
        'model_auto_compact_token_limit = 233000',
        'approval_policy = "never"',
        'max_depth = 2',
        'sandbox = "elevated"',
        'hide_full_access_warning = true',
        'tool_namespace = "agents"'
    )) {
        Assert-TextContains -Text $installedConfig -Expected $managed
    }

    $configBackups = @(Get-ChildItem -LiteralPath (Join-Path $codexHome "portable-backups") -Recurse -File -Filter "config.toml")
    if ($configBackups.Count -ne 1) {
        throw "expected exactly one config.toml backup, found $($configBackups.Count)"
    }
    if ((Get-Content -Raw -LiteralPath $configBackups[0].FullName) -ne $originalConfig) {
        throw "config.toml backup did not contain the original live file"
    }

    $receiptRoot = Join-Path $codexHome "portable-receipts"
    $currentReceipt = Join-Path $receiptRoot "current.json"
    Assert-PathPresent -Path $currentReceipt
    $receiptCountBefore = @(Get-ChildItem -LiteralPath $receiptRoot -File -Filter "install-*.json").Count

    $secondInstall = @(Invoke-TestScript -Path $installPath -Arguments (@("-Apply") + $homeArguments))
    if (@($secondInstall | Where-Object { $_ -like "installed:*" }).Count -gt 0) {
        throw "unchanged second install copied portable items"
    }
    if ($secondInstall -notcontains "reviewed config unchanged: $configPath") {
        throw "unchanged second install did not report reviewed config idempotence"
    }
    if ($secondInstall -notcontains "backups: none") {
        throw "unchanged second install created a backup root"
    }
    if ($secondInstall -notcontains "receipt: unchanged") {
        throw "unchanged second install rewrote installation provenance"
    }
    $receiptCountAfter = @(Get-ChildItem -LiteralPath $receiptRoot -File -Filter "install-*.json").Count
    if ($receiptCountAfter -ne $receiptCountBefore) {
        throw "unchanged second install created another receipt"
    }

    Assert-PathPresent -Path (Join-Path $codexHome "AGENTS.md")
    Assert-PathPresent -Path (Join-Path (Join-Path (Join-Path $agentsHome "skills") "compass") "SKILL.md")
    Assert-PathPresent -Path (Join-Path (Join-Path (Join-Path $agentsHome "skills") "behavior-validator") "SKILL.md")
    Assert-PathPresent -Path (Join-Path $claudeHome "CLAUDE.md")
    Assert-PathPresent -Path (Join-Path (Join-Path (Join-Path $claudeHome "skills") "compass") "SKILL.md")
    Assert-PathPresent -Path (Join-Path (Join-Path (Join-Path $claudeHome "skills") "behavior-validator") "SKILL.md")
    Assert-PathPresent -Path (Join-Path (Join-Path (Join-Path (Join-Path $claudeHome "skills") "pr-review-loop") "scripts") "build-review-bundle.py")
    Assert-PathPresent -Path (Join-Path (Join-Path $claudeHome "agents") "progress-monitor.md")
    Assert-PathPresent -Path (Join-Path (Join-Path $claudeHome "agents") "reviewer.md")

    $whichLlmRoot = Join-Path (Join-Path $agentsHome "skills") "which-llm"
    $runtimeArtifact = Join-Path (Join-Path $whichLlmRoot "artifacts") "exports\local.csv"
    $runtimeCache = Join-Path (Join-Path $whichLlmRoot "__pycache__") "query.pyc"
    New-Item -ItemType Directory -Force (Split-Path -Parent $runtimeArtifact), (Split-Path -Parent $runtimeCache) | Out-Null
    Set-Content -LiteralPath $runtimeArtifact -Value "local runtime data"
    Set-Content -LiteralPath $runtimeCache -Value "local cache"
    [void](Invoke-TestScript -Path $verifyPath -Arguments (@("-SkipCodexCommand", "-SkipPluginCheck", "-RequireInSync") + $homeArguments))

    $whichLlmManagedFile = Join-Path $whichLlmRoot "pick.py"
    Add-Content -LiteralPath $whichLlmManagedFile -Value "# managed drift"
    [void](Invoke-TestScript -Path $verifyPath -Arguments (@("-SkipCodexCommand", "-SkipPluginCheck", "-RequireInSync") + $homeArguments) -ExpectedExitCode 1)
    [void](Invoke-TestScript -Path $installPath -Arguments (@("-Apply") + $homeArguments))
    foreach ($runtimePath in @($runtimeArtifact, $runtimeCache)) {
        Assert-PathPresent -Path $runtimePath
    }
    [void](Invoke-TestScript -Path $verifyPath -Arguments (@("-SkipCodexCommand", "-SkipPluginCheck", "-RequireInSync") + $homeArguments))

    $missingConfig = (Get-Content -Raw -LiteralPath $configPath) -replace '(?m)^model_auto_compact_token_limit = 233000\r?\n', ''
    [System.IO.File]::WriteAllText($configPath, $missingConfig, [System.Text.UTF8Encoding]::new($false))
    $missingOutput = @(Invoke-TestScript -Path $verifyPath -Arguments (@("-SkipCodexCommand", "-SkipPluginCheck", "-RequireInSync") + $homeArguments) -ExpectedExitCode 1)
    if (@($missingOutput | Where-Object { $_ -like "*missing reviewed config key: model_auto_compact_token_limit,*" }).Count -eq 0) {
        throw "verification did not report a missing reviewed config key"
    }
    [void](Invoke-TestScript -Path $installPath -Arguments (@("-Apply") + $homeArguments))

    $mismatchedConfig = (Get-Content -Raw -LiteralPath $configPath) -replace 'model = "gpt-5.6-sol"', 'model = "wrong-model"'
    [System.IO.File]::WriteAllText($configPath, $mismatchedConfig, [System.Text.UTF8Encoding]::new($false))
    $mismatchOutput = @(Invoke-TestScript -Path $verifyPath -Arguments (@("-SkipCodexCommand", "-SkipPluginCheck", "-RequireInSync") + $homeArguments) -ExpectedExitCode 1)
    if (@($mismatchOutput | Where-Object { $_ -like '*reviewed config mismatch: model = "wrong-model", expected "gpt-5.6-sol"*' }).Count -eq 0) {
        throw "verification did not report a reviewed config mismatch"
    }
    [void](Invoke-TestScript -Path $installPath -Arguments (@("-Apply") + $homeArguments))
    [void](Invoke-TestScript -Path $verifyPath -Arguments (@("-SkipCodexCommand", "-SkipPluginCheck", "-RequireInSync") + $homeArguments))

    $driftPath = Join-Path (Join-Path (Join-Path $agentsHome "skills") "compass") "SKILL.md"
    Add-Content -LiteralPath $driftPath -Value "roundtrip drift"
    [void](Invoke-TestScript -Path $verifyPath -Arguments (@("-SkipCodexCommand", "-SkipPluginCheck", "-RequireInSync") + $homeArguments) -ExpectedExitCode 1)

    [void](Invoke-TestScript -Path $installPath -Arguments (@("-Apply") + $homeArguments))
    [void](Invoke-TestScript -Path $verifyPath -Arguments (@("-SkipCodexCommand", "-SkipPluginCheck", "-RequireInSync") + $homeArguments))

    $retiredPaths = @(
        (Join-Path (Join-Path $codexHome "skills") "proper-flowcharts"),
        (Join-Path (Join-Path $codexHome "skills") "benchmark-run-operator"),
        (Join-Path (Join-Path $codexHome "skills") "input-token-economy"),
        (Join-Path (Join-Path $codexHome "skills") "using-codex-goals"),
        (Join-Path (Join-Path $agentsHome "skills") "ui-ux-pro-max"),
        (Join-Path (Join-Path $agentsHome "skills") "benchmark-run-operator"),
        (Join-Path (Join-Path $agentsHome "skills") "input-token-economy"),
        (Join-Path (Join-Path $agentsHome "skills") "using-codex-goals"),
        (Join-Path (Join-Path $claudeHome "skills") "benchmark-run-operator"),
        (Join-Path (Join-Path $claudeHome "skills") "input-token-economy"),
        (Join-Path (Join-Path $claudeHome "skills") "using-codex-goals")
    )
    foreach ($retiredPath in $retiredPaths) {
        New-Item -ItemType Directory -Force $retiredPath | Out-Null
        Set-Content -LiteralPath (Join-Path $retiredPath "legacy.txt") -Value "legacy"
    }
    $retiredClaudeAgent = Join-Path (Join-Path $claudeHome "agents") "benchmark-infra-reviewer.md"
    New-Item -ItemType Directory -Force (Split-Path -Parent $retiredClaudeAgent) | Out-Null
    Set-Content -LiteralPath $retiredClaudeAgent -Value "legacy"

    [void](Invoke-TestScript -Path $installPath -Arguments (@("-Apply") + $homeArguments))
    foreach ($retiredPath in $retiredPaths) {
        if (Test-Path -LiteralPath $retiredPath) {
            throw "retired skill was not removed: $retiredPath"
        }
    }
    if (Test-Path -LiteralPath $retiredClaudeAgent) {
        throw "retired Claude agent was not removed: $retiredClaudeAgent"
    }
    [void](Invoke-TestScript -Path $verifyPath -Arguments (@("-SkipCodexCommand", "-SkipPluginCheck", "-RequireInSync") + $homeArguments))

    Write-Host "install round trip: ok"
}
catch {
    $diagnosticPath = Join-Path $repoRoot "compass-roundtrip-error.txt"
    $diagnostic = @(
        $_ | Format-List * -Force | Out-String
        "script stack:"
        $_.ScriptStackTrace
    ) -join "`n"
    [System.IO.File]::WriteAllText($diagnosticPath, $diagnostic)
    throw
}
finally {
    if (Test-Path -LiteralPath $testRoot) {
        Remove-Item -LiteralPath $testRoot -Recurse -Force
    }
}
