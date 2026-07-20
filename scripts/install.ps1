param(
    [switch]$Apply,
    [Alias("ReplaceForeign")]
    [switch]$Adopt,
    [string]$SourceRef,
    [string]$SourceCommit,
    [string]$CodexHome,
    [string]$AgentsHome,
    [string]$ClaudeHome,
    [switch]$SkipSkillRuntimeSetup,
    [switch]$SkipPluginRetirement
)

. "$PSScriptRoot\common.ps1"
. "$PSScriptRoot\receipt-common.ps1"
. "$PSScriptRoot\reviewed-config.ps1"

[char[]]$pathSeparators = @(
    [System.IO.Path]::DirectorySeparatorChar,
    [System.IO.Path]::AltDirectorySeparatorChar
) | Select-Object -Unique

function Test-FileMapsEqual {
    param(
        [hashtable]$Expected,
        [hashtable]$Actual
    )

    if ($Expected.Count -ne $Actual.Count) {
        return $false
    }
    foreach ($key in $Expected.Keys) {
        if (-not $Actual.ContainsKey($key) -or $Expected[$key] -ne $Actual[$key]) {
            return $false
        }
    }
    return $true
}

function Test-PortableItemInSync {
    param([object]$Item)

    if (-not (Test-Path -LiteralPath $Item.RepoPath)) {
        throw "missing portable source: $($Item.RepoPath)"
    }
    if (-not (Test-Path -LiteralPath $Item.LivePath)) {
        return $false
    }

    if ($Item.Type -eq "file") {
        if (-not (Test-Path -LiteralPath $Item.LivePath -PathType Leaf)) {
            return $false
        }
        $repoHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $Item.RepoPath).Hash
        $liveHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $Item.LivePath).Hash
        return $repoHash -eq $liveHash
    }

    if ($Item.Type -eq "derived-agent") {
        if (-not (Test-Path -LiteralPath $Item.LivePath -PathType Leaf)) {
            return $false
        }

        $tempRoot = Join-Path ([System.IO.Path]::GetTempPath()) "compass-derived-install-$([guid]::NewGuid().ToString('N'))"
        $tempFile = Join-Path $tempRoot "agent.md"
        try {
            New-Item -ItemType Directory -Force $tempRoot | Out-Null
            Copy-PortableItem -Source $Item.RepoPath -Destination $tempFile -Type $Item.Type -AllowedRoot $tempRoot
            $repoHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $tempFile).Hash
            $liveHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $Item.LivePath).Hash
            return $repoHash -eq $liveHash
        }
        finally {
            if (Test-Path -LiteralPath $tempRoot) {
                Remove-Item -LiteralPath $tempRoot -Recurse -Force
            }
        }
    }

    if (-not (Test-Path -LiteralPath $Item.LivePath -PathType Container)) {
        return $false
    }

    $expected = Get-PortableDirectoryFileMap -Root $Item.RepoPath -DerivedSkill:($Item.Type -eq "derived-skill") -Stateful:($Item.Type -eq "stateful-dir")
    $actual = Get-PortableDirectoryFileMap -Root $Item.LivePath -Stateful:($Item.Type -eq "stateful-dir")
    return Test-FileMapsEqual -Expected $expected -Actual $actual
}

function Get-ItemBackupPath {
    param(
        [object]$Item,
        [string]$BackupRoot
    )

    $relative = $Item.LivePath.Substring($Item.LiveRoot.Length).TrimStart($pathSeparators)
    $backupBase = if ($Item.BackupScope) {
        Join-Path $BackupRoot $Item.BackupScope
    }
    else {
        $BackupRoot
    }
    return Join-Path $backupBase $relative
}

function Get-RepoRelativePath {
    param([string]$Path)

    $fullPath = [System.IO.Path]::GetFullPath($Path)
    $fullRoot = [System.IO.Path]::GetFullPath($repoRoot).TrimEnd($pathSeparators)
    Assert-PathUnderRoot -Path $fullPath -Root $fullRoot
    return $fullPath.Substring($fullRoot.Length).TrimStart($pathSeparators).Replace("\", "/")
}

function Get-GitScalar {
    param([string[]]$Arguments)

    if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
        return $null
    }

    $previousErrorActionPreference = $ErrorActionPreference
    try {
        $ErrorActionPreference = "Continue"
        $output = @(& git -C $repoRoot @Arguments 2>$null)
        $exitCode = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $previousErrorActionPreference
    }
    if ($exitCode -ne 0) {
        return $null
    }
    return $output | Select-Object -First 1
}

