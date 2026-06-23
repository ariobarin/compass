param(
    [Parameter(Mandatory = $true)]
    [string]$Path,

    [int]$FirstScreenLines = 25
)

$fullPath = [System.IO.Path]::GetFullPath($Path)
if (-not (Test-Path -LiteralPath $fullPath)) {
    Write-Host "missing handoff: $fullPath"
    exit 1
}

$text = Get-Content -Raw -Encoding UTF8 -LiteralPath $fullPath
$lines = @($text -split "`r?`n")
$firstScreen = ($lines | Select-Object -First $FirstScreenLines) -join "`n"
$problems = New-Object System.Collections.Generic.List[string]

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

Test-Pattern -Name "objective" -Pattern "(?im)^\s*objective\s*:" -FirstScreenOnly
Test-Pattern -Name "done means" -Pattern "(?im)^\s*done means\s*:" -FirstScreenOnly
Test-Pattern -Name "runner owner" -Pattern "(?im)^\s*runner owner\s*:" -FirstScreenOnly
Test-Pattern -Name "controller owner" -Pattern "(?im)^\s*controller owner\s*:" -FirstScreenOnly
Test-Pattern -Name "current next action" -Pattern "(?im)^\s*current next action\s*:" -FirstScreenOnly
Test-Pattern -Name "stop conditions" -Pattern "(?im)^\s*stop conditions\s*:" -FirstScreenOnly
Test-Pattern -Name "validity contract" -Pattern "(?im)^\s*validity contract\s*:" -FirstScreenOnly
Test-Pattern -Name "recovery stance" -Pattern "(?im)^\s*recovery stance\s*:" -FirstScreenOnly

Test-Pattern -Name "debug-and-repair invalid row stance" -Pattern "(?is)invalid rows.*debug.*repair|debug.*repair.*invalid rows"
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

if ($text -match "(?i)\bblock(?:ed|er|ers|ing)?\b" -and $text -notmatch "(?is)recovery|rerun|rescore|debug|repair|next action") {
    $problems.Add("blocker language appears without recovery or next-action language")
}

if ($problems.Count -gt 0) {
    Write-Host "handoff check failed: $fullPath"
    foreach ($problem in $problems) {
        Write-Host "  $problem"
    }
    exit 1
}

Write-Host "handoff check: ok"
