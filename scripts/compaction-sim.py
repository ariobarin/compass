#!/usr/bin/env python3
"""Replay normalized session traces under counterfactual compaction thresholds."""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable, Sequence

SCHEMA_VERSION = 1
BASELINE_THRESHOLD = 233_000
DEFAULT_CONTEXT_WINDOW = 272_000
DEFAULT_THRESHOLDS = (
    32_000,
    48_000,
    64_000,
    80_000,
    96_000,
    128_000,
    160_000,
    192_000,
    224_000,
    BASELINE_THRESHOLD,
)
TOKEN_FIELDS = (
    "input_tokens",
    "cached_input_tokens",
    "cache_write_tokens",
    "output_tokens",
    "reasoning_tokens",
    "active_context_tokens",
    "tool_output_tokens",
    "forked_context_tokens",
    "pre_compaction_tokens",
    "post_compaction_tokens",
)


@dataclass(frozen=True)
class Trace:
    source: str
    session_id_hash: str
    events: tuple[dict[str, Any], ...]


@dataclass(frozen=True)
class CalibrationObservation:
    pre_size: int
    post_size: int
    recent_tail: int
    tool_output_share: float


@dataclass
class CompactionModel:
    requested_mode: str
    used_mode: str
    calibration_observations: int
    overhead: float
    ratio: float
    recent_tail_weight: float
    tool_output_share_weight: float
    warnings: list[str] = field(default_factory=list)

    def predict(
        self,
        pre_size: int,
        recent_tail: int,
        tool_output_share: float,
    ) -> tuple[int, str | None]:
        tool_feature = pre_size * tool_output_share
        raw = (
            self.overhead
            + self.ratio * pre_size
            + self.recent_tail_weight * recent_tail
            + self.tool_output_share_weight * tool_feature
        )
        lower = 1
        upper = max(lower, pre_size - 1)
        clamped = min(max(raw, lower), upper)
        warning = None
        if not math.isclose(raw, clamped, rel_tol=0.0, abs_tol=0.5):
            warning = (
                f"compaction prediction {raw:.1f} was clamped to {clamped:.1f} "
                f"for pre-size {pre_size}"
            )
        return int(round(clamped)), warning

    def summary(self) -> dict[str, Any]:
        return {
            "requested_mode": self.requested_mode,
            "used_mode": self.used_mode,
            "calibration_observations": self.calibration_observations,
            "parameters": {
                "overhead": round(self.overhead, 6),
                "ratio": round(self.ratio, 9),
                "recent_tail_weight": round(self.recent_tail_weight, 9),
                "tool_output_share_weight": round(
                    self.tool_output_share_weight, 9
                ),
            },
        }


@dataclass(frozen=True)
class Turn:
    source: str
    session_id_hash: str
    seq: int
    new_input_tokens: int
    added_after_turn: int
    output_tokens: int
    reasoning_tokens: int
    tool_output_tokens: int
    forked_context_tokens: int
    observed_input_tokens: int | None
    observed_cached_input_tokens: int | None
    observed_cache_write_tokens: int | None
    context_signal_known: bool
    output_signal_known: bool
    cache_signal_known: bool


@dataclass
class SimulationTotals:
    threshold: int
    turns: int = 0
    compactions: int = 0
    context_sum: int = 0
    maximum_context: int = 0
    logical_input: int = 0
    uncached_input: int = 0
    cache_reads: int = 0
    cache_writes: int = 0
    compaction_output: int = 0
    ordinary_output: int = 0
    reasoning_output: int = 0
    overflow_events: int = 0
    turns_between_compactions: list[int] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ScoreWeights:
    uncached_input: float
    cache_read: float
    cache_write: float
    compaction_output: float
    output: float
    reasoning: float
    semantic_loss_per_compaction: float


@dataclass(frozen=True)
class Coverage:
    total_turns: int
    context_signal_turns: int
    output_signal_turns: int
    cache_signal_turns: int
    reset_inference_warnings: int

    def ratios(self) -> dict[str, float]:
        if self.total_turns == 0:
            return {"context": 0.0, "output": 0.0, "cache": 0.0}
        return {
            "context": self.context_signal_turns / self.total_turns,
            "output": self.output_signal_turns / self.total_turns,
            "cache": self.cache_signal_turns / self.total_turns,
        }


