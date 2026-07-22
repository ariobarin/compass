# The ledger schema version lives once in scripts/_orchestration_ledger_core.py.
# Current-tense prose must not pin a different version. Version-neutral phrasing
# passes; a reintroduced stale literal fails doctor. Dated revision records that
# describe a point-in-time schema are out of scope and are not scanned here.
$corePath = Join-Path $repoRoot "scripts\_orchestration_ledger_core.py"
if (-not (Test-Path -LiteralPath $corePath -PathType Leaf)) {
    $problems.Add("missing orchestration ledger core module")
}
else {
    $coreText = Get-Content -Raw -LiteralPath $corePath
    $versionMatch = [regex]::Match($coreText, '(?m)^SCHEMA_VERSION\s*=\s*(\d+)')
    if (-not $versionMatch.Success) {
        $problems.Add("orchestration ledger core module has no SCHEMA_VERSION")
    }
    else {
        $current = [int]$versionMatch.Groups[1].Value
        $docs = @(
            "scripts\README.md",
            "workflows\orchestration-ledger.md",
            "workflows\agent-failures.md",
            "local-docs\benchmark-run-evidence.md"
        )
        $patterns = @(
            '(?i)\bschema\s+(?:version\s+)?v?(\d+)\b',
            '(?i)\bschema\s+versions?\s+v?(\d+)(?:\s+(?:through|to|-)\s+v?(\d+))?',
            '(?i)\brewritten\s+(?:as|to)\s+(?:schema\s+)?version\s+v?(\d+)\b'
        )
        foreach ($relative in $docs) {
            $path = Join-Path $repoRoot $relative
            if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
                $problems.Add("ledger schema prose check target missing: $relative")
                continue
            }
            $text = Get-Content -Raw -LiteralPath $path
            $foundVersions = New-Object System.Collections.Generic.HashSet[int]
            foreach ($pattern in $patterns) {
                foreach ($m in [regex]::Matches($text, $pattern)) {
                    foreach ($group in $m.Groups[1..($m.Groups.Count - 1)]) {
                        if ($group.Success) {
                            [void]$foundVersions.Add([int]$group.Value)
                        }
                    }
                }
            }
            foreach ($found in $foundVersions) {
                if ($found -ne $current) {
                    $problems.Add("$relative names ledger schema version $found but the canonical version is $current")
                }
            }
        }
    }
}
