$skillSourceManifestPath = Join-Path $repoRoot "manifests\skill-sources.json"
$skillSourceValidatorPath = Join-Path $repoRoot "scripts\validate-skill-sources.py"
$skillSourcePythonRunner = @(Get-DoctorPythonRunner)

if ($skillSourcePythonRunner.Count -eq 0) {
    $problems.Add("no runnable Python found for skill source validation")
}
elseif (-not (Test-Path -LiteralPath $skillSourceManifestPath)) {
    $problems.Add("missing skill source manifest: $skillSourceManifestPath")
}
elseif (-not (Test-Path -LiteralPath $skillSourceValidatorPath)) {
    $problems.Add("missing skill source validator: $skillSourceValidatorPath")
}
else {
    $result = Invoke-DoctorPythonScript `
        -Runner $skillSourcePythonRunner `
        -ScriptPath $skillSourceValidatorPath `
        -InputText "" `
        -Arguments @("--root", $repoRoot, "--manifest", $skillSourceManifestPath)

    if ($result.ExitCode -ne 0) {
        $messages = @($result.Output -split "`r?`n" | Where-Object { $_.Trim() })
        if ($messages.Count -eq 0) {
            $problems.Add("skill source validation failed without output")
        }
        else {
            foreach ($message in $messages) {
                $problems.Add($message)
            }
        }
    }
}
