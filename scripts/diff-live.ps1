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

    $repoPath = $item.RepoPath
    $livePath = $item.LivePath
    $tempRoot = $null
    if ($item.Type -eq "stateful-dir" -and (Test-Path $item.RepoPath) -and (Test-Path $item.LivePath)) {
        $tempRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("compass-stateful-diff-" + [guid]::NewGuid().ToString("N"))
        $repoPath = Join-Path $tempRoot "repo"
        $livePath = Join-Path $tempRoot "live"
        Copy-PortableItem -Source $item.RepoPath -Destination $repoPath -Type $item.Type -AllowedRoot $tempRoot -SkipRuntimeBootstrap
        Copy-PortableItem -Source $item.LivePath -Destination $livePath -Type $item.Type -AllowedRoot $tempRoot -SkipRuntimeBootstrap
    }
    elseif (($item.Type -in @("derived-skill", "derived-agent")) -and (Test-Path $item.RepoPath)) {
        $tempRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("compass-derived-diff-" + [guid]::NewGuid().ToString("N"))
        $leaf = if ($item.Type -eq "derived-agent") { "agent.md" } else { "skill" }
        $repoPath = Join-Path $tempRoot $leaf
        Copy-PortableItem -Source $item.RepoPath -Destination $repoPath -Type $item.Type -AllowedRoot $tempRoot
    }

    Write-Host ""
    Write-Host "diff: $repoPath <=> $livePath"
    git diff --no-index -- $repoPath $livePath
    if ($LASTEXITCODE -eq 1) {
        $hadDiff = $true
    }
    elseif ($LASTEXITCODE -gt 1) {
        if ($tempRoot) {
            Remove-Item -LiteralPath $tempRoot -Recurse -Force -ErrorAction SilentlyContinue
        }
        exit $LASTEXITCODE
    }

    if ($tempRoot) {
        Remove-Item -LiteralPath $tempRoot -Recurse -Force
    }
}

if ($hadDiff) {
    exit 1
}