def _token(value: Any, field_name: str, location: str) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{location}.{field_name} must be a non-negative number or null")
    if not math.isfinite(float(value)) or float(value) < 0 or not float(value).is_integer():
        raise ValueError(f"{location}.{field_name} must be a non-negative integer or null")
    return int(value)


def _normalize_trace(raw: Any, source: str, record_index: int) -> Trace:
    location = f"{source} record {record_index}"
    if not isinstance(raw, dict):
        raise ValueError(f"{location} must be a JSON object")
    if raw.get("schema_version") != SCHEMA_VERSION:
        raise ValueError(f"{location} requires schema_version {SCHEMA_VERSION}")

    session = raw.get("session")
    if not isinstance(session, dict):
        raise ValueError(f"{location}.session must be an object")
    session_id = session.get("session_id_hash")
    if not isinstance(session_id, str) or not session_id.strip():
        session_id = f"unknown:{Path(source).name}:{record_index}"

    raw_events = raw.get("events")
    if not isinstance(raw_events, list):
        raise ValueError(f"{location}.events must be an array")

    events: list[dict[str, Any]] = []
    for event_index, raw_event in enumerate(raw_events, start=1):
        event_location = f"{location}.events[{event_index}]"
        if not isinstance(raw_event, dict):
            raise ValueError(f"{event_location} must be an object")
        event = dict(raw_event)
        seq_value = event.get("seq", event_index)
        if isinstance(seq_value, bool) or not isinstance(seq_value, int):
            raise ValueError(f"{event_location}.seq must be an integer")
        event["seq"] = seq_value
        kind = event.get("kind", "turn")
        if not isinstance(kind, str) or not kind.strip():
            raise ValueError(f"{event_location}.kind must be a non-empty string")
        event["kind"] = kind
        for field_name in TOKEN_FIELDS:
            event[field_name] = _token(event.get(field_name), field_name, event_location)
        event["_source_index"] = event_index
        events.append(event)

    events.sort(key=lambda item: (item["seq"], item["_source_index"]))
    return Trace(source=source, session_id_hash=session_id, events=tuple(events))


def _load_json_file(path: Path) -> list[Any]:
    if path.suffix.lower() == ".jsonl":
        records: list[Any] = []
        for line_number, line in enumerate(
            path.read_text(encoding="utf-8-sig").splitlines(), start=1
        ):
            if not line.strip():
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as error:
                raise ValueError(f"invalid JSON in {path}:{line_number}: {error}") from error
        return records

    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as error:
        raise ValueError(f"invalid JSON in {path}: {error}") from error
    return value if isinstance(value, list) else [value]


def load_traces(path: Path) -> list[Trace]:
    if path.is_dir():
        files = sorted(
            candidate
            for candidate in path.rglob("*")
            if candidate.is_file() and candidate.suffix.lower() in {".json", ".jsonl"}
        )
        if not files:
            raise ValueError(f"no .json or .jsonl trace files found under {path}")
    elif path.is_file():
        files = [path]
    else:
        raise ValueError(f"trace input does not exist: {path}")

    traces: list[Trace] = []
    for file_path in files:
        records = _load_json_file(file_path)
        for index, raw in enumerate(records, start=1):
            traces.append(_normalize_trace(raw, str(file_path), index))
    if not traces:
        raise ValueError(f"no trace records found in {path}")
    return traces


def _known_sum(event: dict[str, Any], fields: Sequence[str]) -> int:
    return sum(int(event[field_name]) for field_name in fields if event[field_name] is not None)


def calibration_observations(traces: Sequence[Trace]) -> list[CalibrationObservation]:
    observations: list[CalibrationObservation] = []
    for trace in traces:
        for event in trace.events:
            pre = event["pre_compaction_tokens"]
            post = event["post_compaction_tokens"]
            if pre is None or post is None or pre <= 0 or post <= 0 or post >= pre:
                continue
            tail = min(
                pre,
                _known_sum(
                    event,
                    (
                        "output_tokens",
                        "reasoning_tokens",
                        "tool_output_tokens",
                        "forked_context_tokens",
                    ),
                ),
            )
            tool_tokens = event["tool_output_tokens"] or 0
            observations.append(
                CalibrationObservation(
                    pre_size=pre,
                    post_size=post,
                    recent_tail=tail,
                    tool_output_share=tool_tokens / pre,
                )
            )
    return observations


