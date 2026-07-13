<#
.SYNOPSIS
Reads and updates the local Compass orchestration ledger.

.DESCRIPTION
Stores control state under .local/orchestration-ledger.json. The ledger is
repo-local, ignored, and never installed into Codex or Claude homes.
#>
[CmdletBinding()]
param(
    [ValidateSet("status", "validate", "init", "set-owner", "set-state", "set-next", "add-evidence", "set-gate", "set-decision", "clear-decision", "set-grant", "clear-grant", "claim-successor", "record-successor-failure", "record-successor-success", "reset-recovery", "check-recovery")]
    [string]$Action = "status",
    [string]$GoalId,
    [string]$Goal,
    [Alias("ControlActor")]
    [string]$Actor,
    [string]$ExecutionOwner,
    [Alias("Writer")]
    [string]$ControlWriter,
    [string]$WorkerId,
    [switch]$ClearWorker,
    [ValidateSet("planned", "active", "waiting", "blocked", "complete", "cancelled")]
    [string]$State,
    [string]$NextAction,
    [string]$NextCheckAt,
    [switch]$ClearNext,
    [ValidateSet("test", "artifact", "review", "runtime", "decision", "other")]
    [string]$EvidenceKind,
    [string]$EvidenceSummary,
    [string]$EvidenceLocator,
    [ValidateSet("closed", "authorized", "in_flight", "complete")]
    [string]$Gate,
    [string]$GateAction,
    [string]$DecisionQuestion,
    [string[]]$DecisionOption,
    [Alias("ExpectedControlRevision", "Revision")]
    [Nullable[int]]$ExpectedRevision,
    [Alias("GrantedActor")]
    [string]$GrantActor,
    [string[]]$Mutation,
    [string]$SliceLabel,
    [Alias("RootCauseLocator", "RootCauseEvidenceLocator")]
    [string]$RootCauseEvidence,
    [string]$Ledger,
    [switch]$Json,
    [switch]$Plain
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
    throw "no runnable Python found for orchestration ledger"
}

$arguments = @("--root", $repoRoot)
if ($Ledger) {
    $arguments += @("--ledger", $Ledger)
}
$arguments += $Action

