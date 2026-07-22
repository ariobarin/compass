$maxDescriptionLength = $script:MaxSkillDescriptionLength
$skillRoots = @(
    (Join-Path $repoRoot "codex\skills")
)
$carriedRoot = Join-Path $repoRoot "carried"
if (Test-Path -LiteralPath $carriedRoot) {
    $skillRoots += @(
        Get-ChildItem -LiteralPath $carriedRoot -Directory -ErrorAction SilentlyContinue |
            ForEach-Object { Join-Path $_.FullName "skills" } |
            Where-Object { Test-Path -LiteralPath $_ }
    )
}
$skillFiles = @(
    foreach ($skillRoot in $skillRoots) {
        Get-ChildItem -Path $skillRoot -Recurse -File -Filter "SKILL.md" -ErrorAction SilentlyContinue
    }
)
$skillNames = New-Object 'System.Collections.Generic.Dictionary[string, string]' ([System.StringComparer]::OrdinalIgnoreCase)

function Get-SkillFrontMatterValue {
    param(
        [string[]]$Lines,
        [string]$Field
    )

    $matches = @($Lines | Where-Object { $_ -match "^\s*$([regex]::Escape($Field)):\s*(.*?)\s*$" })
    if ($matches.Count -ne 1) {
        return $null
    }

    $value = ([regex]::Match($matches[0], "^\s*$([regex]::Escape($Field)):\s*(.*?)\s*$").Groups[1].Value).Trim()
    if ($value -match '^"(.*)"$' -or $value -match "^'(.*)'$") {
        $value = $Matches[1].Trim()
    }

    if ([string]::IsNullOrWhiteSpace($value)) {
        return $null
    }

    return $value
}

foreach ($skillFile in $skillFiles) {
    $lines = @(Get-Content -LiteralPath $skillFile.FullName)
    if ($lines.Count -lt 3 -or $lines[0] -ne "---") {
        $problems.Add("skill front matter must start on the first line: $($skillFile.FullName)")
        continue
    }

    $closingIndex = -1
    for ($index = 1; $index -lt $lines.Count; $index += 1) {
        if ($lines[$index] -eq "---") {
            $closingIndex = $index
            break
        }
    }

    if ($closingIndex -lt 0) {
        $problems.Add("skill front matter missing closing delimiter: $($skillFile.FullName)")
        continue
    }

    $frontMatter = @($lines[1..($closingIndex - 1)])
    $name = Get-SkillFrontMatterValue -Lines $frontMatter -Field "name"
    $description = Get-SkillFrontMatterValue -Lines $frontMatter -Field "description"
    if (-not $name) {
        $problems.Add("skill front matter requires one non-empty name: $($skillFile.FullName)")
        continue
    }

    if (-not $description) {
        $problems.Add("skill front matter requires one non-empty description: $($skillFile.FullName)")
        continue
    }

    if ($name -ne $skillFile.Directory.Name) {
        $problems.Add("skill name must match directory '$($skillFile.Directory.Name)': $($skillFile.FullName)")
    }

    if ($skillNames.ContainsKey($name)) {
        $problems.Add("duplicate skill name '$name': $($skillFile.FullName) and $($skillNames[$name])")
    }
    else {
        $skillNames.Add($name, $skillFile.FullName)
    }

    if ($description.Length -gt $maxDescriptionLength) {
        $problems.Add("skill description over $maxDescriptionLength chars: $($skillFile.FullName)")
    }
}