function Test-ReceiptTargetSetEqual {
    param(
        [AllowNull()]
        [object]$Receipt,
        [object[]]$ActiveItems,
        [object[]]$RetiredItems
    )

    if ($null -eq $Receipt) {
        return $false
    }
    $expected = @(@($ActiveItems.LivePath) + @($RetiredItems.LivePath) | Sort-Object -Unique)
    $actual = @(@($Receipt.artifacts | ForEach-Object { $_.target }) | Sort-Object -Unique)
    return @(Compare-Object -ReferenceObject $expected -DifferenceObject $actual).Count -eq 0
}

$repoRoot = Get-RepoRoot
$headCommit = Get-GitScalar -Arguments @("rev-parse", "HEAD")
if ($SourceCommit) {
    if (-not $headCommit) {
        throw "cannot validate source commit without repository HEAD"
    }
    if ($SourceCommit -ne $headCommit) {
        throw "source commit does not match repository HEAD"
    }
}
$resolvedSourceCommit = if ($SourceCommit) { $SourceCommit } else { $headCommit }
$resolvedSourceRef = $SourceRef
if (-not $resolvedSourceRef) {
    $resolvedSourceRef = Get-GitScalar -Arguments @("branch", "--show-current")
    if (-not $resolvedSourceRef) {
        $resolvedSourceRef = Get-GitScalar -Arguments @("describe", "--tags", "--exact-match", "HEAD")
    }
    if (-not $resolvedSourceRef) {
        $resolvedSourceRef = "detached"
    }
}

$liveHome = Get-CodexHome -CodexHome $CodexHome
$agentsHome = Get-AgentsHome -AgentsHome $AgentsHome
$claudeHome = Get-ClaudeHome -ClaudeHome $ClaudeHome
$items = @(Get-PortableFileMap -RepoRoot $repoRoot -CodexHome $liveHome -AgentsHome $agentsHome -ClaudeHome $claudeHome)
$retiredItems = @(Get-RetiredPortableFileMap -CodexHome $liveHome -AgentsHome $agentsHome)
$currentReceipt = Get-PortableCurrentReceipt -CodexHome $liveHome
$reviewedConfigContract = Get-ReviewedConfigContract -RepoRoot $repoRoot -CodexHome $liveHome
$reviewConfigPath = $reviewedConfigContract.ReviewPath
$liveConfigPath = $reviewedConfigContract.LivePath
$reviewedConfigState = Get-ReviewedConfigState -ReviewPath $reviewConfigPath -LivePath $liveConfigPath

$itemStates = @(
    foreach ($item in $items) {
        $exists = Test-Path -LiteralPath $item.LivePath
        $inSync = Test-PortableItemInSync -Item $item
        $owned = Test-PortableReceiptOwnsTarget -Receipt $currentReceipt -Target $item.LivePath
        [pscustomobject]@{
            Item = $item
            Exists = $exists
            InSync = $inSync
            Owned = $owned
            Foreign = ($exists -and -not $inSync -and -not $owned)
        }
    }
)
$retiredStates = @(
    foreach ($item in $retiredItems) {
        $exists = Test-Path -LiteralPath $item.LivePath
        $owned = Test-PortableReceiptOwnsTarget -Receipt $currentReceipt -Target $item.LivePath
        [pscustomobject]@{
            Item = $item
            Exists = $exists
            Owned = $owned
            Foreign = ($exists -and -not $owned)
        }
    }
)

$foreignStates = @(
    @($itemStates | Where-Object { $_.Foreign }) +
    @($retiredStates | Where-Object { $_.Foreign })
)
$blockedForeignStates = @(
    if (-not $Adopt) {
        $foreignStates
    }
)
$installStates = @($itemStates | Where-Object { -not $_.InSync -and ($Adopt -or -not $_.Foreign) })
$missingStates = @($itemStates | Where-Object { -not $_.Exists })
$changedStates = @($installStates | Where-Object { $_.Exists })
$unchangedStates = @($itemStates | Where-Object { $_.InSync })
$retiredRemovalStates = @($retiredStates | Where-Object { $_.Exists -and ($Adopt -or $_.Owned) })
Write-Host "repo: $repoRoot"
Write-Host "codex: $liveHome"
Write-Host "agents: $agentsHome"
Write-Host "claude: $claudeHome"
Write-Host ""

