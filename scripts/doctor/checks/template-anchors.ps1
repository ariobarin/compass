# Shared structural anchors that control-document template copies must carry.
# The maintainer templates, workspace-steward project-template copies, and
# using-goals embedded blocks are intentional canonicals for different audiences.
# They have different field sets, so none is generated from another. This check
# pins the structural anchors shared by each participating copy so no family can
# silently lose its core identity.

$anchors = @(
    @{ File = "workflows\templates\plan.md"; Anchor = "# Plan:" }
    @{ File = "workflows\templates\goal.md"; Anchor = "Goal ID:" }
    @{ File = "workflows\templates\catalog.md"; Anchor = "# Work Catalog" }
    @{ File = "workflows\templates\assignment.md"; Anchor = "Assignment ID:" }
    @{ File = "workflows\templates\checkpoint.md"; Anchor = "# Checkpoint" }
    @{ File = "workflows\templates\decision.md"; Anchor = "Decision ID:" }
    @{ File = "codex\skills\workspace-steward\references\project-template\local-docs\plans\TEMPLATE.md"; Anchor = "# Plan:" }
    @{ File = "codex\skills\workspace-steward\references\project-template\local-docs\goals\TEMPLATE.md"; Anchor = "Goal ID:" }
    @{ File = "codex\skills\workspace-steward\references\project-template\local-docs\catalogs\TEMPLATE.md"; Anchor = "# Work Catalog" }
    @{ File = "codex\skills\workspace-steward\references\project-template\local-docs\assignments\TEMPLATE.md"; Anchor = "Assignment ID:" }
    @{ File = "codex\skills\workspace-steward\references\project-template\local-docs\checkpoints\TEMPLATE.md"; Anchor = "# Checkpoint" }
    @{ File = "codex\skills\workspace-steward\references\project-template\local-docs\decisions\TEMPLATE.md"; Anchor = "Decision ID:" }
    @{ File = "codex\skills\using-goals\references\goal-contracts.md"; Anchor = "Goal ID:" }
    @{ File = "codex\skills\using-goals\references\goal-contracts.md"; Anchor = "# Work Catalog" }
    @{ File = "codex\skills\using-goals\references\goal-contracts.md"; Anchor = "Assignment ID:" }
    @{ File = "codex\skills\using-goals\references\goal-contracts.md"; Anchor = "## Checkpoint" }
)

foreach ($entry in $anchors) {
    $relative = $entry["File"]
    $anchor = $entry["Anchor"]
    $path = Join-Path $repoRoot $relative
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        $problems.Add("template anchor file missing: $relative")
        continue
    }
    $text = Get-Content -Raw -LiteralPath $path
    if (-not $text.Contains($anchor)) {
        $problems.Add("template missing shared anchor '$anchor' in $relative")
    }
}
