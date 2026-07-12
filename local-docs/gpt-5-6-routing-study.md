# GPT-5.6 routing economics study

Research date: 2026-07-12

Repository baseline: `main` at `9dc684635a4fbd271e6f33093500b59a9592b3fb`

Scope: research and recommendations only. This study does not change production
configuration, portable agent files, skills, scripts, or MCP code.

## 1. Executive recommendation

Keep the current Compass root default of GPT-5.6 Sol at medium reasoning. Keep
`service_tier` unspecified in portable configuration. Those choices match the
official OpenAI default, preserve full capability for integration work, and do
not confuse a latency lane with model intelligence.

Route by the work's failure cost, not by a single benchmark score:

1. Use Sol medium for root implementation, coordination, requirements judgment,
   and final synthesis. Escalate to Sol high for broad architecture, difficult
   cross-system verification, or decisions where a small intelligence increase
   can prevent an expensive failure.
2. Use Luna at low or medium for clear mechanical interpretation. Use Luna high
   or xhigh for long, bounded, fresh-context work where persistence and token
   price matter more than frontier judgment. Long-running judgment monitoring is
   the strongest current candidate for Luna xhigh.
3. Do not remove Terra from all specialist roles based on the Artificial
   Analysis chart alone. On that composite index every Terra effort is
   dominated, but OpenAI specifically recommends Terra for exploration,
   read-heavy scans, large-file review, and supporting-document processing.
   Compass has no checked-in role-level session aggregate that resolves this
   conflict.
4. Treat context inheritance as a separate routing dimension. Independent
   critics, explorers, and monitors should start fresh unless the cost of
   rediscovery is known to exceed the cost and bias of inherited context.
5. Verify topology before changing role files. A recommendation is irrelevant if
   the child silently inherits the parent model or effort, or if the runtime
   hides the effective route.

