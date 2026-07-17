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

function Get-NormalizedMarketplaceSource {
    param([string]$Source)

    $normalized = $Source.Trim().TrimEnd("/")
    if ($normalized -match "^[^/]+/[^/]+$") {
        $normalized = "https://github.com/$normalized"
    }
    return ($normalized -replace "\.git$", "").ToLowerInvariant()
}

$script:PortablePythonRunner = $null
$script:PortableGeneratedData = $null
$script:PortableResolvedClaudeHome = $null

function Get-PortablePythonRunner {
    if ($script:PortablePythonRunner) {
        return $script:PortablePythonRunner
    }

    $candidates = @(
        [pscustomobject]@{ Command = "py"; Prefix = @("-3") }
        [pscustomobject]@{ Command = "python"; Prefix = @() }
        [pscustomobject]@{ Command = "python3"; Prefix = @() }
    )

    foreach ($candidate in $candidates) {
        if (-not (Get-Command $candidate.Command -ErrorAction SilentlyContinue)) {
            continue
        }

        & $candidate.Command @($candidate.Prefix) -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)" *> $null
        if ($LASTEXITCODE -eq 0) {
            $script:PortablePythonRunner = $candidate
            return $candidate
        }
    }

    throw "Python 3.11 or newer is required to parse portable TOML"
}

