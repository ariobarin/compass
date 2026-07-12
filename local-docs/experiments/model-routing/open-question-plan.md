# Model-routing open-question plan

Research date: 2026-07-12

This plan turns the routing study's open questions into bounded evidence work. It
adds no production configuration and does not require a generated benchmark.

## Answerability map

| Question | Answerability | Evidence path | Completion signal |
| --- | --- | --- | --- |
| Luna xhigh monitoring versus Sol medium | Substantially answerable | Compare recovery decisions, missed interventions, retries, turns, and final outcome on real long-running jobs | Three or more valid monitoring cases with verified effective routing |
| Terra high exploration value | Substantially answerable | Compare repeated reads, corrections, omissions, parent follow-up, child tokens, and usable map quality | Three or more valid exploration cases, including one large or cross-module scan |
| Fresh versus inherited context | Substantially answerable | Alternate fresh narrow handoffs and inherited context on similar roles; record rediscovery, bias, cache use, and missed constraints | At least two valid cases per context mode, or an earlier decisive failure |
| Inherited-input cache-hit fraction | Mechanically answerable when exposed | Read child-level usage details for cached input and cache writes | Measured fraction, or an explicit finding that the runtime does not expose it |
| MultiAgent V2 routing metadata | Directly answerable | Spawn a harmless probe for each route and inspect effective role, model, effort, tier, context mode, tools, and sandbox | Requested and effective metadata agree, or the mismatch is reproduced |
| Luna and Terra max-effort assignment | Directly answerable | Run one bounded harmless direct or custom-agent probe per model | Effective effort reports max, or the runtime rejects, rewrites, or hides it |
| ChatGPT credits versus API economics | Partially answerable | Compare account usage reporting with API-price counterfactuals | A documented mapping, or a bounded statement that exact conversion is unavailable |
| Intelligence versus context, permission, tool, or topology failures | Substantially answerable | Classify the first causal failure for every natural comparison before comparing cost | Every failed case has one primary class and supporting evidence |
| Terra read-heavy recommendation in Compass | Substantially answerable | Use real repository exploration and large-document review cases, then compare misses and total correction cost | Terra earns a role through shared-success efficiency or loses it |
| Privacy-safe child trace availability | Directly answerable | Define and test a metadata-only record with counts, outcomes, hashes or identifiers, and no prompt or file contents | Required routing and efficiency fields are retained without persistent private content |

## Execution order

1. Prove topology with harmless route probes. Resolve MultiAgent V2 metadata and
   max-effort assignment before comparing model quality.
2. Define the smallest privacy-safe trace. Retain route metadata, token-category
   counts, tool and turn counts, corrections, verification misses, duration, and
   outcome. Do not retain prompts, conversation text, file contents, or tool
   payloads merely for this study.
3. Collect six to ten natural cases across exploration, complex verification,
   and judgment monitoring. Do not create work solely to enlarge the sample.
4. Classify failures before comparing economics. Exclude routing and
   infrastructure failures from model-intelligence conclusions.
5. Close every question as answered, bounded, or currently unobservable.

## Evidence record

Record one row per root or child run:

```text
case_id
role
requested_model
requested_effort
requested_service_tier
requested_fork_mode
effective_model
effective_effort
effective_service_tier
effective_fork_mode
prompt_tokens
cached_input_tokens
cache_write_tokens
reasoning_tokens
answer_tokens
total_tokens
wall_time
turns
model_calls
tool_calls
retries
repeated_file_reads
user_corrections
verification_misses
outcome
failure_class
```

Use identifiers and counts, not private session content. Store infrastructure
failures separately from task failures. Compare all valid cases and the
shared-success subset so a route is not rewarded for failing early.

## Decision boundaries

Questions about effective routing, max effort, and trace availability should be
resolved first. The behavioral questions can then be answered substantially
from the small natural-work sample.

Exact ChatGPT-credit conversion may remain bounded because API prices are a
counterfactual and account credit accounting can use a different unit. That
limitation does not prevent relative model-cost comparisons when token-category
usage is available.