def _solve_linear_system(matrix: list[list[float]], vector: list[float]) -> list[float]:
    size = len(vector)
    augmented = [row[:] + [vector[index]] for index, row in enumerate(matrix)]
    for pivot_column in range(size):
        pivot_row = max(
            range(pivot_column, size),
            key=lambda row_index: abs(augmented[row_index][pivot_column]),
        )
        if abs(augmented[pivot_row][pivot_column]) < 1e-10:
            raise ValueError("fitted model matrix is singular")
        augmented[pivot_column], augmented[pivot_row] = (
            augmented[pivot_row],
            augmented[pivot_column],
        )
        pivot = augmented[pivot_column][pivot_column]
        augmented[pivot_column] = [value / pivot for value in augmented[pivot_column]]
        for row_index in range(size):
            if row_index == pivot_column:
                continue
            factor = augmented[row_index][pivot_column]
            if factor == 0:
                continue
            augmented[row_index] = [
                current - factor * pivot_value
                for current, pivot_value in zip(
                    augmented[row_index], augmented[pivot_column]
                )
            ]
    return [augmented[index][-1] for index in range(size)]


def _fit_model(observations: Sequence[CalibrationObservation]) -> tuple[float, ...]:
    features = [
        [
            1.0,
            float(observation.pre_size),
            float(observation.recent_tail),
            float(observation.pre_size) * observation.tool_output_share,
        ]
        for observation in observations
    ]
    targets = [float(observation.post_size) for observation in observations]
    dimension = len(features[0])
    normal_matrix = [[0.0 for _ in range(dimension)] for _ in range(dimension)]
    normal_vector = [0.0 for _ in range(dimension)]
    for row, target in zip(features, targets):
        for left in range(dimension):
            normal_vector[left] += row[left] * target
            for right in range(dimension):
                normal_matrix[left][right] += row[left] * row[right]
    return tuple(_solve_linear_system(normal_matrix, normal_vector))


def build_compaction_model(
    requested_mode: str,
    observations: Sequence[CalibrationObservation],
    fixed_overhead: float,
    fixed_ratio: float,
    recent_tail_weight: float,
) -> CompactionModel:
    warnings: list[str] = []

    def fixed() -> CompactionModel:
        return CompactionModel(
            requested_mode=requested_mode,
            used_mode="fixed",
            calibration_observations=0,
            overhead=fixed_overhead,
            ratio=fixed_ratio,
            recent_tail_weight=recent_tail_weight,
            tool_output_share_weight=0.0,
            warnings=warnings,
        )

    def empirical() -> CompactionModel:
        ratios = [observation.post_size / observation.pre_size for observation in observations]
        return CompactionModel(
            requested_mode=requested_mode,
            used_mode="empirical",
            calibration_observations=len(observations),
            overhead=0.0,
            ratio=float(statistics.median(ratios)),
            recent_tail_weight=0.0,
            tool_output_share_weight=0.0,
            warnings=warnings,
        )

    def fitted() -> CompactionModel:
        coefficients = _fit_model(observations)
        model = CompactionModel(
            requested_mode=requested_mode,
            used_mode="fitted",
            calibration_observations=len(observations),
            overhead=coefficients[0],
            ratio=coefficients[1],
            recent_tail_weight=coefficients[2],
            tool_output_share_weight=coefficients[3],
            warnings=warnings,
        )
        if model.ratio < 0 or model.ratio >= 1:
            warnings.append(
                f"fitted pre-size coefficient {model.ratio:.4f} is outside [0, 1)"
            )
        if model.recent_tail_weight < 0:
            warnings.append(
                "fitted recent-tail coefficient is negative and predictions may clamp"
            )
        return model

    if requested_mode == "fixed":
        return fixed()
    if requested_mode == "empirical":
        if observations:
            return empirical()
        warnings.append("empirical mode had no valid observed compactions; using fixed mode")
        return fixed()
    if requested_mode == "fitted":
        if len(observations) >= 6:
            try:
                return fitted()
            except ValueError as error:
                warnings.append(f"fitted mode failed: {error}; using empirical mode")
        else:
            warnings.append(
                f"fitted mode needs at least 6 valid observations; found {len(observations)}"
            )
        if observations:
            return empirical()
        warnings.append("no valid observed compactions; using fixed mode")
        return fixed()
    if requested_mode != "auto":
        raise ValueError(f"unsupported compaction mode: {requested_mode}")

    if len(observations) >= 6:
        try:
            return fitted()
        except ValueError as error:
            warnings.append(f"automatic fitted calibration failed: {error}")
    if observations:
        return empirical()
    return fixed()


