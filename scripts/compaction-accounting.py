#!/usr/bin/env python3
"""Replay context and cache mechanics across compaction thresholds."""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence

DEFAULT_THRESHOLDS = (32000, 48000, 64000, 80000, 96000, 128000, 160000, 192000, 224000, 233000)


@dataclass(frozen=True)
class Turn:
    external_growth: int
    retained_output: int
    ordinary_output: int
    reasoning_output: int
    tool_output: int
    forked_context: int
    observed_input: int | None
    observed_cached_input: int | None
    observed_cache_write: int | None
    observed_pre_context: int | None


@dataclass(frozen=True)
class DerivedSession:
    turns: tuple[Turn, ...]
    compaction_pairs: tuple[tuple[int, int], ...]
    warnings: tuple[str, ...]
    context_observations: int
    output_observations: int
    cache_observations: int


@dataclass(frozen=True)
class CompactionModel:
    mode: str
    overhead: int
    ratio: float
    observations: int

    def post_size(self, pre_size: int) -> int:
        predicted = round(self.overhead + self.ratio * pre_size)
        return max(1, min(pre_size - 1, predicted)) if pre_size > 1 else 1


def nonnegative(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int) and value >= 0:
        return value
    if isinstance(value, float) and value >= 0 and value.is_integer():
        return int(value)
    return None


def event_value(event: dict[str, Any], name: str) -> int | None:
    return nonnegative(event.get(name))


def ordered_events(document: dict[str, Any]) -> list[dict[str, Any]]:
    raw = document.get("events")
    if not isinstance(raw, list):
        raise ValueError("trace document requires an events array")
    indexed: list[tuple[int, int, dict[str, Any]]] = []
    for source_order, item in enumerate(raw):
        if not isinstance(item, dict):
            continue
        seq = nonnegative(item.get("seq"))
        indexed.append((seq if seq is not None else source_order + 1, source_order, item))
    indexed.sort(key=lambda value: (value[0], value[1]))
    return [item for _, _, item in indexed]


def derive_session(document: dict[str, Any]) -> DerivedSession:
    """Derive observed new growth without counting retained output twice."""

    turns: list[Turn] = []
    pairs: list[tuple[int, int]] = []
    warnings: list[str] = []
    observed_after: int | None = None
    context_observations = 0
    output_observations = 0
    cache_observations = 0

    for item in ordered_events(document):
        kind = item.get("kind")
        pre_compaction = event_value(item, "pre_compaction_tokens")
        post_compaction = event_value(item, "post_compaction_tokens")

        if kind == "compaction":
            if (
                pre_compaction is not None
                and post_compaction is not None
                and 0 < post_compaction < pre_compaction
            ):
                pairs.append((pre_compaction, post_compaction))
                observed_after = post_compaction
            else:
                warnings.append("compaction_size_missing")
            continue

        if kind != "turn":
            continue

        observed_pre = event_value(item, "active_context_tokens")
        if observed_pre is None:
            observed_pre = event_value(item, "input_tokens")
        if observed_pre is not None:
            context_observations += 1

        ordinary_output = event_value(item, "output_tokens") or 0
        tool_output = event_value(item, "tool_output_tokens") or 0
        reasoning_output = event_value(item, "reasoning_tokens") or 0
        forked_context = event_value(item, "forked_context_tokens") or 0
        retained_output = ordinary_output + tool_output
        if (
            event_value(item, "output_tokens") is not None
            or event_value(item, "tool_output_tokens") is not None
        ):
            output_observations += 1

        cached = event_value(item, "cached_input_tokens")
        cache_write = event_value(item, "cache_write_tokens")
        if cached is not None or cache_write is not None:
            cache_observations += 1

        if observed_pre is None:
            external_growth = 0
            warnings.append("turn_context_missing")
            baseline_before_turn = observed_after or 0
        elif observed_after is None:
            external_growth = observed_pre
            baseline_before_turn = observed_pre
        elif observed_pre >= observed_after:
            external_growth = observed_pre - observed_after
            baseline_before_turn = observed_pre
        else:
            # A source-side reset or unobserved compaction occurred. Treat the
            # new observation as the baseline instead of carrying a negative
            # delta into later turns.
            external_growth = 0
            baseline_before_turn = observed_pre
            warnings.append("observed_context_decrease")

        if (
            pre_compaction is not None
            and post_compaction is not None
            and 0 < post_compaction < pre_compaction
        ):
            pairs.append((pre_compaction, post_compaction))
            # The event contract places output/tool additions after the compacted
            # baseline. Retaining them here prevents the next turn from counting
            # the same additions again as new input.
            observed_after = post_compaction + retained_output
        else:
            observed_after = baseline_before_turn + retained_output

        turns.append(
            Turn(
                external_growth=external_growth,
                retained_output=retained_output,
                ordinary_output=ordinary_output,
                reasoning_output=reasoning_output,
                tool_output=tool_output,
                forked_context=forked_context,
                observed_input=event_value(item, "input_tokens"),
                observed_cached_input=cached,
                observed_cache_write=cache_write,
                observed_pre_context=observed_pre,
            )
        )

    return DerivedSession(
        turns=tuple(turns),
        compaction_pairs=tuple(pairs),
        warnings=tuple(warnings),
        context_observations=context_observations,
        output_observations=output_observations,
        cache_observations=cache_observations,
    )


