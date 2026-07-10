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

    foreach ($checkPath in @(
        "checks\required-files.ps1",
        "checks\manifest-boundaries.ps1",
        "checks\text-policy.ps1",
        "checks\skills.ps1",
        "checks\agents.ps1",
        "checks\policy-contracts.ps1",
        "checks\restart-recovery.ps1",
        "checks\hooks.ps1",
        "checks\claude.ps1"
    )) {
        $fullCheckPath = Join-Path $doctorRoot $checkPath
        if (Test-Path -LiteralPath $fullCheckPath) {
            . $fullCheckPath
        }
        else {
            $problems.Add("missing doctor check module: $checkPath")
        }
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
