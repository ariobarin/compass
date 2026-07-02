# tmp

Scratch files that can be recreated or deleted without loss. This directory is
gitignored in the root repo (see the root `.gitignore`): its contents are not
tracked.

Do not let `tmp/` become a hidden source of truth. Promote useful scratch to the
right durable surface:

- reproducible evidence or reports: `../artifacts/`;
- reusable tooling: `../scripts/` (add it when a tool is reused);
- project or workspace docs: `../docs/`;
- controller notes or handoffs: `../local-docs/`;
- branch-bound code changes: a child repo branch or PR worktree.
