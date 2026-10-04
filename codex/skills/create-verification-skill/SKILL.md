---
name: create-verification-skill
description: Create or update a project-local skill for repeatedly launching, driving, and proving real application behavior. Use when asked for a project control skill, when recurring verification needs a reusable recipe, or when existing verification instructions have drifted.
---

# Create Verification Skill

Write for the next agent reading cold, mid-task. A verification skill is a
proven way to drive the real app and capture evidence.

## Interview The Repo

Find the project's existing verification instructions and harness first.
Update their owning skill; create one only when repeat use justifies maintained
guidance. Keep one-time verification in the task.

Read the repo's own launch commands, user entry points, and existing harnesses
to establish how to run, drive, and observe it. Reuse those tools before adding
machinery. Ask only for prerequisites the repo cannot answer. Keep the skill in
the project's supported skill directory.

## Capture The Working Recipe

Ground every instruction in the actual project and available tools:

- **Launch:** the command, prerequisites, readiness signal, and read-only check
  that identifies the intended instance. After surprising behavior, establish
  health and a known state before driving again.
- **Drive and evidence:** real user actions with stable commands or selectors,
  their observable outcome and relevant side effects, and a named evidence
  location. Capture the action and result. Verify what a dry-run actually
  skips before relying on it to protect state.
- **Ownership and cleanup:** isolate verification data and sessions, preserve
  the user's live state, and track the instances the run creates. Clean up only
  instances and scratch state created by the run, including after failed
  attempts. Evidence must survive cleanup. Resolve uncertain ownership before
  driving. Retain a preview explicitly intended for user inspection; name its
  owner and intended lifetime.

Document what the next agent needs to run and interpret verification. Point to
the existing harness for mechanics it owns instead of narrating its
implementation. Keep project gotchas that inspection or execution established.
Add helpers or feature references only when they earn repeated use; invoke each
helper in the instructions.

## Prove Before Calling It Done

Run the skill's own instructions end to end: launch, establish readiness,
exercise a real user path, capture evidence, clean up, and confirm that evidence
still exists. A recipe that has never been executed is a draft, not a
deliverable.

For upkeep, follow changed or suspect recipes and re-run each corrected path.
Broaden coverage when the risk warrants it, using `$test-for-risk` when
available. Source inspection alone cannot establish that a drive works.

Edit only the verification skill's directory and helpers it owns. Correct
instruction or harness drift; report product regressions separately. If the
checkout cannot run or a prerequisite blocks proof, report the precise blocker
and keep the affected recipe a draft. Return what was exercised, its evidence,
and remaining limits.

Source provenance lives in [references/sources.md](references/sources.md). Do not
load it during normal verification-skill work.
