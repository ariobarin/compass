<#
.SYNOPSIS
Measures the active and portable skill routing surface.

.DESCRIPTION
Runs the stdlib-only skill auditor. By default it asks Codex for the exact
model-visible skill inventory and falls back to the portable manifest when that
command is unavailable. Usage logs are opt-in and only aggregate skill mentions.
#>
[CmdletBinding()]
param(
    [switch]$Json,
    [switch]$Plain,
    [switch]$Check,
    [switch]$NoLive,
    [string]$LivePrompt,
    [string[]]$SkillRoot,
    [string[]]$UsageLog,
    [int]$UsageDays = 90,
    [double]$MaxUsageMb = 64,
    [int]$ContextTokens = 272000,
    [double]$BudgetPercent = 2,
    [double]$DuplicateThreshold = 0.85,
    [int]$DescriptionCandidateChars = 120
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
. "$PSScriptRoot\doctor\common.ps1"

if ($Json -and $Plain) {
    throw "choose either -Json or -Plain"
}

$runner = @(Get-DoctorPythonRunner)
if ($runner.Count -eq 0) {
    throw "no runnable Python found for skill auditing"
}

$arguments = @(
    "--root", $repoRoot,
    "--usage-days", $UsageDays,
    "--max-usage-mb", $MaxUsageMb,
    "--context-tokens", $ContextTokens,
    "--budget-percent", $BudgetPercent,
    "--duplicate-threshold", $DuplicateThreshold,
    "--description-candidate-chars", $DescriptionCandidateChars
)
if ($Json) {
    $arguments += "--json"
}
if ($Plain) {
    $arguments += "--plain"
}
if ($Check) {
    $arguments += "--check"
}
if ($NoLive) {
    $arguments += "--no-live"
}
if ($LivePrompt) {
    $arguments += @("--live-prompt", $LivePrompt)
}
foreach ($root in @($SkillRoot)) {
    if ($root) {
        $arguments += @("--skill-root", $root)
    }
}
foreach ($path in @($UsageLog)) {
    if ($path) {
        $arguments += @("--usage-log", $path)
    }
}

$result = Invoke-DoctorPythonScript `
    -Runner $runner `
    -ScriptPath (Join-Path $PSScriptRoot "skills-audit.py") `
    -InputText "" `
    -Arguments @($arguments | ForEach-Object { $_.ToString() })

if ($result.Output) {
    Write-Output $result.Output
}
exit $result.ExitCode
