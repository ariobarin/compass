$maxDescriptionLength = 160
$skillFiles = Get-ChildItem -Path (Join-Path $repoRoot "codex\skills") -Recurse -File -Filter "SKILL.md" -ErrorAction SilentlyContinue
foreach ($skillFile in $skillFiles) {
    $name = Select-String -Path $skillFile.FullName -Pattern "^name:\s*(.+)$" | Select-Object -First 1
    if (-not $name) {
        $problems.Add("missing skill name: $($skillFile.FullName)")
        continue
    }

    $description = Select-String -Path $skillFile.FullName -Pattern "^description:\s*(.+)$" | Select-Object -First 1
    if (-not $description) {
        $problems.Add("missing skill description: $($skillFile.FullName)")
        continue
    }

    $descriptionText = $description.Matches[0].Groups[1].Value.Trim()
    if ($descriptionText.Length -gt $maxDescriptionLength) {
        $problems.Add("skill description over $maxDescriptionLength chars: $($skillFile.FullName)")
    }
}

$manifestPath = Join-Path $repoRoot "manifests\portable-files.toml"
$manifestText = Get-Content -Raw -LiteralPath $manifestPath
$skillsMatch = [regex]::Match($manifestText, "(?ms)^skills\s*=\s*\[(.*?)^\]")
if (-not $skillsMatch.Success) {
    $problems.Add("missing skills allowlist in portable manifest")
}
else {
    $manifestSkills = @(
        [regex]::Matches($skillsMatch.Groups[1].Value, '"([^"]+)"') |
            ForEach-Object { $_.Groups[1].Value } |
            Sort-Object -Unique
    )

    $skillsRoot = [System.IO.Path]::GetFullPath((Join-Path (Join-Path $repoRoot "codex") "skills")).TrimEnd("\")
    $mappedSkills = @(
        Get-PortableFileMap -RepoRoot $repoRoot -CodexHome $liveHome -AgentsHome $agentsHomePath |
            Where-Object {
                $_.Type -eq "dir" -and
                [System.IO.Path]::GetFullPath($_.RepoPath).TrimEnd("\").StartsWith(
                    "$skillsRoot\",
                    [System.StringComparison]::OrdinalIgnoreCase
                )
            } |
            ForEach-Object { Split-Path -Leaf $_.RepoPath } |
            Sort-Object -Unique
    )

    foreach ($skill in $manifestSkills) {
        if ($mappedSkills -notcontains $skill) {
            $problems.Add("skill in manifest missing from install map: $skill")
        }
    }

    foreach ($skill in $mappedSkills) {
        if ($manifestSkills -notcontains $skill) {
            $problems.Add("skill in install map missing from manifest: $skill")
        }
    }
}
