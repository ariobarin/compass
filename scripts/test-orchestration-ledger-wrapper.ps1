[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$wrapperPath = Join-Path $PSScriptRoot "orchestration-ledger.ps1"
$ledgerName = "orchestration-ledger-wrapper-$([guid]::NewGuid().ToString('N')).json"
$ledgerPath = Join-Path (Join-Path $repoRoot ".local") $ledgerName
$lockPath = "$ledgerPath.lock"
$powerShellPath = (Get-Process -Id $PID).Path

function Invoke-Wrapper {
    param(
        [string[]]$Arguments,
        [int]$ExpectedExitCode = 0
    )

    $processArguments = @("-NoProfile")
    if ($env:OS -eq "Windows_NT") {
        $processArguments += @("-ExecutionPolicy", "Bypass")
    }
    $processArguments += @("-File", $wrapperPath) + $Arguments

    $output = @(& $powerShellPath @processArguments 2>&1 | ForEach-Object { $_.ToString() })
    $exitCode = $LASTEXITCODE
    if ($exitCode -ne $ExpectedExitCode) {
        throw "expected ledger wrapper exit code $ExpectedExitCode, got $exitCode`n$($output -join "`n")"
    }
    return $output
}

try {
    [void](Invoke-Wrapper -Arguments @(
        "-Action", "init",
        "-GoalId", "principal-alias",
        "-Goal", "Prove the PowerShell principal alias",
        "-Anchor", "brief.md",
        "-ControlDocument", "goal.md",
        "-ExecutionOwner", "principal",
        "-Principal", "principal",
        "-Ledger", $ledgerPath
    ))

    [void](Invoke-Wrapper -Arguments @(
        "-Action", "set-phase",
        "-GoalId", "principal-alias",
        "-Principal", "principal",
        "-ExpectedRevision", "1",
        "-Phase", "implementation",
        "-Ledger", $ledgerPath
    ))

    [void](Invoke-Wrapper -Arguments @(
        "-Action", "set-links",
        "-GoalId", "principal-alias",
        "-Principal", "principal",
        "-ExpectedRevision", "2",
        "-Anchor", "brief.md#approved",
        "-ControlDocument", "checkpoint.md",
        "-Ledger", $ledgerPath
    ))

    [void](Invoke-Wrapper -Arguments @(
        "-Action", "add-evidence",
        "-GoalId", "principal-alias",
        "-Principal", "principal",
        "-ExpectedRevision", "3",
        "-EvidenceKind", "test",
        "-EvidenceSummary", "PowerShell wrapper mutation passed",
        "-EvidenceLocator", "wrapper:test",
        "-EvidenceProducer", "wrapper-test",
        "-EvidenceObservedAt", "2026-07-17T12:00:00Z",
        "-Ledger", $ledgerPath
    ))

    [void](Invoke-Wrapper -Arguments @(
        "-Action", "begin-recovery",
        "-GoalId", "principal-alias",
        "-Principal", "principal",
        "-ExpectedRevision", "4",
        "-SliceLabel", "wrapper-slice",
        "-WorkerId", "recovery-01",
        "-Ledger", $ledgerPath
    ))

    [void](Invoke-Wrapper -Arguments @(
        "-Action", "record-recovery-failure",
        "-GoalId", "principal-alias",
        "-Principal", "principal",
        "-ExpectedRevision", "5",
        "-SliceLabel", "wrapper-slice",
        "-FailureEvidence", "wrapper:unchanged-failure",
        "-NoNewEvidence",
        "-Ledger", $ledgerPath
    ))

    $blockedOutput = @(Invoke-Wrapper -Arguments @(
        "-Action", "check-recovery",
        "-GoalId", "principal-alias",
        "-SliceLabel", "wrapper-slice",
        "-Ledger", $ledgerPath
    ) -ExpectedExitCode 1) -join "`n"
    if (-not $blockedOutput.Contains("changed hypothesis")) {
        throw "open recovery circuit did not block an unchanged successor"
    }

    [void](Invoke-Wrapper -Arguments @(
        "-Action", "reset-recovery",
        "-GoalId", "principal-alias",
        "-Principal", "principal",
        "-ExpectedRevision", "6",
        "-SliceLabel", "wrapper-slice",
        "-RootCauseEvidence", "wrapper:changed-route",
        "-Ledger", $ledgerPath
    ))

    # Every wrapper call runs in a new PowerShell process. This mutation proves a
    # fresh process can reopen the ledger and continue from the stored revision.
    [void](Invoke-Wrapper -Arguments @(
        "-Action", "set-state",
        "-GoalId", "principal-alias",
        "-Principal", "principal",
        "-ExpectedRevision", "7",
        "-State", "active",
        "-Ledger", $ledgerPath
    ))

    $statusText = @(Invoke-Wrapper -Arguments @(
        "-Action", "status",
        "-GoalId", "principal-alias",
        "-Ledger", $ledgerPath,
        "-Json"
    )) -join "`n"
    $status = $statusText | ConvertFrom-Json
    $goal = @($status.goals)[0]
    $circuit = @($goal.recovery_circuits)[0]

    if ($goal.control_writer -ne "principal") {
        throw "-Principal did not initialize control_writer"
    }
    if ($goal.execution_owner -ne "principal") {
        throw "ledger wrapper changed the execution owner"
    }
    if ($goal.phase -ne "implementation" -or $goal.state -ne "active") {
        throw "ledger wrapper did not preserve mutation and resume state"
    }
    if (@($goal.control_documents)[0] -ne "checkpoint.md") {
        throw "ledger wrapper did not preserve the checkpoint link"
    }
    if (@($goal.evidence).Count -ne 1 -or $goal.evidence[0].verified_by -ne "principal") {
        throw "ledger wrapper did not preserve principal-verified evidence"
    }
    if ($circuit.state -ne "closed" -or $circuit.last_reset_evidence -ne "wrapper:changed-route") {
        throw "ledger wrapper did not preserve recovery reset evidence"
    }
    if ($goal.control_revision -ne 8) {
        throw "ledger wrapper revision mismatch after round trip: $($goal.control_revision)"
    }

    Write-Host "orchestration ledger wrapper: ok"
}
finally {
    foreach ($path in @($ledgerPath, $lockPath)) {
        if (Test-Path -LiteralPath $path) {
            Remove-Item -LiteralPath $path -Force
        }
    }
}
