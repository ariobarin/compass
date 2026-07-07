param(
    [switch]$Apply,
    [string]$CodexHome,
    [string]$AgentsHome,
    [string]$ClaudeHome
)

. "$PSScriptRoot\common.ps1"

$repoRoot = Get-RepoRoot
$liveHome = Get-CodexHome -CodexHome $CodexHome
$agentsHome = Get-AgentsHome -AgentsHome $AgentsHome
$claudeHome = Get-ClaudeHome -ClaudeHome $ClaudeHome
$items = Get-PortableFileMap -RepoRoot $repoRoot -CodexHome $liveHome -AgentsHome $agentsHome -ClaudeHome $claudeHome

Write-Host "repo: $repoRoot"
Write-Host "codex: $liveHome"
Write-Host "agents: $agentsHome"
Write-Host "claude: $claudeHome"
Write-Host ""

if (-not $Apply) {
    Write-Host "review mode: no files will be changed"
    Write-Host "planned snapshots:"
    foreach ($item in $items) {
        if ($item.Type -in @("derived-skill", "derived-agent")) {
            Write-Host "  skip derived: $($item.LivePath) is generated from $($item.RepoPath)"
            continue
        }

        Write-Host "  $($item.LivePath) -> $($item.RepoPath)"
    }
    Write-Host ""
    Write-Host "run with -Apply to refresh this repo from the live Codex home and user skill home"
    exit 0
}

foreach ($item in $items) {
    if ($item.Type -eq "derived-skill") {
        Write-Host "skipped derived: $($item.LivePath)"
        continue
    }

    Copy-PortableItem -Source $item.LivePath -Destination $item.RepoPath -Type $item.Type -AllowedRoot $repoRoot
    Write-Host "snapshotted: $($item.RepoPath)"
}

Write-Host ""
Write-Host "review the git diff before committing"
