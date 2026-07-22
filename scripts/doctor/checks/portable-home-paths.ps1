# Home paths are executable truth in scripts/common.ps1 (Get-CodexHome,
# Get-AgentsHome, Get-ClaudeHome). The portable manifest and portable-config
# workflow document the same paths for maintainers. This check extracts the
# default directory names from common.ps1 and requires every documented copy to
# match the complete expected expressions exactly.
$commonPath = Join-Path $repoRoot "scripts\common.ps1"
$manifestPath = Join-Path $repoRoot "manifests\portable-files.toml"
$workflowPath = Join-Path $repoRoot "workflows\portable-config.md"
if (
    -not (Test-Path -LiteralPath $commonPath -PathType Leaf) -or
    -not (Test-Path -LiteralPath $manifestPath -PathType Leaf) -or
    -not (Test-Path -LiteralPath $workflowPath -PathType Leaf)
) {
    $problems.Add("missing common.ps1, portable-files.toml, or portable-config.md for home path check")
}
else {
    $common = Get-Content -Raw -LiteralPath $commonPath

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

        function Get-PortableManifestString {
            param($Section, $Key)
            $sectionValue = Get-PortableJsonProperty -Object $manifest -Name $Section
            return Get-PortableJsonProperty -Object $sectionValue -Name $Key
        }

        function Assert-Equals {
            param($Section, $Key, $Expected)
            $value = Get-PortableManifestString $Section $Key
            if ($null -eq $value) {
                $problems.Add("portable manifest [$Section].$Key is missing")
            }
            elseif ($value -cne $Expected) {
                $problems.Add("portable manifest [$Section].$Key documents '$value' but expected '$Expected'")
            }
        }

        $codexHome = '$CODEX_HOME or %USERPROFILE%\' + $defaults.codex
        $agentsHome = '$HOME\' + $defaults.agents
        $claudeHome = '$HOME\' + $defaults.claude

        Assert-Equals "codex" "home" $codexHome
        Assert-Equals "agents" "home" $agentsHome
        Assert-Equals "agents" "skills_dir" ($agentsHome + "\skills")
        Assert-Equals "claude" "home" $claudeHome
        Assert-Equals "claude" "skills_dir" ($claudeHome + "\skills")
        Assert-Equals "claude" "agents_dir" ($claudeHome + "\agents")

        $workflowLines = @(Get-Content -LiteralPath $workflowPath)
        $expectedWorkflowLines = @(
            '- `-CodexHome`, then `$env:CODEX_HOME`, then `%USERPROFILE%\' + $defaults.codex + '`;'
            '- `-AgentsHome`, then `$HOME\' + $defaults.agents + '`;'
            '- `-ClaudeHome`, then `$HOME\' + $defaults.claude + '`.`'
        )
        foreach ($expectedLine in $expectedWorkflowLines) {
            if ($workflowLines -cnotcontains $expectedLine) {
                $problems.Add("portable-config.md home path line missing or stale: $expectedLine")
            }
        }
    }
}
