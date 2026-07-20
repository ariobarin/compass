param(
    [string]$CodexHome,
    [switch]$Apply,
    [switch]$RequireAbsent
)

. "$PSScriptRoot\common.ps1"
. "$PSScriptRoot\plugin-retirement.ps1"

$repoRoot = Get-RepoRoot
$liveHome = Get-CodexHome -CodexHome $CodexHome
$state = Get-RetiredPluginState -RepoRoot $repoRoot -CodexHome $liveHome

if (-not $state.Available) {
    Write-Host "codex command not found; retired plugin state unavailable"
    if ($RequireAbsent) {
        exit 1
    }
    exit 0
}

foreach ($plugin in @($state.Plugins)) {
    Write-Host "retired plugin present: $plugin"
}
foreach ($marketplace in @($state.Marketplaces)) {
    Write-Host "retired marketplace present: $marketplace"
}

if ($Apply -and (@($state.Plugins).Count -gt 0 -or @($state.Marketplaces).Count -gt 0)) {
    Remove-RetiredPluginState -CodexHome $liveHome -State $state
    $state = Get-RetiredPluginState -RepoRoot $repoRoot -CodexHome $liveHome
}

if (@($state.Plugins).Count -eq 0 -and @($state.Marketplaces).Count -eq 0) {
    Write-Host "retired plugins absent"
    exit 0
}

if ($RequireAbsent) {
    exit 1
}
