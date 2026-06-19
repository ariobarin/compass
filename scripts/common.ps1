Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-RepoRoot {
    return (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
}

function Get-CodexHome {
    param([string]$CodexHome)

    if ($CodexHome) {
        return (Resolve-Path $CodexHome).Path
    }

    if ($env:CODEX_HOME) {
        return (Resolve-Path $env:CODEX_HOME).Path
    }

    $default = Join-Path $env:USERPROFILE ".codex"
    return (Resolve-Path $default).Path
}

function New-DirectoryForFile {
    param([string]$Path)

    $dir = Split-Path -Parent $Path
    if ($dir -and -not (Test-Path $dir)) {
        New-Item -ItemType Directory -Force $dir | Out-Null
    }
}

function Assert-PathUnderRoot {
    param(
        [string]$Path,
        [string]$Root
    )

    $fullRoot = [System.IO.Path]::GetFullPath($Root).TrimEnd("\")
    $fullPath = [System.IO.Path]::GetFullPath($Path).TrimEnd("\")

    if ($fullPath -eq $fullRoot) {
        return
    }

    $prefix = "$fullRoot\"
    if (-not $fullPath.StartsWith($prefix, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "refusing to write outside allowed root: $Path"
    }
}

function Get-PortableFileMap {
    param(
        [string]$RepoRoot,
        [string]$CodexHome
    )

    $items = New-Object System.Collections.Generic.List[object]

    foreach ($relative in @("AGENTS.md", "hooks.json", "keybindings.json")) {
        $items.Add([pscustomobject]@{
            Type = "file"
            RepoPath = Join-Path (Join-Path $RepoRoot "codex") $relative
            LivePath = Join-Path $CodexHome $relative
        })
    }

    foreach ($relative in @("agents", "hooks")) {
        $items.Add([pscustomobject]@{
            Type = "dir"
            RepoPath = Join-Path (Join-Path $RepoRoot "codex") $relative
            LivePath = Join-Path $CodexHome $relative
        })
    }

    foreach ($skill in @(
        "action-items-to-prs",
        "benchmark-infra-reviewer",
        "benchmark-run-operator",
        "git-branch-resolver",
        "grill-me",
        "subagent-driven-development",
        "to-prd",
        "ui-ux-pro-max",
        "using-codex-goals",
        "webmcp-eval-triage",
        "webmcp-tool-authoring",
        "webmcp-verify-tool",
        "write-a-skill"
    )) {
        $items.Add([pscustomobject]@{
            Type = "dir"
            RepoPath = Join-Path (Join-Path (Join-Path $RepoRoot "codex") "skills") $skill
            LivePath = Join-Path (Join-Path $CodexHome "skills") $skill
        })
    }

    return $items
}

function Copy-PortableItem {
    param(
        [string]$Source,
        [string]$Destination,
        [string]$Type,
        [string]$AllowedRoot
    )

    if (-not (Test-Path $Source)) {
        Write-Host "skip missing source: $Source"
        return
    }

    if ($AllowedRoot) {
        Assert-PathUnderRoot -Path $Destination -Root $AllowedRoot
    }

    if ($Type -eq "dir") {
        if (Test-Path $Destination) {
            Remove-Item -LiteralPath $Destination -Recurse -Force
        }
        New-Item -ItemType Directory -Force (Split-Path -Parent $Destination) | Out-Null
        Copy-Item -LiteralPath $Source -Destination $Destination -Recurse -Force
        return
    }

    New-DirectoryForFile -Path $Destination
    Copy-Item -LiteralPath $Source -Destination $Destination -Force
}