def choose_model(
    sessions: Sequence[DerivedSession],
    mode: str,
    fixed_overhead: int,
    fixed_ratio: float,
) -> CompactionModel:
    pairs = [pair for session in sessions for pair in session.compaction_pairs]
    if mode in {"auto", "empirical"} and pairs:
        ratios = [post / pre for pre, post in pairs if pre > 0 and 0 < post < pre]
        if ratios:
            return CompactionModel("empirical", 0, statistics.median(ratios), len(ratios))
    if mode == "empirical":
        raise ValueError("empirical mode requires at least one valid compaction pair")
    return CompactionModel("fixed", fixed_overhead, fixed_ratio, 0)


def replay_session(
    session: DerivedSession,
    threshold: int,
    context_window: int,
    cache_min_tokens: int,
    model: CompactionModel,
) -> dict[str, Any]:
    sim_context = 0
    cacheable_previous_prompt: int | None = None
    context_values: list[int] = []
    compaction_intervals: list[int] = []
    turns_since_compaction = 0

    result = {
        "turns": 0,
        "compactions": 0,
        "overflow_events": 0,
        "logical_input": 0,
        "uncached_input": 0,
        "cache_read": 0,
        "cache_write": 0,
        "ordinary_output": 0,
        "reasoning_output": 0,
        "tool_output": 0,
        "retained_output": 0,
        "forked_context": 0,
        "compacted_context": 0,
    }

    for turn in session.turns:
        candidate = sim_context + turn.external_growth
        if candidate > threshold:
            candidate = model.post_size(candidate)
            result["compactions"] += 1
            result["compacted_context"] += candidate
            compaction_intervals.append(turns_since_compaction)
            turns_since_compaction = 0
            cacheable_previous_prompt = None

        pre_turn_context = candidate
        context_values.append(pre_turn_context)
        result["turns"] += 1
        turns_since_compaction += 1
        result["logical_input"] += pre_turn_context
        if pre_turn_context > context_window:
            result["overflow_events"] += 1

        if pre_turn_context < cache_min_tokens:
            # Cache-ineligible prompts cannot seed a reusable prefix for the next
            # turn. They remain ordinary uncached input.
            result["uncached_input"] += pre_turn_context
            cacheable_previous_prompt = None
        elif cacheable_previous_prompt is None:
            result["cache_write"] += pre_turn_context
            cacheable_previous_prompt = pre_turn_context
        else:
            reusable = min(cacheable_previous_prompt, pre_turn_context)
            result["cache_read"] += reusable
            result["cache_write"] += max(0, pre_turn_context - reusable)
            cacheable_previous_prompt = pre_turn_context

        result["ordinary_output"] += turn.ordinary_output
        result["reasoning_output"] += turn.reasoning_output
        result["tool_output"] += turn.tool_output
        result["retained_output"] += turn.retained_output
        result["forked_context"] += turn.forked_context

        # Reasoning tokens and child-inherited context are accounting categories,
        # not assumed root-context additions. Ordinary assistant output and tool
        # output are the retained additions in this first-order model.
        sim_context = pre_turn_context + turn.retained_output

    if session.turns:
        compaction_intervals.append(turns_since_compaction)
    result["context_values"] = context_values
    result["compaction_intervals"] = compaction_intervals
    return result


