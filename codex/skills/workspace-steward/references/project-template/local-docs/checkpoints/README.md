# checkpoints

Write a checkpoint before compaction, restart, interruption, or principal-context
replacement.

A checkpoint names the goal revision, current phase, authoritative inputs,
observed state, evidence locators, active assignments, still-unmet conditions,
next principal judgment, and exact re-anchor action.

A fresh context must verify current repository and runtime state rather than
trusting the checkpoint blindly.