if (-not $Apply) {
    Write-Host "review mode: no files will be changed"
    Write-Host "planned copies:"
    if ($installStates.Count -eq 0) {
        Write-Host "  none"
    }
    else {
        foreach ($state in $installStates) {
            Write-Host "  $($state.Item.RepoPath) -> $($state.Item.LivePath)"
        }
    }

    Write-Host ""
    Write-Host "planned reviewed config changes:"
    if (-not [bool]$reviewedConfigState.changed) {
        Write-Host "  none"
    }
    else {
        foreach ($change in @($reviewedConfigState.changes)) {
            Write-Host "  $($change.path): $($change.actual) -> $($change.expected)"
        }
    }

    if ($retiredRemovalStates.Count -gt 0) {
        Write-Host ""
        Write-Host "planned retired removals:"
        foreach ($state in $retiredRemovalStates) {
            Write-Host "  $($state.Item.LivePath)"
        }
    }

    if ($foreignStates.Count -gt 0) {
        Write-Host ""
        Write-Host "foreign targets:"
        foreach ($state in $foreignStates) {
            Write-Host "  $($state.Item.LivePath)"
        }
        if (-not $Adopt) {
            Write-Host "rerun with -Adopt to authorize replacing or removing these targets"
        }
    }

    Write-Host ""
    Write-Host "changed: $($changedStates.Count)"
    Write-Host "missing: $($missingStates.Count)"
    Write-Host "unchanged: $($unchangedStates.Count)"
    Write-Host "reviewed config: $($reviewedConfigState.changed_count)"
    Write-Host "retired: $($retiredRemovalStates.Count)"
    Write-Host "foreign: $($foreignStates.Count)"
    Write-Host "run with -Apply to install the approved plan"
    if (-not $SkipPluginRetirement) {
        Write-Host ""
        & (Join-Path $PSScriptRoot "retire-plugins.ps1") -CodexHome $liveHome
    }
    exit 0
}

if ($blockedForeignStates.Count -gt 0) {
    Write-Host "foreign targets require explicit adoption:"
    foreach ($state in $blockedForeignStates) {
        Write-Host "  $($state.Item.LivePath)"
    }
    throw "rerun with -Adopt to replace or remove foreign targets"
}

if (-not $SkipPluginRetirement) {
    & (Join-Path $PSScriptRoot "retire-plugins.ps1") -CodexHome $liveHome -Apply -RequireAbsent
    if ($LASTEXITCODE -ne 0) {
        throw "retired plugin cleanup failed"
    }
}

$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$backupRoots = @{}
$changes = New-Object System.Collections.Generic.List[object]

function Get-ItemBackupRoot {
    param([string]$LiveRoot)

    if ($backupRoots.ContainsKey($LiveRoot)) {
        return $backupRoots[$LiveRoot]
    }

    $root = Join-Path $LiveRoot "portable-backups\$stamp"
    New-Item -ItemType Directory -Force $root | Out-Null
    $backupRoots[$LiveRoot] = $root
    return $root
}

foreach ($state in $installStates) {
    $item = $state.Item
    $previousState = "missing"
    $backupPath = $null
    if ($state.Exists) {
        $itemBackupRoot = Get-ItemBackupRoot -LiveRoot $item.LiveRoot
        $backupPath = Get-ItemBackupPath -Item $item -BackupRoot $itemBackupRoot
        Backup-LiveItem -LivePath $item.LivePath -BackupRoot $itemBackupRoot -LiveRoot $item.LiveRoot -BackupScope $item.BackupScope -Type $item.Type
        $previousState = "backup"
    }

    Copy-PortableItem -Source $item.RepoPath -Destination $item.LivePath -Type $item.Type -AllowedRoot $item.LiveRoot
    $changes.Add([pscustomobject]@{
        operation = "install"
        target = $item.LivePath
        type = $item.Type
        live_root = $item.LiveRoot
        previous_state = $previousState
        backup_path = $backupPath
        after = Get-PortablePathFingerprint -Path $item.LivePath
    })
    Write-Host "installed: $($item.LivePath)"
}

foreach ($state in $retiredRemovalStates) {
    $item = $state.Item
    $itemBackupRoot = Get-ItemBackupRoot -LiveRoot $item.LiveRoot
    $backupPath = Get-ItemBackupPath -Item $item -BackupRoot $itemBackupRoot
    Backup-LiveItem -LivePath $item.LivePath -BackupRoot $itemBackupRoot -LiveRoot $item.LiveRoot -BackupScope $item.BackupScope -Type $item.Type
    Remove-Item -LiteralPath $item.LivePath -Recurse -Force
    $changes.Add([pscustomobject]@{
        operation = "retire"
        target = $item.LivePath
        type = $item.Type
        live_root = $item.LiveRoot
        previous_state = "backup"
        backup_path = $backupPath
        after = Get-PortablePathFingerprint -Path $item.LivePath
    })
    Write-Host "removed retired: $($item.LivePath)"
}

