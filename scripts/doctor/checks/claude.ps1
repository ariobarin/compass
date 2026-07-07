$maxDescriptionLength = 160
$claudeRoot = Join-Path $repoRoot "claude"

# Claude skill frontmatter.
$claudeSkillFiles = Get-ChildItem -Path (Join-Path $claudeRoot "skills") -Recurse -File -Filter "SKILL.md" -ErrorAction SilentlyContinue
foreach ($skillFile in $claudeSkillFiles) {
    $name = Select-String -Path $skillFile.FullName -Pattern "^name:\s*(.+)$" | Select-Object -First 1
    if (-not $name) {
        $problems.Add("missing claude skill name: $($skillFile.FullName)")
        continue
    }

    $description = Select-String -Path $skillFile.FullName -Pattern "^description:\s*(.+)$" | Select-Object -First 1
    if (-not $description) {
        $problems.Add("missing claude skill description: $($skillFile.FullName)")
        continue
    }

    $descriptionText = $description.Matches[0].Groups[1].Value.Trim()
    if ($descriptionText.Length -gt $maxDescriptionLength) {
        $problems.Add("claude skill description over $maxDescriptionLength chars: $($skillFile.FullName)")
    }
}

# Claude agent frontmatter.
$claudeAgentFiles = Get-ChildItem -Path (Join-Path $claudeRoot "agents") -File -Filter "*.md" -ErrorAction SilentlyContinue
foreach ($agentFile in $claudeAgentFiles) {
    $agentText = Get-Content -Raw -LiteralPath $agentFile.FullName
    if ($agentText -notmatch "(?ms)^---\s*\r?\n.*?\r?\n---") {
        $problems.Add("claude agent missing frontmatter: $($agentFile.FullName)")
        continue
    }

    if ($agentText -notmatch "(?m)^name:\s*.+") {
        $problems.Add("claude agent missing name: $($agentFile.FullName)")
    }

    if ($agentText -notmatch "(?m)^description:\s*.+") {
        $problems.Add("claude agent missing description: $($agentFile.FullName)")
    }
}

# Manifest [claude] skills and agents must match the install map on disk.
$manifestPath = Join-Path $repoRoot "manifests\portable-files.toml"
$manifestText = Get-Content -Raw -LiteralPath $manifestPath
$claudeSectionMatch = [regex]::Match($manifestText, "(?ms)^\[claude\]\s*(.*?)(?=^\[|\z)")
if (-not $claudeSectionMatch.Success) {
    $problems.Add("missing claude section in portable manifest")
}
else {
    $section = $claudeSectionMatch.Groups[1].Value
    $claudeSkillsMatch = [regex]::Match($section, "(?ms)^\s*skills\s*=\s*\[(.*?)^\s*\]")
    $claudeAgentsMatch = [regex]::Match($section, "(?ms)^\s*agents\s*=\s*\[(.*?)^\s*\]")

    if (-not $claudeSkillsMatch.Success) {
        $problems.Add("missing claude skills list in portable manifest")
    }

    if (-not $claudeAgentsMatch.Success) {
        $problems.Add("missing claude agents list in portable manifest")
    }

    if ($claudeSkillsMatch.Success) {
        $manifestClaudeSkills = @(
            [regex]::Matches($claudeSkillsMatch.Groups[1].Value, '"([^"]+)"') |
                ForEach-Object { $_.Groups[1].Value } |
                Sort-Object -Unique
        )

        $diskClaudeSkills = @(
            Get-ChildItem -Path (Join-Path $claudeRoot "skills") -Directory -ErrorAction SilentlyContinue |
                ForEach-Object { $_.Name } |
                Sort-Object -Unique
        )

        foreach ($skill in $manifestClaudeSkills) {
            if ($diskClaudeSkills -notcontains $skill) {
                $problems.Add("claude skill in manifest missing from disk: $skill")
            }
        }

        foreach ($skill in $diskClaudeSkills) {
            if ($manifestClaudeSkills -notcontains $skill) {
                $problems.Add("claude skill on disk missing from manifest: $skill")
            }
        }
    }

    if ($claudeAgentsMatch.Success) {
        $manifestClaudeAgents = @(
            [regex]::Matches($claudeAgentsMatch.Groups[1].Value, '"([^"]+)"') |
                ForEach-Object { $_.Groups[1].Value } |
                Sort-Object -Unique
        )

        $diskClaudeAgents = @(
            Get-ChildItem -Path (Join-Path $claudeRoot "agents") -File -Filter "*.md" -ErrorAction SilentlyContinue |
                ForEach-Object { [System.IO.Path]::GetFileNameWithoutExtension($_.Name) } |
                Sort-Object -Unique
        )

        foreach ($agent in $manifestClaudeAgents) {
            if ($diskClaudeAgents -notcontains $agent) {
                $problems.Add("claude agent in manifest missing from disk: $agent")
            }
        }

        foreach ($agent in $diskClaudeAgents) {
            if ($manifestClaudeAgents -notcontains $agent) {
                $problems.Add("claude agent on disk missing from manifest: $agent")
            }
        }
    }
}
