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

function Invoke-PortableDefinitionValidation {
    param([string]$Root)

    $python = Get-Command python -ErrorAction SilentlyContinue
    if (-not $python) {
        $python = Get-Command python3 -ErrorAction SilentlyContinue
    }
    if (-not $python) {
        throw "Python 3.11 or newer is required to validate portable definitions"
    }

    $validator = Join-Path $PSScriptRoot "validate-portable-definitions.py"
    $previousErrorAction = $ErrorActionPreference
    try {
        $ErrorActionPreference = "Continue"
        $output = @(& $python.Source $validator $Root 2>&1)
        $exitCode = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $previousErrorAction
    }
    return [pscustomobject]@{
        ExitCode = $exitCode
        Output = $output -join "`n"
    }
}

$testRoot = Join-Path ([System.IO.Path]::GetTempPath()) "compass-test-$([guid]::NewGuid().ToString('N'))"
$codexHome = Join-Path $testRoot "codex"
$agentsHome = Join-Path $testRoot "agents"
$claudeHome = Join-Path $testRoot "claude"

try {
    $repoRoot = Split-Path -Parent $PSScriptRoot
    $invalidRoot = Join-Path $testRoot "invalid-definitions"
    Write-TestFile -Path (Join-Path $invalidRoot "manifests\portable-files.json") -Content @"
{
  "codex": { "agents": ["broken-agent"] },
  "agents": { "skills": ["broken-skill"] },
  "claude": { "skills": [], "agents": [] }
}
"@
    Write-TestFile -Path (Join-Path $invalidRoot "codex\skills\broken-skill\SKILL.md") -Content @"
---
name: wrong-name
description: Deliberately invalid fixture.
---
"@
    Write-TestFile -Path (Join-Path $invalidRoot "codex\agents\broken-agent.toml") -Content @"
name = ["not", "a", "string"]
description = "Deliberately invalid fixture."
developer_instructions = "Do nothing."
"@
    $invalidDefinitions = Invoke-PortableDefinitionValidation -Root $invalidRoot
    if ($invalidDefinitions.ExitCode -eq 0) {
        throw "portable definition validation accepted invalid definitions"
    }
    foreach ($expected in @(
        "Codex agent broken-agent: name must be a non-empty string",
        "shared skill broken-skill: name must match its manifest entry"
    )) {
        if (-not $invalidDefinitions.Output.Contains($expected)) {
            throw "portable definition validation did not report: $expected"
        }
    }

    $validDefinitions = Invoke-PortableDefinitionValidation -Root $repoRoot
    if ($validDefinitions.ExitCode -ne 0) {
        throw $validDefinitions.Output
    }

    $machineLabel = "preserve caf$([char]0x00E9)"
    Write-TestFile -Path (Join-Path $codexHome "AGENTS.md\local.txt") -Content "preserve this backup`n"
    Write-TestFile -Path (Join-Path $codexHome "auth.json") -Content "leave unlisted state alone`n"
    Write-TestFile -Path (Join-Path $codexHome "config.toml") -Content @"
MODEL = "machine-specific"
machine_setting = "$machineLabel"

["features"]
memories = false

[projects.'C:\machine']
trust_level = "trusted"
"@

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

    Write-Host $validDefinitions.Output
    Write-Host "portable tests: ok"
}
finally {
    if (Test-Path -LiteralPath $testRoot) {
        Remove-Item -LiteralPath $testRoot -Recurse -Force
    }
}
