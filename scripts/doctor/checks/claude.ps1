$maxDescriptionLength = 160
$claudeRoot = Join-Path $repoRoot "claude"

# Separately authored Claude global files.
$manifestPath = Join-Path $repoRoot "manifests\portable-files.toml"
$manifestText = Get-Content -Raw -LiteralPath $manifestPath
$manifestClaudeFiles = @(Get-PortableManifestArray -Text $manifestText -Section "claude" -Key "files" | Sort-Object -Unique)
foreach ($relative in $manifestClaudeFiles) {
    $source = Join-Path $claudeRoot $relative
    if (-not (Test-Path -LiteralPath $source -PathType Leaf)) {
        $problems.Add("claude file in manifest missing from disk: $relative")
    }
}

$diskClaudeTopLevelFiles = @(
    Get-ChildItem -LiteralPath $claudeRoot -File -ErrorAction SilentlyContinue |
        ForEach-Object { $_.Name } |
        Sort-Object -Unique
)
foreach ($relative in $diskClaudeTopLevelFiles) {
    if ($manifestClaudeFiles -notcontains $relative) {
        $problems.Add("claude top-level file on disk missing from manifest: $relative")
    }
}

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
$claudeSectionMatch = [regex]::Match($manifestText, "(?ms)^\[claude\]\s*(.*?)(?=^\[|\z)")
if (-not $claudeSectionMatch.Success) {
    $problems.Add("missing claude section in portable manifest")
}
else {
    $manifestClaudeSkills = @(Get-PortableManifestArray -Text $manifestText -Section "claude" -Key "skills" | Sort-Object -Unique)
    $manifestClaudeDerivedSkills = @(Get-PortableManifestArray -Text $manifestText -Section "claude" -Key "derived_skills" | Sort-Object -Unique)
    $manifestClaudeAgents = @(Get-PortableManifestArray -Text $manifestText -Section "claude" -Key "agents" | Sort-Object -Unique)
    $manifestClaudeDerivedAgents = @(Get-PortableManifestArray -Text $manifestText -Section "claude" -Key "derived_agents" | Sort-Object -Unique)

    # Direct and derived lists are both supported. A name must appear in only
    # one list, and each direct source must exist under claude/.

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

    foreach ($skill in $manifestClaudeDerivedSkills) {
        if ($manifestClaudeSkills -contains $skill) {
            $problems.Add("claude skill listed as direct and derived: $skill")
        }

        $source = Join-Path (Join-Path (Join-Path $repoRoot "codex") "skills") $skill
        if (-not (Test-Path -LiteralPath (Join-Path $source "SKILL.md"))) {
            $problems.Add("claude derived skill source missing from codex skills: $skill")
        }

        $claudeSource = Join-Path (Join-Path (Join-Path $repoRoot "claude") "skills") $skill
        if (Test-Path -LiteralPath $claudeSource) {
            $problems.Add("claude derived skill also has source mirror: $skill")
        }
    }

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

    foreach ($agent in $manifestClaudeDerivedAgents) {
        if ($manifestClaudeAgents -contains $agent) {
            $problems.Add("claude agent listed as direct and derived: $agent")
        }

        $source = Join-Path (Join-Path (Join-Path $repoRoot "codex") "agents") "$agent.toml"
        if (-not (Test-Path -LiteralPath $source)) {
            $problems.Add("claude derived agent source missing from codex agents: $agent")
        }
        else {
            $tomlValues = Get-TopLevelTomlStringValues -Text (Get-Content -Raw -LiteralPath $source)
            if (-not $tomlValues["developer_instructions"]) {
                $problems.Add("claude derived agent source missing developer_instructions: $agent")
            }
            if (-not $tomlValues["name"]) {
                $problems.Add("claude derived agent source missing name: $agent")
            }
            if (-not $tomlValues["description"]) {
                $problems.Add("claude derived agent source missing description: $agent")
            }
        }

        $claudeSource = Join-Path (Join-Path (Join-Path $repoRoot "claude") "agents") "$agent.md"
        if (Test-Path -LiteralPath $claudeSource) {
            $problems.Add("claude derived agent also has source mirror: $agent")
        }

        if (-not $script:ClaudeDerivedAgentFrontmatter.ContainsKey($agent)) {
            $problems.Add("claude derived agent missing frontmatter entry: $agent")
        }
    }
}