def derive_turns(traces: Sequence[Trace]) -> tuple[list[list[Turn]], Coverage, list[str]]:
    sessions: list[list[Turn]] = []
    warnings: list[str] = []
    context_signal_turns = 0
    output_signal_turns = 0
    cache_signal_turns = 0
    reset_warnings = 0

    for trace in traces:
        session_turns: list[Turn] = []
        previous_observed_before: int | None = None
        previous_observed_input: int | None = None
        previous_added = 0
        previous_post_compaction: int | None = None

        for event in trace.events:
            if event["kind"].lower() == "compaction":
                previous_post_compaction = event["post_compaction_tokens"]
                continue

            observed_before = (
                event["active_context_tokens"]
                if event["active_context_tokens"] is not None
                else event["input_tokens"]
            )
            context_known = observed_before is not None
            output_known = any(
                event[field_name] is not None
                for field_name in (
                    "output_tokens",
                    "reasoning_tokens",
                    "tool_output_tokens",
                    "forked_context_tokens",
                )
            )
            cache_known = (
                event["input_tokens"] is not None
                and event["cached_input_tokens"] is not None
                and event["cache_write_tokens"] is not None
            )

            if not session_turns:
                new_input = observed_before or 0
            else:
                baseline: int | None
                if previous_post_compaction is not None:
                    baseline = previous_post_compaction
                elif previous_observed_before is not None:
                    baseline = previous_observed_before + previous_added
                else:
                    baseline = previous_observed_input

                if observed_before is not None and baseline is not None:
                    delta = observed_before - baseline
                    if delta < 0:
                        reset_warnings += 1
                        warnings.append(
                            f"{trace.source} session {trace.session_id_hash} seq {event['seq']}: "
                            "observed context reset lacked a usable post-compaction baseline; "
                            "new input was treated as zero"
                        )
                        new_input = 0
                    else:
                        new_input = delta
                elif (
                    event["input_tokens"] is not None
                    and previous_observed_input is not None
                ):
                    new_input = max(0, event["input_tokens"] - previous_observed_input)
                else:
                    new_input = 0

            output_tokens = event["output_tokens"] or 0
            reasoning_tokens = event["reasoning_tokens"] or 0
            tool_tokens = event["tool_output_tokens"] or 0
            forked_tokens = event["forked_context_tokens"] or 0
            added_after = output_tokens + reasoning_tokens + tool_tokens + forked_tokens

            session_turns.append(
                Turn(
                    source=trace.source,
                    session_id_hash=trace.session_id_hash,
                    seq=event["seq"],
                    new_input_tokens=new_input,
                    added_after_turn=added_after,
                    output_tokens=output_tokens,
                    reasoning_tokens=reasoning_tokens,
                    tool_output_tokens=tool_tokens,
                    forked_context_tokens=forked_tokens,
                    observed_input_tokens=event["input_tokens"],
                    observed_cached_input_tokens=event["cached_input_tokens"],
                    observed_cache_write_tokens=event["cache_write_tokens"],
                    context_signal_known=context_known,
                    output_signal_known=output_known,
                    cache_signal_known=cache_known,
                )
            )
            context_signal_turns += int(context_known)
            output_signal_turns += int(output_known)
            cache_signal_turns += int(cache_known)
            previous_observed_before = observed_before
            previous_observed_input = event["input_tokens"]
            previous_added = added_after
            previous_post_compaction = event["post_compaction_tokens"]

        if session_turns:
            sessions.append(session_turns)

    total_turns = sum(len(session) for session in sessions)
    if total_turns == 0:
        raise ValueError("traces contain no replayable turn events")
    return (
        sessions,
        Coverage(
            total_turns=total_turns,
            context_signal_turns=context_signal_turns,
            output_signal_turns=output_signal_turns,
            cache_signal_turns=cache_signal_turns,
            reset_inference_warnings=reset_warnings,
        ),
        warnings,
    )


