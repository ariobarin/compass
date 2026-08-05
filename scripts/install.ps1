[CmdletBinding()]
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
$items = @(
    Get-PortableFileMap `
        -RepoRoot $repoRoot `
        -CodexHome $liveHome `
        -AgentsHome $agentsHome `
        -ClaudeHome $claudeHome
)
$states = @(
    foreach ($item in $items) {
        [pscustomobject]@{
            Item = $item
            Exists = Test-Path -LiteralPath $item.LivePath
            InSync = Test-PortableItemInSync -Item $item
        }
    }
)
$changes = @($states | Where-Object { -not $_.InSync })
$missing = @($states | Where-Object { -not $_.Exists })
$unchanged = @($states | Where-Object { $_.InSync })

Write-Host "repo: $repoRoot"
Write-Host "codex: $liveHome"
Write-Host "agents: $agentsHome"
Write-Host "claude: $claudeHome"
Write-Host ""

if (-not $Apply) {
    Write-Host "review mode: no files will be changed"
    Write-Host "planned copies:"
    if ($changes.Count -eq 0) {
        Write-Host "  none"
    }
    else {
        foreach ($state in $changes) {
            Write-Host "  $($state.Item.RepoPath) -> $($state.Item.LivePath)"
            if ($state.Item.Type -eq "config" -and $state.Exists) {
                foreach ($entry in @(Get-PortableConfigDrift `
                    -Source $state.Item.RepoPath `
                    -Destination $state.Item.LivePath
                )) {
                    Write-Host "    reviewed config key $($entry.State): $($entry.Key)"
                }
            }
        }
    }
    Write-Host ""
    Write-Host "changed: $($changes.Count - $missing.Count)"
    Write-Host "missing: $($missing.Count)"
    Write-Host "unchanged: $($unchanged.Count)"
    Write-Host "run with -Apply to install the approved plan"
    exit 0
}

$backupRoot = $null
if (@($changes | Where-Object { $_.Exists }).Count -gt 0) {
    $stamp = Get-Date -Format "yyyyMMdd-HHmmss-fffffff"
    $backupRoot = Join-Path $liveHome "portable-backups\$stamp"
}

foreach ($state in $changes) {
    $item = $state.Item
    if ($state.Exists) {
        Backup-LiveItem `
            -LivePath $item.LivePath `
            -BackupRoot $backupRoot `
            -BackupAllowedRoot $liveHome `
            -LiveRoot $item.LiveRoot `
            -BackupScope $item.BackupScope
    }
    Copy-PortableItem `
        -Source $item.RepoPath `
        -Destination $item.LivePath `
        -Type $item.Type `
        -AllowedRoot $item.LiveRoot
    Write-Host "installed: $($item.LivePath)"
}

Write-Host ""
Write-Host "changed: $($changes.Count - $missing.Count)"
Write-Host "missing: $($missing.Count)"
Write-Host "unchanged: $($unchanged.Count)"
if ($backupRoot) {
    Write-Host "backups: $backupRoot"
}
else {
    Write-Host "backups: none"
}
