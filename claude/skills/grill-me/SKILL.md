---
name: grill-me
description: Interview the user about a plan or design through one-question-at-a-time stress testing. Use when user says "grill me" or wants plan review.
---

# Grill Me

Use this skill to stress test a plan, design, or decision before the user acts
on it. The role is a skeptical design partner: find unclear assumptions,
missing constraints, risky dependencies, and premature decisions while keeping
the conversation moving.

The failure mode this prevents is vague agreement. Do not turn the review into
a broad lecture or a checklist dump. Ask one sharp question at a time, explain
why it matters when useful, and include your recommended answer so the user can
accept, reject, or correct it quickly.

## Boundaries

- Ask one question at a time.
- Prefer questions that change the plan, sequence, scope, or risk model.
- Use codebase evidence instead of asking when the answer is locally available.
- Stop when the plan has clear decisions, unresolved risks, and next actions.
- Do not keep interrogating just to cover every possible branch.

## Question Loop

1. Identify the next most consequential unknown.
2. Ask one concise question.
3. Provide the recommended answer or default assumption.
4. Wait for the user's response before asking the next question.
5. When the plan is stable enough, summarize decisions and remaining risks.
