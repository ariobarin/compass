param(
    [switch]$Apply,
    [string]$CodexHome,
    [string]$AgentsHome
)

. "$PSScriptRoot\common.ps1"

$repoRoot = Get-RepoRoot
$liveHome = Get-CodexHome -CodexHome $CodexHome
$agentsHome = Get-AgentsHome -AgentsHome $AgentsHome
$items = Get-PortableFileMap -RepoRoot $repoRoot -CodexHome $liveHome -AgentsHome $agentsHome
$retiredItems = Get-RetiredPortableFileMap -CodexHome $liveHome

Write-Host "repo: $repoRoot"
Write-Host "codex: $liveHome"
Write-Host "agents: $agentsHome"
Write-Host ""

if (-not $Apply) {
    Write-Host "review mode: no files will be changed"
    Write-Host "planned copies:"
    foreach ($item in $items) {
        Write-Host "  $($item.RepoPath) -> $($item.LivePath)"
    }

    $existingRetiredItems = @($retiredItems | Where-Object { Test-Path $_.LivePath })
    if ($existingRetiredItems.Count -gt 0) {
        Write-Host ""
        Write-Host "planned retired removals:"
        foreach ($item in $existingRetiredItems) {
            Write-Host "  $($item.LivePath)"
        }
    }

    Write-Host ""
    Write-Host "run with -Apply to copy these files into the live Codex and Agents homes"
    exit 0
}

$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$backupRoot = Join-Path $liveHome "portable-backups\$stamp"
New-Item -ItemType Directory -Force $backupRoot | Out-Null

foreach ($item in $items) {
    if (Test-Path $item.LivePath) {
        Backup-LiveItem -LivePath $item.LivePath -BackupRoot $backupRoot -LiveRoot $item.LiveRoot -BackupScope $item.BackupScope -Type $item.Type
    }

    Copy-PortableItem -Source $item.RepoPath -Destination $item.LivePath -Type $item.Type -AllowedRoot $item.LiveRoot
    Write-Host "installed: $($item.LivePath)"
}

foreach ($item in $retiredItems) {
    if (-not (Test-Path $item.LivePath)) {
        continue
    }

    Backup-LiveItem -LivePath $item.LivePath -BackupRoot $backupRoot -LiveRoot $item.LiveRoot -BackupScope $item.BackupScope -Type $item.Type
    Remove-Item -LiteralPath $item.LivePath -Recurse -Force
    Write-Host "removed retired: $($item.LivePath)"
}

Write-Host ""
Write-Host "backup: $backupRoot"
Write-Host "config.review.toml was not installed automatically"
