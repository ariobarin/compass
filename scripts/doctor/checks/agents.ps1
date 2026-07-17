$agentFiles = @(
    Get-ChildItem -Path (Join-Path $repoRoot "codex\agents") -File -Filter "*.toml" -ErrorAction SilentlyContinue
)
$carriedRoot = Join-Path $repoRoot "carried"
if (Test-Path -LiteralPath $carriedRoot) {
    $agentFiles += @(
        Get-ChildItem -Path (Join-Path $carriedRoot "*\agents\*.toml") -File -ErrorAction SilentlyContinue
    )
}

foreach ($agentFile in $agentFiles) {
    $agentText = Get-Content -Raw -LiteralPath $agentFile.FullName
    $topLevelValues = Get-TopLevelTomlStringValues -Text $agentText
    $topLevelText = $topLevelValues.Values -join "`n"

    if ($topLevelText -match "(?i)\bread-only\b" -and ($topLevelValues["sandbox_mode"] -ne "read-only")) {
        $problems.Add("read-only agent missing sandbox_mode: $($agentFile.FullName)")
    }
    if ($null -ne $topLevelValues["service_tier"]) {
        $problems.Add("portable agent must omit service_tier and inherit the active parent choice: $($agentFile.FullName)")
    }

    $model = $topLevelValues["model"]
    if ($model -eq "gpt-5.6-terra") {
        $problems.Add("agent uses retired current-profile Terra route: $($agentFile.FullName)")
    }
    if ($model -and $model -notin @("gpt-5.6-luna", "gpt-5.6-sol")) {
        $problems.Add("agent uses unreviewed model route '$model': $($agentFile.FullName)")
    }
}
