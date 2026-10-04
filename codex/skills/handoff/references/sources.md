# Sources

Read this provenance when auditing or revising Handoff, not during normal use.

The skill is substantially derived from Matt Pocock's `handoff` skill:

- Source: https://github.com/mattpocock/skills/blob/24fe0ef7737efae15c87225755e9f6f5965e4888/skills/productivity/handoff/SKILL.md
- Inspected: 2026-10-04
- License source: https://github.com/mattpocock/skills/blob/24fe0ef7737efae15c87225755e9f6f5965e4888/LICENSE
- Repository license: MIT
- Upstream copyright: Copyright (c) 2026 Matt Pocock

Compass keeps the upstream artifact-reference discipline, next-session focus,
and requirement for a user-requested handoff. It adds the intent, authorization, working
state, unresolved decisions, next action, and inspection guidance that may be
lost between sessions. It replaces the fixed temporary-directory rule with a
requested or conventional destination, falling back to a nontracked temporary
file. Skill suggestions are conditional on known availability and usefulness;
no section template or Claude-specific Skill tool call is required. Upstream's
separate blanket redaction paragraph is not included in the Compass instruction.

Host metadata keeps this skill discoverable for a natural-language handoff
request; the description still requires the user to ask for a context transfer.

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
