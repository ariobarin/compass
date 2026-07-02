param(
    [string]$CodexHome,
    [string]$AgentsHome,
    [switch]$SkipCodexCommand,
    [switch]$RequireInSync,
    [int]$TimeoutSeconds = 180
)

. "$PSScriptRoot\common.ps1"

$repoRoot = Get-RepoRoot
$liveHome = Get-CodexHome -CodexHome $CodexHome
$agentsHome = Get-AgentsHome -AgentsHome $AgentsHome
$items = Get-PortableFileMap -RepoRoot $repoRoot -CodexHome $liveHome -AgentsHome $agentsHome
$retiredItems = Get-RetiredPortableFileMap -CodexHome $liveHome -AgentsHome $agentsHome
$drift = New-Object System.Collections.Generic.List[string]
$missing = New-Object System.Collections.Generic.List[string]
$retired = New-Object System.Collections.Generic.List[string]

function Get-RelativeFileMap {
    param([string]$Root)

    $map = @{}
    if (-not (Test-Path $Root)) {
        return $map
    }

    foreach ($file in Get-ChildItem -LiteralPath $Root -Recurse -File -Force) {
        $relative = $file.FullName.Substring((Resolve-Path $Root).Path.Length).TrimStart("\")
        $map[$relative] = (Get-FileHash -Algorithm SHA256 -LiteralPath $file.FullName).Hash
    }
    return $map
}

foreach ($item in $items) {
    if (-not (Test-Path $item.LivePath)) {
        $missing.Add($item.LivePath)
        continue
    }

    if (-not (Test-Path $item.RepoPath)) {
        $missing.Add($item.RepoPath)
        continue
    }

    if ($item.Type -eq "file") {
        $repoHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $item.RepoPath).Hash
        $liveHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $item.LivePath).Hash
        if ($repoHash -ne $liveHash) {
            $drift.Add($item.LivePath)
        }
        continue
    }

    $repoMap = Get-RelativeFileMap -Root $item.RepoPath
    $liveMap = Get-RelativeFileMap -Root $item.LivePath
    $allKeys = @(@($repoMap.Keys) + @($liveMap.Keys) | Sort-Object -Unique)
    foreach ($key in $allKeys) {
        if (-not $repoMap.ContainsKey($key) -or -not $liveMap.ContainsKey($key) -or $repoMap[$key] -ne $liveMap[$key]) {
            $drift.Add((Join-Path $item.LivePath $key))
        }
    }
}

foreach ($item in $retiredItems) {
    if (Test-Path $item.LivePath) {
        $retired.Add($item.LivePath)
    }
}

Write-Host "repo: $repoRoot"
Write-Host "codex: $liveHome"
Write-Host "agents: $agentsHome"

if ($missing.Count -gt 0) {
    Write-Host ""
    Write-Host "missing:"
    foreach ($path in $missing) {
        Write-Host "  $path"
    }
}

if ($drift.Count -gt 0) {
    Write-Host ""
    Write-Host "drift:"
    foreach ($path in $drift) {
        Write-Host "  $path"
    }
}
if ($retired.Count -gt 0) {
    Write-Host ""
    Write-Host "retired portable copies:"
    foreach ($path in $retired) {
        Write-Host "  $path"
    }
}
elseif ($missing.Count -eq 0 -and $drift.Count -eq 0) {
    Write-Host "portable files match live allowlist"
}

if ($RequireInSync -and ($missing.Count -gt 0 -or $drift.Count -gt 0 -or $retired.Count -gt 0)) {
    exit 1
}

if ($SkipCodexCommand) {
    Write-Host ""
    Write-Host "codex instruction check skipped"
    exit 0
}

if (-not (Get-Command codex -ErrorAction SilentlyContinue)) {
    Write-Host ""
    Write-Host "codex command not found; file drift check completed"
    exit 0
}

$outputFile = [System.IO.Path]::GetTempFileName()
$logFile = [System.IO.Path]::GetTempFileName()
$prompt = @"
Report the active instruction sources you can infer for this run.
Include whether global AGENTS.md and repository AGENTS.md were loaded.
Do not modify files or run shell commands.
"@

Write-Host ""
Write-Host "running read-only Codex instruction check"

$job = Start-Job -ScriptBlock {
    param($RepoRoot, $OutputFile, $Prompt, $LogFile)
    codex -c approval_policy='"never"' -c model_reasoning_effort='"low"' --sandbox read-only exec --cd $RepoRoot --ephemeral --output-last-message $OutputFile $Prompt *> $LogFile
    [pscustomobject]@{
        ExitCode = $LASTEXITCODE
    }
} -ArgumentList $repoRoot, $outputFile, $prompt, $logFile

$completed = Wait-Job $job -Timeout $TimeoutSeconds
if (-not $completed) {
    Stop-Job $job | Out-Null
    if (Test-Path $logFile) {
        Get-Content -Raw -LiteralPath $logFile | Write-Host
    }
    Receive-Job $job -ErrorAction SilentlyContinue | Out-String | Write-Host
    Remove-Job $job | Out-Null
    throw "codex instruction check timed out"
}

$jobResult = Receive-Job $job -ErrorAction SilentlyContinue -ErrorVariable jobErrors
Remove-Job $job | Out-Null

if ($jobResult.ExitCode -ne 0 -or $jobErrors) {
    if (Test-Path $logFile) {
        Get-Content -Raw -LiteralPath $logFile | Write-Host
    }
    foreach ($errorRecord in $jobErrors) {
        Write-Host $errorRecord.ToString()
    }
    throw "codex instruction check failed"
}

Write-Host ""
Write-Host "codex final message:"
if (-not (Test-Path $outputFile)) {
    throw "codex did not write an output message"
}
Get-Content -Raw -LiteralPath $outputFile
Remove-Item -LiteralPath $outputFile -Force
Remove-Item -LiteralPath $logFile -Force
