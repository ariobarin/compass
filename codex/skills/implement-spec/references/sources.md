# Sources

Read this provenance when auditing or revising Implement Spec, not during
normal implementation.

The skill is substantially derived from Matt Pocock's skills at commit
`24fe0ef7737efae15c87225755e9f6f5965e4888`, inspected October 4, 2026:

- [implement-spec](https://github.com/mattpocock/skills/blob/24fe0ef7737efae15c87225755e9f6f5965e4888/skills/engineering/implement-spec/SKILL.md): task-graph execution, a shared integration branch, context pointers, concurrent implementers, and final review.
- [code-review](https://github.com/mattpocock/skills/blob/24fe0ef7737efae15c87225755e9f6f5965e4888/skills/engineering/code-review/SKILL.md): checking the requested behavior and repository standards as distinct questions.
- Repository license: MIT.
- Upstream copyright: Copyright (c) 2026 Matt Pocock.

Compass retains the task graph and integration ownership. It replaces maximum
concurrency, mandatory worktrees, setup-skill dependencies, and mandatory TDD
with bounded independent ownership and risk-proportionate proof. Readiness
depends on usable integrated prerequisites and inspected evidence, rather than
tracker closure. Review includes the actual work: upstream's committed
base-to-HEAD comparison alone omits staged, unstaged, and untracked changes.
Concrete remaining risk determines further review.

[Theo's workflow demonstration, 45:23 to 48:30](https://www.youtube.com/watch?v=D8PikZ1KhUo&t=2723),
inspected October 4, 2026, motivates delivering the reviewable result and a
running environment together so the next human visit can make a decision.
His worktree examples support independent execution while leaving routine Git
mechanics to current models. This is practitioner guidance, not a measured
claim about optimal worker count or universal worktree requirements.

## Upstream license

MIT License

Copyright (c) 2026 Matt Pocock

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