def aggregate_replay(
    sessions: Sequence[DerivedSession],
    threshold: int,
    context_window: int,
    cache_min_tokens: int,
    model: CompactionModel,
) -> dict[str, Any]:
    sums = {
        "turns": 0,
        "compactions": 0,
        "overflow_events": 0,
        "logical_input": 0,
        "uncached_input": 0,
        "cache_read": 0,
        "cache_write": 0,
        "ordinary_output": 0,
        "reasoning_output": 0,
        "tool_output": 0,
        "retained_output": 0,
        "forked_context": 0,
        "compacted_context": 0,
    }
    context_values: list[int] = []
    intervals: list[int] = []
    for session in sessions:
        replay = replay_session(
            session, threshold, context_window, cache_min_tokens, model
        )
        for key in sums:
            sums[key] += replay[key]
        context_values.extend(replay["context_values"])
        intervals.extend(replay["compaction_intervals"])

    return {
        "threshold": threshold,
        "sessions": len(sessions),
        "turns": sums["turns"],
        "compactions": sums["compactions"],
        "turns_between_compactions": {
            "average": round(statistics.mean(intervals), 3) if intervals else None,
            "minimum": min(intervals) if intervals else None,
            "maximum": max(intervals) if intervals else None,
        },
        "context": {
            "average_pre_turn": round(statistics.mean(context_values), 3)
            if context_values
            else None,
            "maximum_pre_turn": max(context_values) if context_values else None,
            "overflow_events": sums["overflow_events"],
            "context_window": context_window,
        },
        "input_accounting": {
            "logical_input": sums["logical_input"],
            "uncached_input": sums["uncached_input"],
            "estimated_cache_read": sums["cache_read"],
            "estimated_cache_write": sums["cache_write"],
            "cache_min_tokens": cache_min_tokens,
        },
        "output_accounting": {
            "ordinary_output": sums["ordinary_output"],
            "reasoning_output": sums["reasoning_output"],
            "tool_output": sums["tool_output"],
            "retained_root_context_additions": sums["retained_output"],
            "child_inherited_context": sums["forked_context"],
            "simulated_post_compaction_context": sums["compacted_context"],
        },
    }


def build_report(
    documents: Sequence[dict[str, Any]],
    thresholds: Sequence[int],
    context_window: int,
    cache_min_tokens: int,
    mode: str,
    fixed_overhead: int,
    fixed_ratio: float,
) -> dict[str, Any]:
    sessions = [derive_session(document) for document in documents]
    model = choose_model(sessions, mode, fixed_overhead, fixed_ratio)
    turns = sum(len(session.turns) for session in sessions)
    warnings: dict[str, int] = {}
    for session in sessions:
        for warning in session.warnings:
            warnings[warning] = warnings.get(warning, 0) + 1

    return {
        "schema_version": 1,
        "kind": "compaction_accounting",
        "model": {
            "mode": model.mode,
            "overhead": model.overhead,
            "ratio": round(model.ratio, 6),
            "observed_compactions": model.observations,
            "retained_context": "ordinary output plus tool output",
            "excluded_from_root_growth": ["reasoning_output", "forked_context"],
        },
        "coverage": {
            "sessions": len(sessions),
            "turns": turns,
            "turns_with_context": sum(
                session.context_observations for session in sessions
            ),
            "turns_with_output_signal": sum(
                session.output_observations for session in sessions
            ),
            "turns_with_observed_cache_signal": sum(
                session.cache_observations for session in sessions
            ),
            "warnings": dict(sorted(warnings.items())),
        },
        "thresholds": [
            aggregate_replay(
                sessions, threshold, context_window, cache_min_tokens, model
            )
            for threshold in sorted(set(thresholds))
        ],
        "interpretation": {
            "mechanical_accounting_only": True,
            "quality_measured": False,
            "billing_measured": False,
            "recommendation_emitted": False,
        },
    }


