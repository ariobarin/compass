<#
.SYNOPSIS
Reports canonical skill ownership, install targets, and same-name collisions.
#>
[CmdletBinding()]
param(
    [string]$AgentsHome,
    [string]$ClaudeHome,
    [string]$ProjectPath,
    [string[]]$AdditionalSkillRoot,
    [switch]$Json,
    [switch]$Plain
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

. "$PSScriptRoot\common.ps1"

function Resolve-OptionalPath {
    param([string]$Path)

    if (-not $Path) {
        return $null
    }
    return $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($Path)
}

function Add-DiscoveredRoot {
    param(
        [System.Collections.Generic.List[object]]$Roots,
        [string]$Path,
        [string]$Owner,
        [string]$Runtime
    )

    if (-not $Path) {
        return
    }

    $Roots.Add([pscustomobject]@{
        path = $Path
        owner = $Owner
        runtime = $Runtime
        exists = (Test-Path -LiteralPath $Path -PathType Container)
    })
}

function Get-SkillSourceRecords {
    param([string]$RepoRoot)

    $manifestPath = Join-Path $RepoRoot "manifests\skill-sources.json"
    if (-not (Test-Path -LiteralPath $manifestPath -PathType Leaf)) {
        throw "missing skill source manifest: $manifestPath"
    }

    $manifest = Get-Content -Raw -LiteralPath $manifestPath | ConvertFrom-Json
    if ($manifest.schema_version -ne 1 -or -not $manifest.skills) {
        throw "skill source manifest requires schema_version 1 and a non-empty skills array"
    }

    $records = @{}
    foreach ($record in @($manifest.skills)) {
        if (-not $record.name -or $records.ContainsKey($record.name)) {
            throw "skill source manifest contains a missing or duplicate name"
        }
        $records[$record.name] = $record
    }
    return $records
}

if ($Json -and $Plain) {
    throw "choose either -Json or -Plain"
}

$repoRoot = Get-RepoRoot
$agentsHomePath = Get-AgentsHome -AgentsHome $AgentsHome
$claudeHomePath = Get-ClaudeHome -ClaudeHome $ClaudeHome
$projectRoot = Resolve-OptionalPath -Path $ProjectPath
$portableNames = @(Get-PortableSkillNames | Sort-Object -Unique)
$sourceRecords = Get-SkillSourceRecords -RepoRoot $repoRoot

$roots = New-Object System.Collections.Generic.List[object]
if ($projectRoot) {
    Add-DiscoveredRoot -Roots $roots -Path (Join-Path $projectRoot ".agents\skills") -Owner "project" -Runtime "codex"
    Add-DiscoveredRoot -Roots $roots -Path (Join-Path $projectRoot ".claude\skills") -Owner "project" -Runtime "claude"
}
foreach ($root in @($AdditionalSkillRoot)) {
    Add-DiscoveredRoot -Roots $roots -Path (Resolve-OptionalPath -Path $root) -Owner "external" -Runtime "unspecified"
}

$canonicalSources = @{}
foreach ($name in $portableNames) {
    if (-not $sourceRecords.ContainsKey($name)) {
        throw "portable skill lacks a source record: $name"
    }
    $sourceRecord = $sourceRecords[$name]
    $sourcePath = Join-Path $repoRoot $sourceRecord.source
    $canonicalSources[$name] = New-Object System.Collections.Generic.List[object]
    $canonicalSources[$name].Add([pscustomobject]@{
        owner = $sourceRecord.owner
        runtime = "codex-source"
        path = $sourcePath
    })
}

$externalSkills = New-Object System.Collections.Generic.List[object]
foreach ($root in $roots) {
    if (-not $root.exists) {
        continue
    }

    foreach ($directory in Get-ChildItem -LiteralPath $root.path -Directory -ErrorAction Stop) {
        $record = [pscustomobject]@{
            name = $directory.Name
            owner = $root.owner
            runtime = $root.runtime
            path = $directory.FullName
        }
        $externalSkills.Add($record)
        if (-not $canonicalSources.ContainsKey($directory.Name)) {
            $canonicalSources[$directory.Name] = New-Object System.Collections.Generic.List[object]
        }
        $canonicalSources[$directory.Name].Add($record)
    }
}

$skills = @(
    foreach ($name in $portableNames) {
        $sourceRecord = $sourceRecords[$name]
        $targets = New-Object System.Collections.Generic.List[object]
        if ($sourceRecord.targets.codex -eq "copy") {
            $targets.Add([pscustomobject]@{
                runtime = "codex"
                mode = "copy"
                path = Join-Path (Join-Path $agentsHomePath "skills") $name
            })
        }
        if ($sourceRecord.targets.claude -ne "none") {
            $targets.Add([pscustomobject]@{
                runtime = "claude"
                mode = $sourceRecord.targets.claude
                path = Join-Path (Join-Path $claudeHomePath "skills") $name
            })
        }

        $upstream = $null
        if ($sourceRecord.PSObject.Properties.Name -contains "upstream") {
            $upstream = $sourceRecord.upstream
        }

        [pscustomobject]@{
            name = $name
            owner = $sourceRecord.owner
            source = Join-Path $repoRoot $sourceRecord.source
            source_relative = $sourceRecord.source
            profile = $sourceRecord.profile
            upstream = $upstream
            targets = @($targets.ToArray())
        }
    }
)

$collisions = @(
    foreach ($name in ($canonicalSources.Keys | Sort-Object)) {
        $sources = @($canonicalSources[$name].ToArray())
        $uniquePaths = @($sources.path | Sort-Object -Unique)
        if ($uniquePaths.Count -gt 1) {
            [pscustomobject]@{
                name = $name
                sources = $sources
            }
        }
    }
)

$result = [ordered]@{
    schema_version = 1
    repo = $repoRoot
    source_manifest = Join-Path $repoRoot "manifests\skill-sources.json"
    agents_home = $agentsHomePath
    claude_home = $claudeHomePath
    project = $projectRoot
    roots = @($roots.ToArray())
    skills = $skills
    external_skills = @($externalSkills.ToArray())
    collisions = $collisions
}

if ($Json) {
    $result | ConvertTo-Json -Depth 10
    exit 0
}

if ($Plain) {
    foreach ($skill in $skills) {
        Write-Output "skill=$($skill.name) owner=$($skill.owner) profile=$($skill.profile) source=$($skill.source)"
        if ($skill.upstream) {
            Write-Output "upstream=$($skill.name) repository=$($skill.upstream.repository) ref=$($skill.upstream.reviewed_ref) sha256=$($skill.upstream.source_sha256)"
        }
        foreach ($target in $skill.targets) {
            Write-Output "target=$($skill.name) runtime=$($target.runtime) mode=$($target.mode) path=$($target.path)"
        }
    }
    foreach ($collision in $collisions) {
        Write-Output "collision=$($collision.name) sources=$(@($collision.sources.path) -join ',')"
    }
    exit 0
}

Write-Host "portable skills: $($skills.Count)"
Write-Host "external skills: $($externalSkills.Count)"
Write-Host "collisions: $($collisions.Count)"
Write-Host ""
foreach ($skill in $skills) {
    Write-Host "$($skill.name) [$($skill.owner), $($skill.profile)]: $($skill.source)"
    if ($skill.upstream) {
        Write-Host "  upstream: $($skill.upstream.repository)@$($skill.upstream.reviewed_ref)"
    }
    foreach ($target in $skill.targets) {
        Write-Host "  $($target.runtime) [$($target.mode)]: $($target.path)"
    }
}

if ($collisions.Count -gt 0) {
    Write-Host ""
    Write-Host "same-name sources:"
    foreach ($collision in $collisions) {
        Write-Host "  $($collision.name)"
        foreach ($source in $collision.sources) {
            Write-Host "    $($source.owner) [$($source.runtime)]: $($source.path)"
        }
    }
}
