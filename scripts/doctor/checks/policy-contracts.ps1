$contractManifestPath = Join-Path $repoRoot "manifests\policy-contracts.json"
$contractValidatorPath = Join-Path $repoRoot "scripts\validate-policy-contracts.py"
$contractPythonRunner = @(Get-DoctorPythonRunner)

if ($contractPythonRunner.Count -eq 0) {
    $problems.Add("no runnable Python found for policy contract validation")
}
elseif (-not (Test-Path -LiteralPath $contractManifestPath)) {
    $problems.Add("missing policy contract manifest: $contractManifestPath")
}
elseif (-not (Test-Path -LiteralPath $contractValidatorPath)) {
    $problems.Add("missing policy contract validator: $contractValidatorPath")
}
else {
    $result = Invoke-DoctorPythonScript `
        -Runner $contractPythonRunner `
        -ScriptPath $contractValidatorPath `
        -InputText "" `
        -Arguments @("--root", $repoRoot, "--manifest", $contractManifestPath)

    if ($result.ExitCode -ne 0) {
        $messages = @($result.Output -split "`r?`n" | Where-Object { $_.Trim() })
        if ($messages.Count -eq 0) {
            $problems.Add("policy contract validation failed without output")
        }
        else {
            foreach ($message in $messages) {
                $problems.Add($message)
            }
        }
    }
}
