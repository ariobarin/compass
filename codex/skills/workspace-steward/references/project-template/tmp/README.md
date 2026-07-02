# tmp

Scratch files that can be recreated or deleted without loss. The root
`.gitignore` ignores `/tmp/*` but keeps this README, so scratch contents are
not tracked while the directory convention survives a clone.

Do not let `tmp/` become a hidden source of truth. Promote useful scratch to the
right durable surface:

- reproducible evidence or reports: `../artifacts/`;
- reusable tooling: `../scripts/` (add it when a tool is reused);
- project or workspace docs: `../docs/`;
- controller notes or handoffs: `../local-docs/`;
- branch-bound code changes: a child repo branch or PR worktree.
