$pluginManifestPath = Join-Path $repoRoot "manifests\plugins.json"
if (-not (Test-Path -LiteralPath $pluginManifestPath -PathType Leaf)) {
    $problems.Add("missing plugin manifest")
}
else {
    try {
        $pluginManifest = Get-Content -Raw -LiteralPath $pluginManifestPath | ConvertFrom-Json
        $marketplaceNames = @($pluginManifest.marketplaces | ForEach-Object { $_.name })
        if ($marketplaceNames.Count -eq 0) {
            $problems.Add("plugin manifest has no marketplaces")
        }
        if (@($marketplaceNames | Sort-Object -Unique).Count -ne $marketplaceNames.Count) {
            $problems.Add("plugin manifest has duplicate marketplace names")
        }

        foreach ($marketplace in @($pluginManifest.marketplaces)) {
            if (-not $marketplace.name -or -not $marketplace.source) {
                $problems.Add("plugin marketplace entries require name and source")
            }
            if (@($marketplace.sparse).Count -eq 0) {
                $problems.Add("plugin marketplace requires at least one sparse path: $($marketplace.name)")
            }
        }

        foreach ($pluginId in @($pluginManifest.plugins)) {
            $parts = $pluginId -split "@", 2
            if ($parts.Count -ne 2 -or -not $parts[0] -or -not $parts[1]) {
                $problems.Add("invalid plugin selector: $pluginId")
            }
            elseif ($marketplaceNames -notcontains $parts[1]) {
                $problems.Add("plugin selector references undeclared marketplace: $pluginId")
            }
        }
    }
    catch {
        $problems.Add("invalid plugin manifest: $($_.Exception.Message)")
    }
}