The current direction from [PR 236](https://github.com/ariobarin/compass/pull/236)
is therefore reasonable but not fully proven. Sol medium at the root and Luna
xhigh for judgment-heavy monitoring should remain candidate defaults. The
all-Terra specialist layer from
[PR 210](https://github.com/ariobarin/compass/pull/210) should be tested
role by role rather than reverted wholesale.

## 2. Source and date table

| Source | Published or checked | Used for | Important limitation |
| --- | --- | --- | --- |
| [OpenAI model guide](https://learn.chatgpt.com/docs/models) | Checked 2026-07-12 | Official model positioning, effort guidance, Sol medium default, Max and Ultra behavior | Product availability and UI controls can vary by account and runtime |
| [OpenAI subagent guide](https://learn.chatgpt.com/docs/agent-configuration/subagents) | Checked 2026-07-12 | Agent model pinning, effort pinning, inheritance, token overhead, Terra guidance | General Codex guidance, not Compass outcome data |
| [OpenAI configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference) | Checked 2026-07-12 | Independent model, effort, and service-tier controls | The public reference does not document every ChatGPT Work or MultiAgent V2 behavior |
| [OpenAI API pricing](https://developers.openai.com/api/docs/pricing) | Checked 2026-07-12 | Standard, Flex, Batch, Priority, short-context, and long-context token prices | API dollars are an economics proxy for ChatGPT subscription or credit usage, not a direct bill for every Compass run |
| [OpenAI prompt caching guide](https://developers.openai.com/api/docs/guides/prompt-caching) | Checked 2026-07-12 | Cache writes, cache hits, stable-prefix behavior, usage accounting | Cache reuse depends on request shape and runtime behavior |
| [OpenAI Flex processing guide](https://developers.openai.com/api/docs/guides/flex-processing) | Checked 2026-07-12 | Lower-cost, slower, interruptible service lane | Flex changes delivery economics, not model capability |
| [OpenAI Priority processing guide](https://developers.openai.com/api/docs/guides/priority-processing) | Checked 2026-07-12 | Lower and more consistent latency for high-value traffic | Priority changes latency and price, not reasoning capability |
| [Artificial Analysis GPT-5.6 article](https://artificialanalysis.ai/articles/gpt-5-6-has-landed) | Published 2026-07-09, checked 2026-07-12 | Intelligence and cost frontier, max-effort coding scores, max cost per task | Pre-release composite evaluation, not a Compass coding-agent benchmark |
| [Artificial Analysis Luna pages](https://artificialanalysis.ai/models/gpt-5-6-luna-low) | Checked 2026-07-12 | Per-effort Intelligence Index score, output volume, and total suite cost | Figures can be revised as evaluation data changes |
| [Artificial Analysis Terra pages](https://artificialanalysis.ai/models/gpt-5-6-terra-low) | Checked 2026-07-12 | Per-effort Intelligence Index score, output volume, and total suite cost | Figures can be revised as evaluation data changes |
| [Artificial Analysis Sol pages](https://artificialanalysis.ai/models/gpt-5-6-sol-low) | Checked 2026-07-12 | Per-effort Intelligence Index score, output volume, and total suite cost | Figures can be revised as evaluation data changes |
| [Compass PR 210](https://github.com/ariobarin/compass/pull/210) | Merged 2026-07-10 | Origin of Sol root and Terra specialist routing | Configuration change, not comparative evidence |
| [Compass PR 236](https://github.com/ariobarin/compass/pull/236) | Merged 2026-07-12 | Current Sol medium, omitted service tier, and Luna monitor direction | Configuration change, not comparative evidence |
| [Current Compass routing](../codex/AGENTS.md) and [reviewed config](../codex/config.review.toml) | Baseline 2026-07-12 | Current route and runtime cautions | Describes intended behavior, not guaranteed effective child metadata |

### Evidence boundary

Artificial Analysis Intelligence Index v4.1 combines nine evaluations spanning
agentic work, banking tool use, terminal coding, coding, scientific reasoning,
knowledge, and long-context reasoning. Its cost per task is a weighted average
of input, cache hit, cache write, reasoning, and answer-token cost divided by
task count. That is much stronger evidence than raw token price alone, but it is
not a universal predictor of repository implementation success. Artificial
Analysis itself notes that evaluation relevance varies by use case.

The Artificial Analysis model page also contains a generic cache-pricing note
that says OpenAI typically has no cache-write fee. That note conflicts with the
current OpenAI GPT-5.6 price table, which lists a cache-write price. This study
uses OpenAI's current official price table for calculations.

## 3. Intelligence versus cost frontier

### 3.1 Source data

The table below transcribes the per-effort score, total output-token volume, and
total cost to run the full Intelligence Index suite. "AA frontier" refers to the
article's cost-per-task frontier, not the total-suite-cost column.

| Model | Effort | Intelligence Index | Total output tokens | Total suite cost | AA frontier |
| --- | --- | ---: | ---: | ---: | --- |
| Luna | low | 33 | 7.0M | $68.80 | Non-dominated |
| Luna | medium | 38 | 12M | $105.84 | Non-dominated |
| Luna | high | 46 | 37M | $275.02 | Non-dominated |
| Luna | xhigh | 49 | 67M | $479.37 | Non-dominated |
| Luna | max | 51 | 130M | $870.30 | Non-dominated |
| Terra | low | 40 | 5.9M | $160.65 | Dominated |
| Terra | medium | 46 | 10M | $240.23 | Dominated |
| Terra | high | 49 | 24M | $495.77 | Dominated |
| Terra | xhigh | 52 | 36M | $740.21 | Dominated |
| Terra | max | 55 | 96M | $1,753.94 | Dominated |
| Sol | low | 49 | 6.6M | $353.49 | Non-dominated |
| Sol | medium | 54 | 12M | $593.04 | Non-dominated |
| Sol | high | 56 | 21M | $955.55 | Non-dominated |
| Sol | xhigh | 58 | 35M | $1,542.52 | Non-dominated |
| Sol | max | 59 | 70M | $2,824.18 | Non-dominated |

The article reports max-effort weighted cost per task of $0.21 for Luna, $0.55
for Terra, and $1.04 for Sol. It also reports max-effort Coding Agent scores of
75 for Luna, 77 for Terra, and 80 for Sol. Those coding scores are closer than
the overall Intelligence Index scores, which is one reason not to assume the
composite frontier transfers directly to every Compass role.

### 3.2 Dominated routes on the cited measure

Artificial Analysis states that every measured Luna and Sol effort lies on its
cost-intelligence frontier and every Terra effort is dominated. The nearest
named alternative visible from the published scores and frontier is:

| Dominated route | Nearby dominating route | Intelligence comparison | Interpretation |
| --- | --- | --- | --- |
| Terra low | Luna high | 46 vs 40 | More score at lower cost per task |
| Terra medium | Luna high | 46 vs 46 | Same score at lower cost per task |
| Terra high | Luna xhigh | 49 vs 49 | Same score at lower cost per task |
| Terra xhigh | Sol medium | 54 vs 52 | More score at lower cost per task |
| Terra max | Sol high | 56 vs 55 | More score at lower cost per task |

This dominance result is specific to the Artificial Analysis weighted task mix.
It does not prove that Terra is dominated for repository exploration, tool
latency, coding reliability, or any Compass role. Official OpenAI guidance
describes Terra as the everyday workhorse and explicitly recommends it for
read-heavy subagents. Terra remains a useful middle route when either of these
conditions holds:

1. Luna at the required effort causes enough extra turns, retries, tool calls, or
   verification misses to erase its token-price advantage.
2. Sol's additional judgment does not change success, while its price or slower
   output is material.

Compass does not yet have role-level evidence for either condition.

### 3.3 When Luna can beat Sol

Luna high, xhigh, or max can beat Sol medium or high economically only when the
task has a clear success threshold that Luna can meet. They do not beat those
Sol routes on the published overall intelligence score:

- Luna high scores 46.
- Luna xhigh scores 49.
- Luna max scores 51.
- Sol medium scores 54.
- Sol high scores 56.

Luna xhigh matches Sol low at 49. Luna max remains below Sol medium. Therefore
the case for Luna is not "higher effort makes it equally intelligent." The case
is "the task does not need Sol's extra intelligence, and Luna's much lower token
price survives its higher token volume."

The max-effort data also gives a direct warning. Luna max used 130M output
tokens, almost 1.86 times Sol max's 70M. Luna max still cost much less than Sol
max, but its $870.30 total suite cost was higher than Sol medium's $593.04.
Lower model tier plus maximum effort is not automatically the cheapest route.

### 3.4 What the output volumes say about convergence

The hypothesis that long tasks converge toward similar token counts across
nearby tiers is not established.

At the same effort:

| Effort | Luna output | Terra output | Sol output | Read |
| --- | ---: | ---: | ---: | --- |
| low | 7.0M | 5.9M | 6.6M | Close |
| medium | 12M | 10M | 12M | Close |
| high | 37M | 24M | 21M | Luna diverges |
| xhigh | 67M | 36M | 35M | Luna diverges strongly |
| max | 130M | 96M | 70M | All diverge by tier |

Low and medium efforts show approximate convergence in this suite. High through
max do not. This is still not a direct test of long-running coding agents
because the totals aggregate many evaluation tasks. The correct conclusion is
that convergence remains a Compass trace hypothesis, not a finding.

## 4. Constant-token-cost analysis

### 4.1 Official short-context Standard prices

Prices are USD per 1M tokens.

| Model | Input | Cached input | Cache write | Output |
| --- | ---: | ---: | ---: | ---: |
| Sol | $5.00 | $0.50 | $6.25 | $30.00 |
| Terra | $2.50 | $0.25 | $3.125 | $15.00 |
| Luna | $1.00 | $0.10 | $1.25 | $6.00 |

Every token category has the same model ratio:

```text
Sol : Terra : Luna = 5 : 2.5 : 1
```

For any fixed mix of input, cached input, cache writes, reasoning output, and
answer output:

- Terra costs 50 percent of Sol.
- Luna costs 20 percent of Sol.
- Terra can use up to 2 times Sol's tokens before equal-token economics are lost.
- Luna can use up to 5 times Sol's tokens before equal-token economics are lost.
- Luna can use up to 2.5 times Terra's tokens before equal-token economics are
  lost.

OpenAI's long-context schedule preserves the same model ratios. Flex and Batch
halve the Standard rates. Priority doubles the short-context Standard rates.
Those lanes change cost and latency, but the model-capability ordering does not
change.

### 4.2 Observed max-effort output-volume counterfactual

Holding only the observed output volumes from the Artificial Analysis max runs:

```text
Terra output-cost ratio to Sol
= 96M / 70M * 0.5
= 0.686

Luna output-cost ratio to Sol
= 130M / 70M * 0.2
= 0.371
```

The lower tiers used more output tokens, but not enough to erase their
per-token advantage. The actual full-suite cost ratios, which include input and
cache categories, were:

```text
Terra max / Sol max = $1,753.94 / $2,824.18 = 0.621
Luna max / Sol max = $870.30 / $2,824.18 = 0.308
```

For those max runs, output charges represented about 74 percent of Sol total
cost, 82 percent of Terra total cost, and 90 percent of Luna total cost. Higher
reasoning effort can therefore shift the economics toward output volume even
when input context is large.

### 4.3 Context and caching

A useful cost model is:

```text
cost = input_price * uncached_input
     + write_price * cache_write
     + hit_price * cached_input
     + output_price * (reasoning_output + answer_output)
```

Prompt caching starts with a more expensive cache write and can make a stable
reused prefix much cheaper on later requests. This has three routing
implications:

1. Reusing a stable repository instruction prefix can reduce repeated input cost.
2. Forking a large one-off context can pay a cache-write premium without enough
   later hits to recover it.
3. Fan-out can multiply cache writes, child output, tool-result tokens, and
   repeated file reads even when the parent context is cached.

The Responses usage object should be captured at the child-call level. Total
tokens alone cannot separate an efficient fresh child from an inherited child
that benefited from cache hits.

### 4.4 Service-tier separation

Model, reasoning effort, and service tier are independent controls.

- Standard or an inherited default is appropriate for ordinary Compass work.
- Flex is a candidate only when slower responses and occasional unavailability
  are acceptable, such as low-priority asynchronous research or bulk processing.
- Priority is a candidate only when lower and more consistent latency has user
  value. It should not be selected to make a model "smarter."
- Portable role files should continue to omit `service_tier` unless Compass has
  a role-specific latency contract and current runtime evidence that the child
  receives the intended lane.

## 5. Role-routing matrix

"Default service tier" below means leave the portable `service_tier` unset and
inherit the active lane when the runtime supports it.

| Role | Intelligence requirement | Expected duration | Token-volume expectation | Context need | Recommended model and effort | Service tier | Fallback route | Confidence | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Root implementation | High integration judgment | Medium to long | High | Full working context | Sol medium | Default | Sol high for material ambiguity or failure cost | High | OpenAI default, current Compass root, worker owns implementation |
| Broad architecture | Frontier judgment | Medium | Medium to high | Full system constraints, not full chat history | Sol high | Default | Sol medium when decision is reversible, Sol xhigh only for exceptional risk | High | Sol is official complex and open-ended route |
| Repository exploration | Medium to high mapping judgment | Short to medium | Medium to high input, moderate output | Fresh by default, narrow handoff | Terra high for broad exploration | Default | Luna high or xhigh for bounded scans, Sol medium when architecture judgment emerges | Medium | OpenAI recommends Terra for read-heavy scans, AA says Terra high is dominated |
| Mechanical verification | Low to medium | Short | Low to medium | Fresh with explicit claims | Luna low or medium | Default | Terra medium when interpretation becomes nontrivial | Medium | Clear repeatable task fit, tests and scripts provide ground truth |
| Complex behavior verification | High adversarial judgment | Medium to long | Medium to high | Fresh, with artifact and claims, not author narrative | Sol medium | Default | Terra high for ordinary cross-checks, Sol high for high-risk integration | Medium | Verifier contract requires executable and cross-surface proof |
| Research critic | High source judgment and synthesis | Medium to long | High input and moderate output | Fresh with neutral question | Sol medium for synthesis, Luna xhigh child for bounded collection | Default, Flex only for delay-tolerant collection | Terra high when speed and large-document review dominate | Medium | Official Sol research strength, Luna persistence economics, current role uses Terra high |
| Reuse critic | High local-ecology judgment | Medium | High input, moderate output | Fresh with target diff and repository access | Terra high | Default | Sol medium when platform and architecture tradeoffs dominate, Luna xhigh experiment for bounded scans | Medium | Official Terra exploration fit, current role contract, AA domination conflict |
| Requirements critic | High ambiguity and deletion judgment | Short to medium | Moderate | Fresh problem statement plus forcing constraints | Sol medium | Default | Sol high for irreversible product or safety decisions | High | Sol fits ambiguous, difficult, high-value judgment |
| Coordinator | High integration and routing judgment | Long | High cumulative input | Parent context or compact verified ledger | Sol medium | Default | Sol high when specialist conflict or high-risk delivery requires deeper synthesis | High | Compass controller and reviewer roles integrate evidence rather than perform bulk work |
| Long-running judgment monitor | Medium judgment repeated over time | Long | Potentially high cumulative output and wake overhead | Fresh non-forked worker with narrow state | Luna xhigh | Default, Flex only when delayed or failed wakes are acceptable | Sol medium, then Sol high if missed decisions are costly | Medium | Current monitor guidance plus strong token-price advantage, but no Compass trace comparison |
| Pure wait or polling | No model intelligence | Long wall time, negligible reasoning | Model volume should be zero | No inherited model context | Bounded script, watcher, or scheduled automation | Not applicable | Luna low only if an unavoidable turn must classify the final state | High | `monitor-to-completion` forbids spending model turns as a timer |

The matrix deliberately does not recommend a single cheapest route for every
critic. Critics fail through missed judgment, not merely through token use.
Where a role combines bulk collection and final synthesis, split the work
before lowering the model: use a cheap fresh worker for collection and Sol for
the decision.

## 6. Context-forking implications

### Fresh context is the default for independence

Use `fork_turns="none"` or the runtime equivalent for:

- independent critics;
- repository exploration with a narrow question;
- long-running monitors;
- mechanical verification;
- source collection;
- any child whose value depends on avoiding the author's framing.

Benefits include less inherited input, less stale context, less confirmation
bias, and lower risk that a child repeats the parent's entire path. Costs include
re-reading files, reconstructing local terminology, and missing implicit
constraints that were never included in the handoff.

### Inherit context only when it changes success

Context inheritance is justified when the child genuinely needs prior decisions,
unpublished constraints, or a compact execution ledger that would otherwise be
expensive or lossy to reconstruct. It is not justified merely because the
context exists.

Prefer a compact handoff over a full conversation fork:

```text
goal
scope
verified facts
constraints
artifact pointers
decision still needed
```

A compact handoff is easier to cache, audit, and compare across routes.

### Routing interaction

Context and model choice are coupled in practice:

- A fresh Luna worker can be cheaper than inherited Sol even after repeating
  targeted reads.
- A badly briefed fresh Luna worker can spend more on rediscovery and retries
  than a well-cached inherited Terra worker.
- A strong Sol child with a polluted fork can be less reliable than a weaker
  model with a clean role and direct evidence.
- Parallel subagents consume more tokens than a comparable single-agent run, so
  fan-out must earn its coordination cost.

No current public OpenAI page reviewed for this study documents Compass's
`fork_turns` control by name. Treat it as runtime-specific behavior and verify
effective child input and metadata rather than relying on configuration text.

## 7. Runtime-routing limitations

1. **Pinned and inherited fields differ.** OpenAI documents that custom agents
   can pin model and reasoning effort, while optional fields can inherit from
   the parent. Compass must inspect the effective child route, not only the TOML.
2. **MultiAgent V2 can hide or override intent.** Current Compass guidance warns
   that a Sol-selected V2 child can hide routing metadata or inherit parent Sol
   settings. If that occurs, the role file is not controlling economics.
3. **Service tier is independent.** Explicit model or reasoning overrides do not
   imply a service-tier override. `fast` maps to the priority request value in
   current Codex configuration.
4. **Effort availability varies.** High, xhigh, max, and ultra are documented
   only when the selected model and product surface support them. A route must be
   tested in the actual Codex or ChatGPT Work runtime.
5. **Ultra changes topology.** Ultra uses subagents. It is not simply a larger
   single-agent reasoning budget, so its token and coordination economics are a
   separate experiment.
6. **Cloud tasks have a model limitation.** OpenAI currently says the default
   model for Codex cloud tasks cannot be changed after selection through the
   documented route.
7. **Sandbox and permissions inherit.** A cheaper child that cannot access the
   required evidence is not a valid comparison.
8. **Depth constrains routing.** Current Compass `max_depth = 2` permits root to
   reviewer to specialist. Adding another routing layer would fail or require a
   deliberate topology change.
9. **No checked-in session aggregate exists.** Repository search at the baseline
   found no role-level prompt, cached, reasoning, output, retry, or correction
   aggregate. Private session data was not assumed.

## 8. Candidate config changes, proposals only

No production config change is part of this study.

### Proposal A: keep the current root route

Keep:

```toml
model = "gpt-5.6-sol"
model_reasoning_effort = "medium"
```

Keep `service_tier` omitted. Escalate individual sessions to Sol high when the
task, not habit, justifies it.

Rationale: this is the official default, it preserves integration judgment, and
no evidence shows a cheaper root route has equal Compass success.

### Proposal B: create a Luna lane for bounded persistence

After routing metadata is proven, test fresh direct runs using:

```text
gpt-5.6-luna high or xhigh
fork_turns = none
```

Candidate work:

- long-running judgment monitoring;
- large but well-scoped repository scans;
- source collection with explicit inclusion rules;
- mechanical result classification;
- repetitive artifact inspection.

Do not use this lane for final architecture, requirements decisions, or
cross-specialist synthesis without evidence.

### Proposal C: resolve Terra role by role

Do not replace every Terra high role at once. Test three outcomes:

1. Keep Terra high where its official read-heavy fit produces fewer misses than
   Luna.
2. Move clear, bounded work to Luna high or xhigh.
3. Move high-consequence synthesis to Sol medium.

This makes Terra earn its middle position through Compass outcomes rather than
through model-family symmetry.

## 9. Minimal real-work validation plan

Use ordinary work only. Do not create a broad generated benchmark.

### Phase 1: topology preflight

Before comparing quality, prove that a child receives:

- intended role;
- intended model;
- intended reasoning effort;
- intended service tier or inherited default;
- intended fresh or inherited context;
- expected sandbox and tools.

Record the effective metadata. If the runtime hides these fields or silently
inherits Sol, stop the route comparison and use fresh direct runs with explicit
settings.

### Phase 2: three natural comparisons

Collect six to ten valid cases total as suitable work appears:

| Comparison | Natural task | Candidate routes |
| --- | --- | --- |
| Exploration | A real cross-module map or large-file scan | Terra high vs Luna high or xhigh |
| Complex verification | A real behavioral or integration claim | Terra high vs Sol medium |
| Judgment monitoring | A real long-running process with decision wakes | Luna xhigh vs Sol medium |

Do not rerun work solely to manufacture sample size. Alternate routes across
similar new tasks and preserve raw usage when the runtime exposes it.

### Phase 3: metrics

Per root and child, capture:

- model, effort, service tier, and fork mode;
- prompt, cached, cache-write, reasoning, answer, and total tokens;
- wall time, turns, model calls, tool calls, retries, and reruns;
- repeated file reads;
- user corrections;
- verification misses;
- merge, revert, or abandonment outcome;
- infrastructure failures separately from task failures.

Compare the shared-success subset as well as all valid cases. A route that is
cheap only because it fails early is not efficient.

### Stop rule

Stop after six to ten valid natural cases, or earlier if one route shows a clear
operational failure such as hidden routing, repeated correctness misses, or
unacceptable latency. The goal is enough evidence for the next config
experiment, not statistical publication.

## 10. Open questions

1. Does a Luna xhigh monitor make the same recovery decisions as Sol medium on
   real Compass jobs, or does it merely generate cheaper tokens?
2. Do Terra high explorers reduce repeated reads, retries, or parent correction
   enough to justify their dominated Artificial Analysis position?
3. How often do fresh children lose important implicit constraints compared with
   compact handoffs?
4. What fraction of inherited child input becomes a cache hit in the actual
   runtime?
5. Does ChatGPT Work expose reliable child model, effort, service-tier, and
   context metadata for MultiAgent V2?
6. Can max effort be assigned reliably to Luna and Terra through the same custom
   agent surface used by Compass?
7. How do ChatGPT credits map to API-token economics for the user's actual plan?
8. Which failures are intelligence failures, and which are context, permission,
   tool, or topology failures?
9. Does Terra's official read-heavy recommendation hold for the current Compass
   repository and specialist prompts despite the Artificial Analysis frontier?
10. What child-token and correction data will the topology and trace work make
    available without adding persistent logging of private session content?

## Bottom line

The strongest evidence for lower-tier, higher-effort agents is economic:
Luna has one fifth of Sol's per-token price in every short-context Standard token
category, Luna xhigh matches Sol low on the Artificial Analysis Intelligence
Index, and Luna max reaches a Coding Agent score of 75 against Sol max's 80 at a
reported 80 percent lower weighted cost per task.

The strongest evidence against a broad replacement is behavioral uncertainty:
Luna max remains below Sol medium on the overall index, higher Luna efforts use
far more output tokens, Luna max cost more to run across the suite than Sol
medium, and Compass has no checked-in role-level success or correction data.
Terra is also explicitly recommended by OpenAI for read-heavy subagents despite
being dominated on the Artificial Analysis composite.

Adopt the current root and monitor direction as a provisional route. Prove
effective child routing, then test Luna, Terra, and Sol on a few real tasks where
their role boundaries are clear.
