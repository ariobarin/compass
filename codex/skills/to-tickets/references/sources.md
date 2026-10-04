# Sources

Read this provenance when auditing or revising To Tickets, not during normal use.

The skill is substantially derived from Matt Pocock's `to-tickets` skill:

- Source: https://github.com/mattpocock/skills/blob/24fe0ef7737efae15c87225755e9f6f5965e4888/skills/engineering/to-tickets/SKILL.md
- Inspected: October 4, 2026, at repository commit `24fe0ef7737efae15c87225755e9f6f5965e4888`
- Repository license: MIT
- Upstream copyright: Copyright (c) 2026 Matt Pocock

Compass keeps tracer-bullet slices, real blocking edges, the wide-refactor
expand-contract exception, and the distinction between a stable decision and a
stale implementation prescription. Slices cover the layers the behavior needs;
prefactors must earn a separate ticket. Wide migrations can use an explicit
integration point when intermediate batches cannot stay green.

Compass drafts without setup, uses the requested or configured destination and
ticket format, and asks only for material decisions or missing publication
authority. It replaces the unconditional approval round and duplicate templates
with those rules. Parent relationships stay separate from blockers. Publishing
tickets does not itself grant implementation authority; existing authority
still applies. These are Compass adaptations, not upstream changes.

Host metadata keeps this skill discoverable for explicit natural-language
requests to draft or publish tickets. Its description, rather than an
invocation-only catalog flag, limits it to the requested workflow.

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
