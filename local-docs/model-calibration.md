# Model Calibration

Observed and reviewed: 2026-07-17

This file records the current Compass routing profile. It is dated because model
capability, pricing, latency, and runtime support change quickly. Runtime files
carry the compact active policy. This document preserves the reasoning behind
it.

## Codex Profile

### GPT-5.6 Sol

Use Sol for the user-facing principal, top-level orchestration, difficult
integration, and work whose final synthesis benefits from the highest available
capacity.

The reviewed root default remains Sol at medium effort. Raise effort when the
work rewards deeper exploration and verification. A Sol child needs a concrete
reason because Luna is the default delegated route.

### GPT-5.6 Luna

Use Luna for fresh delegated work. Luna provides the strongest current
performance-to-cost fit for Compass coding subagents.

- `high`: ordinary delegated implementation, exploration, review, and monitoring
  that needs judgment.
- `xhigh`: difficult bounded work, independent criticism, behavior validation,
  or recovery where stronger persistence is worth the added latency.
- `max`: long, proof-oriented work where latency is acceptable and the result
  rewards extended exploration, checks, and revision.

### GPT-5.6 Terra

The current Compass coding profile has no default Terra route. Luna is preferred
for cost-efficient delegated coding work, while Sol is preferred when frontier
capacity is justified.

Reconsider this decision when current evaluations show a distinct Terra role.
Do not preserve the route merely because earlier files used it.

### Effort

Treat effort as a persistence and verification budget. Higher effort gives the
model more room to explore alternatives, run checks, and revise its approach.
It is not a guarantee of correctness, and not every task benefits equally.

Use the lowest level that still produces the required evidence. Use `max` only
when the work is latency-tolerant and the additional exploration can change the
result.

## Claude Code Profile

This Compass installation routes Claude Code through GLM-5.2. That is the only
model identity available to Claude delegates in the current setup.

Claude guidance states this directly so the runtime does not invent Opus,
Sonnet, Haiku, or other unavailable child tiers from generic Claude examples.
The actual gateway configuration remains the mechanical source of truth.

## Current Model Counterweights

Observed GPT-5.6 strengths include strong continuation and willingness to carry
work through ordinary friction.

Current counterweights address the corresponding failure risks:

- Establish planning authority before production implementation.
- Reopen the causal model before adding another repair layer.
- Prefer correction and subtraction over accumulating guards and wrappers.
- Review for duplicated state, unnecessary abstractions, and broader edits than
  the owning boundary requires.
- Preserve the objective in principal-authored control documents before context
  pressure forces a handoff.

## Public Sources

- [GPT-5.6 launch](https://openai.com/index/gpt-5-6/): current Sol, Terra, and
  Luna positioning, pricing context, and the behavior of `max` effort.
- [GPT-5 developer guidance](https://openai.com/index/introducing-gpt-5-for-developers/):
  reasoning effort trades quality, time, and task-specific benefit.
- [Claude Code memory](https://docs.anthropic.com/en/docs/claude-code/memory):
  `CLAUDE.md` hierarchy and concise, specific project memory guidance.
