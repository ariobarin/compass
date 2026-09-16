# Sources

Read this provenance when auditing or revising Unslop, not during normal writing.

Compass originally adapted Lauren Tan's `unslop` skill in pstack:

- Source: https://github.com/cursor/plugins/blob/51a96e0dd838404da19ba83dc70aa21eef71f868/pstack/skills/unslop/SKILL.md
- Repository license: MIT
- Upstream copyright: Copyright (c) 2026 Lauren Tan

The September 5, 2026 revision consolidates the upstream pattern catalog while
removing the instruction to add personality and blanket rules about formatting
or vocabulary. Patterns remain useful editorial clues: lists, contrasts, and
technical terms can be appropriate. Unslop applies to prose with recognizable
AI-writing problems, including technical explanations and PR text. The user's
detailed source-voice preferences belong to their website's editorial guidance.

Sources read September 5, 2026:

- [GPT-6 Astra prompting guidance](https://developers.openai.com/api/docs/guides/latest-model#instruction-following): audit skills because stronger instruction following makes their contents more consequential.
- [Fable 5 prompting guidance](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5#recommended-scaffolding-changes): older, prescriptive skills can reduce quality; compare against defaults.
- [Fable 5.1 prompting guidance](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1#formatting-in-chat): older anti-formatting instructions can now suppress useful structure.
- [Matt Pocock's authoring guidance](https://github.com/mattpocock/skills/blob/3cca18b368ae95cdbdebbff572ccafa662551015/skills/productivity/writing-for-agents/SKILL.md): delete instructions that do not change behavior relative to the current model. This is practitioner guidance, not a GPT-6 comparison.

These sources support revisiting instructions and retaining useful distinctions.
They do not establish that every older rule is redundant or that this particular
catalog improves every draft. The accompanying comparisons are limited editing
checks, not a general quality benchmark.

## Source-faithful editing

Primary research checked September 15, 2026. These studies examine different
models, tasks, populations, and outcomes. Their findings motivate checking for
loss, not assuming every edit degrades a document. The editorial applications
below are Compass design judgments, not interventions validated by the papers.

### Content retention is not author retention

Zhivar Sourati et al. (2026), [The shrinking landscape of linguistic diversity
in the age of large language models](https://doi.org/10.1038/s41562-026-02550-0),
*Nature Human Behaviour*, published August 24. The publisher's abstract reports
three studies, seven datasets, and over 880,000 texts. Rewriting retained core
content while homogenizing style and altering author-associated signals. Its
21 to 50 percent figure measures reductions in writing-complexity variance,
not information lost per edit. The full publisher text is subscription-only;
this note relies on its accessible abstract, not an independent methods audit.

Application: review judgments, qualifications, and expression alongside factual
coverage. Do not infer a person's identity from a classifier or a writing sample.

### Effects depend on the assistance

Vishakh Padmakumar and He He (2024), [Does Writing with Language Models Reduce
Content Diversity?](https://arxiv.org/html/2309.05196v2), ICLR 2024.
[Venue record](https://openreview.net/forum?id=Feiz5HtCD0). The controlled
argumentative-writing comparison found reduced lexical and key-point diversity
with InstructGPT, but not the same significant reduction with base GPT-3.
Model-contributed text largely explained the difference. These older model
conditions do not establish the behavior of every current editor.

Application: compare actual edits with their sources and test the current model;
do not turn an observed risk into an unconditional ban on assistance.

### Better ratings can coexist with less distinctiveness

Anil R. Doshi and Oliver P. Hauser (2024), [Generative AI enhances individual
creativity but reduces the collective diversity of novel
content](https://doi.org/10.1126/sciadv.adn5290), *Science Advances*.
[Open article](https://pmc.ncbi.nlm.nih.gov/articles/PMC11244532/).
Access to AI story ideas improved evaluations of individual stories while
making stories more similar to each other. The task was eight-sentence fiction
with supplied ideas, not repeated editing of personal essays.

Application: a polished result is not sufficient evidence that an author's
account survived. This is also a counterexample to claiming assistance can
only make writing worse.

### Normalization can change culturally situated expression

Dhruv Agarwal, Mor Naaman, and Aditya Vashistha (2025), [AI Suggestions Homogenize
Writing Toward Western Styles and Diminish Cultural
Nuances](https://doi.org/10.1145/3706598.3713564), CHI 2025.
[Author text, version 3](https://arxiv.org/html/2409.11360v3).
In English-language writing tasks with 118 participants from India and the
United States, suggestions shifted Indian participants' writing toward Western
styles. This is evidence about the tested populations and setting, not a basis
for inferring any particular author's culture or preferences.

Application: do not assume a more direct, informal, or professional register is
neutral. Let the author's purpose and supplied language determine the register.

### Examples are not a reliable substitute for an account

Zhengxiang Wang et al. (2025), [Catch Me If You Can? Not Yet: LLMs Still Struggle
to Imitate the Implicit Writing Styles of Everyday
Authors](https://arxiv.org/html/2509.14543v1), arXiv version 1, September 18.
The [arXiv record](https://arxiv.org/abs/2509.14543) lists EMNLP 2025 Findings.
The tested models approximated structured writing more successfully than
informal blogs and forums; adding demonstrations had limited benefits.
Evaluation used computational proxies rather than large-scale human judgments.
These are generation-from-examples results, not a test of source-faithful editing.

Application: edit the supplied wording before attempting to reconstruct a
personality from style examples. Keep examples as references, not slang templates.

### What the website review contributed

The September 2026 review of ariobarin.com supplied local, inspectable editing
failures rather than a new universal writing theory. In the September 8
[DocBot diff](https://github.com/ariobarin/ariobarin.com/commit/1fd0664ab45204139e8f72d7b15076d1044fff64), an
objection to a giant, immediately stale generated README became a generic
maintenance requirement. The January 28
[Pollinator revision](https://github.com/ariobarin/ariobarin.com/commit/cbace4c092b69c1786fe4b3e01a19a3f2b545614)
added gratitude and pride absent from the replaced passage. These diffs locate
textual changes; they do not establish who composed the sentences.

The resulting distinction is between deleting thought, leaving source material
unused, having too little source material, and making a legitimate correction.
They require different responses. Older writing can be wrong, withdrawn, or
no longer suitable for publication. Project-specific accounts and disclosure
rules belong in the website, not this portable skill. No private transcripts
or conversation logs are included here.

Repeated editing without returning to fixed sources is a plausible mechanism
for accumulating loss, not a measured law established by these papers. Returning
to sources can also restore information. Revisit the skill after material model
changes; keep it only where it changes real editing decisions.

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
