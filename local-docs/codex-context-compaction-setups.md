# Advanced Codex Context and Compaction Setups

Research snapshot: **2026-07-10**.

This is repo-local evidence for reviewing Codex context and compaction settings. It is not installed into a live Codex home, and the model catalog and config behavior should be rechecked before copying values into `codex/config.review.toml`.

The reduction case is to keep one reviewed comparison of public setups so future config reviews do not repeat the same source survey or treat copied community values as independent evidence.

## What advanced public Codex setups actually use

There is no single consensus. Public configs cluster into three approaches:

1. **Use Codex defaults** and monitor context.
2. **The popular 233K/25K setup**, originating from Peter Steinberger’s workflow.
3. **Aggressive 120K–180K compaction** for bounded or project-specific work.

One caveat: the 233K/25K recipe was copied into many dotfiles almost verbatim, so five appearances do not represent five independent experiments.

## Current GPT-5.6 Sol baseline

Sol currently has a **372,000-token Codex window** and a built-in **10,000-token per-tool-output limit**. When no compaction threshold is configured, Codex derives one at **90% of the context window**, which is **334,800 tokens** for Sol.

The official configuration supports an explicit context window, auto-compaction threshold and either `total` or `body_after_prefix` threshold accounting.

Sources:

- [OpenAI Codex model catalog](https://github.com/openai/codex/blob/main/codex-rs/models-manager/models.json)
- [OpenAI Codex model metadata implementation](https://github.com/openai/codex/blob/main/codex-rs/protocol/src/openai_models.rs)
- [OpenAI Codex configuration reference](https://developers.openai.com/codex/config-reference)

## Verified public setups

| Public setup | Context override | Auto-compact | Tool-output cap | Compaction customization | Practical bias |
|---|---:|---:|---:|---|---|
| **Current Sol defaults** | 372K native | **334.8K** | **10K** | Built-in prompt; `total` | Maximum continuity; largest late-session prompts |
| **Peter Steinberger** | Unset; approximately 273K model at the time | **233K** | **25K** | Built-in prompt | Long autonomous runs with generous command output |
| **Dejan R.** | Unset | **233K** | **25K** | Built-in prompt | Same reserve-headroom recipe |
| **Vitallium** | Unset | **233K** | **25K** | Built-in prompt | Same reserve-headroom recipe |
| **K. Yasuda** | Unset | **233K** | **25K** | Built-in prompt | Same recipe in a large multi-tool setup |
| **Christian Houmann** | Unset | Model default | **25K** | Built-in prompt | Preserve tool output; let Codex manage compaction |
| **TechDufus** | Unset | Model default | Default; 120K appears only commented out | Tracks `context-used` in status line | Defaults plus visibility rather than tuning |
| **Jimeh** | Unset | Model default | Model default | 233K/25K recipe present but commented | Explicitly returned to model defaults |
| **Gonçalo Cabrita** | **200K** | **180K** | Model default | Memories disabled | Hard operating ceiling; cost/predictability oriented |
| **Ilias Almerekov project profile** | Unset | **120K** | Model default | Project-specific profile | Aggressive compaction for structured multi-agent work |
| **Dyne Gestalt agent profiles** | Suggested 200K, commented | Suggested 120K, commented | Suggested **4K**, commented | Custom prompt preserves the external plan | Role-specific, low-noise context design |

### Source notes

Peter Steinberger’s published configuration uses 25K tool outputs and a 233K threshold, reserving approximately 40K for output and overhead:

```toml
tool_output_token_limit = 25000

# Formula:
# 273000 - (tool_output_token_limit + 15000)
model_auto_compact_token_limit = 233000
```

Sources:

- [Peter Steinberger — Shipping at Inference-Speed](https://github.com/steipete/steipete.me/blob/main/src/content/blog/2025/shipping-at-inference-speed.md)
- [Dejan R. Codex configuration](https://github.com/dejanr/dotfiles/blob/master/modules/home/cli/codex.nix)
- [Vitallium Codex configuration](https://github.com/vitallium/dotfiles)
- [K. Yasuda Codex configuration](https://github.com/ksyasuda/dotfiles)
- [Christian Houmann Codex configuration](https://github.com/chhoumann/dotfiles)
- [TechDufus Codex configuration](https://github.com/TechDufus/dotfiles/blob/main/roles/codex/files/config.toml)
- [Jimeh Codex configuration](https://github.com/jimeh/agentic/blob/main/codex/config.toml)
- [Gonçalo Cabrita Codex configuration](https://github.com/gmcabrita/dotfiles)
- [Ilias Almerekov Codex configuration](https://github.com/IliasAlmerekov/swiftly)
- [Dyne Gestalt agent profiles](https://github.com/dyne/gestalt)

## What the numbers mean on Sol

| Setup | Compaction relative to Sol’s 372K | Likely behavior |
|---|---:|---|
| Sol default: 334.8K | **90.0%** | Fewest compactions; expensive late-session turns |
| Recalculated old formula: 332K | **89.2%** | Functionally almost the same as default |
| Literal community value: 233K | **62.6%** | Meaningfully earlier compaction |
| 200K context / 180K compact | **48.4% of native Sol** | Strong ceiling with moderate continuity |
| 120K compact | **32.3%** | Frequent compaction; best for isolated tasks |

There is an important distinction:

- **Keeping the literal `233000` value on Sol** gives real savings because it compacts at about 63% of Sol’s window.
- **Recalculating Steinberger’s old formula for Sol** gives `372000 - 25000 - 15000 = 332000`, almost exactly Sol’s 334.8K default. That version will not meaningfully address spending.
- Raising `tool_output_token_limit` from Sol’s built-in 10K to 25K is a quality and visibility choice, not a cost-saving choice.

## Less-common controls

| Setting | What advanced configs tend to do | Recommendation for spending |
|---|---|---|
| `model_context_window` | Usually unset; one strong cost-oriented setup uses 200K | Set only when you want a firm operating ceiling |
| `model_auto_compact_token_limit_scope` | Few public configs override it | Keep `"total"` |
| `compact_prompt` | Almost always built-in | Customize only when there is a durable plan/state to preserve |
| `tool_output_token_limit` | 25K among throughput-first users; 4K–10K in lean designs | Keep 8K–10K |
| Memories | Mixed: several power users enable them; Cabrita disables them | Disable when cross-session recall is not valuable |
| `[history]` persistence | Often `save-all` | Does not control live model context |

`body_after_prefix` counts only growth following the carried compaction prefix, while `total` counts the full active context. Because `body_after_prefix` can permit a larger overall prompt before the next compaction, `total` is the more predictable choice for controlling spend.

## Best Sol setups to copy

### 1. Balanced and cost-aware

```toml
# Leave Sol's actual 372K capability intact, but compact much earlier.
model_auto_compact_token_limit = 233000
model_auto_compact_token_limit_scope = "total"

# Sol's existing default is 10K; make it explicit.
tool_output_token_limit = 10000
```

This borrows the most established public threshold but avoids the throughput-oriented increase to 25K tool outputs.

### 2. Stronger spending control

```toml
# Codex treats Sol as a 200K-window model for this profile.
model_context_window = 200000
model_auto_compact_token_limit = 180000
model_auto_compact_token_limit_scope = "total"

tool_output_token_limit = 8000

[memories]
use_memories = false
generate_memories = false
```

This is appropriate for ordinary implementation work, but large repository migrations may lose more detail after compaction.

### 3. Aggressive task profile

```toml
model_context_window = 160000
model_auto_compact_token_limit = 120000
model_auto_compact_token_limit_scope = "total"
tool_output_token_limit = 6000

compact_prompt = """
Preserve the current objective, constraints, decisions, modified files,
test results, unresolved failures, and exact next action.
Discard raw logs, repeated discussion, superseded plans, and completed exploration.
"""
```

This works best when each thread has one tightly scoped objective. It is less suitable for multi-hour architectural work.

### 4. Throughput-first setup

```toml
tool_output_token_limit = 25000
model_auto_compact_token_limit = 233000
model_auto_compact_token_limit_scope = "total"
```

This preserves larger compiler, test and shell outputs, but it is not ideal when usage is the primary concern.

### 5. Defaults plus monitoring

```toml
[tui]
status_line = [
  "model-with-reasoning",
  "git-branch",
  "current-dir",
  "context-used"
]
```

This is useful when you trust model-specific defaults, switch models frequently, and manually start new threads as context grows.

## Practical tuning table

| Symptom | Adjustment |
|---|---|
| Late-session turns feel unusually expensive | Lower `model_auto_compact_token_limit` |
| Compaction happens too often | Raise the auto-compact threshold |
| Codex forgets decisions after compaction | Improve `compact_prompt` or raise the threshold |
| Shell logs dominate the thread | Lower `tool_output_token_limit` |
| Important test failures are truncated | Raise `tool_output_token_limit` slightly |
| Context starts too large | Reduce `project_doc_max_bytes`, MCP tools, plugins or memories |
| Distinct tasks pollute each other | Use a new thread per task |
| Long project history is unnecessary | Disable memories |
| You need a strict operating ceiling | Set `model_context_window` and a lower compaction threshold |
| You want automatic model-specific behavior | Leave `model_context_window` unset |

## Notes on history and persistence

The following settings affect local session storage:

```toml
[history]
persistence = "save-all"
max_bytes = 150000000
```

They do **not** directly reduce live model context. They control whether sessions can be resumed and how much history is stored locally.

## Recommended starting configuration

For someone who specifically feels the larger Sol context window increases spend:

```toml
model_auto_compact_token_limit = 233000
model_auto_compact_token_limit_scope = "total"
tool_output_token_limit = 10000
```

Keep `model_context_window` unset initially.

This gives a substantial reduction from Sol’s approximately 334.8K default compaction point while retaining the full model capability in its metadata. Move to the 200K/180K profile only when a stronger ceiling is needed.

## Bottom line

The strongest public patterns are:

1. **Default Sol behavior** for maximum continuity.
2. **233K auto-compaction with a 25K output cap** for long autonomous runs.
3. **233K auto-compaction with a 10K output cap** for a balanced, cost-aware Sol setup.
4. **200K context and 180K compaction** for a firm operational ceiling.
5. **120K compaction** for focused, single-task or multi-agent profiles.

The recommended starting point is:

```toml
model_auto_compact_token_limit = 233000
model_auto_compact_token_limit_scope = "total"
tool_output_token_limit = 10000
```
