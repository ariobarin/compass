[CmdletBinding()]
param(
    [string]$CodexHome,
    [string]$AgentsHome,
    [string]$ClaudeHome,
    [switch]$RequireInSync
)

. "$PSScriptRoot\common.ps1"

$repoRoot = Get-RepoRoot
$liveHome = Get-CodexHome -CodexHome $CodexHome
$agentsHome = Get-AgentsHome -AgentsHome $AgentsHome
$claudeHome = Get-ClaudeHome -ClaudeHome $ClaudeHome
$items = @(
    Get-PortableFileMap `
        -RepoRoot $repoRoot `
        -CodexHome $liveHome `
        -AgentsHome $agentsHome `
        -ClaudeHome $claudeHome
)
$missing = New-Object System.Collections.Generic.List[string]
$drift = New-Object System.Collections.Generic.List[object]

foreach ($item in $items) {
    if (-not (Test-Path -LiteralPath $item.LivePath)) {
        $missing.Add($item.LivePath)
        continue
    }
    if (-not (Test-PortableItemInSync -Item $item)) {
        $drift.Add($item)
    }
}

Write-Host "repo: $repoRoot"
Write-Host "codex: $liveHome"
Write-Host "agents: $agentsHome"
Write-Host "claude: $claudeHome"

if ($missing.Count -gt 0) {
    Write-Host ""
    Write-Host "missing:"
    foreach ($path in $missing) {
        Write-Host "  $path"
    }
}

if ($drift.Count -gt 0) {
    Write-Host ""
    Write-Host "drift:"
    foreach ($item in $drift) {
        Write-Host "  $($item.LivePath)"
        if ($item.Type -eq "config") {
            foreach ($entry in @(Get-PortableConfigDrift `
                -Source $item.RepoPath `
                -Destination $item.LivePath
            )) {
                Write-Host "    reviewed config key $($entry.State): $($entry.Key)"
            }
        }
    }
}

if ($missing.Count -eq 0 -and $drift.Count -eq 0) {
    Write-Host "portable files match live allowlist"
}

if ($RequireInSync -and ($missing.Count -gt 0 -or $drift.Count -gt 0)) {
    exit 1
}
