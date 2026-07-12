<#
.SYNOPSIS
Runs Compass maintenance commands through one stable entry point.

.EXAMPLE
./scripts/compass.ps1 status

.EXAMPLE
./scripts/compass.ps1 skills -ProjectPath . -Json

.EXAMPLE
./scripts/compass.ps1 skills-audit -ProjectPath . -NoLive -Json

.EXAMPLE
./scripts/compass.ps1 orchestration -Plain

.EXAMPLE
./scripts/compass.ps1 install -Apply

.EXAMPLE
./scripts/compass.ps1 update -Ref v2026.07.10

.EXAMPLE
./scripts/compass.ps1 verify -SkipCodexCommand -RequireInSync
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [ValidateSet("status", "skills", "skills-audit", "orchestration", "doctor", "diff", "install", "snapshot", "verify", "update")]
    [string]$Command,

    [switch]$Apply,
    [switch]$Json,
    [switch]$Plain,
    [switch]$Check,
    [switch]$NoLive,
    [switch]$RequireInSync,
    [switch]$SkipCodexCommand,
    [string]$CodexHome,
    [string]$AgentsHome,
    [string]$ClaudeHome,
    [string]$ProjectPath,
    [string[]]$AdditionalSkillRoot,
    [string]$Ledger,
    [string]$GoalId,
    [string]$Remote = "origin",
    [Alias("Branch")]
    [string]$Ref = "main"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

. "$PSScriptRoot\common.ps1"

function Get-HomeArguments {
    $arguments = @{}
    if ($CodexHome) {
        $arguments["CodexHome"] = $CodexHome
    }
    if ($AgentsHome) {
        $arguments["AgentsHome"] = $AgentsHome
    }
    if ($ClaudeHome) {
        $arguments["ClaudeHome"] = $ClaudeHome
    }
    return $arguments
}

function Invoke-CompassScript {
    param(
        [string]$Name,
        [hashtable]$Arguments
    )

    $path = Join-Path $PSScriptRoot $Name
    if (-not (Test-Path -LiteralPath $path)) {
        throw "missing Compass command script: $path"
    }

    & $path @Arguments
    exit 0
}

function Get-RepoCommit {
    if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
        return $null
    }

    $commit = & git -C (Get-RepoRoot) rev-parse HEAD 2>$null | Select-Object -First 1
    if ($LASTEXITCODE -ne 0) {
        return $null
    }

    return $commit
}

function Get-PowerShellProcessPath {
    $process = Get-Process -Id $PID
    if (-not $process.Path) {
        throw "could not resolve the current PowerShell executable"
    }
    return $process.Path
}

function Get-LiveStatus {
    $repoRoot = Get-RepoRoot
    $liveHome = Get-CodexHome -CodexHome $CodexHome
    $agentsHomePath = Get-AgentsHome -AgentsHome $AgentsHome
    $claudeHomePath = Get-ClaudeHome -ClaudeHome $ClaudeHome
    $verifyPath = Join-Path $PSScriptRoot "verify-live.ps1"
    $processArguments = @("-NoProfile")
    if ($env:OS -eq "Windows_NT") {
        $processArguments += @("-ExecutionPolicy", "Bypass")
    }
    $processArguments += @(
        "-File", $verifyPath,
        "-SkipCodexCommand",
        "-RequireInSync",
        "-CodexHome", $liveHome,
        "-AgentsHome", $agentsHomePath,
        "-ClaudeHome", $claudeHomePath
    )

    $powerShellPath = Get-PowerShellProcessPath
    $verifyOutput = @(& $powerShellPath @processArguments 2>&1 | ForEach-Object { $_.ToString() })
    $verifyExitCode = $LASTEXITCODE
    $inSync = $verifyExitCode -eq 0

    $nextCommand = "none"
    if (-not $inSync) {
        $nextCommand = ".\scripts\compass.ps1 diff"
    }

    return [ordered]@{
        schema_version = 1
        repo = $repoRoot
        commit = (Get-RepoCommit)
        codex_home = $liveHome
        agents_home = $agentsHomePath
        claude_home = $claudeHomePath
        in_sync = $inSync
        verify_exit_code = $verifyExitCode
        next_command = $nextCommand
        verify_output = $verifyOutput
    }
}

if (($Json -or $Plain) -and $Command -notin @("status", "skills", "skills-audit", "orchestration")) {
    throw "-Json and -Plain are supported only by status, skills, skills-audit, and orchestration"
}
if ($Json -and $Plain) {
    throw "choose either -Json or -Plain"
}
if ($Apply -and $Command -notin @("install", "snapshot")) {
    throw "-Apply is supported only by install and snapshot"
}
if (($Check -or $NoLive) -and $Command -ne "skills-audit") {
    throw "-Check and -NoLive are supported only by skills-audit"
}
if (($RequireInSync -or $SkipCodexCommand) -and $Command -notin @("status", "verify")) {
    throw "-RequireInSync and -SkipCodexCommand are supported only by status and verify"
}
if (($ProjectPath -or $AdditionalSkillRoot) -and $Command -notin @("skills", "skills-audit")) {
    throw "-ProjectPath and -AdditionalSkillRoot are supported only by skills and skills-audit"
}
if (($Ledger -or $GoalId) -and $Command -ne "orchestration") {
    throw "-Ledger and -GoalId are supported only by orchestration"
}

