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

try {
    New-Item -ItemType Directory -Force $codexHome, $agentsHome, $claudeHome | Out-Null
    Set-Content -LiteralPath (Join-Path $codexHome "config.toml") -Encoding utf8NoBOM -Value @(
        "[agents]",
        "max_depth = 2"
    )

    $homeArguments = @(
        "-CodexHome", $codexHome,
        "-AgentsHome", $agentsHome,
        "-ClaudeHome", $claudeHome
    )
    $installPath = Join-Path $PSScriptRoot "install.ps1"
    $verifyPath = Join-Path $PSScriptRoot "verify-live.ps1"

    [void](Invoke-TestScript -Path $installPath -Arguments (@("-Apply") + $homeArguments))
    [void](Invoke-TestScript -Path $verifyPath -Arguments (@("-SkipCodexCommand", "-RequireInSync") + $homeArguments))

    $secondInstall = @(Invoke-TestScript -Path $installPath -Arguments (@("-Apply") + $homeArguments))
    if (@($secondInstall | Where-Object { $_ -like "installed:*" }).Count -gt 0) {
        throw "unchanged second install copied portable items"
    }
    if ($secondInstall -notcontains "backups: none") {
        throw "unchanged second install created a backup root"
    }

    Assert-PathPresent -Path (Join-Path $codexHome "AGENTS.md")
    Assert-PathPresent -Path (Join-Path (Join-Path (Join-Path $agentsHome "skills") "compass") "SKILL.md")
    Assert-PathPresent -Path (Join-Path (Join-Path (Join-Path $agentsHome "skills") "behavior-validator") "SKILL.md")
    Assert-PathPresent -Path (Join-Path (Join-Path (Join-Path $claudeHome "skills") "compass") "SKILL.md")
    Assert-PathPresent -Path (Join-Path (Join-Path (Join-Path $claudeHome "skills") "behavior-validator") "SKILL.md")
    Assert-PathPresent -Path (Join-Path (Join-Path (Join-Path (Join-Path $claudeHome "skills") "pr-review-loop") "references") "build-review-bundle.py")
    Assert-PathPresent -Path (Join-Path (Join-Path $claudeHome "agents") "reviewer.md")

    $driftPath = Join-Path (Join-Path (Join-Path $agentsHome "skills") "compass") "SKILL.md"
    Add-Content -LiteralPath $driftPath -Value "roundtrip drift"
    [void](Invoke-TestScript -Path $verifyPath -Arguments (@("-SkipCodexCommand", "-RequireInSync") + $homeArguments) -ExpectedExitCode 1)

    [void](Invoke-TestScript -Path $installPath -Arguments (@("-Apply") + $homeArguments))
    [void](Invoke-TestScript -Path $verifyPath -Arguments (@("-SkipCodexCommand", "-RequireInSync") + $homeArguments))

    $retiredCodexSkill = Join-Path (Join-Path $codexHome "skills") "proper-flowcharts"
    $retiredUserSkill = Join-Path (Join-Path $agentsHome "skills") "ui-ux-pro-max"
    New-Item -ItemType Directory -Force $retiredCodexSkill, $retiredUserSkill | Out-Null
    Set-Content -LiteralPath (Join-Path $retiredCodexSkill "legacy.txt") -Value "legacy"
    Set-Content -LiteralPath (Join-Path $retiredUserSkill "legacy.txt") -Value "legacy"

    [void](Invoke-TestScript -Path $installPath -Arguments (@("-Apply") + $homeArguments))
    if (Test-Path -LiteralPath $retiredCodexSkill) {
        throw "retired Codex skill was not removed: $retiredCodexSkill"
    }
    if (Test-Path -LiteralPath $retiredUserSkill) {
        throw "retired user skill was not removed: $retiredUserSkill"
    }
    [void](Invoke-TestScript -Path $verifyPath -Arguments (@("-SkipCodexCommand", "-RequireInSync") + $homeArguments))

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
