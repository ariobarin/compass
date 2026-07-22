# Home paths are executable truth in scripts/common.ps1 (Get-CodexHome,
# Get-AgentsHome, Get-ClaudeHome). The manifest, launchers, operator docs, and
# focused workflow docs repeat those defaults for different audiences. This
# check derives every expected copy from common.ps1 so a default change cannot
# leave an accepted runtime route or current instruction stale.
$paths = @{
    common = Join-Path $repoRoot "scripts\common.ps1"
    manifest = Join-Path $repoRoot "manifests\portable-files.toml"
    portableWorkflow = Join-Path $repoRoot "workflows\portable-config.md"
    claudeWorkflow = Join-Path $repoRoot "workflows\claude-config.md"
    whichLlmWorkflow = Join-Path $repoRoot "workflows\which-llm-skill.md"
    readme = Join-Path $repoRoot "README.md"
    contributing = Join-Path $repoRoot "CONTRIBUTING.md"
    doctor = Join-Path $repoRoot "scripts\doctor.ps1"
    hookPowerShell = Join-Path $repoRoot "codex\hooks\portable_guard.ps1"
    hookShell = Join-Path $repoRoot "codex\hooks\portable_guard.sh"
    hooksJson = Join-Path $repoRoot "codex\hooks.json"
    hooksReadme = Join-Path $repoRoot "codex\hooks\README.md"
}

