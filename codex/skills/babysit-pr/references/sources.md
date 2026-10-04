# Sources

Read this provenance when auditing or revising Babysit PR, not during normal
PR supervision.

The skill is substantially derived from Lauren Tan's pstack at commit
`e43c7ee26e0038c6c1fa8380dd34ce86ff94cb2a`, inspected October 4, 2026:

- [Babysit](https://github.com/cursor/plugins/blob/e43c7ee26e0038c6c1fa8380dd34ce86ff94cb2a/pstack/skills/poteto-mode/playbooks/babysit.md): distinguish status inspection from supervision, own the merge frontier, batch known fixes, triage review claims skeptically, and separate readiness from authority to merge.
- [Shipping](https://github.com/cursor/plugins/blob/e43c7ee26e0038c6c1fa8380dd34ce86ff94cb2a/pstack/skills/poteto-mode/playbooks/shipping.md): verify that evidence still describes the current patch and distinguish requested automatic merge from a confirmed merge.
- [Never Block on the Human](https://github.com/cursor/plugins/blob/e43c7ee26e0038c6c1fa8380dd34ce86ff94cb2a/pstack/skills/principle-never-block-on-the-human/SKILL.md): proceed with reviewable execution and reserve escalation for an actual authority or product decision boundary.
- Repository license: MIT.
- Upstream copyright: Copyright (c) 2026 Lauren Tan.

Compass retains these judgments while using the repository's tools and the
existing Monitor skill for waiting. It omits Cursor loops, forge-specific
watcher scripts and verdicts, mandatory cloud reviewers, stack-rewrite policy,
and rigid report formats. CI diagnosis follows evidence: an untouched failing
caller can still be broken by the patch, and repeated failure alone cannot
disprove flakiness. Review findings remain actionable according to current
code and consequence, regardless of their age or the bot's pass count.

Additional practitioner sources, inspected October 4, 2026:

- [Theo, September 22, 2026, 14:36 to 16:40](https://www.youtube.com/watch?v=-XWSJM-Ue-o&t=876): a short PR supervision skill using native monitoring when available, source verification of bot claims, real fixes, and scope control. The [timestamped transcript](https://www.usetranscribe.io/yt/-XWSJM-Ue-o/fable-optimization-tips) was inspected. Compass qualifies the instruction to act only on comments newer than the last push: stale check success cannot establish current readiness, but an older unresolved finding can still identify a current defect.
- [Theo's workflow demonstration, 45:23 to 48:30](https://www.youtube.com/watch?v=D8PikZ1KhUo&t=2723): prepare the PR and runnable environment before returning for human attention, supervise the PR through feedback, and make any permission to merge conditional and explicit. This is a demonstrated personal workflow, not evidence that every repository should allow automatic merging.

## Upstream license

MIT License

Copyright (c) 2026 Lauren Tan

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