def _cache_accounting(
    turn: Turn,
    logical_input: int,
    previous_prompt_tokens: int,
    prefix_reset: bool,
    cache_min_tokens: int,
) -> tuple[int, int, int]:
    if logical_input < cache_min_tokens:
        return logical_input, 0, 0
    if prefix_reset or previous_prompt_tokens <= 0:
        return 0, 0, logical_input

    if turn.observed_input_tokens and turn.observed_cached_input_tokens is not None:
        read_ratio = min(
            1.0,
            turn.observed_cached_input_tokens / turn.observed_input_tokens,
        )
        cache_read = int(round(logical_input * read_ratio))
    else:
        cache_read = min(previous_prompt_tokens, logical_input)

    remaining = max(0, logical_input - cache_read)
    if turn.observed_input_tokens and turn.observed_cache_write_tokens is not None:
        write_ratio = min(
            1.0,
            turn.observed_cache_write_tokens / turn.observed_input_tokens,
        )
        cache_write = min(remaining, int(round(logical_input * write_ratio)))
    else:
        cache_write = remaining
    uncached = max(0, logical_input - cache_read - cache_write)
    return uncached, cache_read, cache_write


def simulate_threshold(
    sessions: Sequence[Sequence[Turn]],
    threshold: int,
    context_window: int,
    model: CompactionModel,
    recent_tail_tokens: int,
    cache_min_tokens: int,
    weights: ScoreWeights,
    confidence: dict[str, Any],
) -> dict[str, Any]:
    totals = SimulationTotals(threshold=threshold)

    for session in sessions:
        active_context = 0
        previous_prompt_tokens = 0
        turns_since_compaction = 0

        for turn in session:
            candidate_context = active_context + turn.new_input_tokens
            compacted = candidate_context > threshold
            if compacted:
                pre_size = candidate_context
                recent_tail = min(pre_size, recent_tail_tokens)
                tool_share = (
                    min(turn.tool_output_tokens, pre_size) / pre_size if pre_size else 0.0
                )
                candidate_context, clamp_warning = model.predict(
                    pre_size,
                    recent_tail,
                    tool_share,
                )
                totals.compactions += 1
                totals.turns_between_compactions.append(turns_since_compaction)
                turns_since_compaction = 0
                retained_tail = min(recent_tail, candidate_context)
                totals.compaction_output += max(0, candidate_context - retained_tail)
                if clamp_warning:
                    totals.warnings.append(clamp_warning)

            logical_input = candidate_context
            uncached, cache_read, cache_write = _cache_accounting(
                turn=turn,
                logical_input=logical_input,
                previous_prompt_tokens=previous_prompt_tokens,
                prefix_reset=compacted,
                cache_min_tokens=cache_min_tokens,
            )

            totals.turns += 1
            totals.context_sum += logical_input
            totals.maximum_context = max(totals.maximum_context, logical_input)
            totals.logical_input += logical_input
            totals.uncached_input += uncached
            totals.cache_reads += cache_read
            totals.cache_writes += cache_write
            totals.ordinary_output += turn.output_tokens
            totals.reasoning_output += turn.reasoning_tokens
            totals.overflow_events += int(logical_input > context_window)

            previous_prompt_tokens = logical_input
            active_context = logical_input + turn.added_after_turn
            turns_since_compaction += 1

    average_context = totals.context_sum / totals.turns if totals.turns else 0.0
    average_pressure = average_context / context_window
    maximum_pressure = totals.maximum_context / context_window
    context_pressure_component = 10.0 * (0.5 * average_pressure + 0.5 * maximum_pressure)
    compaction_component = float(totals.compactions)
    overflow_component = 1000.0 * totals.overflow_events
    semantic_component = weights.semantic_loss_per_compaction * totals.compactions
    risk_score = (
        context_pressure_component
        + compaction_component
        + overflow_component
        + semantic_component
    )
    usage_score = (
        weights.uncached_input * totals.uncached_input
        + weights.cache_read * totals.cache_reads
        + weights.cache_write * totals.cache_writes
        + weights.compaction_output * totals.compaction_output
        + weights.output * totals.ordinary_output
        + weights.reasoning * totals.reasoning_output
    )

    intervals = totals.turns_between_compactions
    return {
        "threshold": threshold,
        "baseline": threshold == BASELINE_THRESHOLD,
        "turns": totals.turns,
        "compactions": totals.compactions,
        "average_context": round(average_context, 3),
        "maximum_context": totals.maximum_context,
        "logical_input": totals.logical_input,
        "uncached_input": totals.uncached_input,
        "cache_reads": totals.cache_reads,
        "cache_writes": totals.cache_writes,
        "compaction_output": totals.compaction_output,
        "ordinary_output": totals.ordinary_output,
        "reasoning_output": totals.reasoning_output,
        "overflow_events": totals.overflow_events,
        "turns_between_compactions": {
            "values": intervals,
            "average": round(statistics.mean(intervals), 3) if intervals else None,
            "minimum": min(intervals) if intervals else None,
            "maximum": max(intervals) if intervals else None,
        },
        "usage_score": round(usage_score, 6),
        "risk_score": round(risk_score, 6),
        "risk_components": {
            "compactions": round(compaction_component, 6),
            "context_pressure": round(context_pressure_component, 6),
            "overflows": round(overflow_component, 6),
            "semantic_loss": round(semantic_component, 6),
        },
        "confidence": confidence,
        "warnings": sorted(set(totals.warnings)),
    }


