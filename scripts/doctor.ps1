param(
    [string]$CodexHome
)

. "$PSScriptRoot\common.ps1"

$repoRoot = Get-RepoRoot
$liveHome = Get-CodexHome -CodexHome $CodexHome
$problems = New-Object System.Collections.Generic.List[string]

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    $problems.Add("git is not on PATH")
}

foreach ($path in @(
    "codex\AGENTS.md",
    "codex\keybindings.json",
    "codex\config.review.toml",
    "manifests\portable-files.toml"
)) {
    $fullPath = Join-Path $repoRoot $path
    if (-not (Test-Path $fullPath)) {
        $problems.Add("missing required file: $path")
    }
}

$blockedNames = @(
    "auth.json",
    "history.jsonl",
    "session_index.jsonl",
    "installation_id",
    "cap_sid"
)

foreach ($blocked in $blockedNames) {
    $matches = Get-ChildItem -Path $repoRoot -Recurse -Force -File -Filter $blocked -ErrorAction SilentlyContinue
    foreach ($match in $matches) {
        $problems.Add("blocked local-only file tracked in repo tree: $($match.FullName)")
    }
}

$blockedDirs = @(
    ".sandbox",
    ".sandbox-bin",
    ".sandbox-secrets",
    ".tmp",
    "cache",
    "log",
    "memories",
    "plugins",
    "sessions",
    "sqlite",
    "tmp",
    "worktrees"
)

foreach ($dir in Get-ChildItem -Path $repoRoot -Recurse -Force -Directory -ErrorAction SilentlyContinue) {
    if ($blockedDirs -contains $dir.Name) {
        $problems.Add("blocked local-only directory in repo tree: $($dir.FullName)")
    }
}

$dashChars = @([char]0x2014, [char]0x2013)
$textFiles = Get-ChildItem -Path $repoRoot -Recurse -Force -File |
    Where-Object {
        $_.FullName -notmatch "\\.git\\" -and
        $_.Extension -in @(".md", ".toml", ".json", ".ps1", ".yaml", ".yml", ".txt")
    }

foreach ($file in $textFiles) {
    $content = Get-Content -Raw -LiteralPath $file.FullName
    foreach ($char in $dashChars) {
        if ($content.Contains($char)) {
            $problems.Add("disallowed dash character in: $($file.FullName)")
            break
        }
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
