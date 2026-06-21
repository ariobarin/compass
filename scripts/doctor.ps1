param(
    [string]$CodexHome
)

. "$PSScriptRoot\common.ps1"

$repoRoot = Get-RepoRoot
try {
    $liveHome = Get-CodexHome -CodexHome $CodexHome
}
catch {
    $liveHome = Join-Path $env:USERPROFILE ".codex"
}
$problems = New-Object System.Collections.Generic.List[string]
$trackedFiles = @()
$pathSeparators = @([System.IO.Path]::DirectorySeparatorChar, [System.IO.Path]::AltDirectorySeparatorChar) | Select-Object -Unique

function Get-DoctorFullPath {
    param([string]$Path)

    return [System.IO.Path]::GetFullPath($Path).TrimEnd($pathSeparators)
}

$localScratchRoot = Get-DoctorFullPath -Path (Join-Path $repoRoot ".local")

function Test-LocalScratchPath {
    param([string]$Path)

    $fullPath = Get-DoctorFullPath -Path $Path
    if ($fullPath -eq $localScratchRoot) {
        return $true
    }

    foreach ($separator in $pathSeparators) {
        if ($fullPath.StartsWith("$localScratchRoot$separator", [System.StringComparison]::OrdinalIgnoreCase)) {
            return $true
        }
    }

    return $false
}

function Get-DoctorChildItem {
    param(
        [ValidateSet("File", "Directory")]
        [string]$Kind,
        [string]$Filter = "*"
    )

    $items = New-Object System.Collections.Generic.List[object]

    function Add-DoctorChildren {
        param([string]$Path)

        foreach ($child in Get-ChildItem -LiteralPath $Path -Force -ErrorAction SilentlyContinue) {
            if ($child.PSIsContainer) {
                if ($child.FullName -match "\\.git(\\|$)") {
                    continue
                }

                if (Test-LocalScratchPath -Path $child.FullName) {
                    continue
                }

                if ($Kind -eq "Directory" -and $child.Name -like $Filter) {
                    $items.Add($child)
                }

                Add-DoctorChildren -Path $child.FullName
                continue
            }

            if ($Kind -eq "File" -and $child.Name -like $Filter) {
                $items.Add($child)
            }
        }
    }

    Add-DoctorChildren -Path $repoRoot
    return $items
}

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    $problems.Add("git is not on PATH")
}
else {
    $trackedFiles = @(& git -C $repoRoot ls-files 2>$null)
    foreach ($trackedFile in $trackedFiles) {
        $trackedPath = Get-DoctorFullPath -Path (Join-Path $repoRoot $trackedFile)
        if (Test-LocalScratchPath -Path $trackedPath) {
            $problems.Add("tracked local scratch path: $trackedFile")
        }
    }
}

foreach ($path in @(
    ".gitattributes",
    ".github\workflows\portable-checks.yml",
    "AGENTS.md",
    "codex\AGENTS.md",
    "codex\keybindings.json",
    "codex\config.review.toml",
    "manifests\portable-files.toml",
    "manifests\tool-surfaces.md",
    "local-docs\README.md",
    "local-docs\maintenance-learnings.md",
    "workflows\addition-intake.md",
    "workflows\portable-config.md",
    "workflows\multi-thread-pr-coordination.md",
    "workflows\plan-template.md",
    "workflows\read-only-research.md",
    "workflows\agent-failures.md",
    "scripts\verify-live.ps1"
)) {
    $fullPath = Join-Path $repoRoot $path
    if (-not (Test-Path $fullPath)) {
        $problems.Add("missing required file: $path")
    }
}

$blockedNames = @(
    "AGENTS.override.md",
    "auth.json",
    "history.jsonl",
    "session_index.jsonl",
    "installation_id",
    "cap_sid"
)

foreach ($blocked in $blockedNames) {
    $matches = Get-DoctorChildItem -Kind File -Filter $blocked
    foreach ($match in $matches) {
        $problems.Add("blocked local-only file tracked in repo tree: $($match.FullName)")
    }
}

