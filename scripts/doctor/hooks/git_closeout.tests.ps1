$portableHookGuardModules = @("git_closeout")

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