if (-not $SkipSkillRuntimeSetup) {
    & (Join-Path $PSScriptRoot "setup-skill-runtime.ps1") -AgentsHome $agentsHome
    if ($LASTEXITCODE -ne 0) {
        throw "skill runtime setup failed"
    }
}

if ([bool]$reviewedConfigState.changed) {
    $configItem = [pscustomobject]@{
        LivePath = $liveConfigPath
        LiveRoot = $liveHome
        BackupScope = "codex"
        Type = "file"
    }
    $previousState = "missing"
    $backupPath = $null
    if ([bool]$reviewedConfigState.live_exists) {
        $configBackupRoot = Get-ItemBackupRoot -LiveRoot $liveHome
        $backupPath = Get-ItemBackupPath -Item $configItem -BackupRoot $configBackupRoot
        Backup-LiveItem -LivePath $liveConfigPath -BackupRoot $configBackupRoot -LiveRoot $liveHome -BackupScope "codex" -Type "file"
        $previousState = "backup"
    }
    Write-ReviewedConfigAtomically -Path $liveConfigPath -Text ([string]$reviewedConfigState.merged_text)
    $changes.Add([pscustomobject]@{
        operation = "config-overlay"
        target = $liveConfigPath
        type = "config-overlay"
        live_root = $liveHome
        previous_state = $previousState
        backup_path = $backupPath
        after = Get-PortablePathFingerprint -Path $liveConfigPath
    })
    Write-Host "reviewed config overlaid: $liveConfigPath ($($reviewedConfigState.changed_count) settings)"
}
else {
    Write-Host "reviewed config unchanged: $liveConfigPath"
}

$targetSetChanged = -not (Test-ReceiptTargetSetEqual -Receipt $currentReceipt -ActiveItems $items -RetiredItems $retiredItems)
$provenanceChanged = $null -eq $currentReceipt -or
    [string]$currentReceipt.source_ref -ne [string]$resolvedSourceRef -or
    [string]$currentReceipt.source_commit -ne [string]$resolvedSourceCommit
$receiptNeeded = $changes.Count -gt 0 -or $targetSetChanged -or $provenanceChanged
$receiptPath = $null

if ($receiptNeeded) {
    $artifacts = @(
        foreach ($item in $items) {
            [ordered]@{
                source = Get-RepoRelativePath -Path $item.RepoPath
                target = $item.LivePath
                type = $item.Type
                state = "present"
                ownership = "compass"
                fingerprint = Get-PortablePathFingerprint -Path $item.LivePath
            }
        }
        foreach ($item in $retiredItems) {
            [ordered]@{
                source = $null
                target = $item.LivePath
                type = $item.Type
                state = "retired"
                ownership = "compass"
                fingerprint = Get-PortablePathFingerprint -Path $item.LivePath
            }
        }
    )
    $backupRootRecords = @(
        foreach ($entry in $backupRoots.GetEnumerator() | Sort-Object Name) {
            [ordered]@{
                live_root = $entry.Key
                backup_root = $entry.Value
            }
        }
    )
    $receipt = [ordered]@{
        schema_version = 1
        id = "install-$((Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssfffZ'))"
        installed_at = (Get-Date).ToUniversalTime().ToString("o")
        source_ref = $resolvedSourceRef
        source_commit = $resolvedSourceCommit
        previous_receipt_id = if ($currentReceipt) { $currentReceipt.id } else { $null }
        targets = [ordered]@{
            codex_home = $liveHome
            agents_home = $agentsHome
            claude_home = $claudeHome
        }
        backup_roots = $backupRootRecords
        changes = @($changes.ToArray())
        artifacts = $artifacts
    }
    $receiptPath = Write-PortableReceipt -CodexHome $liveHome -Receipt $receipt
}

Write-Host ""
Write-Host "changed: $($changedStates.Count)"
Write-Host "missing: $($missingStates.Count)"
Write-Host "unchanged: $($unchangedStates.Count)"
Write-Host "reviewed config: $($reviewedConfigState.changed_count)"
Write-Host "retired: $($retiredRemovalStates.Count)"
Write-Host "foreign: $($foreignStates.Count)"
if ($backupRoots.Count -gt 0) {
    Write-Host "backups: $($backupRoots.Values -join ', ')"
}
else {
    Write-Host "backups: none"
}
if ($receiptPath) {
    Write-Host "receipt: $receiptPath"
}
else {
    Write-Host "receipt: unchanged"
}
