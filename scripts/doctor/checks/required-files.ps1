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
    "manifests\orchestration-ledger.schema.json",
    "manifests\policy-contracts.json",
    "manifests\portable-files.toml",
    "manifests\tool-surfaces.md",
    "local-docs\README.md",
    "local-docs\maintenance-learnings.md",
    "workflows\addition-intake.md",
    "workflows\codex-restart-recovery.md",
    "workflows\orchestration-ledger.md",
    "workflows\portable-config.md",
    "workflows\multi-thread-pr-coordination.md",
    "workflows\plan-template.md",
    "workflows\read-only-research.md",
    "workflows\agent-failures.md",
    "scripts\codex-restart-recovery.ps1",
    "scripts\orchestration-ledger.py",
    "scripts\orchestration-ledger.ps1",
    "scripts\skills-audit.py",
    "scripts\skills-audit.ps1",
    "scripts\test-orchestration-ledger.py",
    "scripts\test-skills-audit.py",
    "scripts\update-live.ps1",
    "scripts\validate-policy-contracts.py",
    "scripts\verify-live.ps1",
    "scripts\doctor\common.ps1",
    "scripts\doctor\checks\agents.ps1",
    "scripts\doctor\checks\hooks.ps1",
    "scripts\doctor\checks\manifest-boundaries.ps1",
    "scripts\doctor\checks\policy-contracts.ps1",
    "scripts\doctor\checks\required-files.ps1",
    "scripts\doctor\checks\restart-recovery.ps1",
    "scripts\doctor\checks\skills.ps1",
    "scripts\doctor\checks\text-policy.ps1",
    "scripts\doctor\hooks\base.tests.ps1",
    "scripts\doctor\hooks\common.ps1",
    "scripts\doctor\checks\claude.ps1",
    "workflows\claude-config.md"
)) {
    $fullPath = Join-Path $repoRoot $path
    if (-not (Test-Path $fullPath)) {
        $problems.Add("missing required file: $path")
    }
}
