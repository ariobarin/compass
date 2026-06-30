param(
    [string]$CodexHome
)

. "$PSScriptRoot\common.ps1"

$repoRoot = Get-RepoRoot
try {
    $liveHome = Get-CodexHome -CodexHome $CodexHome
}
catch {
    $liveHome = Join-Path $env:USERPROFILE ".codex"
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
        [string]$InputText
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
        $output = $InputText | & $exe @runnerArgs $ScriptPath 2>&1
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
    $content = Get-Content -Raw -LiteralPath $file.FullName
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
    $content = Get-Content -Raw -LiteralPath $file.FullName
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
        Get-PortableFileMap -RepoRoot $repoRoot -CodexHome $liveHome |
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

$portableMap = @(Get-PortableFileMap -RepoRoot $repoRoot -CodexHome $liveHome)
foreach ($item in $portableMap) {
    if (-not (Test-Path -LiteralPath $item.RepoPath)) {
        $problems.Add("install map source missing: $($item.RepoPath)")
    }
}

$codexRoot = Get-DoctorFullPath -Path (Join-Path $repoRoot "codex")
$manifestCodexFiles = @(
    Get-ManifestArrayValues -Text $manifestText -Section "codex" -Key "files" |
        Sort-Object -Unique
)
$mappedCodexFiles = @(
    $portableMap |
        Where-Object {
            $_.Type -eq "file" -and
            (Get-DoctorFullPath -Path (Split-Path -Parent $_.RepoPath)) -eq $codexRoot
        } |
        ForEach-Object { Split-Path -Leaf $_.RepoPath } |
        Sort-Object -Unique
)

foreach ($file in $manifestCodexFiles) {
    if ($mappedCodexFiles -notcontains $file) {
        $problems.Add("codex file in manifest missing from install map: $file")
    }
}

foreach ($file in $mappedCodexFiles) {
    if ($manifestCodexFiles -notcontains $file) {
        $problems.Add("codex file in install map missing from manifest: $file")
    }
}

$manifestCodexDirs = @(
    Get-ManifestArrayValues -Text $manifestText -Section "codex" -Key "dirs" |
        Sort-Object -Unique
)
$mappedCodexDirs = @(
    $portableMap |
        Where-Object {
            $_.Type -eq "dir" -and
            (Get-DoctorFullPath -Path (Split-Path -Parent $_.RepoPath)) -eq $codexRoot
        } |
        ForEach-Object { Split-Path -Leaf $_.RepoPath } |
        Sort-Object -Unique
)

foreach ($dir in $manifestCodexDirs) {
    if ($mappedCodexDirs -notcontains $dir) {
        $problems.Add("codex dir in manifest missing from install map: $dir")
    }
}

foreach ($dir in $mappedCodexDirs) {
    if ($manifestCodexDirs -notcontains $dir) {
        $problems.Add("codex dir in install map missing from manifest: $dir")
    }
}

$hooksJsonPath = Join-Path $repoRoot "codex\hooks.json"
try {
    [void](Get-Content -Raw -LiteralPath $hooksJsonPath | ConvertFrom-Json)
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
    function Invoke-PortableGuardCase {
        param(
            [string]$Name,
            [hashtable]$Payload
        )

        $inputText = $Payload | ConvertTo-Json -Compress -Depth 8
        $result = Invoke-DoctorPythonScript -Runner $pythonRunner -ScriptPath $hookGuardPath -InputText $inputText
        if ($result.ExitCode -ne 0) {
            $problems.Add("portable hook case failed: $Name")
            return $null
        }

        return $result.Output.Trim()
    }

    function Test-PortableGuardDeny {
        param(
            [string]$Name,
            [hashtable]$Payload
        )

        $output = Invoke-PortableGuardCase -Name $Name -Payload $Payload
        if (-not $output) {
            $problems.Add("portable hook did not deny: $Name")
            return
        }

        try {
            $parsed = $output | ConvertFrom-Json
            $decision = $parsed.hookSpecificOutput.permissionDecision
            if ($decision -ne "deny") {
                $problems.Add("portable hook unexpected decision for ${Name}: $decision")
            }
        }
        catch {
            $problems.Add("portable hook emitted invalid deny JSON for ${Name}: $output")
        }
    }

    function Test-PortableGuardBlock {
        param(
            [string]$Name,
            [hashtable]$Payload
        )

        $output = Invoke-PortableGuardCase -Name $Name -Payload $Payload
        if (-not $output) {
            $problems.Add("portable hook did not block: $Name")
            return
        }

        try {
            $parsed = $output | ConvertFrom-Json
            if ($parsed.decision -ne "block") {
                $problems.Add("portable hook unexpected block decision for ${Name}: $($parsed.decision)")
            }
        }
        catch {
            $problems.Add("portable hook emitted invalid block JSON for ${Name}: $output")
        }
    }

    function Test-PortableGuardContext {
        param(
            [string]$Name,
            [hashtable]$Payload,
            [string]$ExpectedContext
        )

        $output = Invoke-PortableGuardCase -Name $Name -Payload $Payload
        if (-not $output) {
            $problems.Add("portable hook did not emit context: $Name")
            return
        }

        try {
            $parsed = $output | ConvertFrom-Json
            if ($parsed.hookSpecificOutput.hookEventName -ne "UserPromptSubmit") {
                $problems.Add("portable hook unexpected context event for ${Name}: $($parsed.hookSpecificOutput.hookEventName)")
            }
            if ($parsed.hookSpecificOutput.additionalContext -ne $ExpectedContext) {
                $problems.Add("portable hook unexpected context for ${Name}: $($parsed.hookSpecificOutput.additionalContext)")
            }
        }
        catch {
            $problems.Add("portable hook emitted invalid context JSON for ${Name}: $output")
        }
    }

    function Test-PortableGuardSilent {
        param(
            [string]$Name,
            [hashtable]$Payload
        )

        $output = Invoke-PortableGuardCase -Name $Name -Payload $Payload
        if ($output) {
            $problems.Add("portable hook unexpectedly emitted output for ${Name}: $output")
        }
    }

    $understandingContext = "The user prompt contains an understanding check such as 'do you understand what I mean', 'dykwim', or 'ykwim'. Only answer the understanding check. Do not use tools. Restate what you think the user means in 1 to 3 sentences, call out any ambiguity, and stop. Do not act on any other request in the same user prompt."

    $dash = [char]0x2014
    Test-PortableGuardDeny -Name "git commit dash" -Payload @{
        hook_event_name = "PreToolUse"
        tool_name = "Bash"
        tool_input = @{
            command = "git commit -m `"bad $dash msg`""
        }
    }
    Test-PortableGuardDeny -Name "git global option dash" -Payload @{
        hook_event_name = "PreToolUse"
        tool_name = "Bash"
        tool_input = @{
            command = "git -C repo commit -m `"bad $dash msg`""
        }
    }
    Test-PortableGuardDeny -Name "patch dash" -Payload @{
        hook_event_name = "PreToolUse"
        tool_name = "apply_patch"
        tool_input = "*** Begin Patch`n*** Add File: sample.md`n+bad $dash msg`n*** End Patch`n"
    }
    Test-PortableGuardSilent -Name "clean git command" -Payload @{
        hook_event_name = "PreToolUse"
        tool_name = "Bash"
        tool_input = @{
            command = "git status"
        }
    }

    $oldDashOptOut = [Environment]::GetEnvironmentVariable("CODEX_PORTABLE_DISABLE_DASH_GUARD", "Process")
    [Environment]::SetEnvironmentVariable("CODEX_PORTABLE_DISABLE_DASH_GUARD", "1", "Process")
    try {
        Test-PortableGuardSilent -Name "dash guard opt-out" -Payload @{
            hook_event_name = "PreToolUse"
            tool_name = "Bash"
            tool_input = @{
                command = "git commit -m `"bad $dash msg`""
            }
        }
    }
    finally {
        [Environment]::SetEnvironmentVariable("CODEX_PORTABLE_DISABLE_DASH_GUARD", $oldDashOptOut, "Process")
    }

    if (Get-Command git -ErrorAction SilentlyContinue) {
        $tempRoot = Join-Path ([System.IO.Path]::GetTempPath()) "codex-portable-hook-$([guid]::NewGuid())"
        try {
            $repo = Join-Path $tempRoot "repo"
            New-Item -ItemType Directory -Force $repo | Out-Null
            & git -C $repo init -q *> $null
            if ($LASTEXITCODE -ne 0) {
                $problems.Add("portable hook git fixture failed to initialize")
            }
            else {
                Test-PortableGuardSilent -Name "clean stop" -Payload @{
                    hook_event_name = "Stop"
                    cwd = $repo
                }

                Set-Content -LiteralPath (Join-Path $repo "dirty.txt") -Value "dirty"
                Test-PortableGuardBlock -Name "dirty stop" -Payload @{
                    hook_event_name = "Stop"
                    cwd = $repo
                }

                $oldGitOptOut = [Environment]::GetEnvironmentVariable("CODEX_PORTABLE_DISABLE_GIT_CLOSEOUT", "Process")
                [Environment]::SetEnvironmentVariable("CODEX_PORTABLE_DISABLE_GIT_CLOSEOUT", "1", "Process")
                try {
                    Test-PortableGuardSilent -Name "git closeout opt-out" -Payload @{
                        hook_event_name = "Stop"
                        cwd = $repo
                    }
                }
                finally {
                    [Environment]::SetEnvironmentVariable("CODEX_PORTABLE_DISABLE_GIT_CLOSEOUT", $oldGitOptOut, "Process")
                }
            }
        }
        finally {
            if (Test-Path -LiteralPath $tempRoot) {
                Remove-Item -LiteralPath $tempRoot -Recurse -Force
            }
        }
    }

    Test-PortableGuardContext -Name "understanding explicit phrase" -ExpectedContext $understandingContext -Payload @{
        hook_event_name = "UserPromptSubmit"
        prompt = "Make the hook narrow, do you understand what i mean?"
    }
    Test-PortableGuardContext -Name "understanding contractions" -ExpectedContext $understandingContext -Payload @{
        hook_event_name = "UserPromptSubmit"
        prompt = "I don't think you're following, do you understand what i mean?"
    }
    Test-PortableGuardContext -Name "understanding dykwim question" -ExpectedContext $understandingContext -Payload @{
        hook_event_name = "UserPromptSubmit"
        prompt = "That should answer only the understanding check, DyKwIm?"
    }
    Test-PortableGuardContext -Name "understanding ykwim trailing" -ExpectedContext $understandingContext -Payload @{
        hook_event_name = "UserPromptSubmit"
        prompt = "Keep it focused on the meaning check, ykwim"
    }
    Test-PortableGuardSilent -Name "understanding implementation request" -Payload @{
        hook_event_name = "UserPromptSubmit"
        prompt = "add a hook off of ``do you understand what i mean?`` / ``dykwim`` / ``ykwim`` etc."
    }
    Test-PortableGuardSilent -Name "understanding quoted examples" -Payload @{
        hook_event_name = "UserPromptSubmit"
        prompt = 'Detect "do you understand what i mean?" and "ykwim".'
    }
    Test-PortableGuardSilent -Name "understanding code block" -Payload @{
        hook_event_name = "UserPromptSubmit"
        prompt = 'Test this fixture: ```text do you understand what i mean? ```'
    }
    Test-PortableGuardSilent -Name "understanding fixture text" -Payload @{
        hook_event_name = "UserPromptSubmit"
        prompt = "Example prompt: do you understand what i mean? should be covered."
    }
    Test-PortableGuardSilent -Name "understanding unquoted phrase discussion" -Payload @{
        hook_event_name = "UserPromptSubmit"
        prompt = "The phrase do you understand what i mean is the one we care about."
    }
    Test-PortableGuardSilent -Name "understanding unquoted review discussion" -Payload @{
        hook_event_name = "UserPromptSubmit"
        prompt = "Review whether do you understand what i mean should be supported."
    }
    Test-PortableGuardSilent -Name "understanding identifier text" -Payload @{
        hook_event_name = "UserPromptSubmit"
        prompt = "Enable ykwim_enabled in the test config."
    }
    Test-PortableGuardSilent -Name "understanding definition query" -Payload @{
        hook_event_name = "UserPromptSubmit"
        prompt = "What does dykwim mean?"
    }

    $oldUnderstandingOptOut = [Environment]::GetEnvironmentVariable("CODEX_PORTABLE_DISABLE_UNDERSTANDING_CHECK", "Process")
    [Environment]::SetEnvironmentVariable("CODEX_PORTABLE_DISABLE_UNDERSTANDING_CHECK", "1", "Process")
    try {
        Test-PortableGuardSilent -Name "understanding opt-out" -Payload @{
            hook_event_name = "UserPromptSubmit"
            prompt = "Do you understand what I mean?"
        }
    }
    finally {
        [Environment]::SetEnvironmentVariable("CODEX_PORTABLE_DISABLE_UNDERSTANDING_CHECK", $oldUnderstandingOptOut, "Process")
    }
}

$hookLauncherPath = Join-Path $repoRoot "codex\hooks\portable_guard.ps1"
if (Test-Path -LiteralPath $hookLauncherPath) {
    $oldCodexHome = [Environment]::GetEnvironmentVariable("CODEX_HOME", "Process")
    [Environment]::SetEnvironmentVariable("CODEX_HOME", (Join-Path $repoRoot "codex"), "Process")
    try {
        $dash = [char]0x2014
        $payload = @{
            hook_event_name = "PreToolUse"
            tool_name = "Bash"
            tool_input = @{
                command = "git commit -m `"bad $dash msg`""
            }
        } | ConvertTo-Json -Compress -Depth 8
        $launcherOutput = $payload | & $hookLauncherPath 2>&1
        if ($LASTEXITCODE -ne 0) {
            $problems.Add("portable hook PowerShell launcher failed")
        }
        elseif (-not (($launcherOutput -join "`n") -match '"permissionDecision":"deny"')) {
            $problems.Add("portable hook PowerShell launcher did not run guard")
        }
    }
    finally {
        [Environment]::SetEnvironmentVariable("CODEX_HOME", $oldCodexHome, "Process")
    }
}

Write-Host "repo: $repoRoot"
Write-Host "live: $liveHome"

if ($problems.Count -gt 0) {
    Write-Host ""
    Write-Host "problems:"
    foreach ($problem in $problems) {
        Write-Host "  $problem"
    }
    exit 1
}

Write-Host "doctor: ok"
