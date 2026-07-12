param(
    [string]$CodexHome,
    [string]$AgentsHome,
    [string]$ClaudeHome,
    [switch]$SkipCodexCommand,
    [switch]$SkipPlugins,
    [switch]$RequireInSync,
    [int]$TimeoutSeconds = 180
)

. "$PSScriptRoot\common.ps1"

$repoRoot = Get-RepoRoot
$liveHome = Get-CodexHome -CodexHome $CodexHome
$agentsHome = Get-AgentsHome -AgentsHome $AgentsHome
$claudeHome = Get-ClaudeHome -ClaudeHome $ClaudeHome
$items = Get-PortableFileMap -RepoRoot $repoRoot -CodexHome $liveHome -AgentsHome $agentsHome -ClaudeHome $claudeHome
$retiredItems = Get-RetiredPortableFileMap -CodexHome $liveHome -AgentsHome $agentsHome
$drift = New-Object System.Collections.Generic.List[string]
$missing = New-Object System.Collections.Generic.List[string]
$retired = New-Object System.Collections.Generic.List[string]
$configProblems = New-Object System.Collections.Generic.List[string]
$pluginProblems = New-Object System.Collections.Generic.List[string]
$expectedAgentDepth = $null

function Get-RelativeFileMap {
    param([string]$Root)

    $map = @{}
    if (-not (Test-Path $Root)) {
        return $map
    }

    foreach ($file in Get-ChildItem -LiteralPath $Root -Recurse -File -Force) {
        $relative = $file.FullName.Substring((Resolve-Path $Root).Path.Length).TrimStart("\")
        $map[$relative] = (Get-FileHash -Algorithm SHA256 -LiteralPath $file.FullName).Hash
    }
    return $map
}

function Get-DerivedSkillFileMap {
    param([string]$Root)

    $map = @{}
    if (-not (Test-Path $Root)) {
        return $map
    }

    $skillFile = Join-Path $Root "SKILL.md"
    if (Test-Path -LiteralPath $skillFile) {
        $map["SKILL.md"] = (Get-FileHash -Algorithm SHA256 -LiteralPath $skillFile).Hash
    }

    $references = Join-Path $Root "references"
    if (Test-Path -LiteralPath $references) {
        foreach ($file in Get-ChildItem -LiteralPath $references -Recurse -File -Force) {
            $relative = $file.FullName.Substring((Resolve-Path $Root).Path.Length).TrimStart("\")
            $map[$relative] = (Get-FileHash -Algorithm SHA256 -LiteralPath $file.FullName).Hash
        }
    }

    return $map
}

foreach ($item in $items) {
    if (-not (Test-Path $item.LivePath)) {
        $missing.Add($item.LivePath)
        continue
    }

    if (-not (Test-Path $item.RepoPath)) {
        $missing.Add($item.RepoPath)
        continue
    }

    if ($item.Type -eq "file") {
        $repoHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $item.RepoPath).Hash
        $liveHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $item.LivePath).Hash
        if ($repoHash -ne $liveHash) {
            $drift.Add($item.LivePath)
        }
        continue
    }

    if ($item.Type -eq "derived-agent") {
        $tempFile = Join-Path ([System.IO.Path]::GetTempPath()) ("compass-derived-agent-" + [guid]::NewGuid().ToString("N") + ".md")
        Copy-PortableItem -Source $item.RepoPath -Destination $tempFile -Type $item.Type -AllowedRoot (Split-Path -Parent $tempFile)
        $repoHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $tempFile).Hash
        $liveHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $item.LivePath).Hash
        Remove-Item -LiteralPath $tempFile -Force
        if ($repoHash -ne $liveHash) {
            $drift.Add($item.LivePath)
        }
        continue
    }

    if ($item.Type -eq "derived-skill") {
        $repoMap = Get-DerivedSkillFileMap -Root $item.RepoPath
    }
    else {
        $repoMap = Get-RelativeFileMap -Root $item.RepoPath
    }
    $liveMap = Get-RelativeFileMap -Root $item.LivePath
    $allKeys = @(@($repoMap.Keys) + @($liveMap.Keys) | Sort-Object -Unique)
    foreach ($key in $allKeys) {
        if (-not $repoMap.ContainsKey($key) -or -not $liveMap.ContainsKey($key) -or $repoMap[$key] -ne $liveMap[$key]) {
            $drift.Add((Join-Path $item.LivePath $key))
        }
    }
}

