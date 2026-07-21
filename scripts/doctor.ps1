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

    # Doctor checks are discovered from disk so the check roster has a single
    # source: the files under scripts/doctor/checks. The expected count is a
    # parity baseline that turns an accidental deletion into a doctor failure;
    # bump it when adding or removing a check.
    $checksRoot = Join-Path $doctorRoot "checks"
    $expectedDoctorCheckCount = 14
    $doctorCheckFiles = @(Get-ChildItem -LiteralPath $checksRoot -File -Filter "*.ps1" | Sort-Object Name)
    if ($doctorCheckFiles.Count -ne $expectedDoctorCheckCount) {
        $problems.Add("doctor check count is $($doctorCheckFiles.Count), expected $expectedDoctorCheckCount")
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
