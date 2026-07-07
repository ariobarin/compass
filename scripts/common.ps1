Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-RepoRoot {
    return (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
}

function Get-CodexHome {
    param([string]$CodexHome)

    if ($CodexHome) {
        return $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($CodexHome)
    }

    if ($env:CODEX_HOME) {
        return $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($env:CODEX_HOME)
    }

    $default = Join-Path $env:USERPROFILE ".codex"
    return $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($default)
}

function Get-AgentsHome {
    param([string]$AgentsHome)

    if ($AgentsHome) {
        return $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($AgentsHome)
    }

    $default = Join-Path $HOME ".agents"
    return $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($default)
}

function Get-ClaudeHome {
    param([string]$ClaudeHome)

    if ($ClaudeHome) {
        return $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($ClaudeHome)
    }

    $default = Join-Path $HOME ".claude"
    return $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($default)
}

function Get-PortableSkillNames {
    $manifestPath = Join-Path (Get-RepoRoot) "manifests\portable-files.toml"
    if (-not (Test-Path -LiteralPath $manifestPath)) {
        throw "missing portable manifest: $manifestPath"
    }

    $manifestText = Get-Content -Raw -LiteralPath $manifestPath
    $sectionPattern = "(?ms)^\[agents\]\s*(.*?)(?=^\[|\z)"
    $sectionMatch = [regex]::Match($manifestText, $sectionPattern)
    if (-not $sectionMatch.Success) {
        throw "missing agents section in portable manifest"
    }

    $skillsPattern = "(?ms)^\s*skills\s*=\s*\[(.*?)^\s*\]"
    $skillsMatch = [regex]::Match($sectionMatch.Groups[1].Value, $skillsPattern)
    if (-not $skillsMatch.Success) {
        throw "missing portable skill list in manifest"
    }

    return @(
        [regex]::Matches($skillsMatch.Groups[1].Value, '"([^"]+)"') |
            ForEach-Object { $_.Groups[1].Value }
    )
}

function Get-PortableManifestArray {
    param(
        [string]$Section,
        [string]$Key
    )

    $manifestPath = Join-Path (Get-RepoRoot) "manifests\portable-files.toml"
    if (-not (Test-Path -LiteralPath $manifestPath)) {
        throw "missing portable manifest: $manifestPath"
    }

    $manifestText = Get-Content -Raw -LiteralPath $manifestPath
    $sectionPattern = "(?ms)^\[$([regex]::Escape($Section))\]\s*(.*?)(?=^\[|\z)"
    $sectionMatch = [regex]::Match($manifestText, $sectionPattern)
    if (-not $sectionMatch.Success) {
        return @()
    }

    $arrayPattern = "(?ms)^\s*$([regex]::Escape($Key))\s*=\s*\[(.*?)^\s*\]"
    $arrayMatch = [regex]::Match($sectionMatch.Groups[1].Value, $arrayPattern)
    if (-not $arrayMatch.Success) {
        return @()
    }

    return @(
        [regex]::Matches($arrayMatch.Groups[1].Value, '"([^"]+)"') |
            ForEach-Object { $_.Groups[1].Value }
    )
}

function Get-PortableClaudeSkillNames {
    return Get-PortableManifestArray -Section "claude" -Key "skills"
}

function Get-PortableClaudeAgentNames {
    return Get-PortableManifestArray -Section "claude" -Key "agents"
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
        [string]$CodexHome,
        [string]$AgentsHome,
        [string]$ClaudeHome
    )

    if (-not $AgentsHome) {
        $AgentsHome = Get-AgentsHome
    }

    if (-not $ClaudeHome) {
        $ClaudeHome = Get-ClaudeHome
    }

    $items = New-Object System.Collections.Generic.List[object]

    foreach ($relative in @("AGENTS.md", "hooks.json", "keybindings.json")) {
        $items.Add([pscustomobject]@{
            Type = "file"
            RepoPath = Join-Path (Join-Path $RepoRoot "codex") $relative
            LivePath = Join-Path $CodexHome $relative
            LiveRoot = $CodexHome
            BackupScope = "codex"
        })
    }

    foreach ($relative in @("agents", "hooks")) {
        $items.Add([pscustomobject]@{
            Type = "dir"
            RepoPath = Join-Path (Join-Path $RepoRoot "codex") $relative
            LivePath = Join-Path $CodexHome $relative
            LiveRoot = $CodexHome
            BackupScope = "codex"
        })
    }

    # User skills follow the current user skill home. Project `.agents/skills`
    # stay with the target repo.
    $userSkillsHome = Join-Path $AgentsHome "skills"
    foreach ($skill in Get-PortableSkillNames) {
        $items.Add([pscustomobject]@{
            Type = "dir"
            RepoPath = Join-Path (Join-Path (Join-Path $RepoRoot "codex") "skills") $skill
            LivePath = Join-Path $userSkillsHome $skill
            LiveRoot = $AgentsHome
            BackupScope = "agents"
        })
    }

    # Claude skills install to ~/.claude/skills and agents to ~/.claude/agents.
    $claudeSkillsHome = Join-Path $ClaudeHome "skills"
    foreach ($skill in Get-PortableClaudeSkillNames) {
        $items.Add([pscustomobject]@{
            Type = "dir"
            RepoPath = Join-Path (Join-Path (Join-Path $RepoRoot "claude") "skills") $skill
            LivePath = Join-Path $claudeSkillsHome $skill
            LiveRoot = $ClaudeHome
            BackupScope = "claude"
        })
    }

    $claudeAgentsHome = Join-Path $ClaudeHome "agents"
    foreach ($agent in Get-PortableClaudeAgentNames) {
        $items.Add([pscustomobject]@{
            Type = "file"
            RepoPath = Join-Path (Join-Path (Join-Path $RepoRoot "claude") "agents") "$agent.md"
            LivePath = Join-Path $claudeAgentsHome "$agent.md"
            LiveRoot = $ClaudeHome
            BackupScope = "claude"
        })
    }

    return $items
}

