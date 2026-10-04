---
name: diagnosing-bugs
description: "Observed software failure or performance regression requiring diagnosis. Use only when the user reports a concrete broken, failing, throwing, crashing, flaky, incorrect, or unexpectedly slow symptom, or explicitly asks to debug or diagnose one. Reproduce that symptom with a tight red-capable command before forming a theory."
---

# Diagnosing Bugs

Do not start with a theory. Build a tight pass/fail signal for the user's exact bug first.

## Build the loop

**This is the skill.** If you have a tight signal that goes red on this bug, bisection, instrumentation, and hypothesis testing can consume it. Without one, staring at code produces stories.

The loop is ready only when you can name **one command you have already run** that is:

- **Red-capable.** It drives the real bug path and asserts the user's exact symptom. "Runs without crashing" is not enough.
- **Deterministic enough to trust.** For a flaky bug, raise and measure the reproduction rate until the signal is useful.
- **Fast.** Prefer seconds, not minutes. Tighten setup and scope before debugging against a slow loop.
- **Agent-runnable.** It can be repeated without a human performing the decisive step.

If you catch yourself reading code to build a theory before this command exists, stop. Jumping to a plausible hypothesis is the failure this skill prevents.

If you genuinely cannot build the loop, say what you tried and name the missing access or artifact that would make the symptom observable. Do not replace a missing signal with speculation.

## Reproduce and minimize

Run the loop and watch the user's symptom appear. Wrong bug means wrong fix.

Shrink the repro one element at a time: input, caller, configuration, data, dependency, or step. Re-run after every cut. Stop when every remaining element is load-bearing and removing any one makes the loop go green.

## Hypothesize after the repro

When the minimized repro still permits several plausible causes, generate 3-5 ranked hypotheses before testing the first attractive one. If the repro already isolates one cause, do not manufacture alternatives. Each real hypothesis must predict an observable result:

`If X is the cause, changing Y will make Z happen.`

A hypothesis without a falsifiable prediction is a vibe. Sharpen or discard it.

Change one variable at a time. Every probe must distinguish between hypotheses. Prefer a debugger or a targeted observation at the deciding boundary over broad logging. For performance regressions, establish a measurement first; do not substitute logs for a baseline or profile.

## Fix the bug, not the story

If a maintained regression test is warranted, put it at a seam that reproduces the real bug pattern. A shallow test that cannot express the failure gives false confidence. Weigh recurrence risk against maintenance cost, using `$test-for-risk` when available, to decide whether the repro should become recurring test code.

Then:

1. Watch the minimized repro or regression test fail for the right reason.
2. Apply the smallest root-cause fix.
3. Watch it pass.
4. Re-run the original repro command against the unminimized symptom.

If no correct test seam exists, say so. That is information about the codebase, not permission to add a misleading test.

## Finish clean

Remove temporary instrumentation and throwaway harnesses unless they earned a durable home. State the confirmed cause in the change record so the next debugger inherits evidence rather than folklore.

Source provenance lives in [references/sources.md](references/sources.md). Do not load it during normal debugging.
