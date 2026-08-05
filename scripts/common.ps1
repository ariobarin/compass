Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-RepoRoot {
    return (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
}

function Get-CodexHome {
    param([string]$CodexHome)

    if ($CodexHome) {
        return $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($CodexHome)
    }
    if ($env:CODEX_HOME) {
        return $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($env:CODEX_HOME)
    }
    return $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath(
        (Join-Path $env:USERPROFILE ".codex")
    )
}

function Get-AgentsHome {
    param([string]$AgentsHome)

    if ($AgentsHome) {
        return $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($AgentsHome)
    }
    return $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath(
        (Join-Path $HOME ".agents")
    )
}

function Get-ClaudeHome {
    param([string]$ClaudeHome)

    if ($ClaudeHome) {
        return $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($ClaudeHome)
    }
    return $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath(
        (Join-Path $HOME ".claude")
    )
}

$script:PortableManifest = $null

function Get-PortableJsonProperty {
    param(
        [object]$Object,
        [string]$Name
    )

    if ($null -eq $Object) {
        return $null
    }
    $property = $Object.PSObject.Properties[$Name]
    if ($null -eq $property) {
        return $null
    }
    return $property.Value
}

function Assert-PortableRelativePath {
    param(
        [string]$Value,
        [string]$Context,
        [switch]$SingleName
    )

    if ([string]::IsNullOrWhiteSpace($Value)) {
        throw "$Context entries must be non-empty strings"
    }
    $normalized = $Value.Replace("\", "/")
    if (
        [System.IO.Path]::IsPathRooted($normalized) -or
        $normalized -match '^[A-Za-z]:'
    ) {
        throw "$Context must contain relative paths: $Value"
    }
    $parts = @($normalized.Split("/"))
    if (@($parts | Where-Object { $_ -in @("", ".", "..") }).Count -gt 0) {
        throw "$Context contains an unsafe path: $Value"
    }
    if ($SingleName -and $parts.Count -ne 1) {
        throw "$Context entries must be one path name: $Value"
    }
}

function Assert-PortableManifestArray {
    param(
        [object]$Section,
        [string]$SectionName,
        [string]$Key,
        [switch]$SingleName
    )

    $property = $Section.PSObject.Properties[$Key]
    if ($null -eq $property) {
        throw "portable manifest requires $SectionName.$Key"
    }
    $value = $property.Value
    if ($value -isnot [System.Array]) {
        throw "portable manifest $SectionName.$Key must be a string array"
    }
    $items = @($value)
    $seen = @{}
    foreach ($item in $items) {
        if ($item -isnot [string]) {
            throw "portable manifest $SectionName.$Key must be a string array"
        }
        Assert-PortableRelativePath `
            -Value $item `
            -Context "portable manifest $SectionName.$Key" `
            -SingleName:$SingleName
        if ($seen.ContainsKey($item)) {
            throw "portable manifest $SectionName.$Key contains duplicates"
        }
        $seen[$item] = $true
    }
}

function Assert-PortableObjectShape {
    param(
        [object]$Object,
        [string]$Context,
        [string[]]$AllowedProperties
    )

    if ($null -eq $Object -or $Object -isnot [pscustomobject]) {
        throw "portable manifest requires $Context object"
    }
    $unknown = @(
        $Object.PSObject.Properties.Name |
            Where-Object { $_ -notin $AllowedProperties }
    )
    if ($unknown.Count -gt 0) {
        throw "$Context contains unsupported properties: $($unknown -join ', ')"
    }
}

function Assert-PortableManifestString {
    param(
        [object]$Section,
        [string]$SectionName,
        [string]$Key
    )

    $value = Get-PortableJsonProperty -Object $Section -Name $Key
    if ($value -isnot [string]) {
        throw "portable manifest $SectionName.$Key must be a string"
    }
    Assert-PortableRelativePath `
        -Value $value `
        -Context "portable manifest $SectionName.$Key" `
        -SingleName
}

function Get-PortableManifest {
    if ($script:PortableManifest) {
        return $script:PortableManifest
    }

    $path = Join-Path (Get-RepoRoot) "manifests\portable-files.json"
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        throw "missing portable manifest: $path"
    }
    try {
        $manifest = Get-Content -Raw -LiteralPath $path | ConvertFrom-Json
    }
    catch {
        throw "invalid portable manifest JSON: $($_.Exception.Message)"
    }

    Assert-PortableObjectShape `
        -Object $manifest `
        -Context "root" `
        -AllowedProperties @("codex", "agents", "claude")

    $codex = Get-PortableJsonProperty -Object $manifest -Name "codex"
    $agents = Get-PortableJsonProperty -Object $manifest -Name "agents"
    $claude = Get-PortableJsonProperty -Object $manifest -Name "claude"
    Assert-PortableObjectShape -Object $codex -Context "codex" -AllowedProperties @("config", "files", "agents")
    Assert-PortableObjectShape -Object $agents -Context "agents" -AllowedProperties @("skills")
    Assert-PortableObjectShape -Object $claude -Context "claude" -AllowedProperties @("files", "skills", "agents")

    Assert-PortableManifestString -Section $codex -SectionName "codex" -Key "config"
    Assert-PortableManifestArray -Section $codex -SectionName "codex" -Key "files"
    Assert-PortableManifestArray -Section $codex -SectionName "codex" -Key "agents" -SingleName
    Assert-PortableManifestArray -Section $agents -SectionName "agents" -Key "skills" -SingleName
    Assert-PortableManifestArray -Section $claude -SectionName "claude" -Key "files"
    Assert-PortableManifestArray -Section $claude -SectionName "claude" -Key "skills" -SingleName
    Assert-PortableManifestArray -Section $claude -SectionName "claude" -Key "agents" -SingleName

    $script:PortableManifest = $manifest
    return $script:PortableManifest
}

function Get-PortableManifestArray {
    param(
        [string]$Section,
        [string]$Key
    )

    $manifest = Get-PortableManifest
    $sectionValue = Get-PortableJsonProperty -Object $manifest -Name $Section
    return @(Get-PortableJsonProperty -Object $sectionValue -Name $Key)
}

function Get-PortableManifestString {
    param(
        [string]$Section,
        [string]$Key
    )

    $manifest = Get-PortableManifest
    $sectionValue = Get-PortableJsonProperty -Object $manifest -Name $Section
    return [string](Get-PortableJsonProperty -Object $sectionValue -Name $Key)
}

function New-DirectoryForFile {
    param([string]$Path)

    $dir = Split-Path -Parent $Path
    if ($dir -and -not (Test-Path -LiteralPath $dir)) {
        New-Item -ItemType Directory -Force $dir | Out-Null
    }
}

function Get-NormalizedPortablePath {
    param([string]$Path)

    $fullPath = [System.IO.Path]::GetFullPath($Path)
    $pathRoot = [System.IO.Path]::GetPathRoot($fullPath)
    if ($fullPath.Length -gt $pathRoot.Length) {
        $fullPath = $fullPath.TrimEnd(
            [System.IO.Path]::DirectorySeparatorChar,
            [System.IO.Path]::AltDirectorySeparatorChar
        )
    }
    return $fullPath
}

function Get-PortableDescendantPrefix {
    param([string]$Path)

    $separator = [System.IO.Path]::DirectorySeparatorChar
    if ($Path.EndsWith([string]$separator, [System.StringComparison]::Ordinal)) {
        return $Path
    }
    return $Path + $separator
}

function Assert-PortablePathHasNoReparsePoint {
    param([string]$Path)

    $fullPath = Get-NormalizedPortablePath -Path $Path
    $pathRoot = [System.IO.Path]::GetPathRoot($fullPath)
    $separators = [char[]]@(
        [System.IO.Path]::DirectorySeparatorChar,
        [System.IO.Path]::AltDirectorySeparatorChar
    )
    $relative = $fullPath.Substring($pathRoot.Length).TrimStart($separators)
    $current = $pathRoot
    foreach ($part in @($relative.Split($separators) | Where-Object { $_ })) {
        $current = Join-Path $current $part
        $item = Get-Item -Force -LiteralPath $current -ErrorAction SilentlyContinue
        if ($null -eq $item) {
            break
        }
        $isReparsePoint = (
            $item.Attributes -band [System.IO.FileAttributes]::ReparsePoint
        ) -ne 0
        $hasLinkType = (
            $null -ne $item.PSObject.Properties["LinkType"] -and
            -not [string]::IsNullOrEmpty([string]$item.LinkType)
        )
        if ($isReparsePoint -or $hasLinkType) {
            throw "portable paths cannot cross links or junctions: $current"
        }
    }
}

function Assert-PortableTreeHasNoReparsePoint {
    param([string]$Root)

    Assert-PortablePathHasNoReparsePoint -Path $Root
    if (-not (Test-Path -LiteralPath $Root -PathType Container)) {
        return
    }
    $pending = New-Object System.Collections.Generic.Queue[string]
    $pending.Enqueue($Root)
    while ($pending.Count -gt 0) {
        $current = $pending.Dequeue()
        foreach ($item in Get-ChildItem -LiteralPath $current -Force) {
            $isReparsePoint = (
                $item.Attributes -band [System.IO.FileAttributes]::ReparsePoint
            ) -ne 0
            $hasLinkType = (
                $null -ne $item.PSObject.Properties["LinkType"] -and
                -not [string]::IsNullOrEmpty([string]$item.LinkType)
            )
            if ($isReparsePoint -or $hasLinkType) {
                throw "portable directory trees cannot contain links or junctions: $($item.FullName)"
            }
            if ($item.PSIsContainer) {
                $pending.Enqueue($item.FullName)
            }
        }
    }
}

function Assert-PathUnderRoot {
    param(
        [string]$Path,
        [string]$Root
    )

    $fullRoot = Get-NormalizedPortablePath -Path $Root
    $fullPath = Get-NormalizedPortablePath -Path $Path
    Assert-PortablePathHasNoReparsePoint -Path $fullPath
    $prefix = Get-PortableDescendantPrefix -Path $fullRoot
    if (
        $fullPath -eq $fullRoot -or
        -not $fullPath.StartsWith($prefix, [System.StringComparison]::OrdinalIgnoreCase)
    ) {
        throw "refusing to write outside allowed root: $Path"
    }
}

function Test-PortablePathsOverlap {
    param(
        [string]$Left,
        [string]$Right
    )

    $leftPath = Get-NormalizedPortablePath -Path $Left
    $rightPath = Get-NormalizedPortablePath -Path $Right
    if ($leftPath -eq $rightPath) {
        return $true
    }
    $leftPrefix = Get-PortableDescendantPrefix -Path $leftPath
    $rightPrefix = Get-PortableDescendantPrefix -Path $rightPath
    return (
        $leftPath.StartsWith($rightPrefix, [System.StringComparison]::OrdinalIgnoreCase) -or
        $rightPath.StartsWith($leftPrefix, [System.StringComparison]::OrdinalIgnoreCase)
    )
}

function Assert-PortableRootsDisjoint {
    param(
        [string]$RepoRoot,
        [string]$CodexHome,
        [string]$AgentsHome,
        [string]$ClaudeHome
    )

    $roots = @(
        [pscustomobject]@{ Name = "repository"; Path = $RepoRoot }
        [pscustomobject]@{ Name = "Codex home"; Path = $CodexHome }
        [pscustomobject]@{ Name = "agents home"; Path = $AgentsHome }
        [pscustomobject]@{ Name = "Claude home"; Path = $ClaudeHome }
    )
    foreach ($root in $roots) {
        Assert-PortablePathHasNoReparsePoint -Path $root.Path
    }
    for ($leftIndex = 0; $leftIndex -lt $roots.Count; $leftIndex++) {
        for ($rightIndex = $leftIndex + 1; $rightIndex -lt $roots.Count; $rightIndex++) {
            $left = $roots[$leftIndex]
            $right = $roots[$rightIndex]
            if (Test-PortablePathsOverlap -Left $left.Path -Right $right.Path) {
                throw "portable roots overlap: $($left.Name) and $($right.Name)"
            }
        }
    }
}

function Add-PortableItem {
    param(
        [System.Collections.Generic.List[object]]$Items,
        [string]$Type,
        [string]$RepoPath,
        [string]$LivePath,
        [string]$LiveRoot,
        [string]$BackupScope
    )

    $Items.Add([pscustomobject]@{
        Type = $Type
        RepoPath = $RepoPath
        LivePath = $LivePath
        LiveRoot = $LiveRoot
        BackupScope = $BackupScope
    })
}

function Get-PortableFileMap {
    param(
        [string]$RepoRoot,
        [string]$CodexHome,
        [string]$AgentsHome,
        [string]$ClaudeHome
    )

    if (-not $AgentsHome) {
        $AgentsHome = Get-AgentsHome
    }
    if (-not $ClaudeHome) {
        $ClaudeHome = Get-ClaudeHome
    }
    Assert-PortableRootsDisjoint `
        -RepoRoot $RepoRoot `
        -CodexHome $CodexHome `
        -AgentsHome $AgentsHome `
        -ClaudeHome $ClaudeHome

    $items = New-Object System.Collections.Generic.List[object]
    $config = Get-PortableManifestString -Section "codex" -Key "config"
    Add-PortableItem -Items $items -Type "config" `
        -RepoPath (Join-Path $RepoRoot "codex\$config") `
        -LivePath (Join-Path $CodexHome "config.toml") `
        -LiveRoot $CodexHome -BackupScope "codex"
    foreach ($relative in Get-PortableManifestArray -Section "codex" -Key "files") {
        Add-PortableItem -Items $items -Type "file" `
            -RepoPath (Join-Path (Join-Path $RepoRoot "codex") $relative) `
            -LivePath (Join-Path $CodexHome $relative) `
            -LiveRoot $CodexHome -BackupScope "codex"
    }
    foreach ($agent in Get-PortableManifestArray -Section "codex" -Key "agents") {
        Add-PortableItem -Items $items -Type "file" `
            -RepoPath (Join-Path $RepoRoot "codex\agents\$agent.toml") `
            -LivePath (Join-Path $CodexHome "agents\$agent.toml") `
            -LiveRoot $CodexHome -BackupScope "codex"
    }
    foreach ($skill in Get-PortableManifestArray -Section "agents" -Key "skills") {
        Add-PortableItem -Items $items -Type "dir" `
            -RepoPath (Join-Path $RepoRoot "codex\skills\$skill") `
            -LivePath (Join-Path $AgentsHome "skills\$skill") `
            -LiveRoot $AgentsHome -BackupScope "agents"
    }
    foreach ($relative in Get-PortableManifestArray -Section "claude" -Key "files") {
        Add-PortableItem -Items $items -Type "file" `
            -RepoPath (Join-Path (Join-Path $RepoRoot "claude") $relative) `
            -LivePath (Join-Path $ClaudeHome $relative) `
            -LiveRoot $ClaudeHome -BackupScope "claude"
    }
    foreach ($skill in Get-PortableManifestArray -Section "claude" -Key "skills") {
        Add-PortableItem -Items $items -Type "dir" `
            -RepoPath (Join-Path $RepoRoot "claude\skills\$skill") `
            -LivePath (Join-Path $ClaudeHome "skills\$skill") `
            -LiveRoot $ClaudeHome -BackupScope "claude"
    }
    foreach ($agent in Get-PortableManifestArray -Section "claude" -Key "agents") {
        Add-PortableItem -Items $items -Type "file" `
            -RepoPath (Join-Path $RepoRoot "claude\agents\$agent.md") `
            -LivePath (Join-Path $ClaudeHome "agents\$agent.md") `
            -LiveRoot $ClaudeHome -BackupScope "claude"
    }

    foreach ($item in $items) {
        Assert-PathUnderRoot -Path $item.RepoPath -Root $RepoRoot
        Assert-PathUnderRoot -Path $item.LivePath -Root $item.LiveRoot
    }
    Assert-PortableTargetsDisjoint -Items $items
    $backupBase = Join-Path $CodexHome "portable-backups"
    foreach ($item in $items) {
        if (Test-PortablePathsOverlap -Left $item.LivePath -Right $backupBase) {
            throw "portable target overlaps backup root: $($item.LivePath)"
        }
    }
    return $items
}

function Assert-PortableTargetsDisjoint {
    param([object[]]$Items)

    $targets = @($Items)
    for ($leftIndex = 0; $leftIndex -lt $targets.Count; $leftIndex++) {
        for ($rightIndex = $leftIndex + 1; $rightIndex -lt $targets.Count; $rightIndex++) {
            $left = $targets[$leftIndex]
            $right = $targets[$rightIndex]
            if (Test-PortablePathsOverlap -Left $left.LivePath -Right $right.LivePath) {
                throw "portable targets overlap: $($left.LivePath) and $($right.LivePath)"
            }
        }
    }
}

function Backup-LiveItem {
    param(
        [string]$LivePath,
        [string]$BackupRoot,
        [string]$BackupAllowedRoot,
        [string]$LiveRoot,
        [string]$BackupScope
    )

    if (-not (Test-Path -LiteralPath $LivePath)) {
        return
    }
    Assert-PathUnderRoot -Path $LivePath -Root $LiveRoot
    Assert-PathUnderRoot -Path $BackupRoot -Root $BackupAllowedRoot
    $relative = $LivePath.Substring($LiveRoot.Length).TrimStart("\", "/")
    $backupPath = Join-Path (Join-Path $BackupRoot $BackupScope) $relative
    Assert-PathUnderRoot -Path $backupPath -Root $BackupAllowedRoot
    if (Test-Path -LiteralPath $LivePath -PathType Container) {
        Assert-PortableTreeHasNoReparsePoint -Root $LivePath
        New-Item -ItemType Directory -Force (Split-Path -Parent $backupPath) | Out-Null
        Copy-Item -LiteralPath $LivePath -Destination $backupPath -Recurse -Force
        return
    }
    New-DirectoryForFile -Path $backupPath
    Copy-Item -LiteralPath $LivePath -Destination $backupPath -Force
}

function Get-PortableUtf8Lines {
    param([string]$Path)

    $encoding = [System.Text.UTF8Encoding]::new($false, $true)
    return [System.IO.File]::ReadAllLines($Path, $encoding)
}

function ConvertFrom-PortableConfigSectionHeader {
    param([string]$Header)

    $segment = '(?:''([A-Za-z0-9_-]+)''|"([A-Za-z0-9_-]+)"|([A-Za-z0-9_-]+))'
    if ($Header -cnotmatch ('^' + $segment + '(?:\s*\.\s*' + $segment + ')*$')) {
        return $Header
    }
    $parts = foreach ($match in [regex]::Matches($Header, $segment)) {
        @($match.Groups[1].Value, $match.Groups[2].Value, $match.Groups[3].Value) |
            Where-Object { $_ } |
            Select-Object -First 1
    }
    return $parts -join "."
}

function Get-PortableConfigEntries {
    param([string]$Path)

    $entries = New-Object System.Collections.Generic.List[object]
    $section = ""
    $seen = [System.Collections.Generic.Dictionary[string, bool]]::new(
        [System.StringComparer]::Ordinal
    )
    foreach ($line in Get-PortableUtf8Lines -Path $Path) {
        $trimmed = $line.Trim()
        if (-not $trimmed -or $trimmed.StartsWith("#")) {
            continue
        }
        if ($trimmed -match '^\[([A-Za-z0-9_.-]+)\]$') {
            $section = $Matches[1]
            continue
        }
        if ($line -notmatch '^\s*([A-Za-z0-9_.-]+)\s*=\s*(.+?)\s*$') {
            throw "portable config supports only scalar keys: $line"
        }
        $key = $Matches[1]
        $value = $Matches[2]
        $identity = "$section`n$key"
        if ($seen.ContainsKey($identity)) {
            throw "portable config contains duplicate key: $identity"
        }
        $seen[$identity] = $true
        $entries.Add([pscustomobject]@{
            Section = $section
            Key = $key
            Value = $value
        })
    }
    return $entries
}

function Get-LiveConfigValueMap {
    param([string]$Path)

    $values = [System.Collections.Generic.Dictionary[string, string]]::new(
        [System.StringComparer]::Ordinal
    )
    $section = ""
    foreach ($line in Get-PortableUtf8Lines -Path $Path) {
        if ($line -match '^\s*\[(.+)\]\s*(?:#.*)?$') {
            $section = ConvertFrom-PortableConfigSectionHeader -Header $Matches[1]
            continue
        }
        if ($line -match '^\s*([A-Za-z0-9_.-]+)\s*=\s*(.+?)\s*$') {
            $values["$section`n$($Matches[1])"] = $Matches[2]
        }
    }
    return $values
}

function Get-PortableConfigDrift {
    param(
        [string]$Source,
        [string]$Destination
    )

    $live = [System.Collections.Generic.Dictionary[string, string]]::new(
        [System.StringComparer]::Ordinal
    )
    if (Test-Path -LiteralPath $Destination -PathType Leaf) {
        $live = Get-LiveConfigValueMap -Path $Destination
    }
    foreach ($entry in Get-PortableConfigEntries -Path $Source) {
        $identity = "$($entry.Section)`n$($entry.Key)"
        if (-not $live.ContainsKey($identity)) {
            $state = "missing"
        }
        elseif ($live[$identity] -ne $entry.Value) {
            $state = "differs"
        }
        else {
            continue
        }
        $key = if ($entry.Section) {
            "$($entry.Section).$($entry.Key)"
        }
        else {
            $entry.Key
        }
        [pscustomobject]@{
            Key = $key
            State = $state
        }
    }
}

function Merge-PortableConfig {
    param(
        [string]$Source,
        [string]$Destination
    )

    $entries = @(Get-PortableConfigEntries -Path $Source)
    if (-not (Test-Path -LiteralPath $Destination -PathType Leaf)) {
        New-DirectoryForFile -Path $Destination
        Copy-Item -LiteralPath $Source -Destination $Destination -Force
        return
    }

    $lines = New-Object System.Collections.Generic.List[string]
    foreach ($line in Get-PortableUtf8Lines -Path $Destination) {
        $lines.Add($line)
    }
    foreach ($entry in $entries) {
        $start = 0
        $end = $lines.Count
        if ($entry.Section) {
            $start = -1
            for ($index = 0; $index -lt $lines.Count; $index++) {
                if ($lines[$index] -match '^\s*\[(.+)\]\s*(?:#.*)?$') {
                    if ($start -ge 0) {
                        $end = $index
                        break
                    }
                    $candidateSection = ConvertFrom-PortableConfigSectionHeader -Header $Matches[1]
                    if ($candidateSection -ceq $entry.Section) {
                        $start = $index + 1
                    }
                }
            }
            if ($start -lt 0) {
                if ($lines.Count -gt 0 -and $lines[$lines.Count - 1].Trim()) {
                    $lines.Add("")
                }
                $lines.Add("[$($entry.Section)]")
                $lines.Add("$($entry.Key) = $($entry.Value)")
                continue
            }
        }
        else {
            for ($index = 0; $index -lt $lines.Count; $index++) {
                if ($lines[$index] -match '^\s*\[') {
                    $end = $index
                    break
                }
            }
        }

        $found = $false
        for ($index = $start; $index -lt $end; $index++) {
            if ($lines[$index] -match '^\s*([A-Za-z0-9_.-]+)\s*=') {
                if ($Matches[1] -ceq $entry.Key) {
                    $lines[$index] = "$($entry.Key) = $($entry.Value)"
                    $found = $true
                    break
                }
            }
        }
        if (-not $found) {
            $lines.Insert($end, "$($entry.Key) = $($entry.Value)")
        }
    }
    $content = ($lines -join "`n").TrimEnd() + "`n"
    [System.IO.File]::WriteAllText(
        $Destination,
        $content,
        [System.Text.UTF8Encoding]::new($false)
    )
}

function Test-PortableConfigInSync {
    param(
        [string]$Source,
        [string]$Destination
    )

    if (-not (Test-Path -LiteralPath $Destination -PathType Leaf)) {
        return $false
    }
    return @(Get-PortableConfigDrift -Source $Source -Destination $Destination).Count -eq 0
}

function Copy-PortableItem {
    param(
        [string]$Source,
        [string]$Destination,
        [string]$Type,
        [string]$AllowedRoot
    )

    $sourceType = if ($Type -eq "dir") { "Container" } else { "Leaf" }
    if (-not (Test-Path -LiteralPath $Source -PathType $sourceType)) {
        throw "missing portable $Type source: $Source"
    }
    Assert-PortableTreeHasNoReparsePoint -Root $Source
    Assert-PathUnderRoot -Path $Destination -Root $AllowedRoot
    if ($Type -eq "dir") {
        if (Test-Path -LiteralPath $Destination) {
            Assert-PortableTreeHasNoReparsePoint -Root $Destination
            Remove-Item -LiteralPath $Destination -Recurse -Force
        }
        New-Item -ItemType Directory -Force (Split-Path -Parent $Destination) | Out-Null
        Copy-Item -LiteralPath $Source -Destination $Destination -Recurse -Force
        return
    }
    if (Test-Path -LiteralPath $Destination -PathType Container) {
        Assert-PortableTreeHasNoReparsePoint -Root $Destination
        Remove-Item -LiteralPath $Destination -Recurse -Force
    }
    New-DirectoryForFile -Path $Destination
    if ($Type -eq "config") {
        Merge-PortableConfig -Source $Source -Destination $Destination
        return
    }
    Copy-Item -LiteralPath $Source -Destination $Destination -Force
}

function Get-PortableDirectoryFileMap {
    param([string]$Root)

    $map = @{}
    if (-not (Test-Path -LiteralPath $Root -PathType Container)) {
        return $map
    }
    Assert-PortableTreeHasNoReparsePoint -Root $Root
    $resolvedRoot = (Resolve-Path -LiteralPath $Root).Path
    foreach ($file in Get-ChildItem -LiteralPath $Root -Recurse -File -Force) {
        $relative = $file.FullName.Substring($resolvedRoot.Length).TrimStart("\", "/")
        $map[$relative] = (Get-FileHash -Algorithm SHA256 -LiteralPath $file.FullName).Hash
    }
    return $map
}

function Test-PortableFileMapsEqual {
    param(
        [hashtable]$Expected,
        [hashtable]$Actual
    )

    if ($Expected.Count -ne $Actual.Count) {
        return $false
    }
    foreach ($key in $Expected.Keys) {
        if (-not $Actual.ContainsKey($key) -or $Expected[$key] -ne $Actual[$key]) {
            return $false
        }
    }
    return $true
}

function Test-PortableItemInSync {
    param([object]$Item)

    $sourceType = if ($Item.Type -eq "dir") { "Container" } else { "Leaf" }
    if (-not (Test-Path -LiteralPath $Item.RepoPath -PathType $sourceType)) {
        throw "missing portable $($Item.Type) source: $($Item.RepoPath)"
    }
    if (-not (Test-Path -LiteralPath $Item.LivePath)) {
        return $false
    }
    if ($Item.Type -eq "config") {
        return Test-PortableConfigInSync `
            -Source $Item.RepoPath `
            -Destination $Item.LivePath
    }
    if ($Item.Type -eq "file") {
        if (-not (Test-Path -LiteralPath $Item.LivePath -PathType Leaf)) {
            return $false
        }
        $sourceHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $Item.RepoPath).Hash
        $liveHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $Item.LivePath).Hash
        return $sourceHash -eq $liveHash
    }
    if (-not (Test-Path -LiteralPath $Item.LivePath -PathType Container)) {
        return $false
    }
    $expected = Get-PortableDirectoryFileMap -Root $Item.RepoPath
    $actual = Get-PortableDirectoryFileMap -Root $Item.LivePath
    return Test-PortableFileMapsEqual -Expected $expected -Actual $actual
}
