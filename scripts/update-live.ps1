param(
    [string]$Remote = "origin",
    [string]$Branch = "main",
    [string]$CodexHome,
    [string]$AgentsHome
)

. "$PSScriptRoot\common.ps1"

$repoRoot = Get-RepoRoot
$liveHome = Get-CodexHome -CodexHome $CodexHome
$agentsHomePath = Get-AgentsHome -AgentsHome $AgentsHome

function Invoke-RepoGit {
    param([string[]]$Arguments)

    & git -C $repoRoot @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "git failed: git $($Arguments -join ' ')"
    }
}

function Get-RepoGitOutput {
    param([string[]]$Arguments)

    $output = & git -C $repoRoot @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "git failed: git $($Arguments -join ' ')"
    }
    if ($null -eq $output) {
        return @()
    }
    return @($output)
}

function Test-RepoGitRef {
    param([string]$Ref)

    & git -C $repoRoot rev-parse --verify --quiet $Ref *> $null
    return $LASTEXITCODE -eq 0
}

function Invoke-RepoScript {
    param(
        [string]$Path,
        [hashtable]$Arguments
    )

    $global:LASTEXITCODE = 0
    & $Path @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "script failed: $Path"
    }
}

function Assert-CleanWorktree {
    $status = @(Get-RepoGitOutput -Arguments @("status", "--porcelain"))
    if ($status.Count -eq 0) {
        return
    }

    Write-Host "working tree has local changes:"
    foreach ($line in $status) {
        Write-Host "  $line"
    }
    throw "refusing automated live update from a dirty checkout"
}

Write-Host "repo: $repoRoot"
Write-Host "remote: $Remote"
Write-Host "branch: $Branch"
Write-Host "codex: $liveHome"
Write-Host "agents: $agentsHomePath"
Write-Host ""

$remoteRef = "refs/remotes/$Remote/$Branch"

Assert-CleanWorktree
Invoke-RepoGit -Arguments @("fetch", $Remote, "+refs/heads/${Branch}:$remoteRef")

$currentBranch = (Get-RepoGitOutput -Arguments @("branch", "--show-current") | Select-Object -First 1)
if ($currentBranch -ne $Branch) {
    if (Test-RepoGitRef -Ref "refs/heads/$Branch") {
        Invoke-RepoGit -Arguments @("switch", "--no-overwrite-ignore", $Branch)
    }
    else {
        Invoke-RepoGit -Arguments @("switch", "--no-overwrite-ignore", "--track", "-c", $Branch, $remoteRef)
    }
}

Invoke-RepoGit -Arguments @("merge", "--ff-only", "--no-overwrite-ignore", $remoteRef)

$head = (Get-RepoGitOutput -Arguments @("rev-parse", "HEAD") | Select-Object -First 1)
$remoteHead = (Get-RepoGitOutput -Arguments @("rev-parse", $remoteRef) | Select-Object -First 1)
if ($head -ne $remoteHead) {
    throw "refusing to install because HEAD does not match $remoteRef"
}

$homeArgs = @{}
if ($CodexHome) {
    $homeArgs["CodexHome"] = $CodexHome
}
if ($AgentsHome) {
    $homeArgs["AgentsHome"] = $AgentsHome
}

$installArgs = @{} + $homeArgs
$installArgs["Apply"] = $true

$verifyArgs = @{} + $homeArgs
$verifyArgs["SkipCodexCommand"] = $true
$verifyArgs["RequireInSync"] = $true

Invoke-RepoScript -Path (Join-Path $PSScriptRoot "doctor.ps1") -Arguments $homeArgs
Invoke-RepoScript -Path (Join-Path $PSScriptRoot "install.ps1") -Arguments $installArgs
Invoke-RepoScript -Path (Join-Path $PSScriptRoot "verify-live.ps1") -Arguments $verifyArgs

Write-Host ""
Write-Host "live portable config is up to date"
