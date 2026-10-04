# Source Grounding

Users discover reality. Vendors describe intent.

For behavior, corroborated lived experience outranks official posting. Official
material defines contracts, releases, policy, and vendor claims. It does not
outrank the people who bear the product's failures, costs, and constraints.

Field knowledge forms in public. A talk explains intent, a repository exposes
the implemented workflow, and an observed run tests what it actually does.
Compare all three. A convincing demo or successful practitioner's setup is a
lead to investigate, not proof that every instruction belongs in Compass.

Research is a hunt for signal. Establish the official record. Then start where
consequences happen: issue trackers, Reddit, X, practitioner blogs, talks,
interviews, and books. Follow promising trails through artifacts, replies,
criticism, and linked work. Dig until the claim becomes a finding or collapses.

Provenance locates a source. Evidence ranks it. Receipts outrank credentials.
Repeated independent experience outranks polish. Discard launch-copy echoes,
generic advice, and certainty without evidence. Look for exact versions, inputs,
outputs, failures, costs, measurements, corrections, and reproducible work.

Taste leaves a trail: sharp distinctions, working artifacts, calibrated claims,
and corrections. Extract the words that work earned. Cite the contribution.
Record the date or model when it can expire.

## Current Workflow Sources

Reviewed October 4, 2026. These sources inform the collection; their complete
frameworks are not requirements. Exact source revisions, license notices, and
adaptation decisions live beside the affected skills.

| Voice | Useful contribution | Boundary in Compass |
| --- | --- | --- |
| [Theo Browne](https://www.youtube.com/watch?v=D8PikZ1KhUo&t=2723) | Use parallel agents to make the next human visit useful, with working artifacts and evidence. | His T3 workflows have their own preview and monitoring tools. Use the available harness and the authority in the task. |
| [Matt Pocock](https://github.com/mattpocock/skills/tree/24fe0ef7737efae15c87225755e9f6f5965e4888) | Separate consequential decisions from execution; use dependency graphs, fresh review, and session retrospectives. | Preserve the useful workflow without hardcoding Claude tools, requiring TDD for every change, or making small tasks pass through a full interview. |
| [Lauren Tan](https://github.com/cursor/plugins/tree/e43c7ee26e0038c6c1fa8380dd34ce86ff94cb2a/pstack) | Make application behavior verifiable and encode recurring lessons at the boundary that prevents the mistake. | Her Cursor setup supplies substantial orchestration and verification infrastructure. Reuse a project's real harness before importing machinery. |
| [Ario's preferences](codex/AGENTS.md) | Minimize reader load, recurring maintenance, and unnecessary handoffs. | A skill must earn its instructions through a real gap. Model and runtime configuration remain local choices. |

[Matt and Lauren's interview](https://www.youtube.com/watch?v=MN9dGgmLyso)
also makes the collection an object of continuous revision: keep the workflows
that help in actual sessions and remove detail newer models can infer.

## Verify The Adaptation

Check the shipped artifact against the explanation. For example, a reviewer
that inspects only committed changes cannot validate an uncommitted patch.
A PR check from an old head cannot establish readiness at the current head,
but an unresolved older review comment can still identify a current defect.
Those distinctions change the skill, even when the original advice sounds
complete.

Use the [Agent Skills specification](https://agentskills.io/specification) for
the content format and the consuming tool's documentation for discovery and
invocation behavior. Test the decision the adaptation is meant to improve and
a nearby case where it should stay out of the way. Separate source claims,
observed outcomes, and inference; a small trial is not a general benchmark.