$missing = @($paths.GetEnumerator() | Where-Object { -not (Test-Path -LiteralPath $_.Value -PathType Leaf) })
if ($missing.Count -gt 0) {
    foreach ($entry in $missing) {
        $problems.Add("missing $($entry.Value) for home path check")
    }
}
else {
    function Get-PortableManifestString {
        param($Manifest, $Section, $Key)
        $sectionValue = Get-PortableJsonProperty -Object $Manifest -Name $Section
        return Get-PortableJsonProperty -Object $sectionValue -Name $Key
    }

    function Assert-Equals {
        param($Actual, $Expected, [string]$Label)
        if ($null -eq $Actual) {
            $problems.Add("$Label is missing")
        }
        elseif ($Actual -cne $Expected) {
            $problems.Add("$Label documents '$Actual' but expected '$Expected'")
        }
    }

    function Normalize-PortableWhitespace {
        param([string]$Text)
        return [regex]::Replace($Text, '\s+', ' ').Trim()
    }

    function Assert-Contains {
        param([string]$Text, [string]$Expected, [string]$Label)
        if ($Text.IndexOf($Expected, [System.StringComparison]::Ordinal) -lt 0) {
            $problems.Add("$Label is missing or stale: $Expected")
        }
    }

    function Assert-NormalizedContains {
        param([string]$Text, [string]$Expected, [string]$Label)
        $normalizedText = Normalize-PortableWhitespace $Text
        $normalizedExpected = Normalize-PortableWhitespace $Expected
        if ($normalizedText.IndexOf($normalizedExpected, [System.StringComparison]::Ordinal) -lt 0) {
            $problems.Add("$Label is missing or stale: $normalizedExpected")
        }
    }

    function Assert-MatchCount {
        param([string]$Text, [string]$Expected, [int]$Count, [string]$Label)
        $actual = [regex]::Matches($Text, [regex]::Escape($Expected)).Count
        if ($actual -ne $Count) {
            $problems.Add("$Label expected $Count copies of '$Expected' but found $actual")
        }
    }

    $common = Get-Content -Raw -LiteralPath $paths.common
    $codexMatch = [regex]::Match($common, 'Join-Path \$env:USERPROFILE "([^"]+)"')
    $homeMatches = [regex]::Matches($common, 'Join-Path \$HOME "([^"]+)"')
    if (-not $codexMatch.Success -or $homeMatches.Count -lt 2) {
        $problems.Add("could not extract home directory defaults from common.ps1")
    }
    else {
        $defaults = @{
            codex = $codexMatch.Groups[1].Value
            agents = $homeMatches[0].Groups[1].Value
            claude = $homeMatches[1].Groups[1].Value
        }
        $manifest = (Get-PortableGeneratedData).manifest

        $codexHome = '$CODEX_HOME or %USERPROFILE%\' + $defaults.codex
        $agentsHome = '$HOME\' + $defaults.agents
        $claudeHome = '$HOME\' + $defaults.claude
        $codexTilde = '~/' + $defaults.codex
        $claudeTilde = '~/' + $defaults.claude
        $agentsSlash = '$HOME/' + $defaults.agents
        $claudeSlash = '$HOME/' + $defaults.claude

        Assert-Equals (Get-PortableManifestString $manifest "codex" "home") $codexHome "portable manifest [codex].home"
        Assert-Equals (Get-PortableManifestString $manifest "agents" "home") $agentsHome "portable manifest [agents].home"
        Assert-Equals (Get-PortableManifestString $manifest "agents" "skills_dir") ($agentsHome + "\skills") "portable manifest [agents].skills_dir"
        Assert-Equals (Get-PortableManifestString $manifest "claude" "home") $claudeHome "portable manifest [claude].home"
        Assert-Equals (Get-PortableManifestString $manifest "claude" "skills_dir") ($claudeHome + "\skills") "portable manifest [claude].skills_dir"
        Assert-Equals (Get-PortableManifestString $manifest "claude" "agents_dir") ($claudeHome + "\agents") "portable manifest [claude].agents_dir"

        $portableWorkflow = Get-Content -Raw -LiteralPath $paths.portableWorkflow
        Assert-Contains $portableWorkflow ('- `-CodexHome`, then `$env:CODEX_HOME`, then `%USERPROFILE%\' + $defaults.codex + '`;') "portable-config Codex resolution"
        Assert-Contains $portableWorkflow ('- `-AgentsHome`, then `$HOME\' + $defaults.agents + '`;') "portable-config agents resolution"
        Assert-Contains $portableWorkflow ('- `-ClaudeHome`, then `$HOME\' + $defaults.claude + '`.') "portable-config Claude resolution"

        $readme = Get-Content -Raw -LiteralPath $paths.readme
        $readmeResolution = 'Scripts use `-CodexHome`, then `$env:CODEX_HOME`, then `%USERPROFILE%\' + $defaults.codex + '`; `-AgentsHome`, then `$HOME\' + $defaults.agents + '`; and `-ClaudeHome`, then `$HOME\' + $defaults.claude + '`.'
        Assert-NormalizedContains $readme $readmeResolution "README home resolution"
        Assert-Contains $readme ($codexTilde + "/AGENTS.md") "README Codex install root"
        Assert-Contains $readme ($claudeTilde + "/CLAUDE.md") "README Claude install root"
        Assert-Contains $readme ($agentsSlash + "/skills") "README agents skill root"
        Assert-Contains $readme ($claudeSlash + "/skills") "README Claude skill root"

        $contributing = Get-Content -Raw -LiteralPath $paths.contributing
        Assert-Contains $contributing ($agentsSlash + "/skills") "CONTRIBUTING agents skill root"

        $claudeWorkflow = Get-Content -Raw -LiteralPath $paths.claudeWorkflow
        Assert-Contains $claudeWorkflow ($claudeSlash + "/CLAUDE.md") "Claude workflow instruction root"
        Assert-Contains $claudeWorkflow $claudeSlash "Claude workflow default root"

        $whichLlmWorkflow = Get-Content -Raw -LiteralPath $paths.whichLlmWorkflow
        Assert-Contains $whichLlmWorkflow ($agentsHome + "\skills\which-llm\pick.py") "which-llm installed pick path"
        Assert-Contains $whichLlmWorkflow ($agentsHome + "\skills\which-llm\query.py") "which-llm installed query path"

        $doctor = Get-Content -Raw -LiteralPath $paths.doctor
        Assert-Contains $doctor ('$liveHome = Join-Path $env:USERPROFILE "' + $defaults.codex + '"') "doctor Codex fallback"
        Assert-Contains $doctor ('$agentsHomePath = Join-Path $HOME "' + $defaults.agents + '"') "doctor agents fallback"
        Assert-Contains $doctor ('$claudeHomePath = Join-Path $HOME "' + $defaults.claude + '"') "doctor Claude fallback"

        $hookPowerShell = Get-Content -Raw -LiteralPath $paths.hookPowerShell
        Assert-Contains $hookPowerShell ('$codexHome = Join-Path $env:USERPROFILE "' + $defaults.codex + '"') "PowerShell hook Codex fallback"

        $hookShell = Get-Content -Raw -LiteralPath $paths.hookShell
        Assert-Contains $hookShell ('codex_home=$HOME/' + $defaults.codex) "shell hook Codex fallback"

        $hooksJson = Get-Content -Raw -LiteralPath $paths.hooksJson
        $hookShellDefault = '${CODEX_HOME:-$HOME/' + $defaults.codex + '}/hooks/portable_guard.sh'
        $hookWindowsDefault = "Join-Path `$env:USERPROFILE '$($defaults.codex)'"
        Assert-MatchCount $hooksJson $hookShellDefault 2 "hook JSON shell Codex fallback"
        Assert-MatchCount $hooksJson $hookWindowsDefault 2 "hook JSON Windows Codex fallback"

        $hooksReadme = Get-Content -Raw -LiteralPath $paths.hooksReadme
        Assert-Contains $hooksReadme $codexTilde "hooks README Codex default"
    }
}
