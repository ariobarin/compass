$ErrorActionPreference = "SilentlyContinue"
$guardModules = @($args)

if ($env:CODEX_HOME) {
    $codexHome = $env:CODEX_HOME
}
else {
    $codexHome = Join-Path $env:USERPROFILE ".codex"
}

$guard = Join-Path $codexHome "hooks\portable_guard.py"
if (-not (Test-Path -LiteralPath $guard)) {
    exit 0
}

$runners = @(
    @("py", "-3"),
    @("python3"),
    @("python")
)

foreach ($runner in $runners) {
    $exe = $runner[0]
    if (-not (Get-Command $exe -ErrorAction SilentlyContinue)) {
        continue
    }

    $runnerArgs = @()
    if ($runner.Count -gt 1) {
        $runnerArgs = @($runner[1..($runner.Count - 1)])
    }

    & $exe @runnerArgs "--version" *> $null
    if ($LASTEXITCODE -eq 0) {
        $pipelineInput = @($input)
        if ($pipelineInput.Count -gt 0) {
            $inputText = $pipelineInput -join [Environment]::NewLine
        }
        else {
            $inputText = [Console]::In.ReadToEnd()
        }

        $oldPythonIoEncoding = [Environment]::GetEnvironmentVariable("PYTHONIOENCODING", "Process")
        $oldOutputEncoding = $global:OutputEncoding
        $oldConsoleOutputEncoding = [Console]::OutputEncoding
        $utf8Encoding = New-Object System.Text.UTF8Encoding $false
        [Environment]::SetEnvironmentVariable("PYTHONIOENCODING", "utf-8", "Process")
        $global:OutputEncoding = $utf8Encoding
        [Console]::OutputEncoding = $utf8Encoding
        try {
            $inputText | & $exe @runnerArgs $guard @guardModules
            $guardExitCode = $LASTEXITCODE
        }
        finally {
            [Environment]::SetEnvironmentVariable("PYTHONIOENCODING", $oldPythonIoEncoding, "Process")
            $global:OutputEncoding = $oldOutputEncoding
            [Console]::OutputEncoding = $oldConsoleOutputEncoding
        }
        exit $guardExitCode
    }
}

exit 0