function Get-RetiredPortableFileMap {
    param(
        [string]$CodexHome,
        [string]$AgentsHome
    )

    $items = New-Object System.Collections.Generic.List[object]

    foreach ($skill in @(@(Get-PortableSkillNames) + @("codex-portable", "ui-ux-pro-max"))) {
        $items.Add([pscustomobject]@{
            Type = "dir"
            LivePath = Join-Path (Join-Path $CodexHome "skills") $skill
            LiveRoot = $CodexHome
            BackupScope = "codex"
        })
    }

    # Keep retired user-skill removals explicit so install does not delete
    # unrelated personal skills that Compass does not own.
    foreach ($skill in @("ui-ux-pro-max")) {
        $items.Add([pscustomobject]@{
            Type = "dir"
            LivePath = Join-Path (Join-Path $AgentsHome "skills") $skill
            LiveRoot = $AgentsHome
            BackupScope = "agents"
        })
    }

    return $items
}

function Backup-LiveItem {
    param(
        [string]$LivePath,
        [string]$BackupRoot,
        [string]$LiveRoot,
        [string]$BackupScope,
        [string]$Type
    )

    if (-not (Test-Path $LivePath)) {
        return
    }

    Assert-PathUnderRoot -Path $LivePath -Root $LiveRoot

    $relative = $LivePath.Substring($LiveRoot.Length).TrimStart("\")
    $backupBase = $BackupRoot
    if ($BackupScope) {
        $backupBase = Join-Path $BackupRoot $BackupScope
    }
    $backupPath = Join-Path $backupBase $relative

    if ($Type -eq "dir") {
        New-Item -ItemType Directory -Force (Split-Path -Parent $backupPath) | Out-Null
        Copy-Item -LiteralPath $LivePath -Destination $backupPath -Recurse -Force
        return
    }

    New-DirectoryForFile -Path $backupPath
    Copy-Item -LiteralPath $LivePath -Destination $backupPath -Force
}

function Copy-PortableItem {
    param(
        [string]$Source,
        [string]$Destination,
        [string]$Type,
        [string]$AllowedRoot
    )

    if (-not (Test-Path $Source)) {
        throw "missing portable source: $Source"
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