foreach ($item in $retiredItems) {
    if (Test-Path $item.LivePath) {
        $retired.Add($item.LivePath)
    }
}

$reviewConfigPath = Join-Path $repoRoot "codex\config.review.toml"
if (-not (Test-Path -LiteralPath $reviewConfigPath)) {
    $configProblems.Add("missing reviewed config fragment needed to verify specialist-review agent depth: $reviewConfigPath")
}
else {
    $reviewConfigText = Get-Content -Raw -LiteralPath $reviewConfigPath
    if ($null -eq $reviewConfigText) {
        $reviewConfigText = ""
    }
    $reviewAgentsSection = [regex]::Match($reviewConfigText, "(?ms)^\[agents\]\s*(.*?)(?=^\[|\z)")
    if (-not $reviewAgentsSection.Success) {
        $configProblems.Add("reviewed config fragment is missing [agents] max_depth for specialist-review")
    }
    else {
        $reviewMaxDepth = [regex]::Match($reviewAgentsSection.Groups[1].Value, "(?m)^\s*max_depth\s*=\s*(\d+)\s*(?:#.*)?$")
        if (-not $reviewMaxDepth.Success) {
            $configProblems.Add("reviewed config fragment is missing [agents] max_depth for specialist-review")
        }
        else {
            $expectedAgentDepth = [int]$reviewMaxDepth.Groups[1].Value
        }
    }
}

$liveConfigPath = Join-Path $liveHome "config.toml"
if ($null -ne $expectedAgentDepth) {
    if (-not (Test-Path -LiteralPath $liveConfigPath)) {
        $configProblems.Add("missing live config.toml needed to verify specialist-review agent depth: $liveConfigPath")
    }
    else {
        $liveConfigText = Get-Content -Raw -LiteralPath $liveConfigPath
        if ($null -eq $liveConfigText) {
            $liveConfigText = ""
        }
        $agentsSection = [regex]::Match($liveConfigText, "(?ms)^\[agents\]\s*(.*?)(?=^\[|\z)")
        if (-not $agentsSection.Success) {
            $configProblems.Add("live config.toml is missing [agents] max_depth = $expectedAgentDepth for specialist-review")
        }
        else {
            $maxDepth = [regex]::Match($agentsSection.Groups[1].Value, "(?m)^\s*max_depth\s*=\s*(\d+)\s*(?:#.*)?$")
            if (-not $maxDepth.Success) {
                $configProblems.Add("live config.toml is missing [agents] max_depth = $expectedAgentDepth for specialist-review")
            }
            elseif ([int]$maxDepth.Groups[1].Value -ne $expectedAgentDepth) {
                $configProblems.Add("live config.toml has [agents] max_depth = $($maxDepth.Groups[1].Value), expected exactly $expectedAgentDepth for specialist-review")
            }
        }
    }
}

