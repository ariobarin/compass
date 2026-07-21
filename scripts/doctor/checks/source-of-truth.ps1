$registerPath = Join-Path $repoRoot "local-docs\source-of-truth.md"
if (-not (Test-Path -LiteralPath $registerPath -PathType Leaf)) {
    $problems.Add("missing source-of-truth register")
}
else {
    $lines = @(Get-Content -LiteralPath $registerPath)
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

        $allowedMechanisms = @("generate", "link", "accepted", "keep")
        $allowedStatuses = @("canonical", "consolidated", "planned", "accepted")
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
            if ($allowedMechanisms -notcontains $mechanism) {
                $problems.Add("source-of-truth register row $id has an invalid mechanism: $mechanism")
            }
            if (-not $boundBy) {
                $problems.Add("source-of-truth register row $id has no binding")
            }
            if ($allowedStatuses -notcontains $status) {
                $problems.Add("source-of-truth register row $id has an invalid status: $status")
            }
        }

        foreach ($expected in 1..13) {
            if ($seenIds -notcontains "$expected") {
                $problems.Add("source-of-truth register is missing cluster row: $expected")
            }
        }
    }
}
