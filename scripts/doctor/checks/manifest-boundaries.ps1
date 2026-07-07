$manifestPath = Join-Path $repoRoot "manifests\portable-files.toml"
$manifestText = Get-Content -Raw -LiteralPath $manifestPath

function ConvertTo-GitPath {
    param([string]$Path)

    return $Path.Replace("\", "/").Trim("/")
}

function Get-ManifestRepoPaths {
    $paths = New-Object System.Collections.Generic.List[string]

    foreach ($file in @(Get-ManifestArrayValues -Text $manifestText -Section "repo_only" -Key "files")) {
        $paths.Add((ConvertTo-GitPath -Path $file))
    }

    foreach ($file in @(Get-ManifestArrayValues -Text $manifestText -Section "codex" -Key "files")) {
        $paths.Add((ConvertTo-GitPath -Path (Join-Path "codex" $file)))
    }

    $configReviewFile = Get-ManifestStringValue -Section "config" -Key "review_file"
    if ($configReviewFile) {
        $paths.Add((ConvertTo-GitPath -Path (Join-Path "codex" $configReviewFile)))
    }

    foreach ($file in @(Get-ManifestArrayValues -Text $manifestText -Section "claude" -Key "files")) {
        $paths.Add((ConvertTo-GitPath -Path (Join-Path "claude" $file)))
    }

    foreach ($agent in @(Get-ManifestArrayValues -Text $manifestText -Section "claude" -Key "agents")) {
        $paths.Add((ConvertTo-GitPath -Path (Join-Path (Join-Path "claude" "agents") "$agent.md")))
    }

    return @($paths)
}

function Get-ManifestRepoDirPrefixes {
    $prefixes = New-Object System.Collections.Generic.List[string]

    foreach ($dir in @(Get-ManifestArrayValues -Text $manifestText -Section "repo_only" -Key "dirs")) {
        $prefixes.Add("$(ConvertTo-GitPath -Path $dir)/")
    }

    foreach ($dir in @(Get-ManifestArrayValues -Text $manifestText -Section "codex" -Key "dirs")) {
        $prefixes.Add("$(ConvertTo-GitPath -Path (Join-Path "codex" $dir))/")
    }

    foreach ($skill in @(Get-ManifestArrayValues -Text $manifestText -Section "agents" -Key "skills")) {
        $prefixes.Add("$(ConvertTo-GitPath -Path (Join-Path (Join-Path "codex" "skills") $skill))/")
    }

    foreach ($dir in @(Get-ManifestArrayValues -Text $manifestText -Section "claude" -Key "dirs")) {
        $prefixes.Add("$(ConvertTo-GitPath -Path (Join-Path "claude" $dir))/")
    }

    foreach ($skill in @(Get-ManifestArrayValues -Text $manifestText -Section "claude" -Key "skills")) {
        $prefixes.Add("$(ConvertTo-GitPath -Path (Join-Path (Join-Path "claude" "skills") $skill))/")
    }

    return @($prefixes)
}

function Get-ManifestStringValue {
    param(
        [string]$Section,
        [string]$Key
    )

    $sectionPattern = "(?ms)^\[$([regex]::Escape($Section))\]\s*(.*?)(?=^\[|\z)"
    $sectionMatch = [regex]::Match($manifestText, $sectionPattern)
    if (-not $sectionMatch.Success) {
        return $null
    }

    $keyPattern = "(?m)^\s*$([regex]::Escape($Key))\s*=\s*`"([^`"]+)`""
    $keyMatch = [regex]::Match($sectionMatch.Groups[1].Value, $keyPattern)
    if (-not $keyMatch.Success) {
        return $null
    }

    return $keyMatch.Groups[1].Value
}

$blockedNames = @(Get-ManifestArrayValues -Text $manifestText -Section "local_only" -Key "files")
if ($blockedNames.Count -eq 0) {
    $problems.Add("missing local-only files in portable manifest")
}

foreach ($blocked in $blockedNames) {
    $matches = Get-DoctorChildItem -Kind File -Filter $blocked
    foreach ($match in $matches) {
        $problems.Add("blocked local-only file in repo tree: $($match.FullName)")
    }
}

$blockedPatterns = @(Get-ManifestArrayValues -Text $manifestText -Section "local_only" -Key "patterns")
if ($blockedPatterns.Count -eq 0) {
    $problems.Add("missing local-only patterns in portable manifest")
}

foreach ($blockedPattern in $blockedPatterns) {
    $matches = Get-DoctorChildItem -Kind File -Filter $blockedPattern
    foreach ($match in $matches) {
        $problems.Add("blocked local-only file pattern in repo tree: $($match.FullName)")
    }
}

$blockedDirs = @(Get-ManifestArrayValues -Text $manifestText -Section "local_only" -Key "dirs")
if ($blockedDirs.Count -eq 0) {
    $problems.Add("missing local-only dirs in portable manifest")
}

foreach ($dir in Get-DoctorChildItem -Kind Directory) {
    if ($dir.FullName -match "\\.git(\\|$)") {
        continue
    }

    if ($blockedDirs -contains $dir.Name) {
        $problems.Add("blocked local-only directory in repo tree: $($dir.FullName)")
    }
}

if (Get-Command git -ErrorAction SilentlyContinue) {
    $trackedRepoFiles = @(& git -C $repoRoot ls-files)
    if ($LASTEXITCODE -ne 0) {
        $problems.Add("could not list tracked files for manifest boundary check")
    }
    else {
        $allowedFiles = @(Get-ManifestRepoPaths)
        $allowedDirPrefixes = @(Get-ManifestRepoDirPrefixes)
        foreach ($trackedFile in $trackedRepoFiles) {
            $repoPath = ConvertTo-GitPath -Path $trackedFile
            $allowed = $allowedFiles -contains $repoPath
            if (-not $allowed) {
                foreach ($prefix in $allowedDirPrefixes) {
                    if ($repoPath.StartsWith($prefix, [System.StringComparison]::OrdinalIgnoreCase)) {
                        $allowed = $true
                        break
                    }
                }
            }

            if (-not $allowed) {
                $problems.Add("tracked file outside portable manifest boundary: $repoPath")
            }
        }
    }
}

foreach ($path in @(Get-ManifestRepoPaths)) {
    $fullPath = Join-Path $repoRoot ($path.Replace("/", "\"))
    if (-not (Test-Path -LiteralPath $fullPath)) {
        $problems.Add("manifest-listed file missing from repo: $path")
    }
}

foreach ($prefix in @(Get-ManifestRepoDirPrefixes)) {
    $path = $prefix.TrimEnd("/")
    $fullPath = Join-Path $repoRoot ($path.Replace("/", "\"))
    if (-not (Test-Path -LiteralPath $fullPath)) {
        $problems.Add("manifest-listed directory missing from repo: $path")
    }
}
