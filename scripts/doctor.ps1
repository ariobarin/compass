param(
    [string]$CodexHome,
    [string]$AgentsHome
)

. "$PSScriptRoot\common.ps1"

$repoRoot = Get-RepoRoot
try {
    $liveHome = Get-CodexHome -CodexHome $CodexHome
}
catch {
    $liveHome = Join-Path $env:USERPROFILE ".codex"
}
try {
    $agentsHomePath = Get-AgentsHome -AgentsHome $AgentsHome
}
catch {
    $agentsHomePath = Join-Path $HOME ".agents"
}
$problems = New-Object System.Collections.Generic.List[string]
$trackedFiles = @()
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

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    $problems.Add("git is not on PATH")
}
else {
    $trackedFiles = @(& git -C $repoRoot ls-files 2>$null)
    foreach ($trackedFile in $trackedFiles) {
        $trackedPath = Get-DoctorFullPath -Path (Join-Path $repoRoot $trackedFile)
        if (Test-LocalScratchPath -Path $trackedPath) {
            $problems.Add("tracked local scratch path: $trackedFile")
        }
    }
}

foreach ($path in @(
    ".gitattributes",
    ".github\workflows\portable-checks.yml",
    "AGENTS.md",
    "codex\AGENTS.md",
    "codex\hooks.json",
    "codex\hooks\README.md",
    "codex\hooks\portable_guard.py",
    "codex\hooks\portable_guard.ps1",
    "codex\hooks\portable_guard.sh",
    "codex\keybindings.json",
    "codex\config.review.toml",
    "manifests\portable-files.toml",
    "manifests\tool-surfaces.md",
    "local-docs\README.md",
    "local-docs\maintenance-learnings.md",
    "workflows\addition-intake.md",
    "workflows\portable-config.md",
    "workflows\multi-thread-pr-coordination.md",
    "workflows\plan-template.md",
    "workflows\read-only-research.md",
    "workflows\agent-failures.md",
    "scripts\update-live.ps1",
    "scripts\verify-live.ps1"
)) {
    $fullPath = Join-Path $repoRoot $path
    if (-not (Test-Path $fullPath)) {
        $problems.Add("missing required file: $path")
    }
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

$manifestPath = Join-Path $repoRoot "manifests\portable-files.toml"
$manifestText = Get-Content -Raw -LiteralPath $manifestPath

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

$blockedNames = @(Get-ManifestArrayValues -Text $manifestText -Section "local_only" -Key "files")
if ($blockedNames.Count -eq 0) {
    $problems.Add("missing local-only files in portable manifest")
}

foreach ($blocked in $blockedNames) {
    $matches = Get-DoctorChildItem -Kind File -Filter $blocked
    foreach ($match in $matches) {
        $problems.Add("blocked local-only file in repo tree: $($match.FullName)")
    }
}

$blockedPatterns = @(Get-ManifestArrayValues -Text $manifestText -Section "local_only" -Key "patterns")
if ($blockedPatterns.Count -eq 0) {
    $problems.Add("missing local-only patterns in portable manifest")
}

foreach ($blockedPattern in $blockedPatterns) {
    $matches = Get-DoctorChildItem -Kind File -Filter $blockedPattern
    foreach ($match in $matches) {
        $problems.Add("blocked local-only file pattern in repo tree: $($match.FullName)")
    }
}

$blockedDirs = @(Get-ManifestArrayValues -Text $manifestText -Section "local_only" -Key "dirs")
if ($blockedDirs.Count -eq 0) {
    $problems.Add("missing local-only dirs in portable manifest")
}

foreach ($dir in Get-DoctorChildItem -Kind Directory) {
    if ($dir.FullName -match "\\.git(\\|$)") {
        continue
    }

    if ($blockedDirs -contains $dir.Name) {
        $problems.Add("blocked local-only directory in repo tree: $($dir.FullName)")
    }
}

$textFiles = Get-DoctorChildItem -Kind File |
    Where-Object {
        $_.FullName -notmatch "\\.git\\" -and
        $_.Extension -in @(".md", ".toml", ".json", ".ps1", ".yaml", ".yml", ".txt")
    }

foreach ($file in $textFiles) {
    $content = Get-Content -Raw -Encoding UTF8 -LiteralPath $file.FullName
    if ($content -match "[^\x00-\x7F]") {
        $problems.Add("non-ASCII text in: $($file.FullName)")
    }
}

$dashCheckedExtensions = @(".md", ".toml", ".json", ".ps1", ".yaml", ".yml", ".txt", ".py", ".csv")
$dashCheckedFiles = Get-DoctorChildItem -Kind File |
    Where-Object {
        $_.FullName -notmatch "\\.git\\" -and
        $_.Extension -in $dashCheckedExtensions
    }
$blockedDashChars = @([char]0x2013, [char]0x2014)

foreach ($file in $dashCheckedFiles) {
    $content = Get-Content -Raw -Encoding UTF8 -LiteralPath $file.FullName
    foreach ($dashChar in $blockedDashChars) {
        if ($content.Contains($dashChar)) {
            $problems.Add("non-ASCII dash text in: $($file.FullName)")
            break
        }
    }
}

$maxDescriptionLength = 160
$skillFiles = Get-ChildItem -Path (Join-Path $repoRoot "codex\skills") -Recurse -File -Filter "SKILL.md" -ErrorAction SilentlyContinue
foreach ($skillFile in $skillFiles) {
    $name = Select-String -Path $skillFile.FullName -Pattern "^name:\s*(.+)$" | Select-Object -First 1
    if (-not $name) {
        $problems.Add("missing skill name: $($skillFile.FullName)")
        continue
    }

    $description = Select-String -Path $skillFile.FullName -Pattern "^description:\s*(.+)$" | Select-Object -First 1
    if (-not $description) {
        $problems.Add("missing skill description: $($skillFile.FullName)")
        continue
    }

    $descriptionText = $description.Matches[0].Groups[1].Value.Trim()
    if ($descriptionText.Length -gt $maxDescriptionLength) {
        $problems.Add("skill description over $maxDescriptionLength chars: $($skillFile.FullName)")
    }
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

$agentFiles = Get-ChildItem -Path (Join-Path $repoRoot "codex\agents") -File -Filter "*.toml" -ErrorAction SilentlyContinue
foreach ($agentFile in $agentFiles) {
    $agentText = Get-Content -Raw -LiteralPath $agentFile.FullName
    $topLevelValues = Get-TopLevelTomlStringValues -Text $agentText
    $topLevelText = $topLevelValues.Values -join "`n"

    if ($topLevelText -match "(?i)\bread-only\b" -and ($topLevelValues["sandbox_mode"] -ne "read-only")) {
        $problems.Add("read-only agent missing sandbox_mode: $($agentFile.FullName)")
    }
}

$skillsMatch = [regex]::Match($manifestText, "(?ms)^skills\s*=\s*\[(.*?)^\]")
if (-not $skillsMatch.Success) {
    $problems.Add("missing skills allowlist in portable manifest")
}
else {
    $manifestSkills = @(
        [regex]::Matches($skillsMatch.Groups[1].Value, '"([^"]+)"') |
            ForEach-Object { $_.Groups[1].Value } |
            Sort-Object -Unique
    )

    $skillsRoot = [System.IO.Path]::GetFullPath((Join-Path (Join-Path $repoRoot "codex") "skills")).TrimEnd("\")
    $mappedSkills = @(
        Get-PortableFileMap -RepoRoot $repoRoot -CodexHome $liveHome -AgentsHome $agentsHomePath |
            Where-Object {
                $_.Type -eq "dir" -and
                [System.IO.Path]::GetFullPath($_.RepoPath).TrimEnd("\").StartsWith(
                    "$skillsRoot\",
                    [System.StringComparison]::OrdinalIgnoreCase
                )
            } |
            ForEach-Object { Split-Path -Leaf $_.RepoPath } |
            Sort-Object -Unique
    )

    foreach ($skill in $manifestSkills) {
        if ($mappedSkills -notcontains $skill) {
            $problems.Add("skill in manifest missing from install map: $skill")
        }
    }

    foreach ($skill in $mappedSkills) {
        if ($manifestSkills -notcontains $skill) {
            $problems.Add("skill in install map missing from manifest: $skill")
        }
    }
}

$hooksJsonPath = Join-Path $repoRoot "codex\hooks.json"
try {
    [void](Get-Content -Raw -Encoding UTF8 -LiteralPath $hooksJsonPath | ConvertFrom-Json)
}
catch {
    $problems.Add("invalid hooks.json: $($_.Exception.Message)")
}

$hookGuardPath = Join-Path $repoRoot "codex\hooks\portable_guard.py"
$pythonRunner = @(Get-DoctorPythonRunner)
if ($pythonRunner.Count -eq 0) {
    $problems.Add("no runnable Python found for portable hook guard")
}
elseif (Test-Path -LiteralPath $hookGuardPath) {
    $payload = @{ hook_event_name = "UnknownEvent" } | ConvertTo-Json -Compress -Depth 4
    $result = Invoke-DoctorPythonScript -Runner $pythonRunner -ScriptPath $hookGuardPath -InputText $payload
    if ($result.ExitCode -ne 0) {
        $problems.Add("portable hook guard failed unknown event smoke")
    }
    elseif ($result.Output.Trim()) {
        $problems.Add("portable hook guard emitted output for unknown event: $($result.Output.Trim())")
    }

    $tempRoot = Join-Path ([System.IO.Path]::GetTempPath()) "compass-hook-$([guid]::NewGuid())"
    try {
        New-Item -ItemType Directory -Force $tempRoot | Out-Null
        $standaloneGuardPath = Join-Path $tempRoot "portable_guard.py"
        Copy-Item -LiteralPath $hookGuardPath -Destination $standaloneGuardPath
        $standaloneResult = Invoke-DoctorPythonScript -Runner $pythonRunner -ScriptPath $standaloneGuardPath -InputText $payload
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
            $externalResult = Invoke-DoctorPythonScript -Runner $pythonRunner -ScriptPath $standaloneGuardPath -InputText $payload
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
        $missingRunnerResult = Invoke-DoctorPythonScript -Runner $pythonRunner -ScriptPath $missingProbePath -InputText $payload
        if ($missingRunnerResult.ExitCode -eq 0) {
            $problems.Add("portable hook guard hid missing packaged guard module")
        }

        $brokenCacheRoot = Join-Path $brokenGuardRoot "__pycache__"
        if (Test-Path -LiteralPath $brokenCacheRoot) {
            Remove-Item -LiteralPath $brokenCacheRoot -Recurse -Force
        }
        Set-Content -LiteralPath (Join-Path $brokenGuardRoot "runner.py") -Value "raise PermissionError('unreadable guard package')"
        $unreadableResult = Invoke-DoctorPythonScript -Runner $pythonRunner -ScriptPath $standaloneGuardPath -InputText $payload
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
        $brokenResult = Invoke-DoctorPythonScript -Runner $pythonRunner -ScriptPath $standaloneGuardPath -InputText $payload
        if ($brokenResult.ExitCode -eq 0) {
            $problems.Add("portable hook guard hid broken guard package")
        }

        $bytecodeRoot = Join-Path $tempRoot "bytecode"
        $bytecodeGuardRoot = Join-Path $bytecodeRoot "guard"
        New-Item -ItemType Directory -Force $bytecodeGuardRoot | Out-Null
        $bytecodeGuardPath = Join-Path $bytecodeRoot "portable_guard.py"
        Copy-Item -LiteralPath $hookGuardPath -Destination $bytecodeGuardPath
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
        $missingSelectedResult = Invoke-DoctorPythonScript -Runner $pythonRunner -ScriptPath $missingSelectedProbePath -InputText $payload
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
        $chainedResult = Invoke-DoctorPythonScript -Runner $pythonRunner -ScriptPath $bytecodeGuardPath -InputText $payload -Arguments @("first_false", "second_true")
        if ($chainedResult.ExitCode -ne 0) {
            $problems.Add("portable hook guard failed chained module smoke")
        }
        elseif (-not ($chainedResult.Output.Trim() -match '"handled":true')) {
            $problems.Add("portable hook guard skipped later handling module")
        }
        $bytecodeResult = Invoke-DoctorPythonScript -Runner $pythonRunner -ScriptPath $bytecodeGuardPath -InputText $payload
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
}

$hookLauncherPath = Join-Path $repoRoot "codex\hooks\portable_guard.ps1"
if (Test-Path -LiteralPath $hookLauncherPath) {
    $oldCodexHome = [Environment]::GetEnvironmentVariable("CODEX_HOME", "Process")
    [Environment]::SetEnvironmentVariable("CODEX_HOME", (Join-Path $repoRoot "codex"), "Process")
    try {
        $payload = @{ hook_event_name = "UnknownEvent" } | ConvertTo-Json -Compress -Depth 4
        $launcherOutput = $payload | & $hookLauncherPath 2>&1
        if ($LASTEXITCODE -ne 0) {
            $problems.Add("portable hook PowerShell launcher failed")
        }
        elseif (($launcherOutput -join "`n").Trim()) {
            $problems.Add("portable hook PowerShell launcher emitted output for unknown event")
        }
    }
    finally {
        [Environment]::SetEnvironmentVariable("CODEX_HOME", $oldCodexHome, "Process")
    }
}

Write-Host "repo: $repoRoot"
Write-Host "codex: $liveHome"
Write-Host "agents: $agentsHomePath"

if ($problems.Count -gt 0) {
    Write-Host ""
    Write-Host "problems:"
    foreach ($problem in $problems) {
        Write-Host "  $problem"
    }
    exit 1
}

Write-Host "doctor: ok"
