$registerPath = Join-Path $repoRoot "local-docs\source-of-truth.md"
if (-not (Test-Path -LiteralPath $registerPath -PathType Leaf)) {
    $problems.Add("missing source-of-truth register")
}
else {
    $lines = @(Get-Content -LiteralPath $registerPath)
    $registerText = Get-Content -Raw -LiteralPath $registerPath

    # The register is the single source of the mechanism and status vocabularies.
    # Parse them from the legend sections so adding a value needs no check edit.
    $mechanismStart = $registerText.IndexOf("Mechanism values:")
    $statusStart = $registerText.IndexOf("Status values:")
    $tableStart = $registerText.IndexOf("| ID |")
    $allowedMechanisms = @()
    $allowedStatuses = @()
    if ($mechanismStart -ge 0 -and $statusStart -gt $mechanismStart) {
        $region = $registerText.Substring($mechanismStart, $statusStart - $mechanismStart)
        $allowedMechanisms = @([regex]::Matches($region, '(?m)^\s*-\s*`([^`]+)`') | ForEach-Object { $_.Groups[1].Value })
    }
    if ($statusStart -ge 0 -and $tableStart -gt $statusStart) {
        $region = $registerText.Substring($statusStart, $tableStart - $statusStart)
        $allowedStatuses = @([regex]::Matches($region, '(?m)^\s*-\s*`([^`]+)`') | ForEach-Object { $_.Groups[1].Value })
    }
    if ($allowedMechanisms.Count -eq 0) {
        $problems.Add("source-of-truth register has no Mechanism legend")
    }
    if ($allowedStatuses.Count -eq 0) {
        $problems.Add("source-of-truth register has no Status legend")
    }

    $tableRows = @($lines | Where-Object { $_ -match '^\|' })
    if ($tableRows.Count -lt 2) {
        $problems.Add("source-of-truth register has no table")
    }
    else {
        $header = $tableRows[0]
        foreach ($column in @("ID", "Fact family", "Canonical source", "Mechanism", "Bound by", "Status")) {
            if ($header -notmatch [regex]::Escape($column)) {
                $problems.Add("source-of-truth register missing column: $column")
            }
        }

        $dataRows = @()
        if ($tableRows.Count -gt 2) {
            $dataRows = @($tableRows[2..($tableRows.Count - 1)])
        }

        $seenIds = New-Object System.Collections.Generic.List[string]
        foreach ($row in $dataRows) {
            $parts = @($row -split '\|')
            if ($parts.Count -lt 3) {
                $problems.Add("source-of-truth register row is malformed: $row")
                continue
            }
            $cells = @($parts[1..($parts.Count - 2)] | ForEach-Object { $_.Trim() })
            if ($cells.Count -lt 6) {
                $problems.Add("source-of-truth register row has too few cells: $row")
                continue
            }
            $id = $cells[0]
            $canonical = $cells[2]
            $mechanism = $cells[3]
            $boundBy = $cells[4]
            $status = $cells[5]
            if ($id -notmatch '^\d+$') {
                $problems.Add("source-of-truth register row has a non-numeric ID: $row")
                continue
            }
            if ($seenIds -contains $id) {
                $problems.Add("source-of-truth register has a duplicate ID: $id")
            }
            $seenIds.Add($id)
            if (-not $canonical) {
                $problems.Add("source-of-truth register row $id has no canonical source")
            }
            if ($allowedMechanisms.Count -gt 0 -and $allowedMechanisms -notcontains $mechanism) {
                $problems.Add("source-of-truth register row $id has an invalid mechanism: $mechanism")
            }
            if (-not $boundBy) {
                $problems.Add("source-of-truth register row $id has no binding")
            }
            if ($allowedStatuses.Count -gt 0 -and $allowedStatuses -notcontains $status) {
                $problems.Add("source-of-truth register row $id has an invalid status: $status")
            }

            # Literal file paths named as the canonical source must exist on
            # disk. Glob patterns and non-file descriptions are skipped, so the
            # check catches a row that names a missing file without false
            # positives on intentionally patterned or prose sources.
            foreach ($match in [regex]::Matches($canonical, '[A-Za-z0-9_./-]+\.(?:md|json|toml|py|ps1|yaml|yml)')) {
                $token = $match.Value
                if ($token -match '[\*\?]') { continue }
                $candidate = Join-Path $repoRoot ($token -replace '/', '\')
                if (-not (Test-Path -LiteralPath $candidate)) {
                    $problems.Add("source-of-truth register row $id names a missing canonical source: $token")
                }
            }
        }

        foreach ($expected in 1..14) {
            if ($seenIds -notcontains "$expected") {
                $problems.Add("source-of-truth register is missing cluster row: $expected")
            }
        }
    }
}
