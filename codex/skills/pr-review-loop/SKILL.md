---
name: pr-review-loop
description: Drive a named pull request through current-head evidence, independent review, repairs, behavior proof, and its authorized merge boundary.
---

# PR Review Loop

Move one named pull request from its current head to a truthful readiness
judgment. This skill exists because checks, approvals, runtime evidence, and
comments become stale whenever the head changes, while a polished summary can
make old proof look current.

The terminal result is a current-head evidence packet and an explicit statement
of the remaining review or mutation boundary.

Read [review-loop-playbook.md](references/review-loop-playbook.md) for confined
review bundles, source-blind behavior proof, waiting, and stale-PR decisions.

## Preserve The Named Identity

Record repository, PR number, base branch, head branch, current head SHA, checks,
review decision, inline findings, and merge state.

Continue on the named PR unless the user explicitly asks to replace, retarget,
close, or rebuild it. When the requested outcome is current-main intent rather
than historical branch preservation, make that decision explicit before
creating a replacement.

## Bind Every Gate To The Head

All readiness conclusions target one exact head SHA. After a push, rebase,
force-push, retarget, or material build change:

- reread the head SHA;
- rerun affected checks;
- refresh independent review;
- refresh observable behavior evidence;
- inspect current inline and top-level findings.

A local check supports a gate. It does not replace independent judgment when
that judgment is required.

## Choose Proportionate Independent Evidence

Every PR review loop includes current-head independent review. Use
`neutral-critic` unless the user or repository names another accepted reviewer.
Apply additional reviewers when repository policy, user direction, change risk,
or specialist scope requires them.

Observable user or operator behavior receives source-blind validation when the
claim is material and ordinary current-head tests do not fully establish it.
Small documentation-only, metadata-only, or mechanically proven changes need no
invented runtime ceremony.

Record the gate selection and its reason. Strong review is evidence-bearing, not
a fixed number of agents.

## Iterate Through The Implementation Owner

1. Inspect current PR state and unresolved comments.
2. Run the narrow checks that cover changed behavior.
3. Obtain independent current-head review.
4. Route actionable findings to the implementation owner.
5. Rerun affected checks after every material change.
6. Refresh stale reviewers and behavior evidence against the new SHA.
7. Stop at the named public-mutation boundary.

Use `scripts/build-review-bundle.py` when a fresh source-aware reviewer needs the
complete selected patch without arbitrary checkout or conversation context.

## Wait On Actual State

After review or check acknowledgement, use `monitor-to-completion` for the
observable terminal state. Derive the timeout from repository expectations,
user deadline, or an explicit service window.

A timeout returns judgment. Reread the current head, checks, reviews, and
comments, then choose a named alternate route, a new evidence-based wait, or a
truthful pending-gate report.

## Completion

Report:

- repository and PR identity;
- base, head branch, and current SHA;
- checks and exact results;
- independent review gates and the SHA each covered;
- behavior contract result when used;
- unresolved findings;
- public-mutation authority.

Merge only when explicitly authorized and every required current-head gate is
satisfied. Otherwise leave the PR open and name the exact remaining gate or
owner.
