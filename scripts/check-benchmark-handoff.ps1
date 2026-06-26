param(
    [Parameter(Mandatory = $true)]
    [string]$Path,

    [int]$FirstScreenLines = 25,

    [switch]$AllowPlaceholders
)

$fullPath = [System.IO.Path]::GetFullPath($Path)
if (-not (Test-Path -LiteralPath $fullPath)) {
    Write-Host "missing handoff: $fullPath"
    exit 1
}

$text = Get-Content -Raw -Encoding UTF8 -LiteralPath $fullPath
$lines = @($text -split "`r?`n")
$firstScreenLinesValue = @($lines | Select-Object -First $FirstScreenLines)
$firstScreen = $firstScreenLinesValue -join "`n"
$problems = New-Object System.Collections.Generic.List[string]

function Get-FirstScreenField {
    param([string]$FieldName)

    $fieldPattern = "^$([regex]::Escape($FieldName))\s*:\s*(.*)$"
    for ($index = 0; $index -lt $firstScreenLinesValue.Count; $index++) {
        $match = [regex]::Match(
            $firstScreenLinesValue[$index],
            $fieldPattern,
            [System.Text.RegularExpressions.RegexOptions]::IgnoreCase
        )
        if (-not $match.Success) {
            continue
        }

        $fieldLines = New-Object System.Collections.Generic.List[string]
        $fieldLines.Add($match.Groups[1].Value.Trim())

        for ($nextIndex = $index + 1; $nextIndex -lt $firstScreenLinesValue.Count; $nextIndex++) {
            $line = $firstScreenLinesValue[$nextIndex]
            if ($line -match "^\S[^:]*:\s*") {
                break
            }

            if ($line -match "^\s+\S") {
                $fieldLines.Add($line.Trim())
                continue
            }

            break
        }

        return ($fieldLines -join " ").Trim()
    }

    return $null
}

function Test-FirstScreenField {
    param(
        [string]$Name,
        [string]$FieldName,
        [switch]$RequireValue
    )

    $value = Get-FirstScreenField -FieldName $FieldName
    if ($null -eq $value) {
        $problems.Add("missing $Name in first $FirstScreenLines lines")
        return
    }

    if ($RequireValue -and [string]::IsNullOrWhiteSpace($value)) {
        $problems.Add("missing $Name value in first $FirstScreenLines lines")
        return
    }

    if (-not $AllowPlaceholders -and $value -match "(?i)<[^>]+>|\b(todo|tbd|fixme|replace me)\b") {
        $problems.Add("placeholder $Name value in first $FirstScreenLines lines")
    }
}

function Test-Pattern {
    param(
        [string]$Name,
        [string]$Pattern,
        [switch]$FirstScreenOnly
    )

    $haystack = if ($FirstScreenOnly) { $firstScreen } else { $text }
    if ($haystack -notmatch $Pattern) {
        $location = if ($FirstScreenOnly) { "first $FirstScreenLines lines" } else { "handoff" }
        $problems.Add("missing $Name in $location")
    }
}

Test-FirstScreenField -Name "objective" -FieldName "objective" -RequireValue
Test-FirstScreenField -Name "done means" -FieldName "done means" -RequireValue
Test-FirstScreenField -Name "runner owner" -FieldName "runner owner" -RequireValue
Test-FirstScreenField -Name "controller owner" -FieldName "controller owner" -RequireValue
Test-FirstScreenField -Name "current next action" -FieldName "current next action" -RequireValue
Test-FirstScreenField -Name "stop conditions" -FieldName "stop conditions" -RequireValue
Test-FirstScreenField -Name "validity contract" -FieldName "validity contract" -RequireValue
Test-FirstScreenField -Name "recovery stance" -FieldName "recovery stance"

$recoveryStance = Get-FirstScreenField -FieldName "recovery stance"
if ($null -ne $recoveryStance -and $recoveryStance -notmatch "(?is)invalid rows.*debug.*repair|debug.*repair.*invalid rows") {
    $problems.Add("missing debug-and-repair invalid row stance in recovery stance")
}
Test-Pattern -Name "smallest poisoned slice rule" -Pattern "(?is)smallest poisoned.*slice|pause only.*poisoned"
Test-Pattern -Name "healthy comparable work rule" -Pattern "(?is)healthy comparable work|unrelated comparable work|unaffected comparable"

$duplicateParagraphs = @(
    [regex]::Split($text.Trim(), "(\r?\n\s*){2,}") |
        ForEach-Object { $_.Trim() } |
        Where-Object { $_.Length -gt 80 } |
        Group-Object |
        Where-Object { $_.Count -gt 1 }
)
foreach ($duplicate in $duplicateParagraphs) {
    $sample = $duplicate.Name
    if ($sample.Length -gt 90) {
        $sample = $sample.Substring(0, 90)
    }
    $problems.Add("duplicate paragraph: $sample")
}

if (-not $AllowPlaceholders -and $text -match "(?i)<[^>]+>|\b(todo|tbd|fixme|replace me)\b") {
    $problems.Add("placeholder text appears in handoff")
}

$blockerContextPattern = "(?is)\bdebug\b|\brepair\b|\brerun\b|\brescore\b|\bretry\b|\breproduce\b|\bisolat(?:e|ion)\b|smallest poisoned"
$blockerParagraphs = @(
    [regex]::Split($text.Trim(), "(\r?\n\s*){2,}") |
        ForEach-Object { $_.Trim() } |
        Where-Object { $_ -match "(?i)\bblock(?:ed|er|ers|ing)?\b" }
)
foreach ($paragraph in $blockerParagraphs) {
    if ($paragraph -match $blockerContextPattern) {
        continue
    }

    $sample = $paragraph
    if ($sample.Length -gt 90) {
        $sample = $sample.Substring(0, 90)
    }
    $problems.Add("blocker language appears without local recovery or next-action context: $sample")
    break
}

if ($problems.Count -gt 0) {
    Write-Host "handoff check failed: $fullPath"
    foreach ($problem in $problems) {
        Write-Host "  $problem"
    }
    exit 1
}

Write-Host "handoff check: ok"