def confidence_report(coverage: Coverage, model: CompactionModel) -> dict[str, Any]:
    ratios = coverage.ratios()
    data_score = 0.6 * ratios["context"] + 0.2 * ratios["output"] + 0.2 * ratios["cache"]
    if model.used_mode == "fixed":
        calibration_score = 0.55
    elif model.used_mode == "empirical":
        calibration_score = min(0.9, 0.55 + 0.07 * model.calibration_observations)
    else:
        calibration_score = min(0.95, 0.55 + 0.05 * model.calibration_observations)
    score = 0.8 * data_score + 0.2 * calibration_score
    score -= min(0.2, 0.03 * coverage.reset_inference_warnings)
    score = min(1.0, max(0.0, score))
    if score >= 0.8:
        level = "high"
    elif score >= 0.55:
        level = "medium"
    else:
        level = "low"
    return {
        "score": round(score, 3),
        "level": level,
        "coverage": {name: round(value, 3) for name, value in ratios.items()},
        "reset_inference_warnings": coverage.reset_inference_warnings,
    }


def pareto_frontier(results: Sequence[dict[str, Any]]) -> list[int]:
    frontier: list[int] = []
    ordered = sorted(results, key=lambda result: result["threshold"])
    for candidate in ordered:
        dominated = False
        for other in ordered:
            if other is candidate:
                continue
            usage_no_worse = other["usage_score"] <= candidate["usage_score"]
            risk_no_worse = other["risk_score"] <= candidate["risk_score"]
            strictly_better = (
                other["usage_score"] < candidate["usage_score"]
                or other["risk_score"] < candidate["risk_score"]
            )
            if usage_no_worse and risk_no_worse and strictly_better:
                dominated = True
                break
        if not dominated:
            frontier.append(candidate["threshold"])
    return frontier


