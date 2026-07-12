# Compaction Threshold Simulator

`scripts/compaction-sim.py` replays normalized session token events under
counterfactual compaction thresholds. It makes no model or network calls. The
result is a first-order context pressure and accounting model, not a semantic
quality benchmark and not a billing calculator.

OpenAI compaction replaces earlier conversation state with a compacted item that
can be carried forward while older items are dropped. Prompt caching is a
separate mechanism based on reusable prompt prefixes. The simulator therefore
keeps compaction output, logical input, cache reads, cache writes, and uncached
input as separate categories.

References:

- [OpenAI compaction guide](https://developers.openai.com/api/docs/guides/compaction)
- [OpenAI prompt caching guide](https://developers.openai.com/api/docs/guides/prompt-caching)

## Input

The input can be one JSON file, one JSONL file, or a directory containing JSON
and JSONL files. Each record must use schema version 1:

```json
{
  "schema_version": 1,
  "session": {
    "session_id_hash": "example",
    "root_model": null,
    "root_reasoning_effort": null
  },
  "events": [
    {
      "seq": 1,
      "kind": "turn",
      "input_tokens": null,
      "cached_input_tokens": null,
      "cache_write_tokens": null,
      "output_tokens": null,
      "reasoning_tokens": null,
      "active_context_tokens": null,
      "tool_output_tokens": null,
      "forked_context_tokens": null,
      "pre_compaction_tokens": null,
      "post_compaction_tokens": null
    }
  ]
}
```

Unknown token values are `null`. The simulator does not fill unknown categories
with invented precision. It uses available context deltas for replay and lowers
the confidence score when context, output, or cache signals are missing.

The integration contract assumes:

- `active_context_tokens` is context immediately before a turn. When absent,
  `input_tokens` is the fallback context signal.
- `output_tokens` is ordinary output excluding `reasoning_tokens`.
- `tool_output_tokens` and `forked_context_tokens` are additions retained after
  the turn.
- An observed compaction has both `pre_compaction_tokens` and
  `post_compaction_tokens` on the same event.
- Event order is defined by `seq`, with source order breaking ties.

## Replay model

For each threshold and session, the simulator tracks active context, inferred
new input, retained output, cache categories, compactions, and overflows.
Compaction occurs before a turn when the candidate context is greater than the
threshold. The prior context is replaced by the selected compaction-size model,
and the prompt prefix is treated as reset for cache accounting.

The fixed and fitted forms use:

```text
post_size =
  overhead
  + ratio * pre_size
  + recent_tail_weight * recent_tail
  + tool_output_share_weight * pre_size * tool_output_share
```

Predictions are clamped to at least one token and below the pre-compaction size.
Clamps are reported as warnings.

## Calibration modes

`--compaction-mode` supports:

- `fixed`: uses `--fixed-overhead`, `--fixed-ratio`, and
  `--recent-tail-weight`. Defaults are transparent assumptions, not measured
  production values.
- `empirical`: uses the median observed `post_size / pre_size` ratio. It reports
  the number of valid observations.
- `fitted`: fits the configurable form above with ordinary least squares when
  at least six valid observations exist. It falls back to empirical or fixed
  mode when the data is insufficient or singular.
- `auto`: selects fitted with at least six observations, then empirical with at
  least one, otherwise fixed.

The fitted model is intentionally simple. It estimates size, not whether a
compaction retained the right semantic details.

## Cache and usage accounting

The first eligible prompt and every simulated compaction reset are estimated as
cache writes. Later turns use observed cache read and write ratios when those
fields are present. Otherwise, the previous prompt length is the estimated
reusable prefix. Prompts below `--cache-min-tokens` are treated as uncached.

All usage weights default to `1.0`, except semantic loss which defaults to zero:

```text
usage_score =
  uncached_input_weight * uncached_input
  + cache_read_weight * cache_read
  + cache_write_weight * cache_write
  + compaction_output_weight * compaction_output
  + output_weight * ordinary_output
  + reasoning_weight * reasoning_output
```

This neutral default preserves the token categories without claiming API or
subscription billing equivalence. Set weights for the accounting question being
modeled.

Risk remains separate:

```text
risk_score =
  compactions
  + 10 * context_pressure
  + 1000 * overflow_events
  + semantic_loss_penalty * compactions
```

The output shows each risk component. The simulator never merges usage and risk
into one hidden objective.

## CLI

```powershell
python scripts/compaction-sim.py traces.jsonl
python scripts/compaction-sim.py traces.jsonl --thresholds 64000,96000,128000,233000
python scripts/compaction-sim.py traces.jsonl --json
python scripts/compaction-sim.py traces.jsonl --compaction-mode empirical
python scripts/compaction-sim.py traces.jsonl --cache-read-weight 0.1 --cache-write-weight 1.0
```

The default threshold grid is:

```text
32000, 48000, 64000, 80000, 96000, 128000, 160000, 192000, 224000, 233000
```

These are simulation points. They are not a declaration that every value is a
valid production setting. The current 233000 threshold is added as a labeled
baseline whenever it fits within `--context-window`. Use `--exclude-baseline`
to omit it from an explicit comparison.

## Output and frontier

Text and JSON output include:

- threshold and baseline marker
- compactions and turns between compactions
- average and maximum context
- logical, uncached, cache read, and cache write input
- compaction, ordinary, and reasoning output
- usage score and risk score with components
- overflow events, confidence, warnings, and model calibration details

A threshold is on the Pareto frontier when no other threshold has both a usage
score no higher and a risk score no higher, with at least one strictly lower.
The simulator reports all non-dominated points rather than naming one universal
optimum.

A synthetic fixture run currently produces this frontier:

| threshold | compactions | average context | maximum context | usage score | risk score |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 32000 | 3 | 13756.0 | 25780 | 230546 | 3.727 |
| 48000 | 1 | 20108.6 | 46007 | 317628 | 2.215 |

The fixture values prove model behavior only. Real threshold decisions require
representative traces and a separate quality evaluation.

## Confidence

Confidence combines coverage of context, output, and cache fields with the
amount and type of compaction calibration. It is reported as a score and a
`low`, `medium`, or `high` label. Missing values lower confidence instead of
being silently imputed as measured facts.

Confidence does not measure semantic quality. A high score means the accounting
replay had strong token signals and calibration, not that compaction preserved
all task-critical information.

## Validation

```powershell
python scripts/test-compaction-sim.py
python scripts/compaction-sim.py scripts/fixtures/compaction-sim --json
.\scripts\doctor.ps1
```

The tests use only synthetic data and cover threshold ordering, context growth,
empirical and fitted calibration, cache prefix resets, partial trace confidence,
deterministic Pareto selection, baseline inclusion, deterministic CLI output,
and absence of model or network dependencies.

## Limitations

- Context deltas are a first-order reconstruction. Missing context and retained
  output fields can understate growth.
- Cache reuse is prefix-based accounting, not a replica of provider cache
  placement, retention, routing, or billing policy.
- The fitted model can expose correlations in observed compaction sizes but
  cannot infer semantic loss.
- One semantic-loss penalty per compaction is a user-supplied sensitivity term,
  not an observed quality metric.
- Synthetic fixtures establish deterministic mechanics. Representative real
  traces are required to estimate practical tradeoffs.
- Equal neutral weights make categories comparable as token counts. They do not
  imply equal monetary or latency cost.

## Extractor integration

The session-trace extractor can emit one trace per JSONL line or one JSON object
per file. It should preserve `null` for unknown fields, avoid raw content, and
keep stable session hashes only for grouping. Compaction observations should
place pre and post token counts on one event. Output and reasoning tokens should
remain distinct so configurable weights do not double count them.

No extractor module is imported. The simulator depends only on the schema
contract, so the extractor can land independently.
