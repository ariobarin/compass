function Read-DoctorJson {
    param(
        [string]$Path,
        [string]$Label
    )

    if (-not (Test-Path -LiteralPath $Path)) {
        $problems.Add("missing $Label JSON: $Path")
        return $null
    }

    try {
        return Get-Content -Raw -LiteralPath $Path | ConvertFrom-Json
    }
    catch {
        $problems.Add("invalid $Label JSON: $($_.Exception.Message)")
        return $null
    }
}

$pluginManifestPath = Join-Path $repoRoot "codex\.codex-plugin\plugin.json"
$pluginManifest = Read-DoctorJson -Path $pluginManifestPath -Label "plugin manifest"

if ($pluginManifest) {
    if ($pluginManifest.name -ne "compass") {
        $problems.Add("plugin manifest name must be compass")
    }

    if ($pluginManifest.version -notmatch "^\d+\.\d+\.\d+$") {
        $problems.Add("plugin manifest version must use semantic version form")
    }

    if ($pluginManifest.skills -ne "./skills/") {
        $problems.Add("plugin manifest skills path must be ./skills/")
    }

    $pluginSkillsPath = Join-Path $repoRoot "codex\skills"
    if (-not (Test-Path -LiteralPath $pluginSkillsPath -PathType Container)) {
        $problems.Add("plugin skills directory is missing: $pluginSkillsPath")
    }
}

$marketplacePath = Join-Path $repoRoot ".agents\plugins\marketplace.json"
$marketplace = Read-DoctorJson -Path $marketplacePath -Label "plugin marketplace"

if ($marketplace) {
    if ($marketplace.name -ne "compass") {
        $problems.Add("plugin marketplace name must be compass")
    }

    $entries = @($marketplace.plugins | Where-Object { $_.name -eq "compass" })
    if ($entries.Count -ne 1) {
        $problems.Add("plugin marketplace must contain exactly one compass entry")
    }
    else {
        $entry = $entries[0]
        if ($entry.source.source -ne "local") {
            $problems.Add("compass marketplace source must be local")
        }
        if ($entry.source.path -ne "./codex") {
            $problems.Add("compass marketplace source path must be ./codex")
        }
        if ($entry.policy.installation -ne "AVAILABLE") {
            $problems.Add("compass marketplace install policy must be AVAILABLE")
        }
        if ($entry.policy.authentication -ne "ON_INSTALL") {
            $problems.Add("compass marketplace auth policy must be ON_INSTALL")
        }
        if (-not $entry.category) {
            $problems.Add("compass marketplace entry must define a category")
        }
    }
}
