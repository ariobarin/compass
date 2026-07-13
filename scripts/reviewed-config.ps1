Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-ReviewedConfigContract {
    param(
        [Parameter(Mandatory)]
        [string]$RepoRoot,
        [Parameter(Mandatory)]
        [string]$CodexHome
    )

    $manifest = (Get-PortableGeneratedData).manifest
    $config = Get-PortableJsonProperty -Object $manifest -Name "config"
    $reviewFile = [string](Get-PortableJsonProperty -Object $config -Name "review_file")
    $installMode = [string](Get-PortableJsonProperty -Object $config -Name "install_mode")
    if (-not $reviewFile) {
        throw "portable manifest is missing [config].review_file"
    }
    if ($installMode -ne "overlay") {
        throw "portable manifest [config].install_mode must be overlay"
    }

    return [pscustomobject]@{
        ReviewPath = Join-Path (Join-Path $RepoRoot "codex") $reviewFile
        LivePath = Join-Path $CodexHome "config.toml"
    }
}

function Get-ReviewedConfigState {
    param(
        [Parameter(Mandatory)]
        [string]$ReviewPath,
        [Parameter(Mandatory)]
        [string]$LivePath
    )

    $toolPath = Join-Path $PSScriptRoot "reviewed-config.py"
    if (-not (Test-Path -LiteralPath $toolPath -PathType Leaf)) {
        throw "missing reviewed config helper: $toolPath"
    }

    $runner = Get-PortablePythonRunner
    $arguments = @($runner.Prefix) + @(
        $toolPath,
        "--reviewed-config", $ReviewPath,
        "--live-config", $LivePath
    )
    $previousPythonIoEncoding = $env:PYTHONIOENCODING
    $previousOutputEncoding = [Console]::OutputEncoding

    try {
        $env:PYTHONIOENCODING = "utf-8"
        [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
        $output = @(& $runner.Command @arguments 2>&1)
        $exitCode = $LASTEXITCODE
    }
    finally {
        $env:PYTHONIOENCODING = $previousPythonIoEncoding
        [Console]::OutputEncoding = $previousOutputEncoding
    }

    if ($exitCode -ne 0) {
        $message = @($output | ForEach-Object { $_.ToString() }) -join "`n"
        throw "reviewed config helper failed: $message"
    }

    try {
        $state = (@($output | ForEach-Object { $_.ToString() }) -join "`n") | ConvertFrom-Json
    }
    catch {
        throw "reviewed config helper returned invalid JSON: $($_.Exception.Message)"
    }

    if ($state.schema_version -ne 1) {
        throw "unsupported reviewed config state schema version"
    }
    return $state
}

function Write-ReviewedConfigAtomically {
    param(
        [Parameter(Mandatory)]
        [string]$Path,
        [Parameter(Mandatory)]
        [AllowEmptyString()]
        [string]$Text
    )

    New-DirectoryForFile -Path $Path
    $directory = Split-Path -Parent $Path
    $name = Split-Path -Leaf $Path
    $tempPath = Join-Path $directory ".$name.$([guid]::NewGuid().ToString('N')).tmp"
    try {
        [System.IO.File]::WriteAllText($tempPath, $Text, [System.Text.UTF8Encoding]::new($false))
        [System.IO.File]::Move($tempPath, $Path, $true)
    }
    finally {
        if (Test-Path -LiteralPath $tempPath) {
            Remove-Item -LiteralPath $tempPath -Force
        }
    }
}

function Get-ReviewedConfigProblemStrings {
    param(
        [Parameter(Mandatory)]
        [object]$State
    )

    foreach ($change in @($State.changes)) {
        if ($change.kind -eq "missing") {
            "missing reviewed config key: $($change.path), expected $($change.expected)"
        }
        else {
            "reviewed config mismatch: $($change.path) = $($change.actual), expected $($change.expected)"
        }
    }
}
