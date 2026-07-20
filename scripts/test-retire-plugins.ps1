[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$testRoot = Join-Path ([System.IO.Path]::GetTempPath()) "compass-retired-plugins-$([guid]::NewGuid().ToString('N'))"
$binRoot = Join-Path $testRoot "bin"
$codexHome = Join-Path $testRoot "codex"
$statePath = Join-Path $codexHome "retired-test-state.json"
$retireScript = Join-Path $PSScriptRoot "retire-plugins.ps1"
$powerShellPath = (Get-Process -Id $PID).Path
$originalPath = $env:PATH

function Invoke-Retirement {
    param(
        [string[]]$Arguments,
        [int]$ExpectedExitCode
    )

    $output = @(& $powerShellPath -NoProfile -File $retireScript -CodexHome $codexHome @Arguments 2>&1 | ForEach-Object { $_.ToString() })
    if ($LASTEXITCODE -ne $ExpectedExitCode) {
        throw "expected retirement exit $ExpectedExitCode, got $LASTEXITCODE`n$($output -join [Environment]::NewLine)"
    }
    return $output
}

try {
    New-Item -ItemType Directory -Force $binRoot, $codexHome | Out-Null
    $fakeCodex = @'
$statePath = Join-Path $env:CODEX_HOME "retired-test-state.json"
$state = Get-Content -Raw -LiteralPath $statePath | ConvertFrom-Json
$joined = $args -join " "
if ($joined -eq "plugin list --json") {
    $installed = @()
    if ($state.plugin) {
        $installed += [ordered]@{ pluginId = "which-llm@which-llm"; installed = $true }
    }
    [ordered]@{ installed = $installed; available = @() } | ConvertTo-Json -Depth 5
    exit 0
}
if ($joined -eq "plugin marketplace list --json") {
    $marketplaces = @()
    if ($state.marketplace) {
        $marketplaces += [ordered]@{ name = "which-llm"; root = "test" }
    }
    [ordered]@{ marketplaces = $marketplaces } | ConvertTo-Json -Depth 5
    exit 0
}
if ($args[0] -eq "plugin" -and $args[1] -eq "remove") {
    $state.plugin = $false
    $state | ConvertTo-Json | Set-Content -LiteralPath $statePath -Encoding utf8NoBOM
    [ordered]@{ removed = $true } | ConvertTo-Json
    exit 0
}
if ($joined -eq "plugin marketplace remove which-llm --json") {
    $state.marketplace = $false
    $state | ConvertTo-Json | Set-Content -LiteralPath $statePath -Encoding utf8NoBOM
    [ordered]@{ removed = $true } | ConvertTo-Json
    exit 0
}
Write-Error "unexpected fake codex arguments: $joined"
exit 1
'@
    [System.IO.File]::WriteAllText((Join-Path $binRoot "codex.ps1"), $fakeCodex, [System.Text.UTF8Encoding]::new($false))
    [System.IO.File]::WriteAllText($statePath, '{"plugin":true,"marketplace":true}', [System.Text.UTF8Encoding]::new($false))
    $env:PATH = "$binRoot$([System.IO.Path]::PathSeparator)$originalPath"

    $review = @(Invoke-Retirement -Arguments @() -ExpectedExitCode 0)
    if ($review -notcontains "retired plugin present: which-llm@which-llm") {
        throw "review did not report the retired plugin"
    }
    [void](Invoke-Retirement -Arguments @("-RequireAbsent") -ExpectedExitCode 1)
    [void](Invoke-Retirement -Arguments @("-Apply", "-RequireAbsent") -ExpectedExitCode 0)
    $final = @(Invoke-Retirement -Arguments @("-RequireAbsent") -ExpectedExitCode 0)
    if ($final -notcontains "retired plugins absent") {
        throw "retirement did not reach an absent state"
    }

    Write-Host "retired plugin test: ok"
}
finally {
    $env:PATH = $originalPath
    if (Test-Path -LiteralPath $testRoot) {
        Remove-Item -LiteralPath $testRoot -Recurse -Force
    }
}