$homeArguments = Get-HomeArguments

switch ($Command) {
    "status" {
        $status = Get-LiveStatus
        if ($Json) {
            $status | ConvertTo-Json -Depth 5
        }
        elseif ($Plain) {
            Write-Output "repo=$($status.repo)"
            Write-Output "commit=$($status.commit)"
            Write-Output "codex_home=$($status.codex_home)"
            Write-Output "agents_home=$($status.agents_home)"
            Write-Output "claude_home=$($status.claude_home)"
            Write-Output "in_sync=$($status.in_sync.ToString().ToLowerInvariant())"
            Write-Output "verify_exit_code=$($status.verify_exit_code)"
            Write-Output "next_command=$($status.next_command)"
        }
        else {
            Write-Host "repo: $($status.repo)"
            Write-Host "commit: $($status.commit)"
            Write-Host "codex: $($status.codex_home)"
            Write-Host "agents: $($status.agents_home)"
            Write-Host "claude: $($status.claude_home)"
            Write-Host "live: $(if ($status.in_sync) { 'in sync' } else { 'drift detected' })"
            Write-Host "next: $($status.next_command)"
            if (-not $status.in_sync -and $status.verify_output.Count -gt 0) {
                Write-Host ""
                $status.verify_output | ForEach-Object { Write-Host $_ }
            }
        }

        if ($RequireInSync -and -not $status.in_sync) {
            exit $status.verify_exit_code
        }
        exit 0
    }
    "skills" {
        $arguments = @{} + $homeArguments
        [void]$arguments.Remove("CodexHome")
        if ($ProjectPath) {
            $arguments["ProjectPath"] = $ProjectPath
        }
        if ($AdditionalSkillRoot) {
            $arguments["AdditionalSkillRoot"] = $AdditionalSkillRoot
        }
        if ($Json) {
            $arguments["Json"] = $true
        }
        if ($Plain) {
            $arguments["Plain"] = $true
        }
        Invoke-CompassScript -Name "skills-status.ps1" -Arguments $arguments
    }
    "skills-audit" {
        $arguments = @{}
        $skillRoots = New-Object System.Collections.Generic.List[string]
        if ($ProjectPath) {
            $projectRoot = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($ProjectPath)
            $skillRoots.Add("project-codex=$(Join-Path $projectRoot '.agents\skills')")
            $skillRoots.Add("project-claude=$(Join-Path $projectRoot '.claude\skills')")
        }
        foreach ($root in @($AdditionalSkillRoot)) {
            if ($root) {
                $skillRoots.Add($root)
            }
        }
        if ($skillRoots.Count -gt 0) {
            $arguments["SkillRoot"] = @($skillRoots.ToArray())
        }
        if ($Json) {
            $arguments["Json"] = $true
        }
        if ($Plain) {
            $arguments["Plain"] = $true
        }
        if ($Check) {
            $arguments["Check"] = $true
        }
        if ($NoLive) {
            $arguments["NoLive"] = $true
        }
        Invoke-CompassScript -Name "skills-audit.ps1" -Arguments $arguments
    }
    "orchestration" {
        $arguments = @{ Action = "status" }
        if ($Ledger) {
            $arguments["Ledger"] = $Ledger
        }
        if ($GoalId) {
            $arguments["GoalId"] = $GoalId
        }
        if ($Json) {
            $arguments["Json"] = $true
        }
        if ($Plain) {
            $arguments["Plain"] = $true
        }
        Invoke-CompassScript -Name "orchestration-ledger.ps1" -Arguments $arguments
    }
    "doctor" {
        Invoke-CompassScript -Name "doctor.ps1" -Arguments $homeArguments
    }
    "diff" {
        Invoke-CompassScript -Name "diff-live.ps1" -Arguments $homeArguments
    }
    "install" {
        $arguments = @{} + $homeArguments
        if ($Apply) {
            $arguments["Apply"] = $true
        }
        Invoke-CompassScript -Name "install.ps1" -Arguments $arguments
    }
    "snapshot" {
        $arguments = @{} + $homeArguments
        if ($Apply) {
            $arguments["Apply"] = $true
        }
        Invoke-CompassScript -Name "snapshot.ps1" -Arguments $arguments
    }
    "verify" {
        $arguments = @{} + $homeArguments
        if ($SkipCodexCommand) {
            $arguments["SkipCodexCommand"] = $true
        }
        if ($RequireInSync) {
            $arguments["RequireInSync"] = $true
        }
        Invoke-CompassScript -Name "verify-live.ps1" -Arguments $arguments
    }
    "update" {
        $arguments = @{} + $homeArguments
        $arguments["Remote"] = $Remote
        $arguments["Ref"] = $Ref
        Invoke-CompassScript -Name "update-live.ps1" -Arguments $arguments
    }
}
