# Workflows

These files guide recurring Compass maintenance. They are not installed into a
Codex home, user-skill home, or Claude home.

Choose the workflow by the decision or operation it owns:

| Work | Workflow |
| --- | --- |
| Decide whether a durable artifact belongs in Compass | [addition-intake.md](addition-intake.md) |
| Audit skills, agents, hooks, docs, manifests, and config | [compass-review-program.md](compass-review-program.md) |
| Maintain separate Claude global guidance and derived surfaces | [claude-config.md](claude-config.md) |
| Install, diff, snapshot, verify, or update portable source | [portable-config.md](portable-config.md) |
| Preserve one objective across contexts and delegates | [long-running-work.md](long-running-work.md) |
| Operate the local mechanical control index | [orchestration-ledger.md](orchestration-ledger.md) |
| Author a reviewed durable plan artifact | [plan-template.md](plan-template.md) |
| Coordinate parallel PR work without public sprawl | [multi-thread-pr-coordination.md](multi-thread-pr-coordination.md) |
| Recover unfinished Codex sessions after restart | [codex-restart-recovery.md](codex-restart-recovery.md) |
| Map repository or external evidence before editing | [read-only-research.md](read-only-research.md) |
| Turn repeated agent failures into durable improvements | [agent-failures.md](agent-failures.md) |
| Install and refresh the separately owned `which-llm` plugin | [which-llm-plugin.md](which-llm-plugin.md) |

Use [../glossary.md](../glossary.md) when a term changes ownership, authority,
or lifecycle behavior. Keep workflows focused on maintainer action. Put reusable
runtime judgment in skills or agents, and put exact mechanics in scripts.
