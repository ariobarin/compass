Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-RetiredPluginContract {
    param([string]$RepoRoot)

    $path = Join-Path $RepoRoot "manifests\retired-plugins.json"
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        throw "missing retired plugin manifest: $path"
    }
    try {
        $contract = Get-Content -Raw -LiteralPath $path | ConvertFrom-Json
    }
    catch {
        throw "invalid retired plugin manifest: $path"
    }
    if ($contract.schema_version -ne 1) {
        throw "unsupported retired plugin manifest schema"
    }
    return $contract
}

function Invoke-CodexPluginJson {
    param(
        [string]$CodexHome,
        [string[]]$Arguments
    )

    $previousCodexHome = $env:CODEX_HOME
    try {
        $env:CODEX_HOME = $CodexHome
        $output = @(& codex @Arguments 2>&1 | ForEach-Object { $_.ToString() })
        if ($LASTEXITCODE -ne 0) {
            throw "codex $($Arguments -join ' ') failed: $($output -join [Environment]::NewLine)"
        }
        return ($output -join "`n") | ConvertFrom-Json
    }
    finally {
        $env:CODEX_HOME = $previousCodexHome
    }
}

function Get-RetiredPluginState {
    param(
        [string]$RepoRoot,
        [string]$CodexHome
    )

    if (-not (Get-Command codex -ErrorAction SilentlyContinue)) {
        return [pscustomobject]@{
            Available = $false
            Plugins = @()
            Marketplaces = @()
        }
    }

    $contract = Get-RetiredPluginContract -RepoRoot $RepoRoot
    $pluginData = Invoke-CodexPluginJson -CodexHome $CodexHome -Arguments @("plugin", "list", "--json")
    $marketplaceData = Invoke-CodexPluginJson -CodexHome $CodexHome -Arguments @("plugin", "marketplace", "list", "--json")

    $plugins = @(
        @($pluginData.installed) |
            Where-Object { $_.installed -and @($contract.plugins) -contains [string]$_.pluginId } |
            ForEach-Object { [string]$_.pluginId }
    )
    $marketplaces = @(
        @($marketplaceData.marketplaces) |
            Where-Object { @($contract.marketplaces) -contains [string]$_.name } |
            ForEach-Object { [string]$_.name }
    )
    return [pscustomobject]@{
        Available = $true
        Plugins = $plugins
        Marketplaces = $marketplaces
    }
}

function Remove-RetiredPluginState {
    param(
        [string]$CodexHome,
        [object]$State
    )

    $previousCodexHome = $env:CODEX_HOME
    try {
        $env:CODEX_HOME = $CodexHome
        foreach ($plugin in @($State.Plugins)) {
            & codex plugin remove $plugin --json *> $null
            if ($LASTEXITCODE -ne 0) {
                throw "failed to remove retired plugin: $plugin"
            }
            Write-Host "removed retired plugin: $plugin"
        }
        foreach ($marketplace in @($State.Marketplaces)) {
            & codex plugin marketplace remove $marketplace --json *> $null
            if ($LASTEXITCODE -ne 0) {
                throw "failed to remove retired marketplace: $marketplace"
            }
            Write-Host "removed retired marketplace: $marketplace"
        }
    }
    finally {
        $env:CODEX_HOME = $previousCodexHome
    }
}
