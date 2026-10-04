# Sources

Read this provenance when auditing or revising Create Verification Skill, not
during normal verification-skill work. These are the actual upstream artifacts
inspected on October 4, 2026.

- [Lauren Tan, pstack create-verification-skill](https://github.com/cursor/plugins/blob/e43c7ee26e0038c6c1fa8380dd34ce86ff94cb2a/pstack/skills/create-verification-skill/SKILL.md): source for this adaptation. Interview the repo for its launch, drive, evidence, and isolation model; reuse existing harnesses; run the resulting skill end to end; keep proof after cleanup.
- [Lauren Tan, pstack maintain-verification-skill](https://github.com/cursor/plugins/blob/e43c7ee26e0038c6c1fa8380dd34ce86ff94cb2a/pstack/skills/maintain-verification-skill/SKILL.md): source for the upkeep branch. Re-establish health after surprising behavior, confine edits to owned verification artifacts, distinguish instruction drift from product regressions, and re-drive harness fixes.

## Adaptation Decisions

Merge creation and upkeep at the same project boundary. Require repeat use to
earn a maintained skill, reuse the project's actual tools, and keep a recipe
unproven until it runs successfully. Preserve the user's live state, track
owned instances, and retain evidence after successful or failed attempts.
Keep an intended inspection preview available with its owner and lifetime
stated.

Replace the fixed Cursor directory with the project's supported skill
location. Omit the mandatory feature catalog, parallel reader per feature,
whole-application audit, and automatic pull request workflow. Add references
or helpers only when their repeated use earns maintenance. Scope verification
to the task and the risk, expanding when the evidence warrants it.

## Lauren Tan License

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
