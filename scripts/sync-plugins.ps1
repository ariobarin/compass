param(
    [switch]$Apply,
    [switch]$Refresh,
    [string]$CodexHome
)

. "$PSScriptRoot\common.ps1"

if (-not (Get-Command codex -ErrorAction SilentlyContinue)) {
    throw "codex command not found; cannot sync declared plugins"
}

$repoRoot = Get-RepoRoot
$liveHome = Get-CodexHome -CodexHome $CodexHome
$manifestPath = Join-Path $repoRoot "manifests\plugins.json"
if (-not (Test-Path -LiteralPath $manifestPath -PathType Leaf)) {
    throw "missing plugin manifest: $manifestPath"
}

$manifest = Get-Content -Raw -LiteralPath $manifestPath | ConvertFrom-Json
$previousCodexHome = $env:CODEX_HOME
$env:CODEX_HOME = $liveHome

function Invoke-CodexJson {
    param([string[]]$Arguments)

    $output = & codex @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "codex failed: codex $($Arguments -join ' ')"
    }
    return ($output | Out-String | ConvertFrom-Json)
}

try {
    $marketplaceState = Invoke-CodexJson -Arguments @("plugin", "marketplace", "list", "--json")
    $marketplaces = @($marketplaceState.marketplaces)

    foreach ($marketplace in @($manifest.marketplaces)) {
        $existing = @($marketplaces | Where-Object { $_.name -eq $marketplace.name })
        if ($existing.Count -eq 0) {
            Write-Host "marketplace missing: $($marketplace.name)"
            if ($Apply) {
                $arguments = @("plugin", "marketplace", "add", $marketplace.source, "--json")
                foreach ($sparsePath in @($marketplace.sparse)) {
                    $arguments += @("--sparse", $sparsePath)
                }
                Invoke-CodexJson -Arguments $arguments | Out-Null
                Write-Host "marketplace added: $($marketplace.name)"
            }
        }
        elseif ((Get-NormalizedMarketplaceSource -Source $existing[0].marketplaceSource.source) -ne (Get-NormalizedMarketplaceSource -Source $marketplace.source)) {
            throw "marketplace source mismatch for $($marketplace.name): $($existing[0].marketplaceSource.source)"
        }
        elseif ($Apply -and $Refresh) {
            & codex plugin marketplace upgrade $marketplace.name
            if ($LASTEXITCODE -ne 0) {
                throw "codex failed: codex plugin marketplace upgrade $($marketplace.name)"
            }
            Write-Host "marketplace refreshed: $($marketplace.name)"
        }
        else {
            Write-Host "marketplace present: $($marketplace.name)"
        }
    }

    $pluginState = Invoke-CodexJson -Arguments @("plugin", "list", "--json")
    $installedIds = @($pluginState.installed | ForEach-Object { $_.pluginId })
    foreach ($pluginId in @($manifest.plugins)) {
        $installed = $installedIds -contains $pluginId
        if ($installed -and -not ($Apply -and $Refresh)) {
            Write-Host "plugin present: $pluginId"
            continue
        }

        if ($installed) {
            & codex plugin remove $pluginId
            if ($LASTEXITCODE -ne 0) {
                throw "codex failed: codex plugin remove $pluginId"
            }
            Write-Host "plugin removed for refresh: $pluginId"
        }
        else {
            Write-Host "plugin missing: $pluginId"
        }

        if ($Apply) {
            Invoke-CodexJson -Arguments @("plugin", "add", $pluginId, "--json") | Out-Null
            Write-Host "plugin installed: $pluginId"
        }
    }

    if (-not $Apply) {
        Write-Host "review mode: no plugin state was changed"
    }
}
finally {
    $env:CODEX_HOME = $previousCodexHome
}
