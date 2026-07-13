$textFiles = Get-DoctorChildItem -Kind File |
    Where-Object {
        $_.FullName -notmatch "\\.git\\" -and
        $_.Extension -in @(".md", ".toml", ".json", ".ps1", ".yaml", ".yml", ".txt")
    }

foreach ($file in $textFiles) {
    $content = Get-Content -Raw -Encoding UTF8 -LiteralPath $file.FullName
    if ($content -match "[^\x00-\x7F]") {
        $problems.Add("non-ASCII text in: $($file.FullName)")
    }
}

$dashCheckedExtensions = @(".md", ".toml", ".json", ".ps1", ".yaml", ".yml", ".txt", ".py", ".csv")
$dashCheckedFiles = Get-DoctorChildItem -Kind File |
    Where-Object {
        $_.FullName -notmatch "\\.git\\" -and
        $_.Extension -in $dashCheckedExtensions
    }
$blockedDashChars = @([char]0x2013, [char]0x2014)

foreach ($file in $dashCheckedFiles) {
    $content = Get-Content -Raw -Encoding UTF8 -LiteralPath $file.FullName
    foreach ($dashChar in $blockedDashChars) {
        if ($content.Contains($dashChar)) {
            $problems.Add("non-ASCII dash text in: $($file.FullName)")
            break
        }
    }
}

$powerShellFiles = Get-DoctorChildItem -Kind File -Filter "*.ps1"
foreach ($file in $powerShellFiles) {
    $parseTokens = $null
    $parseErrors = $null
    [System.Management.Automation.Language.Parser]::ParseFile(
        $file.FullName,
        [ref]$parseTokens,
        [ref]$parseErrors
    ) | Out-Null

    foreach ($parseError in @($parseErrors)) {
        $problems.Add("PowerShell parse error in $($file.FullName): $($parseError.Message)")
    }
}
