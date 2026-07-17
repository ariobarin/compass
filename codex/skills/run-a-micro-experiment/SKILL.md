---
name: run-a-micro-experiment
description: Answer one technical uncertainty with the smallest disposable program, preserve the finding, then reimplement deliberately.
---

# Run A Micro-Experiment

Answer one uncertainty with the smallest disposable program that makes the
mechanism visible. This skill exists because prototypes easily grow into hidden
partial products whose copied code, accidental architecture, and broad context
contaminate the real implementation.

The terminal result is a verified finding that changes a production decision.
The experiment itself remains disposable.

## Define One Question

State the uncertainty in a form the experiment can settle:

> Given X, does Y produce Z under conditions C?

Name:

- the decision this result will change;
- the smallest observation that answers the question;
- what the experiment intentionally does not represent;
- the stopping condition.

A vague goal such as "prototype the feature" is too broad. Reduce it until one
mechanism can be observed directly.

## Build The Smallest Revealing Program

Create only the code, input, dependency, and output needed to expose the
mechanism. Optimize for fast iteration and legibility of the result, not
production architecture.

A micro-experiment lives outside production code and does not copy the whole
project. Mock or reduce surrounding systems when the question permits it.

When the uncertainty genuinely depends on the real build, integration boundary,
performance profile, or repository behavior, use a clearly labeled disposable
integration-spike worktree instead. That is not a micro-experiment.

## Observe And Record

Run enough controlled cases to distinguish the proposed mechanism from plausible
alternatives. Record:

- question;
- environment and relevant versions;
- tiny program or command;
- observed output;
- interpretation and uncertainty;
- production consequence;
- timestamp.

Preserve the finding in a compact note or artifact when it will inform later
work.

## Graduate The Finding

Experimental code does not graduate into production. The finding graduates.
Return to the production repository, create or use the correct worktree, and
implement the learned behavior against real ownership, tests, style, and review
requirements.

Delete or archive the experiment after the decision is captured. Promote a
reusable test fixture or tool only through an explicit review that justifies its
new durable purpose.
