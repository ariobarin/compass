$manifestPath = Join-Path $repoRoot "manifests\model-tiers.json"
if (-not (Test-Path -LiteralPath $manifestPath -PathType Leaf)) {
    $problems.Add("missing model-tiers manifest")
}
else {
    try {
        $manifest = Get-Content -Raw -LiteralPath $manifestPath | ConvertFrom-Json
        if ($manifest.schema_version -ne 1) {
            $problems.Add("unsupported model-tiers manifest schema")
        }

        $allowedEfforts = @("low", "medium", "high", "xhigh", "max")
        $tiers = @($manifest.tiers)
        $seenModels = New-Object System.Collections.Generic.List[string]
        foreach ($tier in $tiers) {
            if (-not $tier.model -or -not $tier.display_name -or -not $tier.effort) {
                $problems.Add("model-tiers manifest row is incomplete")
                continue
            }
            if ($seenModels -contains $tier.model) {
                $problems.Add("model-tiers manifest has duplicate model: $($tier.model)")
            }
            $seenModels.Add($tier.model)
            if ($allowedEfforts -notcontains $tier.effort) {
                $problems.Add("model-tiers manifest has invalid effort: $($tier.effort)")
            }
        }

        # The calibration doc must carry each tier row verbatim.
        $calibrationPath = Join-Path $repoRoot "local-docs\model-calibration.md"
        $calibration = Get-Content -Raw -LiteralPath $calibrationPath
        foreach ($tier in $tiers) {
            $row = "| $($tier.display_name) | ``$($tier.effort)`` |"
            if (-not $calibration.Contains($row)) {
                $problems.Add("model-calibration.md missing tier row: $row")
            }
        }

        # The active reviewed config must match exactly one tier row.
        $configPath = Join-Path $repoRoot "codex\config.review.toml"
        $configText = Get-Content -Raw -LiteralPath $configPath
        $modelMatch = [regex]::Match($configText, '(?m)^model\s*=\s*"([^"]+)"')
        $effortMatch = [regex]::Match($configText, '(?m)^model_reasoning_effort\s*=\s*"([^"]+)"')
        if (-not $modelMatch.Success -or -not $effortMatch.Success) {
            $problems.Add("codex config.review.toml missing model or model_reasoning_effort")
        }
        else {
            $activeModel = $modelMatch.Groups[1].Value
            $activeEffort = $effortMatch.Groups[1].Value
            $matched = $false
            foreach ($tier in $tiers) {
                if ($tier.model -eq $activeModel -and $tier.effort -eq $activeEffort) {
                    $matched = $true
                    break
                }
            }
            if (-not $matched) {
                $problems.Add("codex config.review.toml model $activeModel effort $activeEffort is not a reviewed tier")
            }
        }
    }
    catch {
        $problems.Add("invalid model-tiers manifest: $($_.Exception.Message)")
    }
}