def iter_documents(path: Path) -> Iterable[dict[str, Any]]:
    if path.suffix.lower() == ".jsonl":
        with path.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, 1):
                if not line.strip():
                    continue
                try:
                    value = json.loads(line)
                except json.JSONDecodeError as error:
                    raise ValueError(f"invalid JSONL at line {line_number}") from error
                if isinstance(value, dict):
                    yield value
        return

    value = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(value, dict):
        yield value
    elif isinstance(value, list):
        for item in value:
            if isinstance(item, dict):
                yield item


def load_documents(inputs: Sequence[Path]) -> list[dict[str, Any]]:
    files: set[Path] = set()
    for raw in inputs:
        path = raw.expanduser()
        if path.is_file() and path.suffix.lower() in {".json", ".jsonl"}:
            files.add(path)
        elif path.is_dir():
            files.update(
                candidate
                for candidate in path.rglob("*")
                if candidate.is_file()
                and candidate.suffix.lower() in {".json", ".jsonl"}
            )
    documents = [document for path in sorted(files) for document in iter_documents(path)]
    if not documents:
        raise ValueError("no trace documents found")
    return documents


def parse_thresholds(raw: str) -> list[int]:
    try:
        values = [int(part.strip()) for part in raw.split(",") if part.strip()]
    except ValueError as error:
        raise argparse.ArgumentTypeError("thresholds must be comma-separated integers") from error
    if not values or any(value <= 1 for value in values):
        raise argparse.ArgumentTypeError("thresholds must be integers greater than one")
    return values


def render_text(report: dict[str, Any]) -> str:
    coverage = report["coverage"]
    model = report["model"]
    lines = [
        "compaction accounting",
        f"sessions: {coverage['sessions']}",
        f"turns: {coverage['turns']}",
        f"model: {model['mode']} overhead={model['overhead']} ratio={model['ratio']}",
        "",
        "threshold compactions overflows avg_context max_context "
        "logical_input cache_read cache_write",
    ]
    for item in report["thresholds"]:
        lines.append(
            f"{item['threshold']:>9} "
            f"{item['compactions']:>11} "
            f"{item['context']['overflow_events']:>9} "
            f"{str(item['context']['average_pre_turn']):>11} "
            f"{str(item['context']['maximum_pre_turn']):>11} "
            f"{item['input_accounting']['logical_input']:>13} "
            f"{item['input_accounting']['estimated_cache_read']:>10} "
            f"{item['input_accounting']['estimated_cache_write']:>11}"
        )
    lines.extend(
        [
            "",
            "interpretation: mechanical context and cache accounting only; "
            "no quality or threshold recommendation",
        ]
    )
    return "\n".join(lines)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument(
        "--thresholds",
        type=parse_thresholds,
        default=list(DEFAULT_THRESHOLDS),
    )
    parser.add_argument("--context-window", type=int, default=272000)
    parser.add_argument("--cache-min-tokens", type=int, default=1024)
    parser.add_argument("--compaction-mode", choices=("auto", "fixed", "empirical"), default="auto")
    parser.add_argument("--fixed-overhead", type=int, default=2000)
    parser.add_argument("--fixed-ratio", type=float, default=0.15)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if args.context_window <= 1 or args.cache_min_tokens < 0 or args.fixed_overhead < 0:
        parser.error("context, cache, and overhead values must be nonnegative and valid")
    if not 0 < args.fixed_ratio < 1:
        parser.error("fixed ratio must be within (0, 1)")
    return args


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        documents = load_documents(args.inputs)
        report = build_report(
            documents,
            args.thresholds,
            args.context_window,
            args.cache_min_tokens,
            args.compaction_mode,
            args.fixed_overhead,
            args.fixed_ratio,
        )
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"compaction accounting failed: {error}", file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2, sort_keys=True) if args.json else render_text(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
