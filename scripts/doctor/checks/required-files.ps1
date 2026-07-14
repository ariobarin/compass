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
    ".github\workflows\orchestration-ledger-checks.yml",
    ".github\workflows\portable-checks.yml",
    "AGENTS.md",
    "carried\webmcp\README.md",
    "claude\agents\behavior-validator.md",
    "claude\agents\benchmark-infra-reviewer.md",
    "codex\AGENTS.md",
    "codex\agents\behavior-validator.toml",
    "codex\agents\benchmark-infra-reviewer.toml",
    "codex\hooks.json",
    "codex\hooks\README.md",
    "codex\hooks\portable_guard.py",
    "codex\hooks\portable_guard.ps1",
    "codex\hooks\portable_guard.sh",
    "codex\keybindings.json",
    "codex\config.review.toml",
    "codex\skills\behavior-validator\SKILL.md",
    "codex\skills\behavior-validator\references\contract-template.md",
    "codex\skills\behavior-validator\references\report-schema.md",
    "codex\skills\behavior-validator\scripts\prepare-workspace.py",
    "codex\skills\pr-review-loop\scripts\build-review-bundle.py",
    "manifests\orchestration-ledger.schema.json",
    "manifests\policy-contracts.json",
    "manifests\plugins.json",
    "manifests\portable-files.toml",
    "manifests\skill-sources.json",
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
    "scripts\_orchestration_ledger_cli.py",
    "scripts\_orchestration_ledger_core.py",
    "scripts\_orchestration_ledger_model.py",
    "scripts\_orchestration_ledger_mutation.py",
    "scripts\_orchestration_ledger_parser.py",
    "scripts\_orchestration_ledger_storage.py",
    "scripts\orchestration-ledger.ps1",
    "scripts\portable-data.py",
    "scripts\skills-audit.py",
    "scripts\skills-audit.ps1",
    "scripts\test-behavior-validator-workspace.py",
    "scripts\test-orchestration-ledger-lock.py",
    "scripts\test-orchestration-ledger-output.py",
    "scripts\test-orchestration-ledger.py",
    "scripts\_test_orchestration_ledger_common.py",
    "scripts\_test_orchestration_ledger_cases1.py",
    "scripts\_test_orchestration_ledger_cases2.py",
    "scripts\_test_orchestration_ledger_cases3.py",
    "scripts\test-review-bundle.py",
    "scripts\test-skills-audit.py",
    "scripts\test-validate-skill-sources.py",
    "scripts\update-live.ps1",
    "scripts\sync-plugins.ps1",
    "scripts\validate-policy-contracts.py",
    "scripts\validate-skill-sources.py",
    "scripts\verify-live.ps1",
    "scripts\doctor\common.ps1",
    "scripts\doctor\checks\agents.ps1",
    "scripts\doctor\checks\hooks.ps1",
    "scripts\doctor\checks\manifest-boundaries.ps1",
    "scripts\doctor\checks\plugins.ps1",
    "scripts\doctor\checks\policy-contracts.ps1",
    "scripts\doctor\checks\required-files.ps1",
    "scripts\doctor\checks\restart-recovery.ps1",
    "scripts\doctor\checks\skill-sources.ps1",
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
