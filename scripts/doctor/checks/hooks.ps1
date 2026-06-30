$hooksJsonPath = Join-Path $repoRoot "codex\hooks.json"
try {
    [void](Get-Content -Raw -Encoding UTF8 -LiteralPath $hooksJsonPath | ConvertFrom-Json)
}
catch {
    $problems.Add("invalid hooks.json: $($_.Exception.Message)")
}

$portableHookGuardPath = Join-Path $repoRoot "codex\hooks\portable_guard.py"
$portableHookLauncherPath = Join-Path $repoRoot "codex\hooks\portable_guard.ps1"
$portableHookPythonRunner = @(Get-DoctorPythonRunner)
if ($portableHookPythonRunner.Count -eq 0) {
    $problems.Add("no runnable Python found for portable hook guard")
}
elseif (Test-Path -LiteralPath $portableHookGuardPath) {
    $payload = @{ hook_event_name = "UnknownEvent" } | ConvertTo-Json -Compress -Depth 4
    $tempRoot = Join-Path ([System.IO.Path]::GetTempPath()) "compass-hook-$([guid]::NewGuid())"
    try {
        New-Item -ItemType Directory -Force $tempRoot | Out-Null
        $standaloneGuardPath = Join-Path $tempRoot "portable_guard.py"
        Copy-Item -LiteralPath $portableHookGuardPath -Destination $standaloneGuardPath
        $standaloneResult = Invoke-DoctorPythonScript -Runner $portableHookPythonRunner -ScriptPath $standaloneGuardPath -InputText $payload
        if ($standaloneResult.ExitCode -ne 0) {
            $problems.Add("portable hook guard failed missing package smoke")
        }
        elseif ($standaloneResult.Output.Trim()) {
            $problems.Add("portable hook guard emitted output without guard package: $($standaloneResult.Output.Trim())")
        }

        $externalGuardRoot = Join-Path $tempRoot "external\guard"
        New-Item -ItemType Directory -Force $externalGuardRoot | Out-Null
        Set-Content -LiteralPath (Join-Path $externalGuardRoot "__init__.py") -Value ""
        Set-Content -LiteralPath (Join-Path $externalGuardRoot "runner.py") -Value "raise SystemExit(29)"
        $oldPythonPath = [Environment]::GetEnvironmentVariable("PYTHONPATH", "Process")
        [Environment]::SetEnvironmentVariable("PYTHONPATH", (Split-Path -Parent $externalGuardRoot), "Process")
        try {
            $externalResult = Invoke-DoctorPythonScript -Runner $portableHookPythonRunner -ScriptPath $standaloneGuardPath -InputText $payload
        }
        finally {
            [Environment]::SetEnvironmentVariable("PYTHONPATH", $oldPythonPath, "Process")
        }
        if ($externalResult.ExitCode -ne 0) {
            $problems.Add("portable hook guard imported non-adjacent guard package")
        }
        elseif ($externalResult.Output.Trim()) {
            $problems.Add("portable hook guard emitted output with non-adjacent guard package: $($externalResult.Output.Trim())")
        }

        $brokenGuardRoot = Join-Path $tempRoot "guard"
        New-Item -ItemType Directory -Force $brokenGuardRoot | Out-Null
        Set-Content -LiteralPath (Join-Path $brokenGuardRoot "__init__.py") -Value ""
        Set-Content -LiteralPath (Join-Path $brokenGuardRoot "runner.py") -Value "import guard.missing"
        $missingProbePath = Join-Path $tempRoot "missing_probe.py"
        Set-Content -LiteralPath $missingProbePath -Value @(
            "import runpy",
            "try:",
            "    runpy.run_path(r'$standaloneGuardPath', run_name='__main__')",
            "except ModuleNotFoundError as error:",
            "    if error.name == 'guard.missing':",
            "        raise SystemExit(17)",
            "    raise",
            "raise SystemExit(0)"
        )
        $missingRunnerResult = Invoke-DoctorPythonScript -Runner $portableHookPythonRunner -ScriptPath $missingProbePath -InputText $payload
        if ($missingRunnerResult.ExitCode -eq 0) {
            $problems.Add("portable hook guard hid missing packaged guard module")
        }

        $brokenCacheRoot = Join-Path $brokenGuardRoot "__pycache__"
        if (Test-Path -LiteralPath $brokenCacheRoot) {
            Remove-Item -LiteralPath $brokenCacheRoot -Recurse -Force
        }
        Set-Content -LiteralPath (Join-Path $brokenGuardRoot "runner.py") -Value "raise PermissionError('unreadable guard package')"
        $unreadableResult = Invoke-DoctorPythonScript -Runner $portableHookPythonRunner -ScriptPath $standaloneGuardPath -InputText $payload
        if ($unreadableResult.ExitCode -ne 0) {
            $problems.Add("portable hook guard failed unreadable package smoke")
        }
        elseif ($unreadableResult.Output.Trim()) {
            $problems.Add("portable hook guard emitted output for unreadable guard package: $($unreadableResult.Output.Trim())")
        }

        if (Test-Path -LiteralPath $brokenCacheRoot) {
            Remove-Item -LiteralPath $brokenCacheRoot -Recurse -Force
        }
        Set-Content -LiteralPath (Join-Path $brokenGuardRoot "runner.py") -Value "raise SystemExit(17)"
        $brokenResult = Invoke-DoctorPythonScript -Runner $portableHookPythonRunner -ScriptPath $standaloneGuardPath -InputText $payload
        if ($brokenResult.ExitCode -eq 0) {
            $problems.Add("portable hook guard hid broken guard package")
        }

        $bytecodeRoot = Join-Path $tempRoot "bytecode"
        $bytecodeGuardRoot = Join-Path $bytecodeRoot "guard"
        New-Item -ItemType Directory -Force $bytecodeGuardRoot | Out-Null
        $bytecodeGuardPath = Join-Path $bytecodeRoot "portable_guard.py"
        Copy-Item -LiteralPath $portableHookGuardPath -Destination $bytecodeGuardPath
        foreach ($guardFile in @("__init__.py", "common.py", "runner.py")) {
            Copy-Item -LiteralPath (Join-Path $repoRoot "codex\hooks\guard\$guardFile") -Destination (Join-Path $bytecodeGuardRoot $guardFile)
        }
        $missingSelectedProbePath = Join-Path $bytecodeRoot "missing_selected_probe.py"
        Set-Content -LiteralPath $missingSelectedProbePath -Value @(
            "import runpy",
            "import sys",
            "sys.argv = [r'$bytecodeGuardPath', 'missing_guard']",
            "try:",
            "    runpy.run_path(r'$bytecodeGuardPath', run_name='__main__')",
            "except ModuleNotFoundError as error:",
            "    if error.name == 'guard.missing_guard':",
            "        raise SystemExit(17)",
            "    raise",
            "raise SystemExit(0)"
        )
        $missingSelectedResult = Invoke-DoctorPythonScript -Runner $portableHookPythonRunner -ScriptPath $missingSelectedProbePath -InputText $payload
        if ($missingSelectedResult.ExitCode -eq 0) {
            $problems.Add("portable hook guard hid missing selected guard module")
        }
        Set-Content -LiteralPath (Join-Path $bytecodeGuardRoot "z_probe.py") -Value "raise SystemExit(31)"
        Set-Content -LiteralPath (Join-Path $bytecodeGuardRoot "first_false.py") -Value @(
            "def handle(data):",
            "    return False",
            "HANDLERS = {'UnknownEvent': handle}"
        )
        Set-Content -LiteralPath (Join-Path $bytecodeGuardRoot "second_true.py") -Value @(
            "from .common import write_json",
            "def handle(data):",
            "    write_json({'handled': True})",
            "    return True",
            "HANDLERS = {'UnknownEvent': handle}"
        )
        $chainedResult = Invoke-DoctorPythonScript -Runner $portableHookPythonRunner -ScriptPath $bytecodeGuardPath -InputText $payload -Arguments @("first_false", "second_true")
        if ($chainedResult.ExitCode -ne 0) {
            $problems.Add("portable hook guard failed chained module smoke")
        }
        elseif (-not ($chainedResult.Output.Trim() -match '"handled":true')) {
            $problems.Add("portable hook guard skipped later handling module")
        }
        $bytecodeResult = Invoke-DoctorPythonScript -Runner $portableHookPythonRunner -ScriptPath $bytecodeGuardPath -InputText $payload
        if ($bytecodeResult.ExitCode -ne 0) {
            $problems.Add("portable hook guard failed bytecode smoke")
        }
        elseif ($bytecodeResult.Output.Trim()) {
            $problems.Add("portable hook guard emitted output for bytecode smoke: $($bytecodeResult.Output.Trim())")
        }
        if (Test-Path -LiteralPath (Join-Path $bytecodeGuardRoot "__pycache__")) {
            $problems.Add("portable hook guard wrote bytecode cache")
        }
    }
    finally {
        if (Test-Path -LiteralPath $tempRoot) {
            Remove-Item -LiteralPath $tempRoot -Recurse -Force
        }
    }

    $portableHookDoctorRoot = Join-Path $repoRoot "scripts\doctor\hooks"
    $portableHookDoctorCommon = Join-Path $portableHookDoctorRoot "common.ps1"
    if (-not (Test-Path -LiteralPath $portableHookDoctorCommon)) {
        $problems.Add("missing portable hook doctor helpers")
    }
    else {
        . $portableHookDoctorCommon
        $portableHookDoctorTests = @(
            Get-ChildItem -LiteralPath $portableHookDoctorRoot -File -Filter "*.tests.ps1" |
                Sort-Object Name
        )
        if ($portableHookDoctorTests.Count -eq 0) {
            $problems.Add("missing portable hook doctor tests")
        }

        foreach ($portableHookDoctorTest in $portableHookDoctorTests) {
            . $portableHookDoctorTest.FullName
        }
    }
}
