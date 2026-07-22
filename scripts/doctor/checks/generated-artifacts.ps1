# Generated-artifact freshness check.
#
# Contract: every script under scripts/generators/<name>.py derives one or more
# committed files from a canonical source. Each generator must accept a --check
# argument that regenerates its outputs to a temporary location, compares them
# byte-for-byte against the committed files, and exits 0 when fresh or exits
# non-zero (printing the stale path) when drift is detected. This check runs
# every generator in --check mode and reports a problem when any generated file
# is stale. With no generators present the check is a no-op that passes.

$generatorsDir = Join-Path $repoRoot "scripts\generators"
if (Test-Path -LiteralPath $generatorsDir -PathType Container) {
    $runner = Get-DoctorPythonRunner
    if ($runner.Count -eq 0) {
        $problems.Add("python runner unavailable for generated-artifacts check")
    }
    else {
        $generators = @(Get-ChildItem -LiteralPath $generatorsDir -File -Filter "*.py" | Sort-Object Name)
        foreach ($generator in $generators) {
            $result = Invoke-DoctorPythonScript -Runner $runner -ScriptPath $generator.FullName -Arguments @("--check")
            if ($result.ExitCode -ne 0) {
                $detail = $result.Output
                if (-not $detail) {
                    $detail = "output is stale"
                }
                $problems.Add("stale generated artifact ($($generator.Name)): $detail")
            }
        }
    }
}
