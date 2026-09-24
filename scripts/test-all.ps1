[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Write-TestFile {
    param(
        [string]$Path,
        [string]$Content
    )

    $parent = Split-Path -Parent $Path
    if ($parent) {
        New-Item -ItemType Directory -Force $parent | Out-Null
    }
    [System.IO.File]::WriteAllText(
        $Path,
        $Content,
        [System.Text.UTF8Encoding]::new($false)
    )
}

function Assert-TestFileContains {
    param(
        [string]$Path,
        [string]$Expected
    )

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "missing expected file: $Path"
    }
    $encoding = [System.Text.UTF8Encoding]::new($false, $true)
    if (-not ([System.IO.File]::ReadAllText($Path, $encoding)).Contains($Expected)) {
        throw "expected $Path to contain: $Expected"
    }
}

function Assert-TestDriftOutput {
    param([string]$Text)

    foreach ($expected in @(
        "reviewed config key differs: model_reasoning_effort"
        "reviewed config key missing: features.goals"
    )) {
        if (-not $Text.Contains($expected)) {
            throw "expected output to contain: $expected"
        }
    }
    foreach ($unexpected in @(
        "machine_setting"
        "machine-sensitive-preview-value"
    )) {
        if ($Text.Contains($unexpected)) {
            throw "expected output not to contain: $unexpected"
        }
    }
}

$testRoot = Join-Path ([System.IO.Path]::GetTempPath()) "compass-test-$([guid]::NewGuid().ToString('N'))"
$codexHome = Join-Path $testRoot "codex"
$agentsHome = Join-Path $testRoot "agents"
$claudeHome = Join-Path $testRoot "claude"

try {
    . "$PSScriptRoot\common.ps1"

    $emptyConfigPath = Join-Path $testRoot "empty-config.toml"
    $directoryTarget = Join-Path $testRoot "config-directory"
    Write-TestFile -Path $emptyConfigPath -Content ""
    New-Item -ItemType Directory -Path $directoryTarget | Out-Null
    if (Test-PortableConfigInSync -Source $emptyConfigPath -Destination $directoryTarget) {
        throw "config directory target reported in sync"
    }

    $machineLabel = "preserve caf$([char]0x00E9)"
    Write-TestFile -Path (Join-Path $codexHome "AGENTS.md\local.txt") -Content "preserve this backup`n"
    Write-TestFile -Path (Join-Path $codexHome "auth.json") -Content "leave unlisted state alone`n"
    Write-TestFile -Path (Join-Path $codexHome "config.toml") -Content @"
MODEL = "machine-specific"
model_reasoning_effort = "machine-sensitive-preview-value"
machine_setting = "$machineLabel"

["features"]
memories = false

[projects.'C:\machine']
trust_level = "trusted"
"@

    $configPath = Join-Path $codexHome "config.toml"
    $configBeforePreview = Get-Content -Raw -LiteralPath $configPath
    $powerShellPath = (Get-Process -Id $PID).Path
    $previewOutput = & $powerShellPath `
        -NoProfile `
        -ExecutionPolicy Bypass `
        -File (Join-Path $PSScriptRoot "install.ps1") `
        -CodexHome $codexHome `
        -AgentsHome $agentsHome `
        -ClaudeHome $claudeHome 2>&1 | Out-String
    if ($LASTEXITCODE -ne 0) {
        throw "install preview failed: $previewOutput"
    }
    if ((Get-Content -Raw -LiteralPath $configPath) -cne $configBeforePreview) {
        throw "install preview changed live config"
    }
    Assert-TestDriftOutput -Text $previewOutput

    $verifyOutput = & (Join-Path $PSScriptRoot "verify-live.ps1") `
        -CodexHome $codexHome `
        -AgentsHome $agentsHome `
        -ClaudeHome $claudeHome 6>&1 | Out-String
    Assert-TestDriftOutput -Text $verifyOutput

    & (Join-Path $PSScriptRoot "install.ps1") `
        -Apply `
        -CodexHome $codexHome `
        -AgentsHome $agentsHome `
        -ClaudeHome $claudeHome
    & (Join-Path $PSScriptRoot "verify-live.ps1") `
        -RequireInSync `
        -CodexHome $codexHome `
        -AgentsHome $agentsHome `
        -ClaudeHome $claudeHome

    Assert-TestFileContains -Path (Join-Path $codexHome "config.toml") -Expected 'model = "gpt-5.6-sol"'
    Assert-TestFileContains -Path (Join-Path $codexHome "config.toml") -Expected 'MODEL = "machine-specific"'
    Assert-TestFileContains -Path (Join-Path $codexHome "config.toml") -Expected '["features"]'
    Assert-TestFileContains -Path (Join-Path $codexHome "config.toml") -Expected 'memories = true'
    if ((Get-Content -Raw -LiteralPath (Join-Path $codexHome "config.toml")).Contains("[features]")) {
        throw "config overlay duplicated a quoted table"
    }
    Assert-TestFileContains `
        -Path (Join-Path $codexHome "config.toml") `
        -Expected "machine_setting = `"$machineLabel`""
    Assert-TestFileContains -Path (Join-Path $codexHome "config.toml") -Expected 'trust_level = "trusted"'
    Assert-TestFileContains -Path (Join-Path $codexHome "auth.json") -Expected "leave unlisted state alone"

    $backupRoot = Join-Path $codexHome "portable-backups"
    Assert-TestFileContains `
        -Path (@(Get-ChildItem -LiteralPath $backupRoot -Recurse -Filter "local.txt" -File)[0].FullName) `
        -Expected "preserve this backup"
    if (@(Get-ChildItem -LiteralPath $backupRoot -Recurse -Filter "config.toml" -File).Count -ne 1) {
        throw "expected one live config backup"
    }

    Write-Host "portable tests: ok"
}
finally {
    if (Test-Path -LiteralPath $testRoot) {
        Remove-Item -LiteralPath $testRoot -Recurse -Force
    }
}