switch ($Action) {
    "status" {
        if ($GoalId) { $arguments += @("--goal-id", $GoalId) }
        if ($Json) { $arguments += "--json" }
        if ($Plain) { $arguments += "--plain" }
    }
    "validate" {
        if ($Json) { $arguments += "--json" }
    }
    "check-recovery" {
        if ($GoalId) { $arguments += @("--goal-id", $GoalId) }
        if ($SliceLabel) { $arguments += @("--slice-label", $SliceLabel) }
        if ($Json) { $arguments += "--json" }
    }
    "init" {
        if ($GoalId) { $arguments += @("--goal-id", $GoalId) }
        if ($Goal) { $arguments += @("--goal", $Goal) }
        if ($ExecutionOwner) { $arguments += @("--execution-owner", $ExecutionOwner) }
        if ($ControlWriter) { $arguments += @("--control-writer", $ControlWriter) }
        if ($WorkerId) { $arguments += @("--worker-id", $WorkerId) }
        if ($State) { $arguments += @("--state", $State) }
    }
    "set-owner" {
        if (-not $PSBoundParameters.ContainsKey("Actor") -or -not $PSBoundParameters.ContainsKey("ExpectedRevision")) { throw "mutations require -Actor and -ExpectedRevision" }
        $arguments += @("--actor", $Actor, "--expected-revision", $ExpectedRevision)
        if ($GoalId) { $arguments += @("--goal-id", $GoalId) }
        if ($ExecutionOwner) { $arguments += @("--execution-owner", $ExecutionOwner) }
        if ($ClearWorker) {
            $arguments += "--clear-worker"
        }
        elseif ($WorkerId) {
            $arguments += @("--worker-id", $WorkerId)
        }
    }
    "set-state" {
        if (-not $PSBoundParameters.ContainsKey("Actor") -or -not $PSBoundParameters.ContainsKey("ExpectedRevision")) { throw "mutations require -Actor and -ExpectedRevision" }
        $arguments += @("--actor", $Actor, "--expected-revision", $ExpectedRevision)
        if ($GoalId) { $arguments += @("--goal-id", $GoalId) }
        if ($State) { $arguments += @("--state", $State) }
    }
    "set-next" {
        if (-not $PSBoundParameters.ContainsKey("Actor") -or -not $PSBoundParameters.ContainsKey("ExpectedRevision")) { throw "mutations require -Actor and -ExpectedRevision" }
        $arguments += @("--actor", $Actor, "--expected-revision", $ExpectedRevision)
        if ($GoalId) { $arguments += @("--goal-id", $GoalId) }
        if ($ClearNext) {
            $arguments += "--clear"
        }
        elseif ($NextAction) {
            $arguments += @("--action", $NextAction)
        }
        if ($NextCheckAt) { $arguments += @("--check-at", $NextCheckAt) }
    }
    "add-evidence" {
        if (-not $PSBoundParameters.ContainsKey("Actor") -or -not $PSBoundParameters.ContainsKey("ExpectedRevision")) { throw "mutations require -Actor and -ExpectedRevision" }
        $arguments += @("--actor", $Actor, "--expected-revision", $ExpectedRevision)
        if ($GoalId) { $arguments += @("--goal-id", $GoalId) }
        if ($EvidenceKind) { $arguments += @("--kind", $EvidenceKind) }
        if ($EvidenceSummary) { $arguments += @("--summary", $EvidenceSummary) }
        if ($EvidenceLocator) { $arguments += @("--locator", $EvidenceLocator) }
    }
    "set-gate" {
        if (-not $PSBoundParameters.ContainsKey("Actor") -or -not $PSBoundParameters.ContainsKey("ExpectedRevision")) { throw "mutations require -Actor and -ExpectedRevision" }
        $arguments += @("--actor", $Actor, "--expected-revision", $ExpectedRevision)
        if ($GoalId) { $arguments += @("--goal-id", $GoalId) }
        if ($Gate) { $arguments += @("--gate", $Gate) }
        if ($GateAction) { $arguments += @("--action", $GateAction) }
    }
    "set-decision" {
        if (-not $PSBoundParameters.ContainsKey("Actor") -or -not $PSBoundParameters.ContainsKey("ExpectedRevision")) { throw "mutations require -Actor and -ExpectedRevision" }
        $arguments += @("--actor", $Actor, "--expected-revision", $ExpectedRevision)
        if ($GoalId) { $arguments += @("--goal-id", $GoalId) }
        if ($DecisionQuestion) { $arguments += @("--question", $DecisionQuestion) }
        foreach ($option in @($DecisionOption)) {
            if ($option) { $arguments += @("--option", $option) }
        }
    }
    "clear-decision" {
        if (-not $PSBoundParameters.ContainsKey("Actor") -or -not $PSBoundParameters.ContainsKey("ExpectedRevision")) { throw "mutations require -Actor and -ExpectedRevision" }
        $arguments += @("--actor", $Actor, "--expected-revision", $ExpectedRevision)
        if ($GoalId) { $arguments += @("--goal-id", $GoalId) }
    }
    "set-grant" {
        if (-not $PSBoundParameters.ContainsKey("Actor") -or -not $PSBoundParameters.ContainsKey("ExpectedRevision")) { throw "mutations require -Actor and -ExpectedRevision" }
        $arguments += @("--actor", $Actor, "--expected-revision", $ExpectedRevision)
        if ($GoalId) { $arguments += @("--goal-id", $GoalId) }
        if ($GrantActor) { $arguments += @("--grant-actor", $GrantActor) }
        foreach ($item in @($Mutation)) {
            if ($item) { $arguments += @("--mutation", $item) }
        }
    }
    "clear-grant" {
        if (-not $PSBoundParameters.ContainsKey("Actor") -or -not $PSBoundParameters.ContainsKey("ExpectedRevision")) { throw "mutations require -Actor and -ExpectedRevision" }
        $arguments += @("--actor", $Actor, "--expected-revision", $ExpectedRevision)
        if ($GoalId) { $arguments += @("--goal-id", $GoalId) }
        if ($GrantActor) { $arguments += @("--grant-actor", $GrantActor) }
    }
    "claim-successor" {
        if (-not $PSBoundParameters.ContainsKey("Actor") -or -not $PSBoundParameters.ContainsKey("ExpectedRevision")) { throw "mutations require -Actor and -ExpectedRevision" }
        $arguments += @("--actor", $Actor, "--expected-revision", $ExpectedRevision)
        if ($GoalId) { $arguments += @("--goal-id", $GoalId) }
        if ($SliceLabel) { $arguments += @("--slice-label", $SliceLabel) }
    }
    "record-successor-failure" {
        if (-not $PSBoundParameters.ContainsKey("Actor") -or -not $PSBoundParameters.ContainsKey("ExpectedRevision")) { throw "mutations require -Actor and -ExpectedRevision" }
        $arguments += @("--actor", $Actor, "--expected-revision", $ExpectedRevision)
        if ($GoalId) { $arguments += @("--goal-id", $GoalId) }
        if ($SliceLabel) { $arguments += @("--slice-label", $SliceLabel) }
    }
    "record-successor-success" {
        if (-not $PSBoundParameters.ContainsKey("Actor") -or -not $PSBoundParameters.ContainsKey("ExpectedRevision")) { throw "mutations require -Actor and -ExpectedRevision" }
        $arguments += @("--actor", $Actor, "--expected-revision", $ExpectedRevision)
        if ($GoalId) { $arguments += @("--goal-id", $GoalId) }
        if ($SliceLabel) { $arguments += @("--slice-label", $SliceLabel) }
    }
    "reset-recovery" {
        if (-not $PSBoundParameters.ContainsKey("Actor") -or -not $PSBoundParameters.ContainsKey("ExpectedRevision")) { throw "mutations require -Actor and -ExpectedRevision" }
        $arguments += @("--actor", $Actor, "--expected-revision", $ExpectedRevision)
        if ($GoalId) { $arguments += @("--goal-id", $GoalId) }
        if ($SliceLabel) { $arguments += @("--slice-label", $SliceLabel) }
        if ($RootCauseEvidence) { $arguments += @("--root-cause-evidence", $RootCauseEvidence) }
    }
}

$result = Invoke-DoctorPythonScript `
    -Runner $runner `
    -ScriptPath (Join-Path $PSScriptRoot "orchestration-ledger.py") `
    -InputText "" `
    -Arguments @($arguments | ForEach-Object { $_.ToString() })

if ($result.Output) {
    Write-Output $result.Output
}
exit $result.ExitCode
