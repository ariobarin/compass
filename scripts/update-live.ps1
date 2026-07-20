param(
    [string]$Remote = "origin",
    [Alias("Branch")]
    [string]$Ref = "main",
    [string]$CodexHome,
    [string]$AgentsHome,
    [string]$ClaudeHome
)

. "$PSScriptRoot\common.ps1"

$repoRoot = Get-RepoRoot
$liveHome = Get-CodexHome -CodexHome $CodexHome
$agentsHomePath = Get-AgentsHome -AgentsHome $AgentsHome
$claudeHomePath = Get-ClaudeHome -ClaudeHome $ClaudeHome

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
    param([string]$GitRef)

    & git -C $repoRoot rev-parse --verify --quiet $GitRef *> $null
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

if ([string]::IsNullOrWhiteSpace($Ref)) {
    throw "update ref must be non-empty"
}

Write-Host "repo: $repoRoot"
Write-Host "remote: $Remote"
Write-Host "ref: $Ref"
Write-Host "codex: $liveHome"
Write-Host "agents: $agentsHomePath"
Write-Host "claude: $claudeHomePath"
Write-Host ""

Assert-CleanWorktree
Invoke-RepoGit -Arguments @("fetch", "--prune", "--tags", "--prune-tags", $Remote)

$remoteBranchRef = "refs/remotes/$Remote/$Ref"
$tagRef = "refs/tags/$Ref"
$targetRef = $null
$branchUpdate = $false

if (Test-RepoGitRef -GitRef "${remoteBranchRef}^{commit}") {
    $targetRef = $remoteBranchRef
    $branchUpdate = $true
}
elseif (Test-RepoGitRef -GitRef "${tagRef}^{commit}") {
    $targetRef = $tagRef
}
elseif (Test-RepoGitRef -GitRef "${Ref}^{commit}") {
    $targetRef = $Ref
}
else {
    Invoke-RepoGit -Arguments @("fetch", $Remote, $Ref)
    if (-not (Test-RepoGitRef -GitRef "FETCH_HEAD^{commit}")) {
        throw "could not resolve update ref from ${Remote}: $Ref"
    }
    $targetRef = "FETCH_HEAD"
}

$resolvedCommit = (Get-RepoGitOutput -Arguments @("rev-parse", "${targetRef}^{commit}") | Select-Object -First 1)
if (-not $resolvedCommit) {
    throw "could not resolve update commit for $Ref"
}

if ($branchUpdate) {
    $currentBranch = (Get-RepoGitOutput -Arguments @("branch", "--show-current") | Select-Object -First 1)
    if ($currentBranch -ne $Ref) {
        if (Test-RepoGitRef -GitRef "refs/heads/$Ref") {
            Invoke-RepoGit -Arguments @("switch", "--no-overwrite-ignore", $Ref)
        }
        else {
            Invoke-RepoGit -Arguments @("switch", "--no-overwrite-ignore", "--track", "-c", $Ref, $remoteBranchRef)
        }
    }
    Invoke-RepoGit -Arguments @("merge", "--ff-only", "--no-overwrite-ignore", $remoteBranchRef)
}
else {
    Invoke-RepoGit -Arguments @("switch", "--detach", $resolvedCommit)
}

$head = (Get-RepoGitOutput -Arguments @("rev-parse", "HEAD") | Select-Object -First 1)
if ($head -ne $resolvedCommit) {
    throw "refusing to install because HEAD does not match resolved ref $Ref"
}

Write-Host "resolved commit: $resolvedCommit"
Write-Host ""

$homeArgs = @{}
if ($CodexHome) {
    $homeArgs["CodexHome"] = $CodexHome
}
if ($AgentsHome) {
    $homeArgs["AgentsHome"] = $AgentsHome
}
if ($ClaudeHome) {
    $homeArgs["ClaudeHome"] = $ClaudeHome
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
Write-Host "source ref: $Ref"
Write-Host "source commit: $resolvedCommit"
Write-Host "live portable config is up to date"
