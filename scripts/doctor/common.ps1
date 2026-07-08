$pathSeparators = @([System.IO.Path]::DirectorySeparatorChar, [System.IO.Path]::AltDirectorySeparatorChar) | Select-Object -Unique

function Get-DoctorFullPath {
    param([string]$Path)

    return [System.IO.Path]::GetFullPath($Path).TrimEnd($pathSeparators)
}

$localScratchRoot = Get-DoctorFullPath -Path (Join-Path $repoRoot ".local")

function Test-LocalScratchPath {
    param([string]$Path)

    $fullPath = Get-DoctorFullPath -Path $Path
    if ($fullPath -eq $localScratchRoot) {
        return $true
    }

    foreach ($separator in $pathSeparators) {
        if ($fullPath.StartsWith("$localScratchRoot$separator", [System.StringComparison]::OrdinalIgnoreCase)) {
            return $true
        }
    }

    return $false
}

function Get-DoctorChildItem {
    param(
        [ValidateSet("File", "Directory")]
        [string]$Kind,
        [string]$Filter = "*"
    )

    $items = New-Object System.Collections.Generic.List[object]

    function Add-DoctorChildren {
        param([string]$Path)

        foreach ($child in Get-ChildItem -LiteralPath $Path -Force -ErrorAction SilentlyContinue) {
            if ($child.PSIsContainer) {
                if ($child.FullName -match "\\.git(\\|$)") {
                    continue
                }

                if (Test-LocalScratchPath -Path $child.FullName) {
                    continue
                }

                if ($Kind -eq "Directory" -and $child.Name -like $Filter) {
                    $items.Add($child)
                }

                Add-DoctorChildren -Path $child.FullName
                continue
            }

            if ($Kind -eq "File" -and $child.Name -like $Filter) {
                $items.Add($child)
            }
        }
    }

    Add-DoctorChildren -Path $repoRoot
    return $items
}

function Get-DoctorPythonRunner {
    $candidates = New-Object System.Collections.Generic.List[object]

    if ($env:OS -eq "Windows_NT") {
        $candidates.Add(@("py", "-3"))
    }

    $candidates.Add(@("python3"))
    $candidates.Add(@("python"))

    foreach ($candidate in $candidates) {
        $exe = $candidate[0]
        if (-not (Get-Command $exe -ErrorAction SilentlyContinue)) {
            continue
        }

        $runnerArgs = @()
        if ($candidate.Count -gt 1) {
            $runnerArgs = @($candidate[1..($candidate.Count - 1)])
        }

        & $exe @runnerArgs "--version" *> $null
        if ($LASTEXITCODE -eq 0) {
            return @($candidate)
        }
    }

    return @()
}

function Invoke-DoctorPythonScript {
    param(
        [string[]]$Runner,
        [string]$ScriptPath,
        [string]$InputText,
        [string[]]$Arguments = @()
    )

    $exe = $Runner[0]
    $runnerArgs = @()
    if ($Runner.Count -gt 1) {
        $runnerArgs = @($Runner[1..($Runner.Count - 1)])
    }

    $oldPythonIoEncoding = [Environment]::GetEnvironmentVariable("PYTHONIOENCODING", "Process")
    $oldOutputEncoding = $global:OutputEncoding
    $oldConsoleOutputEncoding = [Console]::OutputEncoding
    $utf8Encoding = New-Object System.Text.UTF8Encoding $false
    [Environment]::SetEnvironmentVariable("PYTHONIOENCODING", "utf-8", "Process")
    $global:OutputEncoding = $utf8Encoding
    [Console]::OutputEncoding = $utf8Encoding
    try {
        $output = $InputText | & $exe @runnerArgs $ScriptPath @Arguments 2>&1
        return [pscustomobject]@{
            ExitCode = $LASTEXITCODE
            Output = ($output -join "`n")
        }
    }
    finally {
        [Environment]::SetEnvironmentVariable("PYTHONIOENCODING", $oldPythonIoEncoding, "Process")
        $global:OutputEncoding = $oldOutputEncoding
        [Console]::OutputEncoding = $oldConsoleOutputEncoding
    }
}
