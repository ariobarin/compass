Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-PortableReceiptRoot {
    param([string]$CodexHome)

    return Join-Path $CodexHome "portable-receipts"
}

function Get-PortableCurrentReceipt {
    param([string]$CodexHome)

    $path = Join-Path (Get-PortableReceiptRoot -CodexHome $CodexHome) "current.json"
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        return $null
    }

    try {
        $receipt = Get-Content -Raw -LiteralPath $path | ConvertFrom-Json
    }
    catch {
        throw "invalid current installation receipt: $path"
    }
    if ($receipt.schema_version -ne 1 -or -not $receipt.id) {
        throw "unsupported current installation receipt: $path"
    }
    return $receipt
}

function Get-PortableReceipt {
    param(
        [string]$CodexHome,
        [string]$Receipt
    )

    if ([string]::IsNullOrWhiteSpace($Receipt)) {
        throw "receipt id must be non-empty"
    }
    if ($Receipt -match '[\\/]' -or $Receipt -notmatch '^[A-Za-z0-9._-]+$') {
        throw "receipt id must be a filename-safe id, not a path"
    }

    $fileName = if ($Receipt.EndsWith(".json", [System.StringComparison]::OrdinalIgnoreCase)) {
        $Receipt
    }
    else {
        "$Receipt.json"
    }
    $path = Join-Path (Get-PortableReceiptRoot -CodexHome $CodexHome) $fileName
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        throw "installation receipt not found: $Receipt"
    }

    try {
        $data = Get-Content -Raw -LiteralPath $path | ConvertFrom-Json
    }
    catch {
        throw "invalid installation receipt: $path"
    }
    if ($data.schema_version -ne 1 -or -not $data.id) {
        throw "unsupported installation receipt: $path"
    }
    return $data
}

function Test-PortableReceiptOwnsTarget {
    param(
        [AllowNull()]
        [object]$Receipt,
        [string]$Target
    )

    if ($null -eq $Receipt) {
        return $false
    }
    foreach ($artifact in @($Receipt.artifacts)) {
        if ($artifact.target -and $artifact.target.Equals($Target, [System.StringComparison]::OrdinalIgnoreCase)) {
            return $true
        }
    }
    return $false
}

function Get-PortablePathFingerprint {
    param([string]$Path)

    if (-not (Test-Path -LiteralPath $Path)) {
        return [ordered]@{
            exists = $false
            kind = "missing"
            files = @()
        }
    }

    $item = Get-Item -LiteralPath $Path -Force
    if (-not $item.PSIsContainer) {
        return [ordered]@{
            exists = $true
            kind = "file"
            files = @(
                [ordered]@{
                    path = ""
                    sha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $Path).Hash
                }
            )
        }
    }

    $root = $item.FullName
    $separatorChars = @(
        [System.IO.Path]::DirectorySeparatorChar,
        [System.IO.Path]::AltDirectorySeparatorChar
    ) | Select-Object -Unique
    $files = @(
        foreach ($file in Get-ChildItem -LiteralPath $root -Recurse -File -Force | Sort-Object FullName) {
            [ordered]@{
                path = $file.FullName.Substring($root.Length).TrimStart($separatorChars).Replace("\", "/")
                sha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $file.FullName).Hash
            }
        }
    )

    return [ordered]@{
        exists = $true
        kind = "directory"
        files = $files
    }
}

function Test-PortableFingerprintMatches {
    param(
        [AllowNull()]
        [object]$Expected,
        [string]$Path
    )

    if ($null -eq $Expected) {
        return $false
    }
    $actual = Get-PortablePathFingerprint -Path $Path
    if ([bool]$Expected.exists -ne [bool]$actual.exists) {
        return $false
    }
    if ([string]$Expected.kind -ne [string]$actual.kind) {
        return $false
    }

    $expectedFiles = @($Expected.files)
    $actualFiles = @($actual.files)
    if ($expectedFiles.Count -ne $actualFiles.Count) {
        return $false
    }
    for ($index = 0; $index -lt $expectedFiles.Count; $index += 1) {
        if ([string]$expectedFiles[$index].path -ne [string]$actualFiles[$index].path) {
            return $false
        }
        if ([string]$expectedFiles[$index].sha256 -ne [string]$actualFiles[$index].sha256) {
            return $false
        }
    }
    return $true
}

function Write-PortableReceipt {
    param(
        [string]$CodexHome,
        [object]$Receipt
    )

    $receiptRoot = Get-PortableReceiptRoot -CodexHome $CodexHome
    New-Item -ItemType Directory -Force $receiptRoot | Out-Null

    $json = $Receipt | ConvertTo-Json -Depth 12
    $receiptPath = Join-Path $receiptRoot "$($Receipt.id).json"
    $currentPath = Join-Path $receiptRoot "current.json"
    $tempReceipt = "$receiptPath.tmp-$([guid]::NewGuid().ToString('N'))"
    $tempCurrent = "$currentPath.tmp-$([guid]::NewGuid().ToString('N'))"

    [System.IO.File]::WriteAllText($tempReceipt, $json, [System.Text.UTF8Encoding]::new($false))
    Move-Item -LiteralPath $tempReceipt -Destination $receiptPath -Force
    [System.IO.File]::WriteAllText($tempCurrent, $json, [System.Text.UTF8Encoding]::new($false))
    Move-Item -LiteralPath $tempCurrent -Destination $currentPath -Force

    return $receiptPath
}

function Test-PortablePathUnderAnyRoot {
    param(
        [string]$Path,
        [string[]]$Roots
    )

    foreach ($root in $Roots) {
        if (-not $root) {
            continue
        }
        try {
            Assert-PathUnderRoot -Path $Path -Root $root
            return $true
        }
        catch {
        }
    }
    return $false
}