function Invoke-PortableTomlParser {
    param(
        [string[]]$Arguments,
        [AllowNull()]
        [string]$InputText
    )

    $parserPath = Join-Path (Get-RepoRoot) "scripts\portable-data.py"
    if (-not (Test-Path -LiteralPath $parserPath)) {
        throw "missing portable TOML parser: $parserPath"
    }

    $runner = Get-PortablePythonRunner
    $commandArguments = @($runner.Prefix) + @($parserPath) + @($Arguments)
    $previousPythonIoEncoding = $env:PYTHONIOENCODING
    $previousOutputEncoding = [Console]::OutputEncoding

    try {
        $env:PYTHONIOENCODING = "utf-8"
        [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
        if ($PSBoundParameters.ContainsKey("InputText")) {
            $output = @($InputText | & $runner.Command @commandArguments 2>&1)
        }
        else {
            $output = @(& $runner.Command @commandArguments 2>&1)
        }
        $exitCode = $LASTEXITCODE
    }
    finally {
        $env:PYTHONIOENCODING = $previousPythonIoEncoding
        [Console]::OutputEncoding = $previousOutputEncoding
    }

    if ($exitCode -ne 0) {
        $message = @($output | ForEach-Object { $_.ToString() }) -join "`n"
        throw "portable TOML parser failed: $message"
    }

    return [string](@($output | ForEach-Object { $_.ToString() }) -join "`n")
}

function Get-PortableGeneratedData {
    if ($script:PortableGeneratedData) {
        return $script:PortableGeneratedData
    }

    $json = Invoke-PortableTomlParser -Arguments @("--root", (Get-RepoRoot))
    try {
        $script:PortableGeneratedData = $json | ConvertFrom-Json
    }
    catch {
        throw "portable TOML parser returned invalid JSON: $($_.Exception.Message)"
    }

    if ($script:PortableGeneratedData.schema_version -ne 1) {
        throw "unsupported portable data schema version"
    }
    return $script:PortableGeneratedData
}

function Get-PortableJsonProperty {
    param(
        [object]$Object,
        [string]$Name
    )

    if ($null -eq $Object) {
        return $null
    }
    $property = $Object.PSObject.Properties[$Name]
    if ($null -eq $property) {
        return $null
    }
    return $property.Value
}

function Get-PortableSkillNames {
    return Get-PortableManifestArray -Section "agents" -Key "skills"
}

function Get-PortableManifestArray {
    param(
        [string]$Section,
        [string]$Key,
        [string]$Text
    )

    if ($PSBoundParameters.ContainsKey("Text")) {
        $json = Invoke-PortableTomlParser -Arguments @("--stdin") -InputText $Text
        $manifest = $json | ConvertFrom-Json
    }
    else {
        $manifest = (Get-PortableGeneratedData).manifest
    }

    $sectionValue = Get-PortableJsonProperty -Object $manifest -Name $Section
    $keyValue = Get-PortableJsonProperty -Object $sectionValue -Name $Key
    if ($null -eq $keyValue) {
        return @()
    }
    return @($keyValue)
}

function Get-PortableClaudeFileNames {
    return Get-PortableManifestArray -Section "claude" -Key "files"
}

function Get-PortableClaudeSkillNames {
    return Get-PortableManifestArray -Section "claude" -Key "skills"
}

function Get-PortableClaudeDerivedSkillNames {
    return Get-PortableManifestArray -Section "claude" -Key "derived_skills"
}

function Get-PortableClaudeAgentNames {
    return Get-PortableManifestArray -Section "claude" -Key "agents"
}

function Get-PortableClaudeDerivedAgentNames {
    return Get-PortableManifestArray -Section "claude" -Key "derived_agents"
}

# Claude agent frontmatter is install wiring, not runtime guidance, so it lives
# here next to the derive transform instead of in the manifest. Each derived
# agent gets these tools and color; model is always inherit. The reviewer
# coordinator has no tools entry, so its derived file omits the tools line.
$script:ClaudeDerivedAgentFrontmatter = @{
    "algorithm-critic" = @{ Tools = "Read, Grep, Glob, Bash"; Color = "red" }
    "neutral-critic"   = @{ Tools = "Read, Grep, Glob, Bash"; Color = "red" }
    "progress-monitor" = @{ Tools = "Read, Grep, Glob, Bash"; Color = "yellow" }
    "repo-explorer"    = @{ Tools = "Read, Grep, Glob, Bash"; Color = "blue" }
    "research-critic"  = @{ Tools = "Read, Grep, Glob, Bash, WebSearch, WebFetch"; Color = "red" }
    "reuse-critic"     = @{ Tools = "Read, Grep, Glob, Bash"; Color = "red" }
    "reviewer"         = @{ Color = "purple" }
    "verifier"         = @{ Tools = "Read, Grep, Glob, Bash"; Color = "green" }
}

function Get-TopLevelTomlStringValues {
    param([string]$Text)

    $json = Invoke-PortableTomlParser -Arguments @("--stdin") -InputText $Text
    $parsed = $json | ConvertFrom-Json
    $values = @{}
    foreach ($property in $parsed.PSObject.Properties) {
        if ($property.Value -is [string]) {
            $values[$property.Name] = $property.Value
        }
    }
    return $values
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
    $script:PortableResolvedClaudeHome = $ClaudeHome

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

    # Claude owns a separately authored global instruction file. Shared skills
    # and most agents still derive from the reviewed Codex source.
    foreach ($relative in Get-PortableClaudeFileNames) {
        $items.Add([pscustomobject]@{
            Type = "file"
            RepoPath = Join-Path (Join-Path $RepoRoot "claude") $relative
            LivePath = Join-Path $ClaudeHome $relative
            LiveRoot = $ClaudeHome
            BackupScope = "claude"
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

    foreach ($skill in Get-PortableClaudeDerivedSkillNames) {
        $items.Add([pscustomobject]@{
            Type = "derived-skill"
            RepoPath = Join-Path (Join-Path (Join-Path $RepoRoot "codex") "skills") $skill
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

    foreach ($agent in Get-PortableClaudeDerivedAgentNames) {
        $items.Add([pscustomobject]@{
            Type = "derived-agent"
            RepoPath = Join-Path (Join-Path (Join-Path $RepoRoot "codex") "agents") "$agent.toml"
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

    foreach ($skill in @(@(Get-PortableSkillNames) + @("benchmark-run-operator", "codex-portable", "input-token-economy", "pr-merge-closeout", "proper-flowcharts", "ui-ux-pro-max", "using-codex-goals"))) {
        $items.Add([pscustomobject]@{
            Type = "dir"
            LivePath = Join-Path (Join-Path $CodexHome "skills") $skill
            LiveRoot = $CodexHome
            BackupScope = "codex"
        })
    }

    # Keep retired user-skill removals explicit so install does not delete
    # unrelated personal skills that Compass does not own.
    foreach ($skill in @("benchmark-infra-reviewer", "benchmark-run-operator", "input-token-economy", "pr-merge-closeout", "ui-ux-pro-max", "using-codex-goals", "webmcp-eval-triage", "webmcp-tool-authoring", "webmcp-verify-tool")) {
        $items.Add([pscustomobject]@{
            Type = "dir"
            LivePath = Join-Path (Join-Path $AgentsHome "skills") $skill
            LiveRoot = $AgentsHome
            BackupScope = "agents"
        })
    }

    # Get-PortableFileMap runs first in install and verification, so this retains
    # an explicitly supplied Claude home without coupling callers to another map argument.
    $claudeHome = $script:PortableResolvedClaudeHome
    if (-not $claudeHome) {
        $claudeHome = Get-ClaudeHome
    }
    foreach ($skill in @("benchmark-infra-reviewer", "benchmark-run-operator", "input-token-economy", "using-codex-goals")) {
        $items.Add([pscustomobject]@{
            Type = "dir"
            LivePath = Join-Path (Join-Path $claudeHome "skills") $skill
            LiveRoot = $claudeHome
            BackupScope = "claude"
        })
    }

    $items.Add([pscustomobject]@{
        Type = "file"
        LivePath = Join-Path (Join-Path $claudeHome "agents") "benchmark-infra-reviewer.md"
        LiveRoot = $claudeHome
        BackupScope = "claude"
    })

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

    if ($Type -in @("dir", "derived-skill")) {
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

    if ($Type -eq "derived-skill") {
        if (Test-Path $Destination) {
            Remove-Item -LiteralPath $Destination -Recurse -Force
        }

        New-Item -ItemType Directory -Force $Destination | Out-Null
        Copy-Item -LiteralPath (Join-Path $Source "SKILL.md") -Destination (Join-Path $Destination "SKILL.md") -Force

        foreach ($resourceDirectory in @("references", "scripts", "assets")) {
            $resourceSource = Join-Path $Source $resourceDirectory
            if (Test-Path -LiteralPath $resourceSource) {
                Copy-Item -LiteralPath $resourceSource -Destination (Join-Path $Destination $resourceDirectory) -Recurse -Force
            }
        }

        return
    }

    if ($Type -eq "derived-agent") {
        $values = Get-TopLevelTomlStringValues -Text (Get-Content -Raw -LiteralPath $Source)
        $name = $values["name"]
        $body = $values["developer_instructions"]
        $body = $body -replace "`r`n", "`n"
        $body = $body -replace "^\n", ""
        $body = $body -replace "\n+$", "`n"

        $fm = $script:ClaudeDerivedAgentFrontmatter[$name]
        $lines = @(
            "---"
            "name: $name"
            "description: $($values["description"])"
        )
        if ($fm -and $fm["Tools"]) { $lines += "tools: $($fm["Tools"])" }
        $lines += "model: inherit"
        if ($fm -and $fm["Color"]) { $lines += "color: $($fm["Color"])" }
        $lines += "---"

        $content = ($lines -join "`n") + "`n`n" + $body

        New-DirectoryForFile -Path $Destination
        [System.IO.File]::WriteAllText($Destination, $content)
        return
    }

    New-DirectoryForFile -Path $Destination
    Copy-Item -LiteralPath $Source -Destination $Destination -Force
}