$pluginManifestPath = Join-Path $repoRoot "manifests\plugins.json"
if (-not $SkipPlugins) {
    if (-not (Test-Path -LiteralPath $pluginManifestPath -PathType Leaf)) {
        $pluginProblems.Add("missing plugin manifest: $pluginManifestPath")
    }
    elseif (-not (Get-Command codex -ErrorAction SilentlyContinue)) {
        $pluginProblems.Add("codex command not found; use -SkipPlugins only when plugin verification is intentionally out of scope")
    }
    else {
        $previousCodexHome = $env:CODEX_HOME
        $env:CODEX_HOME = $liveHome
        try {
            $pluginManifest = Get-Content -Raw -LiteralPath $pluginManifestPath | ConvertFrom-Json
            $marketplaceOutput = & codex plugin marketplace list --json
            if ($LASTEXITCODE -ne 0) {
                $pluginProblems.Add("codex plugin marketplace list failed")
            }
            else {
                $marketplaceState = $marketplaceOutput | Out-String | ConvertFrom-Json
                foreach ($marketplace in @($pluginManifest.marketplaces)) {
                    $configured = @($marketplaceState.marketplaces | Where-Object { $_.name -eq $marketplace.name })
                    if ($configured.Count -eq 0) {
                        $pluginProblems.Add("declared marketplace is not configured: $($marketplace.name)")
                    }
                    elseif ((Get-NormalizedMarketplaceSource -Source $configured[0].marketplaceSource.source) -ne (Get-NormalizedMarketplaceSource -Source $marketplace.source)) {
                        $pluginProblems.Add("declared marketplace source mismatch for $($marketplace.name): $($configured[0].marketplaceSource.source)")
                    }
                }
            }

            $pluginOutput = & codex plugin list --json
            if ($LASTEXITCODE -ne 0) {
                $pluginProblems.Add("codex plugin list failed")
            }
            else {
                $pluginState = $pluginOutput | Out-String | ConvertFrom-Json
                $installedIds = @($pluginState.installed | ForEach-Object { $_.pluginId })
                foreach ($pluginId in @($pluginManifest.plugins)) {
                    if ($installedIds -notcontains $pluginId) {
                        $pluginProblems.Add("declared plugin is not installed: $pluginId")
                    }
                }
            }
        }
        finally {
            $env:CODEX_HOME = $previousCodexHome
        }
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
    foreach ($path in $drift) {
        Write-Host "  $path"
    }
}
if ($retired.Count -gt 0) {
    Write-Host ""
    Write-Host "retired portable copies:"
    foreach ($path in $retired) {
        Write-Host "  $path"
    }
}
if ($configProblems.Count -gt 0) {
    Write-Host ""
    Write-Host "config problems:"
    foreach ($problem in $configProblems) {
        Write-Host "  $problem"
    }
}
if ($pluginProblems.Count -gt 0) {
    Write-Host ""
    Write-Host "plugin problems:"
    foreach ($problem in $pluginProblems) {
        Write-Host "  $problem"
    }
}
if ($missing.Count -eq 0 -and $drift.Count -eq 0 -and $retired.Count -eq 0 -and $configProblems.Count -eq 0 -and $pluginProblems.Count -eq 0) {
    Write-Host "portable files match live allowlist"
}

if ($RequireInSync -and ($missing.Count -gt 0 -or $drift.Count -gt 0 -or $retired.Count -gt 0 -or $configProblems.Count -gt 0 -or $pluginProblems.Count -gt 0)) {
    exit 1
}

if ($SkipCodexCommand) {
    Write-Host ""
    Write-Host "codex instruction check skipped"
    exit 0
}

if (-not (Get-Command codex -ErrorAction SilentlyContinue)) {
    Write-Host ""
    Write-Host "codex command not found; file drift check completed"
    exit 0
}

$outputFile = [System.IO.Path]::GetTempFileName()
$logFile = [System.IO.Path]::GetTempFileName()
$prompt = @"
Report the active instruction sources you can infer for this run.
Include whether global AGENTS.md and repository AGENTS.md were loaded.
Do not modify files or run shell commands.
"@

Write-Host ""
Write-Host "running read-only Codex instruction check"

$job = Start-Job -ScriptBlock {
    param($RepoRoot, $OutputFile, $Prompt, $LogFile)
    codex -c approval_policy='"never"' -c model_reasoning_effort='"low"' --sandbox read-only exec --cd $RepoRoot --ephemeral --output-last-message $OutputFile $Prompt *> $LogFile
    [pscustomobject]@{
        ExitCode = $LASTEXITCODE
    }
} -ArgumentList $repoRoot, $outputFile, $prompt, $logFile

$completed = Wait-Job $job -Timeout $TimeoutSeconds
if (-not $completed) {
    Stop-Job $job | Out-Null
    if (Test-Path $logFile) {
        Get-Content -Raw -LiteralPath $logFile | Write-Host
    }
    Receive-Job $job -ErrorAction SilentlyContinue | Out-String | Write-Host
    Remove-Job $job | Out-Null
    throw "codex instruction check timed out"
}

$jobResult = Receive-Job $job -ErrorAction SilentlyContinue -ErrorVariable jobErrors
Remove-Job $job | Out-Null

if ($jobResult.ExitCode -ne 0 -or $jobErrors) {
    if (Test-Path $logFile) {
        Get-Content -Raw -LiteralPath $logFile | Write-Host
    }
    foreach ($errorRecord in $jobErrors) {
        Write-Host $errorRecord.ToString()
    }
    throw "codex instruction check failed"
}

Write-Host ""
Write-Host "codex final message:"
if (-not (Test-Path $outputFile)) {
    throw "codex did not write an output message"
}
Get-Content -Raw -LiteralPath $outputFile
Remove-Item -LiteralPath $outputFile -Force
Remove-Item -LiteralPath $logFile -Force
