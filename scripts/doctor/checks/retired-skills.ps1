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

        # The manifest owns the full roster. These narrow pins preserve the
        # historically replaced global surfaces in the bucket whose live path
        # install actually removes.
        $requiredByBucket = @{
            codex_home_skills = @("benchmark-run-operator", "input-token-economy", "using-codex-goals")
            user_skills_home = @("benchmark-infra-reviewer", "benchmark-run-operator", "input-token-economy", "using-codex-goals")
            claude_skills = @("benchmark-infra-reviewer", "benchmark-run-operator", "input-token-economy", "using-codex-goals")
            claude_agents = @("benchmark-infra-reviewer.md")
        }
        $actualByBucket = @{
            codex_home_skills = $codexHomeSkills
            user_skills_home = $userSkillsHome
            claude_skills = $claudeSkills
            claude_agents = $claudeAgents
        }
        foreach ($bucket in $requiredByBucket.Keys) {
            foreach ($required in $requiredByBucket[$bucket]) {
                if ($actualByBucket[$bucket] -notcontains $required) {
                    $problems.Add("retired skill manifest bucket $bucket is missing required entry: $required")
                }
            }
        }

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
