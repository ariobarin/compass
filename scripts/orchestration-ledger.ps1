<#
.SYNOPSIS
Reads and updates the local Compass orchestration ledger.

.DESCRIPTION
Stores a principal-authored mechanical index under
.local/orchestration-ledger.json. The durable goal, plan, catalog,
assignments, and checkpoints remain Markdown control documents. Delegated
workers return artifacts and evidence; only the named principal writes ledger
control state.
#>
[CmdletBinding()]
param(
    [ValidateSet("status", "validate", "init", "set-owner", "set-phase", "set-links", "set-state", "set-next", "add-evidence", "set-gate", "set-decision", "clear-decision", "begin-recovery", "record-recovery-failure", "record-recovery-success", "reset-recovery", "check-recovery")]
    [string]$Action = "status",
    [string]$GoalId,
    [string]$Goal,
    [Alias("Principal", "ControlActor")]
    [string]$Actor,
    [string]$ExecutionOwner,
    [Alias("Writer")]
    [string]$ControlWriter,
    [string]$WorkerId,
    [switch]$ClearWorker,
    [string[]]$Anchor,
    [string[]]$ControlDocument,
    [ValidateSet("planning", "implementation")]
    [string]$Phase,
    [ValidateSet("planned", "active", "waiting", "blocked", "complete", "cancelled")]
    [string]$State,
    [string]$NextAction,
    [string]$NextCheckAt,
    [switch]$ClearNext,
    [ValidateSet("test", "artifact", "review", "runtime", "decision", "other")]
    [string]$EvidenceKind,
    [string]$EvidenceSummary,
    [string]$EvidenceLocator,
    [string]$EvidenceProducer,
    [string]$EvidenceObservedAt,
    [ValidateSet("closed", "authorized", "in_flight", "complete")]
    [string]$Gate,
    [string]$GateAction,
    [string]$DecisionQuestion,
    [string[]]$DecisionOption,
    [Alias("ExpectedControlRevision", "Revision")]
    [Nullable[int]]$ExpectedRevision,
    [string]$SliceLabel,
    [string]$FailureEvidence,
    [string]$DiscriminatingEvidence,
    [switch]$NoNewEvidence,
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

function Add-MutationAuth {
    if ([string]::IsNullOrWhiteSpace($Actor) -or $null -eq $ExpectedRevision) {
        throw "mutations require -Actor and -ExpectedRevision"
    }
    $script:arguments += @("--actor", $Actor, "--expected-revision", $ExpectedRevision)
}

function Add-RepeatedArgument {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name,
        [string[]]$Values
    )
    foreach ($value in @($Values)) {
        if ($value) {
            $script:arguments += @($Name, $value)
        }
    }
}

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
        if ($ControlWriter -and $Actor -and $ControlWriter -ne $Actor) {
            throw "init received conflicting -ControlWriter and -Principal values"
        }
        $principal = if ($ControlWriter) { $ControlWriter } else { $Actor }

        if ($GoalId) { $arguments += @("--goal-id", $GoalId) }
        if ($Goal) { $arguments += @("--goal", $Goal) }
        Add-RepeatedArgument -Name "--anchor" -Values $Anchor
        Add-RepeatedArgument -Name "--control-document" -Values $ControlDocument
        if ($Phase) { $arguments += @("--phase", $Phase) }
        if ($ExecutionOwner) { $arguments += @("--execution-owner", $ExecutionOwner) }
        if ($principal) { $arguments += @("--control-writer", $principal) }
        if ($WorkerId) { $arguments += @("--worker-id", $WorkerId) }
        if ($State) { $arguments += @("--state", $State) }
    }
    "set-owner" {
        Add-MutationAuth
        if ($GoalId) { $arguments += @("--goal-id", $GoalId) }
        if ($ExecutionOwner) { $arguments += @("--execution-owner", $ExecutionOwner) }
        if ($ClearWorker) {
            $arguments += "--clear-worker"
        }
        elseif ($WorkerId) {
            $arguments += @("--worker-id", $WorkerId)
        }
    }
    "set-phase" {
        Add-MutationAuth
        if ($GoalId) { $arguments += @("--goal-id", $GoalId) }
        if ($Phase) { $arguments += @("--phase", $Phase) }
    }
    "set-links" {
        Add-MutationAuth
        if ($GoalId) { $arguments += @("--goal-id", $GoalId) }
        Add-RepeatedArgument -Name "--anchor" -Values $Anchor
        Add-RepeatedArgument -Name "--control-document" -Values $ControlDocument
    }
    "set-state" {
        Add-MutationAuth
        if ($GoalId) { $arguments += @("--goal-id", $GoalId) }
        if ($State) { $arguments += @("--state", $State) }
    }
    "set-next" {
        Add-MutationAuth
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
        Add-MutationAuth
        if ($GoalId) { $arguments += @("--goal-id", $GoalId) }
        if ($EvidenceKind) { $arguments += @("--kind", $EvidenceKind) }
        if ($EvidenceSummary) { $arguments += @("--summary", $EvidenceSummary) }
        if ($EvidenceLocator) { $arguments += @("--locator", $EvidenceLocator) }
        if ($EvidenceProducer) { $arguments += @("--producer", $EvidenceProducer) }
        if ($EvidenceObservedAt) { $arguments += @("--observed-at", $EvidenceObservedAt) }
    }
    "set-gate" {
        Add-MutationAuth
        if ($GoalId) { $arguments += @("--goal-id", $GoalId) }
        if ($Gate) { $arguments += @("--gate", $Gate) }
        if ($GateAction) { $arguments += @("--action", $GateAction) }
    }
    "set-decision" {
        Add-MutationAuth
        if ($GoalId) { $arguments += @("--goal-id", $GoalId) }
        if ($DecisionQuestion) { $arguments += @("--question", $DecisionQuestion) }
        Add-RepeatedArgument -Name "--option" -Values $DecisionOption
    }
    "clear-decision" {
        Add-MutationAuth
        if ($GoalId) { $arguments += @("--goal-id", $GoalId) }
    }
    "begin-recovery" {
        Add-MutationAuth
        if ($GoalId) { $arguments += @("--goal-id", $GoalId) }
        if ($SliceLabel) { $arguments += @("--slice-label", $SliceLabel) }
        if ($WorkerId) { $arguments += @("--worker-id", $WorkerId) }
    }
    "record-recovery-failure" {
        Add-MutationAuth
        if ($GoalId) { $arguments += @("--goal-id", $GoalId) }
        if ($SliceLabel) { $arguments += @("--slice-label", $SliceLabel) }
        if ($FailureEvidence) { $arguments += @("--failure-evidence", $FailureEvidence) }
        if ($DiscriminatingEvidence) {
            $arguments += @("--discriminating-evidence", $DiscriminatingEvidence)
        }
        if ($NoNewEvidence) {
            $arguments += "--no-new-evidence"
        }
    }
    "record-recovery-success" {
        Add-MutationAuth
        if ($GoalId) { $arguments += @("--goal-id", $GoalId) }
        if ($SliceLabel) { $arguments += @("--slice-label", $SliceLabel) }
    }
    "reset-recovery" {
        Add-MutationAuth
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
