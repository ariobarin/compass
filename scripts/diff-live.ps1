param(
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
$hadDiff = $false

foreach ($item in $items) {
    if (-not (Test-Path $item.RepoPath) -and -not (Test-Path $item.LivePath)) {
        continue
    }

    Write-Host ""
    Write-Host "diff: $($item.RepoPath) <=> $($item.LivePath)"
    git diff --no-index -- $item.RepoPath $item.LivePath
    if ($LASTEXITCODE -eq 1) {
        $hadDiff = $true
    }
    elseif ($LASTEXITCODE -gt 1) {
        exit $LASTEXITCODE
    }
}

if ($hadDiff) {
    exit 1
}
