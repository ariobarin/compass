<#
.SYNOPSIS
Reads and updates the local Compass orchestration ledger.
#>
[CmdletBinding()]
param(
    [ValidateSet("Status", "Init", "SetState", "SetNext", "ClearNext", "AddEvidence", "SetGate", "SetDecision", "ClearDecision", "Remove", "Validate")]
    [string]$Action = "Status",
    [string]$Id,
    [string]$Goal,
    [string]$Repository,
    [string]$ExecutionOwner,
    [string]$WorkerId,
    [string[]]$CompletionEvidence,
    [ValidateSet("planned", "active", "waiting", "blocked", "review", "complete", "cancelled")]
    [string]$State,
    [string]$NextAction,
    [string]$NextCheckAt,
    [ValidateSet("command", "check", "review", "artifact", "status", "decision")]
    [string]$EvidenceKind,
    [string]$EvidenceSummary,
    [string]$EvidenceLocator,
    [ValidateSet("closed", "open", "blocked")]
    [string]$GateState,
    [string]$GateReason,
    [string]$DecisionQuestion,
    [string[]]$DecisionOption,
    [string]$DecisionEvidence,
    [string]$LedgerPath,
    [switch]$Json,
    [switch]$Plain,
    [switch]$Force
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
    throw "no runnable Python found for the orchestration ledger"
}

$actionMap = @{
    Status = "status"
    Init = "init"
    SetState = "set-state"
    SetNext = "set-next"
    ClearNext = "clear-next"
    AddEvidence = "add-evidence"
    SetGate = "set-gate"
    SetDecision = "set-decision"
    ClearDecision = "clear-decision"
    Remove = "remove"
    Validate = "validate"
}
$arguments = @("--root", $repoRoot)
if ($LedgerPath) {
    $arguments += @("--ledger", $LedgerPath)
}
$arguments += $actionMap[$Action]

function Add-ValueArgument {
    param([string]$Name, [object]$Value)
    if ($null -ne $Value -and -not [string]::IsNullOrWhiteSpace($Value.ToString())) {
        $script:arguments += @($Name, $Value.ToString())
    }
}

Add-ValueArgument "--id" $Id
Add-ValueArgument "--goal" $Goal
Add-ValueArgument "--repository" $Repository
Add-ValueArgument "--execution-owner" $ExecutionOwner
Add-ValueArgument "--worker-id" $WorkerId
foreach ($value in @($CompletionEvidence)) {
    Add-ValueArgument "--completion-evidence" $value
}
Add-ValueArgument "--state" $State
if ($Action -eq "SetNext") {
    Add-ValueArgument "--summary" $NextAction
}
elseif ($Action -eq "AddEvidence") {
    Add-ValueArgument "--summary" $EvidenceSummary
}
Add-ValueArgument "--check-at" $NextCheckAt
Add-ValueArgument "--kind" $EvidenceKind
Add-ValueArgument "--locator" $EvidenceLocator
if ($Action -eq "SetGate") {
    Add-ValueArgument "--state" $GateState
    Add-ValueArgument "--reason" $GateReason
}
Add-ValueArgument "--question" $DecisionQuestion
foreach ($value in @($DecisionOption)) {
    Add-ValueArgument "--option" $value
}
Add-ValueArgument "--evidence" $DecisionEvidence
if ($Json) { $arguments += "--json" }
if ($Plain) { $arguments += "--plain" }
if ($Force) { $arguments += "--force" }

$result = Invoke-DoctorPythonScript `
    -Runner $runner `
    -ScriptPath (Join-Path $PSScriptRoot "orchestration-ledger.py") `
    -InputText "" `
    -Arguments @($arguments)

if ($result.Output) {
    Write-Output $result.Output
}
exit $result.ExitCode
