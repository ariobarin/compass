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

Write-Host "repo: $repoRoot"
Write-Host "codex: $liveHome"
Write-Host "agents: $agentsHome"
Write-Host ""

if (-not $Apply) {
    Write-Host "review mode: no files will be changed"
    Write-Host "planned snapshots:"
    foreach ($item in $items) {
        Write-Host "  $($item.LivePath) -> $($item.RepoPath)"
    }
    Write-Host ""
    Write-Host "run with -Apply to refresh this repo from the live Codex and Agents homes"
    exit 0
}

foreach ($item in $items) {
    Copy-PortableItem -Source $item.LivePath -Destination $item.RepoPath -Type $item.Type -AllowedRoot $repoRoot
    Write-Host "snapshotted: $($item.RepoPath)"
}

Write-Host ""
Write-Host "review the git diff before committing"
