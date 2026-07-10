<#
.SYNOPSIS
Previews or restores the live state recorded before one installation receipt.

.EXAMPLE
./scripts/rollback.ps1 -Receipt install-20260710T180000000Z

.EXAMPLE
./scripts/rollback.ps1 -Receipt install-20260710T180000000Z -Apply
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$Receipt,

    [switch]$Apply,
    [switch]$Force,
    [string]$CodexHome
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

. "$PSScriptRoot\common.ps1"
. "$PSScriptRoot\receipt-common.ps1"

function Copy-PortablePath {
    param(
        [string]$Source,
        [string]$Destination
    )

    if (-not (Test-Path -LiteralPath $Source)) {
        throw "rollback source is missing: $Source"
    }
    if (Test-Path -LiteralPath $Destination) {
        Remove-Item -LiteralPath $Destination -Recurse -Force
    }

    $sourceItem = Get-Item -LiteralPath $Source -Force
    if ($sourceItem.PSIsContainer) {
        New-Item -ItemType Directory -Force (Split-Path -Parent $Destination) | Out-Null
        Copy-Item -LiteralPath $Source -Destination $Destination -Recurse -Force
    }
    else {
        New-DirectoryForFile -Path $Destination
        Copy-Item -LiteralPath $Source -Destination $Destination -Force
    }
}

function Get-RollbackBackupPath {
    param(
        [string]$Root,
        [int]$Index,
        [string]$Target
    )

    $leaf = Split-Path -Leaf $Target
    if (-not $leaf) {
        $leaf = "target"
    }
    $safeLeaf = $leaf -replace '[^A-Za-z0-9._-]', '_'
    return Join-Path $Root ("{0:D3}-{1}" -f $Index, $safeLeaf)
}

$liveHome = Get-CodexHome -CodexHome $CodexHome
$receipt = Get-PortableReceipt -CodexHome $liveHome -Receipt $Receipt
if ($receipt.kind -and $receipt.kind -ne "install") {
    throw "only installation receipts can be rolled back"
}
if (-not $receipt.changes) {
    throw "receipt has no recorded changes to roll back: $($receipt.id)"
}
if (-not $receipt.targets -or -not $receipt.targets.codex_home) {
    throw "receipt is missing target roots"
}
if (-not $receipt.targets.codex_home.Equals($liveHome, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "receipt belongs to a different Codex home: $($receipt.targets.codex_home)"
}

$targetRoots = @(
    $receipt.targets.codex_home,
    $receipt.targets.agents_home,
    $receipt.targets.claude_home
) | Where-Object { $_ }
$backupRoots = @(
    foreach ($entry in @($receipt.backup_roots)) {
        if ($entry.backup_root) {
            $entry.backup_root
        }
    }
)
$changes = @($receipt.changes)
$problems = New-Object System.Collections.Generic.List[string]
$plan = @(
    for ($index = $changes.Count - 1; $index -ge 0; $index -= 1) {
        $change = $changes[$index]
        if (-not $change.target -or -not (Test-PortablePathUnderAnyRoot -Path $change.target -Roots $targetRoots)) {
            $problems.Add("unsafe rollback target: $($change.target)")
            continue
        }
        if ($change.previous_state -notin @("missing", "backup")) {
            $problems.Add("unsupported previous state for $($change.target): $($change.previous_state)")
            continue
        }
        if ($change.previous_state -eq "backup") {
            if (-not $change.backup_path) {
                $problems.Add("missing backup path for $($change.target)")
            }
            elseif (-not (Test-PortablePathUnderAnyRoot -Path $change.backup_path -Roots $backupRoots)) {
                $problems.Add("unsafe backup path for $($change.target): $($change.backup_path)")
            }
            elseif (-not (Test-Path -LiteralPath $change.backup_path)) {
                $problems.Add("rollback backup is missing for $($change.target): $($change.backup_path)")
            }
        }

        $matches = Test-PortableFingerprintMatches -Expected $change.after -Path $change.target
        [pscustomobject]@{
            Change = $change
            CurrentMatches = $matches
            Action = if ($change.previous_state -eq "backup") { "restore backup" } else { "remove installed target" }
        }
    }
)

foreach ($item in $plan) {
    if (-not $item.CurrentMatches -and -not $Force) {
        $problems.Add("live target changed after receipt $($receipt.id): $($item.Change.target)")
    }
}

Write-Host "receipt: $($receipt.id)"
Write-Host "source ref: $($receipt.source_ref)"
Write-Host "source commit: $($receipt.source_commit)"
Write-Host "codex: $liveHome"
Write-Host ""
Write-Host "rollback plan:"
foreach ($item in $plan) {
    $drift = if ($item.CurrentMatches) { "" } else { " [live drift]" }
    Write-Host "  $($item.Action): $($item.Change.target)$drift"
}

if ($problems.Count -gt 0) {
    Write-Host ""
    Write-Host "blocked:"
    foreach ($problem in $problems) {
        Write-Host "  $problem"
    }
    if (-not $Apply) {
        Write-Host "preview only: use -Force with -Apply only after reviewing live drift"
        exit 0
    }
    throw "rollback validation failed"
}

if (-not $Apply) {
    Write-Host ""
    Write-Host "review mode: no files were changed"
    Write-Host "run again with -Apply to restore this receipt"
    exit 0
}

$stamp = (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssfffZ")
$rollbackBackupRoot = Join-Path $liveHome "portable-backups\rollback-$stamp"
$actions = New-Object System.Collections.Generic.List[object]

for ($index = 0; $index -lt $plan.Count; $index += 1) {
    $item = $plan[$index]
    $change = $item.Change
    $currentBackupPath = $null
    if (Test-Path -LiteralPath $change.target) {
        $currentBackupPath = Get-RollbackBackupPath -Root $rollbackBackupRoot -Index $index -Target $change.target
        Copy-PortablePath -Source $change.target -Destination $currentBackupPath
    }

    if ($change.previous_state -eq "missing") {
        if (Test-Path -LiteralPath $change.target) {
            Remove-Item -LiteralPath $change.target -Recurse -Force
        }
    }
    else {
        Copy-PortablePath -Source $change.backup_path -Destination $change.target
    }

    $actions.Add([pscustomobject]@{
        target = $change.target
        restored_from = $change.backup_path
        displaced_to = $currentBackupPath
        after = Get-PortablePathFingerprint -Path $change.target
    })
    Write-Host "rolled back: $($change.target)"
}

$restoredArtifacts = @(
    foreach ($artifact in @($receipt.artifacts)) {
        [ordered]@{
            source = $artifact.source
            target = $artifact.target
            type = $artifact.type
            state = $artifact.state
            ownership = $artifact.ownership
            fingerprint = Get-PortablePathFingerprint -Path $artifact.target
        }
    }
)
$rollbackReceipt = [ordered]@{
    schema_version = 1
    kind = "rollback"
    id = "rollback-$stamp"
    installed_at = (Get-Date).ToUniversalTime().ToString("o")
    source_ref = $receipt.source_ref
    source_commit = $receipt.source_commit
    previous_receipt_id = $receipt.id
    rollback_of = $receipt.id
    targets = $receipt.targets
    backup_roots = @(
        [ordered]@{
            live_root = $liveHome
            backup_root = $rollbackBackupRoot
        }
    )
    changes = @()
    actions = @($actions.ToArray())
    artifacts = $restoredArtifacts
}
$rollbackReceiptPath = Write-PortableReceipt -CodexHome $liveHome -Receipt $rollbackReceipt

Write-Host ""
Write-Host "rollback receipt: $rollbackReceiptPath"
Write-Host "displaced live state: $rollbackBackupRoot"
