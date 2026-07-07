$portableHookGuardModules = @("git_closeout")

if (Get-Command cmd.exe -ErrorAction SilentlyContinue) {
    $hooksConfig = Get-Content -Raw -Encoding UTF8 -LiteralPath (Join-Path $repoRoot "codex\hooks.json") | ConvertFrom-Json
    $closeoutHook = $hooksConfig.hooks.Stop[0].hooks[0]
    if ($closeoutHook.commandWindows -match "\`$home\s*=") {
        $problems.Add("git closeout hook Windows command assigns read-only home variable")
    }
    if ($closeoutHook.commandWindows -notmatch "\`$codexHome") {
        $problems.Add("git closeout hook Windows command does not use codexHome variable")
    }
}

if (Get-Command git -ErrorAction SilentlyContinue) {
    $tempRoot = Join-Path ([System.IO.Path]::GetTempPath()) "compass-hook-$([guid]::NewGuid())"
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
