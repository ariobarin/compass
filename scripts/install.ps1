param(
    [switch]$Apply,
    [string]$CodexHome
)

. "$PSScriptRoot\common.ps1"

$repoRoot = Get-RepoRoot
$liveHome = Get-CodexHome -CodexHome $CodexHome
$items = Get-PortableFileMap -RepoRoot $repoRoot -CodexHome $liveHome

Write-Host "repo: $repoRoot"
Write-Host "live: $liveHome"
Write-Host ""

if (-not $Apply) {
    Write-Host "review mode: no files will be changed"
    Write-Host "planned copies:"
    foreach ($item in $items) {
        Write-Host "  $($item.RepoPath) -> $($item.LivePath)"
    }
    Write-Host ""
    Write-Host "run with -Apply to copy these files into the live Codex home"
    exit 0
}

$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$backupRoot = Join-Path $liveHome "portable-backups\$stamp"
New-Item -ItemType Directory -Force $backupRoot | Out-Null

foreach ($item in $items) {
    if (Test-Path $item.LivePath) {
        $relative = $item.LivePath.Substring($liveHome.Length).TrimStart("\")
        $backupPath = Join-Path $backupRoot $relative
        if ($item.Type -eq "dir") {
            New-Item -ItemType Directory -Force (Split-Path -Parent $backupPath) | Out-Null
            Copy-Item -LiteralPath $item.LivePath -Destination $backupPath -Recurse -Force
        }
        else {
            New-DirectoryForFile -Path $backupPath
            Copy-Item -LiteralPath $item.LivePath -Destination $backupPath -Force
        }
    }

    Copy-PortableItem -Source $item.RepoPath -Destination $item.LivePath -Type $item.Type -AllowedRoot $liveHome
    Write-Host "installed: $($item.LivePath)"
}

Write-Host ""
Write-Host "backup: $backupRoot"
Write-Host "config.review.toml was not installed automatically"
