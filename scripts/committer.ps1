<#
.SYNOPSIS
Previews or creates one exact-scope Compass commit from explicit paths.

.EXAMPLE
./scripts/committer.ps1 "add command dispatcher" scripts/compass.ps1 scripts/README.md

.EXAMPLE
./scripts/committer.ps1 -Apply "add command dispatcher" scripts/compass.ps1 scripts/README.md
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$Subject,

    [Parameter(Mandatory = $true, Position = 1, ValueFromRemainingArguments = $true)]
    [string[]]$Paths,

    [switch]$Apply,
    [switch]$SkipDoctor
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$pathTrimChars = @([System.IO.Path]::DirectorySeparatorChar, [System.IO.Path]::AltDirectorySeparatorChar) | Select-Object -Unique

function Invoke-RepoGit {
    param(
        [string]$RepoRoot,
        [string[]]$Arguments
    )

    $output = & git -C $RepoRoot @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "git failed: git $($Arguments -join ' ')"
    }
    return @($output)
}

function Test-GitPathCovered {
    param(
        [string]$Candidate,
        [string[]]$AllowedPaths
    )

    $candidatePath = $Candidate.Replace("\", "/").Trim("/")
    foreach ($allowed in $AllowedPaths) {
        $allowedPath = $allowed.Replace("\", "/").Trim("/")
        if ($candidatePath.Equals($allowedPath, [System.StringComparison]::OrdinalIgnoreCase)) {
            return $true
        }
        if ($candidatePath.StartsWith("$allowedPath/", [System.StringComparison]::OrdinalIgnoreCase)) {
            return $true
        }
    }
    return $false
}

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw "git is not on PATH"
}

if ($Subject -ne $Subject.Trim()) {
    throw "commit subject must not have leading or trailing whitespace"
}
if ($Subject -match "[\r\n]") {
    throw "commit subject must be one line"
}
if ($Subject -notmatch "^[a-z0-9]") {
    throw "commit subject must start with a lowercase letter or number"
}
if ($Subject -cne $Subject.ToLowerInvariant()) {
    throw "commit subject must be lowercase"
}
if ($Subject -match "[^\p{L}\p{N}]$") {
    throw "commit subject must not end with punctuation"
}
if ($Subject -match "[\u2013\u2014]") {
    throw "commit subject must use ASCII punctuation"
}
if ($Subject -match "(?i)co-authored-by") {
    throw "commit subject must not contain a co-author trailer"
}
if ($Subject.Length -gt 72) {
    throw "commit subject must be 72 characters or fewer"
}
if (([regex]::Matches($Subject, "\S+")).Count -gt 8) {
    throw "commit subject must be around eight words or fewer"
}

$repoRoot = (Invoke-RepoGit -RepoRoot (Get-Location).Path -Arguments @("rev-parse", "--show-toplevel") | Select-Object -First 1)
if (-not $repoRoot) {
    throw "could not resolve repository root"
}
$repoRoot = [System.IO.Path]::GetFullPath($repoRoot).TrimEnd($pathTrimChars)

$normalizedPaths = New-Object System.Collections.Generic.List[string]
$seenPaths = New-Object 'System.Collections.Generic.HashSet[string]' ([System.StringComparer]::OrdinalIgnoreCase)
foreach ($path in $Paths) {
    if ([string]::IsNullOrWhiteSpace($path)) {
        throw "commit paths must be non-empty"
    }

    $candidate = $path.Trim()
    if ($candidate -in @(".", "./", ".\")) {
        throw "refusing repository-wide path: $path"
    }

    $fullPath = if ([System.IO.Path]::IsPathRooted($candidate)) {
        [System.IO.Path]::GetFullPath($candidate)
    }
    else {
        [System.IO.Path]::GetFullPath((Join-Path $repoRoot $candidate))
    }

    $rootPrefix = "$repoRoot$([System.IO.Path]::DirectorySeparatorChar)"
    $altRootPrefix = "$repoRoot$([System.IO.Path]::AltDirectorySeparatorChar)"
    if ($fullPath.Equals($repoRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "refusing repository-wide path: $path"
    }
    if (-not $fullPath.StartsWith($rootPrefix, [System.StringComparison]::OrdinalIgnoreCase) -and
        -not $fullPath.StartsWith($altRootPrefix, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "refusing path outside repository: $path"
    }

    $relativePath = $fullPath.Substring($repoRoot.Length).TrimStart($pathTrimChars).Replace("\", "/")
    if ($relativePath -eq ".git" -or $relativePath.StartsWith(".git/", [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "refusing git metadata path: $path"
    }

    if ($seenPaths.Add($relativePath)) {
        $normalizedPaths.Add($relativePath)
    }
}

if ($normalizedPaths.Count -eq 0) {
    throw "provide at least one explicit path"
}

$literalPathspecs = @($normalizedPaths | ForEach-Object { ":(literal)$_" })
$status = @(Invoke-RepoGit -RepoRoot $repoRoot -Arguments (@("status", "--short", "--") + $literalPathspecs))
if ($status.Count -eq 0) {
    throw "no changes found in the requested paths"
}

Write-Host "repo: $repoRoot"
Write-Host "subject: $Subject"
Write-Host "paths:"
foreach ($path in $normalizedPaths) {
    Write-Host "  $path"
}
Write-Host ""
Write-Host "changes:"
$status | ForEach-Object { Write-Host "  $_" }

if (-not $Apply) {
    Write-Host ""
    Write-Host "review mode: index and history were not changed"
    Write-Host "run again with -Apply to validate, stage exactly these paths, and commit"
    exit 0
}

$stagedBefore = @(Invoke-RepoGit -RepoRoot $repoRoot -Arguments @("diff", "--cached", "--name-only", "--"))
$unrelatedStaged = @($stagedBefore | Where-Object { -not (Test-GitPathCovered -Candidate $_ -AllowedPaths @($normalizedPaths)) })
if ($unrelatedStaged.Count -gt 0) {
    Write-Host "unrelated staged paths:"
    $unrelatedStaged | ForEach-Object { Write-Host "  $_" }
    throw "refusing to disturb unrelated staged work"
}

if (-not $SkipDoctor) {
    $doctorPath = Join-Path $repoRoot "scripts\doctor.ps1"
    if (-not (Test-Path -LiteralPath $doctorPath)) {
        throw "missing doctor script: $doctorPath"
    }
    & $doctorPath
    if ($LASTEXITCODE -ne 0) {
        throw "doctor failed"
    }
}

[void](Invoke-RepoGit -RepoRoot $repoRoot -Arguments @("reset", "--quiet"))
[void](Invoke-RepoGit -RepoRoot $repoRoot -Arguments (@("add", "-A", "--") + $literalPathspecs))

$stagedAfter = @(Invoke-RepoGit -RepoRoot $repoRoot -Arguments @("diff", "--cached", "--name-only", "--"))
if ($stagedAfter.Count -eq 0) {
    throw "requested paths produced no staged changes"
}

$unexpected = @($stagedAfter | Where-Object { -not (Test-GitPathCovered -Candidate $_ -AllowedPaths @($normalizedPaths)) })
if ($unexpected.Count -gt 0) {
    throw "staged paths escaped requested scope: $($unexpected -join ', ')"
}

Write-Host ""
Write-Host "staged:"
Invoke-RepoGit -RepoRoot $repoRoot -Arguments @("diff", "--cached", "--name-status", "--") |
    ForEach-Object { Write-Host "  $_" }
Write-Host ""
Invoke-RepoGit -RepoRoot $repoRoot -Arguments @("diff", "--cached", "--stat", "--") |
    ForEach-Object { Write-Host $_ }

[void](Invoke-RepoGit -RepoRoot $repoRoot -Arguments @("commit", "-m", $Subject))