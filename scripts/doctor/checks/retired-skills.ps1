$manifestPath = Join-Path $repoRoot "manifests\retired-skills.json"
if (-not (Test-Path -LiteralPath $manifestPath -PathType Leaf)) {
    $problems.Add("missing retired skill manifest")
}
else {
    try {
        $manifest = Get-Content -Raw -LiteralPath $manifestPath | ConvertFrom-Json
        if ($manifest.schema_version -ne 1) {
            $problems.Add("unsupported retired skill manifest schema")
        }

        $codexHomeSkills = @($manifest.codex_home_skills)
        $userSkillsHome = @($manifest.user_skills_home)
        $claudeSkills = @($manifest.claude_skills)
        $claudeAgents = @($manifest.claude_agents)

        if ($codexHomeSkills.Count -ne @($codexHomeSkills | Sort-Object -Unique).Count) {
            $problems.Add("retired skill manifest contains duplicate entries in codex_home_skills")
        }
        if ($userSkillsHome.Count -ne @($userSkillsHome | Sort-Object -Unique).Count) {
            $problems.Add("retired skill manifest contains duplicate entries in user_skills_home")
        }
        if ($claudeSkills.Count -ne @($claudeSkills | Sort-Object -Unique).Count) {
            $problems.Add("retired skill manifest contains duplicate entries in claude_skills")
        }
        if ($claudeAgents.Count -ne @($claudeAgents | Sort-Object -Unique).Count) {
            $problems.Add("retired skill manifest contains duplicate entries in claude_agents")
        }

        foreach ($value in $codexHomeSkills + $userSkillsHome + $claudeSkills + $claudeAgents) {
            if ($value -notmatch '^[a-z0-9][a-z0-9._-]*$') {
                $problems.Add("invalid retired skill name: $value")
            }
        }
    }
    catch {
        $problems.Add("invalid retired skill manifest: $($_.Exception.Message)")
    }
}
