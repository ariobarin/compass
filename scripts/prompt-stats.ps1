<#
.SYNOPSIS
Reports static statistics for repository-owned prompt surfaces.

.DESCRIPTION
Runs the stdlib-only prompt statistics tool. The command reads only prompt files
owned by the repository and reports deterministic size, steering, duplication,
routing, and budget data.
#>
[CmdletBinding()]
param(
    [switch]$Json,
    [switch]$Check,
    [double]$CharsPerToken = 4,
    [double]$DuplicateThreshold = 0.9,
    [int]$DuplicateMinWords = 8,
    [int]$MaxDuplicateResults = 50,
    [int]$GlobalBudget = 4000,
    [int]$AgentTotalBudget = 12000,
    [int]$AgentFileBudget = 2500,
    [int]$SkillRoutingBudget = 2000,
    [int]$SelectedSkillBudget = 4000
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
. "$PSScriptRoot\doctor\common.ps1"

$runner = @(Get-DoctorPythonRunner)
if ($runner.Count -eq 0) {
    throw "no runnable Python found for prompt statistics"
}

$arguments = @(
    "--root", $repoRoot,
    "--chars-per-token", $CharsPerToken,
    "--duplicate-threshold", $DuplicateThreshold,
    "--duplicate-min-words", $DuplicateMinWords,
    "--max-duplicate-results", $MaxDuplicateResults,
    "--global-budget", $GlobalBudget,
    "--agent-total-budget", $AgentTotalBudget,
    "--agent-file-budget", $AgentFileBudget,
    "--skill-routing-budget", $SkillRoutingBudget,
    "--selected-skill-budget", $SelectedSkillBudget
)
if ($Json) {
    $arguments += "--json"
}
if ($Check) {
    $arguments += "--check"
}

$result = Invoke-DoctorPythonScript `
    -Runner $runner `
    -ScriptPath (Join-Path $PSScriptRoot "prompt-stats.py") `
    -InputText "" `
    -Arguments @($arguments | ForEach-Object { $_.ToString() })

if ($result.Output) {
    Write-Output $result.Output
}
exit $result.ExitCode
