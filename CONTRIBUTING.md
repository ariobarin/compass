# Contributing

Compass carries reviewed agent skills and working preferences. Keep each skill
focused on a decision or capability that benefits from explicit guidance.

Project guidance belongs in its project. Runtime settings belong in the agent's
environment. Keep source archives, generated state, and installation machinery
out of Compass.

For a skill change, name the observed gap and inspect the current upstream
artifact when one exists. Keep useful source wording, preserve license notices,
and record the exact revision and material adaptations in `references/sources.md`.
Keep provenance separate from instructions the agent needs during execution.

Exercise consequential behavior changes with a fresh agent given a realistic
task and the relevant skill. Include a nearby task that should not trigger it.
For a new intervention, compare with a run that does not receive the skill.
Report what changed and any limits; do not turn a few trials into a claim about
all models. Keep disposable experiments out of the repository unless they
protect a recurring risk.

Before opening a pull request, run:

```sh
git diff --check
python3 scripts/check.py
```

The source checker requires Python 3.11 or newer. It protects the skill catalog
and local source references; it does not measure instruction quality. Keep PRs
cohesive and explain the changed behavior and useful evidence.
