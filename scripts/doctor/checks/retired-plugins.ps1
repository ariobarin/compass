$manifestPath = Join-Path $repoRoot "manifests\retired-plugins.json"
if (-not (Test-Path -LiteralPath $manifestPath -PathType Leaf)) {
    $problems.Add("missing retired plugin manifest")
}
else {
    try {
        $manifest = Get-Content -Raw -LiteralPath $manifestPath | ConvertFrom-Json
        if ($manifest.schema_version -ne 1) {
            $problems.Add("unsupported retired plugin manifest schema")
        }
        $plugins = @($manifest.plugins)
        $marketplaces = @($manifest.marketplaces)
        if ($plugins.Count -ne @($plugins | Sort-Object -Unique).Count) {
            $problems.Add("retired plugin manifest contains duplicate plugins")
        }
        if ($marketplaces.Count -ne @($marketplaces | Sort-Object -Unique).Count) {
            $problems.Add("retired plugin manifest contains duplicate marketplaces")
        }
        foreach ($plugin in $plugins) {
            if ($plugin -notmatch '^[a-z0-9][a-z0-9._-]*@[a-z0-9][a-z0-9._-]*$') {
                $problems.Add("invalid retired plugin selector: $plugin")
            }
        }
        foreach ($marketplace in $marketplaces) {
            if ($marketplace -notmatch '^[a-z0-9][a-z0-9._-]*$') {
                $problems.Add("invalid retired marketplace name: $marketplace")
            }
        }
    }
    catch {
        $problems.Add("invalid retired plugin manifest: $($_.Exception.Message)")
    }
}
