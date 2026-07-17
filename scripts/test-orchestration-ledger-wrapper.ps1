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
    param([string[]]$Arguments)

    $processArguments = @("-NoProfile")
    if ($env:OS -eq "Windows_NT") {
        $processArguments += @("-ExecutionPolicy", "Bypass")
    }
    $processArguments += @("-File", $wrapperPath) + $Arguments

    $output = @(& $powerShellPath @processArguments 2>&1 | ForEach-Object { $_.ToString() })
    if ($LASTEXITCODE -ne 0) {
        throw "ledger wrapper failed with exit code $LASTEXITCODE`n$($output -join "`n")"
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

    $statusText = @(Invoke-Wrapper -Arguments @(
        "-Action", "status",
        "-GoalId", "principal-alias",
        "-Ledger", $ledgerPath,
        "-Json"
    )) -join "`n"
    $status = $statusText | ConvertFrom-Json
    $goal = @($status.goals)[0]

    if ($goal.control_writer -ne "principal") {
        throw "-Principal did not initialize control_writer"
    }
    if ($goal.execution_owner -ne "principal") {
        throw "ledger wrapper changed the execution owner"
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