def parse_thresholds(
    text: str | None,
    context_window: int,
    include_baseline: bool,
) -> list[int]:
    if text is None:
        thresholds = [value for value in DEFAULT_THRESHOLDS if value <= context_window]
        if not thresholds:
            thresholds = [context_window]
    else:
        thresholds = []
        for part in text.split(","):
            part = part.strip().replace("_", "")
            if not part:
                continue
            try:
                value = int(part)
            except ValueError as error:
                raise ValueError(f"invalid threshold: {part!r}") from error
            if value <= 0:
                raise ValueError("thresholds must be positive integers")
            thresholds.append(value)
        if not thresholds:
            raise ValueError("--thresholds did not contain any values")

    if include_baseline and BASELINE_THRESHOLD <= context_window:
        thresholds.append(BASELINE_THRESHOLD)
    return sorted(set(thresholds))


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    traces = load_traces(args.input.resolve())
    observations = calibration_observations(traces)
    model = build_compaction_model(
        requested_mode=args.compaction_mode,
        observations=observations,
        fixed_overhead=args.fixed_overhead,
        fixed_ratio=args.fixed_ratio,
        recent_tail_weight=args.recent_tail_weight,
    )
    sessions, coverage, derivation_warnings = derive_turns(traces)
    confidence = confidence_report(coverage, model)
    thresholds = parse_thresholds(
        args.thresholds,
        args.context_window,
        include_baseline=not args.exclude_baseline,
    )
    weights = ScoreWeights(
        uncached_input=args.uncached_input_weight,
        cache_read=args.cache_read_weight,
        cache_write=args.cache_write_weight,
        compaction_output=args.compaction_output_weight,
        output=args.output_weight,
        reasoning=args.reasoning_weight,
        semantic_loss_per_compaction=args.semantic_loss_penalty,
    )
    results = [
        simulate_threshold(
            sessions=sessions,
            threshold=threshold,
            context_window=args.context_window,
            model=model,
            recent_tail_tokens=args.recent_tail_tokens,
            cache_min_tokens=args.cache_min_tokens,
            weights=weights,
            confidence=confidence,
        )
        for threshold in thresholds
    ]
    frontier = pareto_frontier(results)
    for result in results:
        result["pareto"] = result["threshold"] in frontier

    result_warnings = [
        warning
        for result in results
        for warning in result["warnings"]
    ]
    warnings = sorted(
        set(model.warnings + derivation_warnings + result_warnings)
    )
    return {
        "schema_version": 1,
        "input": {
            "path": str(args.input.resolve()),
            "traces": len(traces),
            "sessions": len(sessions),
            "turns": coverage.total_turns,
        },
        "compaction_model": model.summary(),
        "simulation": {
            "context_window": args.context_window,
            "recent_tail_tokens": args.recent_tail_tokens,
            "cache_min_tokens": args.cache_min_tokens,
            "baseline_threshold": (
                BASELINE_THRESHOLD if BASELINE_THRESHOLD <= args.context_window else None
            ),
            "weights": asdict(weights),
            "risk_formula": {
                "compaction_weight": 1.0,
                "context_pressure_weight": 10.0,
                "overflow_weight": 1000.0,
            },
        },
        "results": results,
        "pareto_frontier": frontier,
        "confidence": confidence,
        "warnings": warnings,
        "assumptions": [
            "active_context_tokens, or input_tokens when active context is absent, is treated as context before each turn",
            "new turn input is inferred from context deltas after known output and tool additions",
            "a simulated compaction invalidates the reusable prompt prefix for that turn",
            "cache categories are accounting estimates, not a claim about subscription or API billing",
            "usage and risk remain separate objectives",
        ],
    }


def _format_int(value: int | float) -> str:
    if isinstance(value, float) and not value.is_integer():
        return f"{value:,.1f}"
    return f"{int(value):,}"


