param(
    [string]$AgentsHome
)

. "$PSScriptRoot\common.ps1"

$liveAgentsHome = Get-AgentsHome -AgentsHome $AgentsHome
$skillRoot = Join-Path (Join-Path $liveAgentsHome "skills") "which-llm"
$queryPath = Join-Path $skillRoot "query.py"
if (-not (Test-Path -LiteralPath $queryPath -PathType Leaf)) {
    throw "which-llm runtime setup requires installed skill: $queryPath"
}

$runner = Get-PortablePythonRunner
function Invoke-WhichLlmPython {
    param(
        [string[]]$Arguments,
        [switch]$AllowFailure
    )

    $commandArguments = @($runner.Prefix) + @($Arguments)
    & $runner.Command @commandArguments
    $exitCode = $LASTEXITCODE
    if (-not $AllowFailure -and $exitCode -ne 0) {
        throw "which-llm Python command failed: $($Arguments -join ' ')"
    }
    return $exitCode
}

$statusExit = Invoke-WhichLlmPython -Arguments @($queryPath, "data", "status") -AllowFailure
if ($statusExit -eq 0) {
    Write-Host "which-llm snapshot is fresh"
    exit 0
}

$dependencyExit = Invoke-WhichLlmPython -Arguments @("-c", "import cryptography; assert tuple(map(int, cryptography.__version__.split('.')[:2])) >= (45, 0)") -AllowFailure
if ($dependencyExit -ne 0) {
    $venvArguments = @($runner.Prefix) + @("-c", "import sys; print('yes' if sys.prefix != sys.base_prefix else 'no')")
    $venvOutput = @(& $runner.Command @venvArguments)
    if ($LASTEXITCODE -ne 0) {
        throw "could not inspect the Python environment for which-llm"
    }
    $pipArguments = @("-m", "pip", "install")
    if (($venvOutput | Select-Object -Last 1).Trim() -ne "yes") {
        $pipArguments += "--user"
    }
    $pipArguments += "cryptography>=45.0.0"
    [void](Invoke-WhichLlmPython -Arguments $pipArguments)
}

[void](Invoke-WhichLlmPython -Arguments @($queryPath, "data", "refresh"))
[void](Invoke-WhichLlmPython -Arguments @($queryPath, "data", "status"))
Write-Host "which-llm runtime is ready"