$blockedDirs = @(
    ".sandbox",
    ".sandbox-bin",
    ".sandbox-secrets",
    ".tmp",
    ".local",
    "archived_sessions",
    "automations",
    "browser",
    "cache",
    "computer-use",
    "log",
    "memories",
    "memories_extensions",
    "node_repl",
    "plugins",
    "process_manager",
    "rules",
    "sessions",
    "sqlite",
    "threads",
    "tmp",
    "vendor_imports",
    "worktrees"
)

foreach ($dir in Get-DoctorChildItem -Kind Directory) {
    if ($dir.FullName -match "\\.git(\\|$)") {
        continue
    }

    if ($blockedDirs -contains $dir.Name) {
        $problems.Add("blocked local-only directory in repo tree: $($dir.FullName)")
    }
}

$textFiles = Get-DoctorChildItem -Kind File |
    Where-Object {
        $_.FullName -notmatch "\\.git\\" -and
        $_.Extension -in @(".md", ".toml", ".json", ".ps1", ".yaml", ".yml", ".txt")
    }

foreach ($file in $textFiles) {
    $content = Get-Content -Raw -LiteralPath $file.FullName
    if ($content -match "[^\x00-\x7F]") {
        $problems.Add("non-ASCII text in: $($file.FullName)")
    }
}

$maxDescriptionLength = 160
$skillFiles = Get-ChildItem -Path (Join-Path $repoRoot "codex\skills") -Recurse -File -Filter "SKILL.md" -ErrorAction SilentlyContinue
foreach ($skillFile in $skillFiles) {
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

function Get-TopLevelTomlStringValues {
    param([string]$Text)

    $topLevelValues = @{}
    $currentKey = $null
    $currentValue = New-Object System.Text.StringBuilder
    $inMultilineString = $false
    $inTable = $false

    foreach ($line in ($Text -split "`r?`n")) {
        if ($inMultilineString) {
            $closingIndex = $line.IndexOf('"""')
            if ($closingIndex -ge 0) {
                [void]$currentValue.AppendLine($line.Substring(0, $closingIndex))
                $topLevelValues[$currentKey] = $currentValue.ToString()
                $currentKey = $null
                [void]$currentValue.Clear()
                $inMultilineString = $false
            }
            else {
                [void]$currentValue.AppendLine($line)
            }
            continue
        }

        if ($line -match '^\s*\[') {
            $inTable = $true
            continue
        }

        if ($inTable) {
            continue
        }

        $multiline = [regex]::Match($line, '^\s*([A-Za-z0-9_-]+)\s*=\s*"""(.*)$')
        if ($multiline.Success) {
            $key = $multiline.Groups[1].Value
            $remainingText = $multiline.Groups[2].Value
            $closingIndex = $remainingText.IndexOf('"""')
            if ($closingIndex -ge 0) {
                $topLevelValues[$key] = $remainingText.Substring(0, $closingIndex)
            }
            else {
                $currentKey = $key
                [void]$currentValue.Clear()
                [void]$currentValue.AppendLine($remainingText)
                $inMultilineString = $true
            }
            continue
        }

        $assignment = [regex]::Match($line, '^\s*([A-Za-z0-9_-]+)\s*=\s*"([^"]*)"\s*(#.*)?$')
        if ($assignment.Success) {
            $topLevelValues[$assignment.Groups[1].Value] = $assignment.Groups[2].Value
        }
    }

    return $topLevelValues
}

$agentFiles = Get-ChildItem -Path (Join-Path $repoRoot "codex\agents") -File -Filter "*.toml" -ErrorAction SilentlyContinue
foreach ($agentFile in $agentFiles) {
    $agentText = Get-Content -Raw -LiteralPath $agentFile.FullName
    $topLevelValues = Get-TopLevelTomlStringValues -Text $agentText
    $topLevelText = $topLevelValues.Values -join "`n"

    if ($topLevelText -match "(?i)\bread-only\b" -and ($topLevelValues["sandbox_mode"] -ne "read-only")) {
        $problems.Add("read-only agent missing sandbox_mode: $($agentFile.FullName)")
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
        Get-PortableFileMap -RepoRoot $repoRoot -CodexHome $liveHome |
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

Write-Host "repo: $repoRoot"
Write-Host "live: $liveHome"

if ($problems.Count -gt 0) {
    Write-Host ""
    Write-Host "problems:"
    foreach ($problem in $problems) {
        Write-Host "  $problem"
    }
    exit 1
}

Write-Host "doctor: ok"