def render_text(report: dict[str, Any]) -> str:
    model = report["compaction_model"]
    lines = [
        "Compaction threshold simulator",
        (
            f"Model: {model['used_mode']} "
            f"({model['calibration_observations']} calibration observations)"
        ),
        "Thresholds are counterfactual simulation points, not production settings.",
        "",
    ]
    headers = (
        "threshold",
        "frontier",
        "comp",
        "avg ctx",
        "max ctx",
        "logical",
        "uncached",
        "cache read",
        "cache write",
        "compact out",
        "usage",
        "risk",
        "confidence",
    )
    rows: list[tuple[str, ...]] = []
    for result in report["results"]:
        rows.append(
            (
                _format_int(result["threshold"]),
                "yes" if result["pareto"] else "",
                _format_int(result["compactions"]),
                _format_int(result["average_context"]),
                _format_int(result["maximum_context"]),
                _format_int(result["logical_input"]),
                _format_int(result["uncached_input"]),
                _format_int(result["cache_reads"]),
                _format_int(result["cache_writes"]),
                _format_int(result["compaction_output"]),
                _format_int(result["usage_score"]),
                f"{result['risk_score']:.3f}",
                (
                    f"{result['confidence']['level']} "
                    f"{result['confidence']['score']:.3f}"
                ),
            )
        )
    widths = [
        max(len(headers[index]), *(len(row[index]) for row in rows))
        for index in range(len(headers))
    ]
    lines.append("  ".join(header.ljust(widths[index]) for index, header in enumerate(headers)))
    lines.append("  ".join("-" * width for width in widths))
    for row in rows:
        lines.append("  ".join(value.rjust(widths[index]) for index, value in enumerate(row)))
    lines.extend(
        [
            "",
            "Pareto frontier: "
            + ", ".join(_format_int(value) for value in report["pareto_frontier"]),
        ]
    )
    if report["warnings"]:
        lines.append("")
        lines.append("Warnings:")
        lines.extend(f"- {warning}" for warning in report["warnings"])
    return "\n".join(lines) + "\n"


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Replay normalized session token traces under counterfactual compaction "
            "thresholds without model or network calls."
        )
    )
    parser.add_argument("input", type=Path, help="trace JSON, JSONL, or directory")
    parser.add_argument(
        "--thresholds",
        help="comma-separated simulation thresholds; the compatible 233000 baseline is added",
    )
    parser.add_argument(
        "--exclude-baseline",
        action="store_true",
        help="do not add the compatible 233000 baseline",
    )
    parser.add_argument("--json", action="store_true", help="emit JSON instead of text")
    parser.add_argument(
        "--compaction-mode",
        choices=("auto", "fixed", "empirical", "fitted"),
        default="auto",
    )
    parser.add_argument("--fixed-overhead", type=float, default=2_000.0)
    parser.add_argument("--fixed-ratio", type=float, default=0.12)
    parser.add_argument("--recent-tail-weight", type=float, default=0.5)
    parser.add_argument("--recent-tail-tokens", type=int, default=8_000)
    parser.add_argument("--context-window", type=int, default=DEFAULT_CONTEXT_WINDOW)
    parser.add_argument("--cache-min-tokens", type=int, default=1_024)
    parser.add_argument("--uncached-input-weight", type=float, default=1.0)
    parser.add_argument("--cache-read-weight", type=float, default=1.0)
    parser.add_argument("--cache-write-weight", type=float, default=1.0)
    parser.add_argument("--compaction-output-weight", type=float, default=1.0)
    parser.add_argument("--output-weight", type=float, default=1.0)
    parser.add_argument("--reasoning-weight", type=float, default=1.0)
    parser.add_argument("--semantic-loss-penalty", type=float, default=0.0)
    args = parser.parse_args(argv)

    if args.context_window <= 0:
        parser.error("--context-window must be positive")
    if args.recent_tail_tokens < 0:
        parser.error("--recent-tail-tokens must be non-negative")
    if args.cache_min_tokens < 0:
        parser.error("--cache-min-tokens must be non-negative")
    if args.fixed_overhead < 0:
        parser.error("--fixed-overhead must be non-negative")
    if args.fixed_ratio < 0:
        parser.error("--fixed-ratio must be non-negative")
    if args.recent_tail_weight < 0:
        parser.error("--recent-tail-weight must be non-negative")
    weight_names = (
        "uncached_input_weight",
        "cache_read_weight",
        "cache_write_weight",
        "compaction_output_weight",
        "output_weight",
        "reasoning_weight",
        "semantic_loss_penalty",
    )
    for name in weight_names:
        if getattr(args, name) < 0:
            parser.error(f"--{name.replace('_', '-')} must be non-negative")
    return args


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        report = build_report(args)
    except (OSError, UnicodeDecodeError, ValueError) as error:
        print(error, file=sys.stderr)
        return 1

    if args.json:
        json.dump(report, sys.stdout, ensure_ascii=False, indent=2, sort_keys=True)
        sys.stdout.write("\n")
    else:
        sys.stdout.write(render_text(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
