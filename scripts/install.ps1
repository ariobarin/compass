param(
    [switch]$Apply,
    [switch]$SkipPlugins,
    [string]$CodexHome,
    [string]$AgentsHome,
    [string]$ClaudeHome
)

. "$PSScriptRoot\common.ps1"

[char[]]$pathSeparators = @(
    [System.IO.Path]::DirectorySeparatorChar,
    [System.IO.Path]::AltDirectorySeparatorChar
) | Select-Object -Unique

function Get-RelativeFileMap {
    param(
        [string]$Root,
        [switch]$DerivedSkill
    )

    $map = @{}
    if (-not (Test-Path -LiteralPath $Root -PathType Container)) {
        return $map
    }

    $files = if ($DerivedSkill) {
        $selected = New-Object System.Collections.Generic.List[object]
        $skillFile = Join-Path $Root "SKILL.md"
        if (Test-Path -LiteralPath $skillFile -PathType Leaf) {
            $selected.Add((Get-Item -LiteralPath $skillFile))
        }
        $references = Join-Path $Root "references"
        if (Test-Path -LiteralPath $references -PathType Container) {
            foreach ($file in Get-ChildItem -LiteralPath $references -Recurse -File -Force) {
                $selected.Add($file)
            }
        }
        $selected.ToArray()
    }
    else {
        @(Get-ChildItem -LiteralPath $Root -Recurse -File -Force)
    }

    $resolvedRoot = (Resolve-Path -LiteralPath $Root).Path
    foreach ($file in $files) {
        $relative = $file.FullName.Substring($resolvedRoot.Length).TrimStart($pathSeparators)
        $map[$relative] = (Get-FileHash -Algorithm SHA256 -LiteralPath $file.FullName).Hash
    }
    return $map
}

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

    $expected = Get-RelativeFileMap -Root $Item.RepoPath -DerivedSkill:($Item.Type -eq "derived-skill")
    $actual = Get-RelativeFileMap -Root $Item.LivePath
    return Test-FileMapsEqual -Expected $expected -Actual $actual
}

$repoRoot = Get-RepoRoot
$liveHome = Get-CodexHome -CodexHome $CodexHome
$agentsHome = Get-AgentsHome -AgentsHome $AgentsHome
$claudeHome = Get-ClaudeHome -ClaudeHome $ClaudeHome
$items = Get-PortableFileMap -RepoRoot $repoRoot -CodexHome $liveHome -AgentsHome $agentsHome -ClaudeHome $claudeHome
$retiredItems = Get-RetiredPortableFileMap -CodexHome $liveHome -AgentsHome $agentsHome
$itemStates = @(
    foreach ($item in $items) {
        [pscustomobject]@{
            Item = $item
            InSync = Test-PortableItemInSync -Item $item
        }
    }
)
$changedStates = @($itemStates | Where-Object { -not $_.InSync })
$unchangedStates = @($itemStates | Where-Object { $_.InSync })
$existingRetiredItems = @($retiredItems | Where-Object { Test-Path -LiteralPath $_.LivePath })

Write-Host "repo: $repoRoot"
Write-Host "codex: $liveHome"
Write-Host "agents: $agentsHome"
Write-Host "claude: $claudeHome"
Write-Host ""

if (-not $Apply) {
    Write-Host "review mode: no files will be changed"
    Write-Host "planned copies:"
    if ($changedStates.Count -eq 0) {
        Write-Host "  none"
    }
    else {
        foreach ($state in $changedStates) {
            Write-Host "  $($state.Item.RepoPath) -> $($state.Item.LivePath)"
        }
    }

    if ($existingRetiredItems.Count -gt 0) {
        Write-Host ""
        Write-Host "planned retired removals:"
        foreach ($item in $existingRetiredItems) {
            Write-Host "  $($item.LivePath)"
        }
    }

    Write-Host ""
    Write-Host "changed: $($changedStates.Count)"
    Write-Host "unchanged: $($unchangedStates.Count)"
    Write-Host "retired: $($existingRetiredItems.Count)"
    if (-not $SkipPlugins) {
        Write-Host ""
        & (Join-Path $PSScriptRoot "sync-plugins.ps1") -CodexHome $liveHome
        if ($LASTEXITCODE -ne 0) {
            throw "plugin sync review failed"
        }
    }
    Write-Host "run with -Apply to copy changed files into the live Codex home, user skill home, and Claude home"
    exit 0
}

$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$backupRoots = @{}

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

foreach ($state in $changedStates) {
    $item = $state.Item
    if (Test-Path -LiteralPath $item.LivePath) {
        $itemBackupRoot = Get-ItemBackupRoot -LiveRoot $item.LiveRoot
        Backup-LiveItem -LivePath $item.LivePath -BackupRoot $itemBackupRoot -LiveRoot $item.LiveRoot -BackupScope $item.BackupScope -Type $item.Type
    }

    Copy-PortableItem -Source $item.RepoPath -Destination $item.LivePath -Type $item.Type -AllowedRoot $item.LiveRoot
    Write-Host "installed: $($item.LivePath)"
}

foreach ($item in $existingRetiredItems) {
    $itemBackupRoot = Get-ItemBackupRoot -LiveRoot $item.LiveRoot
    Backup-LiveItem -LivePath $item.LivePath -BackupRoot $itemBackupRoot -LiveRoot $item.LiveRoot -BackupScope $item.BackupScope -Type $item.Type
    Remove-Item -LiteralPath $item.LivePath -Recurse -Force
    Write-Host "removed retired: $($item.LivePath)"
}

Write-Host ""
Write-Host "changed: $($changedStates.Count)"
Write-Host "unchanged: $($unchangedStates.Count)"
Write-Host "retired: $($existingRetiredItems.Count)"
if ($backupRoots.Count -gt 0) {
    Write-Host "backups: $($backupRoots.Values -join ', ')"
}
else {
    Write-Host "backups: none"
}
if (-not $SkipPlugins) {
    & (Join-Path $PSScriptRoot "sync-plugins.ps1") -Apply -CodexHome $liveHome
    if ($LASTEXITCODE -ne 0) {
        throw "plugin sync failed"
    }
}
Write-Host "config.review.toml was not installed automatically"
