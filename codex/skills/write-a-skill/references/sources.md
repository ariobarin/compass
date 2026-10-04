# Sources

Read this provenance when auditing or revising Write A Skill, not during normal
skill authoring.

- [OpenAI skill creator](https://github.com/openai/skills/blob/4ab6e0fd99c6667163bc34173e3ed3a3fed75ebc/skills/.system/skill-creator/SKILL.md): Codex structure, metadata, progressive disclosure, and validation at this archived revision.
- [Anthropic skill creator](https://github.com/anthropics/skills/blob/b0cbd3df1533b396d281a6886d5132f623393a9c/skills/skill-creator/SKILL.md): behavioral evaluation and iterative revision.
- [Vercel agent skill guidance](https://github.com/vercel-labs/agent-skills/blob/39c80b2503f531605ae7476832a2b54af4e6db83/AGENTS.md): selective descriptions, lean runtime context, and direct references.
- [Practitioner critique of skill-creator noise](https://github.com/anthropics/skills/issues/202): remove obvious exposition and passive, non-executable language.
- [Matt Pocock writing-for-agents](https://github.com/mattpocock/skills/blob/24fe0ef7737efae15c87225755e9f6f5965e4888/skills/productivity/writing-for-agents/SKILL.md): model-relative no-op tests, context pointers, strong leading words, observable completion criteria, and treating environment lookups as source rather than prompt prose.
- [pstack skill authoring](https://github.com/cursor/plugins/blob/e43c7ee26e0038c6c1fa8380dd34ce86ff94cb2a/pstack/skills/poteto-mode/playbooks/authoring-a-skill.md): begin with workflows that recur, own the skill's voice, and delegate rather than restate.
- [pstack structural learning](https://github.com/cursor/plugins/blob/e43c7ee26e0038c6c1fa8380dd34ce86ff94cb2a/pstack/skills/principle-encode-lessons-in-structure/SKILL.md): route repeated corrections to code, checks, or tools when they can enforce the rule; reserve prose for judgment.
- [pstack eval playbook](https://github.com/cursor/plugins/blob/e43c7ee26e0038c6c1fa8380dd34ce86ff94cb2a/pstack/skills/poteto-mode/playbooks/eval.md): blind organic prompts, same-condition comparisons, and judging behavior from artifacts rather than candidate self-report.
- [pstack reflect](https://github.com/cursor/plugins/blob/e43c7ee26e0038c6c1fa8380dd34ce86ff94cb2a/pstack/skills/reflect/SKILL.md): durable, decision-changing learnings only; prefer existing skills and structural enforcement before adding prompt text.

The Matt and pstack artifacts were inspected on October 4, 2026, at the pinned
commits above. Compass adopts their decision-changing guidance, not pstack's
Cursor-specific orchestration or Matt's runtime-specific invocation claims.
Use the actual host's available mechanism to reach a skill, including directly
reading a copied folder. That does not establish the availability of any other
skill, tool, or credential. Blind with/without comparisons and trigger tests
must establish whether the guidance still earns its place on the current model.

## Upstream MIT notices

The adapted Matt Pocock and Lauren Tan materials retain their MIT notices:

MIT License

Copyright (c) 2026 Matt Pocock
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
