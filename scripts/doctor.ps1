param(
    [string]$CodexHome,
    [string]$AgentsHome,
    [string]$ClaudeHome
)

. "$PSScriptRoot\common.ps1"

$repoRoot = Get-RepoRoot
try {
    $liveHome = Get-CodexHome -CodexHome $CodexHome
}
catch {
    $liveHome = Join-Path $env:USERPROFILE ".codex"
}
try {
    $agentsHomePath = Get-AgentsHome -AgentsHome $AgentsHome
}
catch {
    $agentsHomePath = Join-Path $HOME ".agents"
}

try {
    $claudeHomePath = Get-ClaudeHome -ClaudeHome $ClaudeHome
}
catch {
    $claudeHomePath = Join-Path $HOME ".claude"
}

$problems = New-Object System.Collections.Generic.List[string]
$trackedFiles = @()
$doctorRoot = Join-Path $PSScriptRoot "doctor"
$doctorCommonPath = Join-Path $doctorRoot "common.ps1"

if (-not (Test-Path -LiteralPath $doctorCommonPath)) {
    $problems.Add("missing doctor helper module")
}
else {
    . $doctorCommonPath

    # Doctor checks are discovered from disk and their identities are bound to
    # one manifest so a rename, replacement, addition, or deletion fails here.
    $checksRoot = Join-Path $doctorRoot "checks"
    $checkManifestPath = Join-Path $repoRoot "manifests\doctor-checks.json"
    $doctorCheckFiles = @(Get-ChildItem -LiteralPath $checksRoot -File -Filter "*.ps1" | Sort-Object Name)
    $actualDoctorChecks = @($doctorCheckFiles | ForEach-Object { $_.Name })
    $expectedDoctorChecks = @()

    if (-not (Test-Path -LiteralPath $checkManifestPath -PathType Leaf)) {
        $problems.Add("missing doctor check manifest")
    }
    else {
        try {
            $checkManifest = Get-Content -LiteralPath $checkManifestPath -Raw | ConvertFrom-Json
            if ($checkManifest.schema_version -ne 1) {
                $problems.Add("doctor check manifest requires schema_version 1")
            }
            $expectedDoctorChecks = @($checkManifest.checks)
            if ($expectedDoctorChecks.Count -eq 0) {
                $problems.Add("doctor check manifest requires a non-empty checks array")
            }
            elseif (@($expectedDoctorChecks | Where-Object {
                $_ -isnot [string] -or $_ -notmatch "^[A-Za-z0-9][A-Za-z0-9.-]*\.ps1$"
            }).Count -gt 0) {
                $problems.Add("doctor check manifest contains an invalid identity")
            }
            elseif (@($expectedDoctorChecks | Sort-Object -Unique).Count -ne $expectedDoctorChecks.Count) {
                $problems.Add("doctor check manifest contains duplicate identities")
            }
        }
        catch {
            $problems.Add("invalid doctor check manifest: $($_.Exception.Message)")
        }
    }

    foreach ($missingCheck in @($expectedDoctorChecks | Where-Object { $actualDoctorChecks -notcontains $_ })) {
        $problems.Add("missing doctor check: $missingCheck")
    }
    foreach ($unexpectedCheck in @($actualDoctorChecks | Where-Object { $expectedDoctorChecks -notcontains $_ })) {
        $problems.Add("unexpected doctor check: $unexpectedCheck")
    }
    foreach ($checkFile in $doctorCheckFiles) {
        . $checkFile.FullName
    }
}

Write-Host "repo: $repoRoot"
Write-Host "codex: $liveHome"
Write-Host "agents: $agentsHomePath"
Write-Host "claude: $claudeHomePath"

if ($problems.Count -gt 0) {
    Write-Host ""
    Write-Host "problems:"
    foreach ($problem in $problems) {
        Write-Host "  $problem"
    }
    exit 1
}

Write-Host "doctor: ok"
