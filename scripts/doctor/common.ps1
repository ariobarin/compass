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

function Get-ManifestArrayValues {
    param(
        [string]$Text,
        [string]$Section,
        [string]$Key
    )

    $sectionPattern = "(?ms)^\[$([regex]::Escape($Section))\]\s*(.*?)(?=^\[|\z)"
    $sectionMatch = [regex]::Match($Text, $sectionPattern)
    if (-not $sectionMatch.Success) {
        return @()
    }

    $keyPattern = "(?ms)^\s*$([regex]::Escape($Key))\s*=\s*\[(.*?)^\s*\]"
    $keyMatch = [regex]::Match($sectionMatch.Groups[1].Value, $keyPattern)
    if (-not $keyMatch.Success) {
        return @()
    }

    return @(
        [regex]::Matches($keyMatch.Groups[1].Value, '"([^"]+)"') |
            ForEach-Object { $_.Groups[1].Value }
    )
}

function Get-TopLevelTomlStringValues {
    param([string]$Text)

    $topLevelValues = @{}
    $currentKey = $null
    $currentValue = New-Object System.Text.StringBuilder
    $inMultilineString = $false
    $inTable = $false

    foreach ($line in ($Text -split "`r?`n")) {
        if ($inMultilineString) {
            $closingIndex = $line.IndexOf('"""')
            if ($closingIndex -ge 0) {
                [void]$currentValue.AppendLine($line.Substring(0, $closingIndex))
                $topLevelValues[$currentKey] = $currentValue.ToString()
                $currentKey = $null
                [void]$currentValue.Clear()
                $inMultilineString = $false
            }
            else {
                [void]$currentValue.AppendLine($line)
            }
            continue
        }

        if ($line -match '^\s*\[') {
            $inTable = $true
            continue
        }

        if ($inTable) {
            continue
        }

        $multiline = [regex]::Match($line, '^\s*([A-Za-z0-9_-]+)\s*=\s*"""(.*)$')
        if ($multiline.Success) {
            $key = $multiline.Groups[1].Value
            $remainingText = $multiline.Groups[2].Value
            $closingIndex = $remainingText.IndexOf('"""')
            if ($closingIndex -ge 0) {
                $topLevelValues[$key] = $remainingText.Substring(0, $closingIndex)
            }
            else {
                $currentKey = $key
                [void]$currentValue.Clear()
                [void]$currentValue.AppendLine($remainingText)
                $inMultilineString = $true
            }
            continue
        }

        $assignment = [regex]::Match($line, '^\s*([A-Za-z0-9_-]+)\s*=\s*"([^"]*)"\s*(#.*)?$')
        if ($assignment.Success) {
            $topLevelValues[$assignment.Groups[1].Value] = $assignment.Groups[2].Value
        }
    }

    return $topLevelValues
}
