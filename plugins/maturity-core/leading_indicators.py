"""Leading Indicator Layer — thesis Sec.3.5.6.

A second, parallel diagnostic layer alongside the 5-KPI layer in
run_analysis.py. Computes 12 "weak" (leading) indicators across three
horizons (planning / in_sprint / closure).

Leading indicators are NOT KPIs. This module enforces that separation
structurally, not just by convention:

- `risk_flag` (this module's output vocabulary) is restricted to
  `none | watch | concern | not_evaluated` — never `RED | YELLOW | GREEN`,
  which is reserved for KPI `level` in run_analysis.py / evaluate.py.
- Indicator definitions live in a declarative reference file
  (maturity-engine/references/leading-indicator-rules.md), parsed by
  `load_indicator_specs` below, the same way org-kpi-definitions.md's
  ```pipeline blocks are parsed — but unlike KPI formulas, the 12
  indicators do not go through evaluate.py's DSL. D2/D15 scope that DSL
  deliberately to the 5 known KPIs; inventing a second, parallel DSL
  vocabulary for 12 more-varied, largely proxy-based formulas would be a
  much larger surface than this version needs. The formulas below are
  Python instead, exactly as the build spec's own compute_leading_indicators
  signature (Sec.4.1) specifies.
- This module never wires into `run_analysis.py::recommend_interventions`.
  Leading indicators only report in this version — see guardrails.md
  Rule 9.

Per-org applicability (`filter_applicable_indicators` /
`validate_leading_indicator_thresholds` below) is a separate axis from the
watch/concern thresholds: an indicator can be *applicable* with *no
confirmed threshold* (`not_evaluated`), or *not applicable to this org at
all* (excluded before `compute_leading_indicators` ever sees it). The two
must never be conflated — see each function's docstring.
"""

import json
import re
from datetime import datetime
from pathlib import Path

import yaml

CORE_DIR = Path(__file__).resolve().parent


def _resolve_default_rules_path():
    """The engine-level indicator spec lives in a sibling skill directory,
    named "maturity-engine" in the live ~/.claude/skills checkout but
    "engine" inside a packaged team-maturity-agent.skill bundle (see
    dist/team-maturity-agent.skill's SKILL.md "Package layout"). Try both
    so this module works unmodified in either layout; fall back to the
    historical default if neither exists, so a missing file still raises a
    clear, named FileNotFoundError instead of resolving to None.
    """
    for sibling in ("maturity-engine", "engine"):
        candidate = CORE_DIR.parents[0] / sibling / "references" / "leading-indicator-rules.md"
        if candidate.exists():
            return candidate
    return CORE_DIR.parents[0] / "maturity-engine" / "references" / "leading-indicator-rules.md"


DEFAULT_RULES_PATH = _resolve_default_rules_path()

RISK_FLAGS = {"none", "watch", "concern", "not_evaluated"}

# Late-completion "end-loading" window, carried over unchanged from the
# prior signal-design draft (second-level-signals-summary.md Sec.6) as the
# *definitional* meaning of "late" -- distinct from the deferred
# watch/concern bands, which govern risk_flag, not what counts as late.
LATE_COMPLETION_WINDOW_DAYS = 2


# ---------------------------------------------------------------------------
# 4.2 — Availability by sprint phase, a single central map
# ---------------------------------------------------------------------------

HORIZON_AVAILABILITY = {
    "planning": {"future", "active", "closed"},
    "in_sprint": {"active", "closed"},  # NOT future
    "closure": {"closed"},  # closed only
}


def compute_mode_for(horizon, sprint_state):
    if sprint_state not in HORIZON_AVAILABILITY[horizon]:
        return "not_available"
    if horizon == "closure":
        return "verified"
    if horizon == "in_sprint" and sprint_state == "active":
        return "provisional"
    if horizon == "planning" and sprint_state != "closed":
        return "provisional"  # even a future-state planning horizon is provisional --
        # tasks may still be reshuffled between future -> active
    return "verified"


# ---------------------------------------------------------------------------
# Loading indicator_specs from leading-indicator-rules.md
# ---------------------------------------------------------------------------

def load_indicator_specs(text):
    """Extract fenced ```indicator blocks from leading-indicator-rules.md.

    Mirrors run_analysis.py::load_kpi_pipelines exactly (same fence-scanning
    approach), parsing a different fence tag so the two vocabularies (KPI
    pipelines vs. indicator definitions) stay visibly distinct in the source
    file too.
    """
    specs = {}
    in_block = False
    buf = []
    for raw_line in text.splitlines():
        stripped = raw_line.strip()
        if not in_block and stripped == "```indicator":
            in_block = True
            buf = []
            continue
        if in_block and stripped == "```":
            in_block = False
            spec = yaml.safe_load("\n".join(buf)) or {}
            indicator_id = spec.get("indicator_id")
            if not indicator_id:
                raise ValueError("An ```indicator block is missing its required 'indicator_id' field.")
            specs[indicator_id] = spec
            continue
        if in_block:
            buf.append(raw_line)
    return specs


# ---------------------------------------------------------------------------
# Per-org indicator applicability -- not every org's workflow makes every
# probabilistic indicator meaningful (e.g. no story points -> no meaningful
# MISSING_SP_RATIO). `applicable` / `applicability_reason` live on the same
# per-indicator entries in org-config.md's leading_indicator_thresholds
# block as the watch/concern thresholds above -- one lookup, not two.
# `not_applicable` (this section) and `not_evaluated` (risk_flag, above) are
# deliberately distinct and must never be conflated: not_evaluated means
# "applies here, no confirmed threshold yet"; not_applicable means "does not
# apply to this org at all" and must not appear in the report as any kind of
# indicator row, not even a not_evaluated one -- see output-template.md §4.
# ---------------------------------------------------------------------------

def validate_leading_indicator_thresholds(org_config):
    """Fails config loading with a clear error if any indicator entry sets
    `applicable: false` without a non-empty `applicability_reason` --
    an unexplained exclusion must never be silently accepted (mirrors the
    guardrails.md Rule 10 principle: a missing/unjustified value must stay
    visibly wrong, not read as "fine"). No-op if the org config has no
    leading_indicator_thresholds block at all (older configs, or configs
    that never touch leading indicators).
    """
    thresholds_cfg = org_config.get("leading_indicator_thresholds")
    if not thresholds_cfg:
        return
    for indicator_id, entry in thresholds_cfg.items():
        if not isinstance(entry, dict):
            continue
        if entry.get("applicable", True) is False:
            reason = entry.get("applicability_reason")
            if not reason or not str(reason).strip():
                raise ValueError(
                    f"org-config.md: leading_indicator_thresholds.{indicator_id} sets "
                    f"'applicable: false' but has no non-empty 'applicability_reason'. "
                    f"A non-applicable indicator must record why -- see "
                    f"maturity-onboarding/references/leading-indicator-applicability.md."
                )


def filter_applicable_indicators(indicator_specs, org_config):
    """Splits indicator_specs into (applicable, excluded).

    `applicable` is the subset of indicator_specs to actually pass into
    compute_leading_indicators -- non-applicable indicators are never
    computed, not computed-then-hidden, because some may not even have
    valid source data for this org (e.g. no story points field at all),
    so computing them could error or produce meaningless zeros.

    `excluded` is a list of {indicator_id, reason} dicts, for the report's
    top-level excluded_indicators field (transparency to the CTO).

    Reads org_config['leading_indicator_thresholds'][id]['applicable'],
    defaulting to True when the block, the per-indicator entry, or the
    field itself is absent -- so a pre-existing config with no applicability
    fields set at all behaves exactly as before this filter existed.
    Structural/deterministic indicators (not part of
    leading_indicator_thresholds -- see leading-indicator-rules.md) have no
    entry to look up and are therefore always applicable.

    Call this once per org config load, before compute_leading_indicators
    -- see validate_leading_indicator_thresholds above, which should run
    first so a malformed config fails loudly rather than filtering silently
    around the problem.
    """
    thresholds_cfg = org_config.get("leading_indicator_thresholds") or {}
    applicable = {}
    excluded = []
    for indicator_id, spec in indicator_specs.items():
        entry = thresholds_cfg.get(indicator_id.lower()) or {}
        if entry.get("applicable", True):
            applicable[indicator_id] = spec
        else:
            excluded.append({
                "indicator_id": indicator_id,
                "reason": entry.get("applicability_reason"),
            })
    return applicable, excluded


# ---------------------------------------------------------------------------
# KPI threshold resolution (for structural/deterministic "preview" indicators)
# ---------------------------------------------------------------------------

def _load_engine_defaults():
    defaults_path = CORE_DIR / "engine_defaults.json"
    with defaults_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _threshold_prefix(kpi_id):
    # Mirrors run_analysis.py::THRESHOLD_PREFIX (cycle_time_p50 is the one
    # KPI whose org-config prefix differs from its KPI id). Kept as a small,
    # local special-case here rather than imported, to avoid a circular
    # import between run_analysis.py and this module.
    return "cycle_time" if kpi_id == "cycle_time_p50" else kpi_id


def resolve_kpi_thresholds(kpi_id, org_values, defaults=None):
    defaults = defaults or _load_engine_defaults()
    prefix = _threshold_prefix(kpi_id)
    kpi_defaults = defaults["kpis"][kpi_id]
    thresholds = {
        "direction": kpi_defaults["direction"],
        "green": org_values.get(f"{prefix}_green", kpi_defaults["green"]),
        "yellow": org_values.get(f"{prefix}_yellow", kpi_defaults["yellow"]),
    }
    return thresholds


def _invert_thresholds(thresholds):
    """For indicators where value = 1 - kpi_value (invert_of_kpi: true).

    Green/yellow boundaries and direction invert exactly around 1, since
    the indicator's value is a deterministic linear transform of the KPI's.
    """
    inverted_direction = (
        "lower_is_better" if thresholds["direction"] == "higher_is_better" else "higher_is_better"
    )
    return {
        "direction": inverted_direction,
        "green": 1 - thresholds["green"],
        "yellow": 1 - thresholds["yellow"],
    }


def threshold_lookup(value, kpi_thresholds):
    """RED/YELLOW/GREEN preview of a KPI's own thresholds, applied to a
    leading indicator's value. Mirrors evaluate.py::classify's boundary
    logic exactly (same inclusive/exclusive edges), but returns the
    RED/YELLOW/GREEN vocabulary instead of a numeric level, since that
    vocabulary never leaves this module (see evaluate_structural_indicator).
    """
    if value is None:
        return None
    direction = kpi_thresholds["direction"]
    green = kpi_thresholds["green"]
    yellow = kpi_thresholds["yellow"]
    if direction == "higher_is_better":
        if value > green:
            return "GREEN"
        if value >= yellow:
            return "YELLOW"
        return "RED"
    if direction == "lower_is_better":
        if value <= green:
            return "GREEN"
        if value <= yellow:
            return "YELLOW"
        return "RED"
    raise ValueError(f"Unknown classify direction '{direction}'")


# ---------------------------------------------------------------------------
# 4.3 — Two separate evaluators
# ---------------------------------------------------------------------------

_LEVEL_TO_RISK_FLAG = {"RED": "concern", "YELLOW": "watch", "GREEN": "none"}


def evaluate_structural_indicator(indicator_id, value, kpi_thresholds):
    """For relationship_type in {structural, deterministic}."""
    if value is None:
        return {
            "risk_flag": "not_evaluated",
            "confidence": "high",
            "basis": "kpi_threshold_preview",
            "value": None,
        }
    level = threshold_lookup(value, kpi_thresholds)
    return {
        "risk_flag": _LEVEL_TO_RISK_FLAG[level],
        "confidence": "high",
        "basis": "kpi_threshold_preview",
        "value": value,
    }


def band_lookup(ratio, bands):
    if ratio is None:
        return "not_evaluated"
    concern = bands.get("concern_threshold")
    watch = bands.get("watch_threshold")
    if concern is not None and ratio >= concern:
        return "concern"
    if watch is not None and ratio >= watch:
        return "watch"
    return "none"


def evaluate_probabilistic_indicator(indicator_id, count, sprint_size, bands):
    """For relationship_type == probabilistic.

    `bands` is the watch/concern threshold dict from org-config.md's
    leading_indicator_thresholds block -- as of the market-benchmark
    population (see leading-indicator-rules.md "Threshold status"), it also
    usually carries a `confidence_basis` (one of
    market_benchmark_convergent / market_benchmark_proxy /
    market_benchmark_proxy_different_metric / qualitative_pattern_operationalized
    / no_market_benchmark_found), which is surfaced verbatim as this
    result's `basis` field -- never a hardcoded generic value. If bands
    carries no `confidence_basis` (older/manually-authored configs), this
    falls back to the previous hardcoded basis strings, so configs written
    before the market-benchmark population still behave identically.

    If bands is missing or its watch_threshold is null (still true for
    2 of 9 indicators in this version -- see leading-indicator-rules.md),
    this returns risk_flag "not_evaluated", never a silent fallback to
    "none".
    """
    if bands is None or bands.get("watch_threshold") is None:
        basis = (bands or {}).get("confidence_basis") or "threshold_not_yet_defined"
        return {
            "risk_flag": "not_evaluated",
            "confidence": "hypothesis",
            "basis": basis,
            "raw_count": count,
            "sprint_size": sprint_size,
        }
    ratio = count / sprint_size if sprint_size else None
    risk_flag = band_lookup(ratio, bands)
    basis = bands.get("confidence_basis") or "directional_n6_finding"
    return {
        "risk_flag": risk_flag,
        "confidence": "hypothesis",
        "basis": basis,
        "raw_count": count,
        "sprint_size": sprint_size,
        "ratio": ratio,
    }


# ---------------------------------------------------------------------------
# Per-indicator raw value/count computation
# ---------------------------------------------------------------------------

def _numeric(value):
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


_ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}")


def _parse_date(value):
    """Parses an ISO-8601 date or datetime string (with or without a 'Z'
    suffix / time component) into a naive `datetime`. Returns None on
    anything unparseable rather than raising -- date fields are frequently
    null in the real dataset.

    Always strips tzinfo before returning: the real dataset mixes
    full-datetime-with-'Z' fields (which parse as tz-aware) and
    date-only fields (which parse as naive via the strptime fallback
    below), and comparing/subtracting an aware value against a naive one
    raises TypeError. Every date in this dataset is UTC in practice, so
    dropping tzinfo loses no real information for day-level comparisons.
    """
    if not value or not isinstance(value, str) or not _ISO_DATE_RE.match(value):
        return None
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        try:
            parsed = datetime.strptime(text[:10], "%Y-%m-%d")
        except ValueError:
            return None
    return parsed.replace(tzinfo=None)


def _sprint_field(sprint_rows, field):
    for row in sprint_rows:
        value = row.get(field)
        if value:
            return value
    return None


def _epic_initiative_linked(task, epic_by_id):
    epic_id = task.get("Parent key")
    if not epic_id:
        return False
    epic = epic_by_id.get(epic_id)
    return bool(epic and epic.get("Initiative key"))


def _compute_solo_task_ratio(tasks, sprint_rows, epic_by_id, prior_sprint_tasks):
    if not tasks:
        return None
    solo = sum(1 for t in tasks if not t.get("Parent key"))
    return solo / len(tasks)


def _compute_initiative_link_ratio(tasks, sprint_rows, epic_by_id, prior_sprint_tasks):
    if not tasks:
        return None
    linked = sum(1 for t in tasks if _epic_initiative_linked(t, epic_by_id))
    return 1 - (linked / len(tasks))


def _compute_epic_sprawl(tasks, sprint_rows, epic_by_id, prior_sprint_tasks):
    epics = {t.get("Parent key") for t in tasks if t.get("Parent key")}
    return len(epics)


_STRUCTURAL_VALUE_FNS = {
    "SOLO_TASK_RATIO": _compute_solo_task_ratio,
    "INITIATIVE_LINK_RATIO_TASK_WEIGHTED": _compute_initiative_link_ratio,
    "EPIC_SPRAWL": _compute_epic_sprawl,
}


def _compute_missing_sp_ratio(tasks, sprint_rows, epic_by_id, prior_sprint_tasks):
    count = sum(1 for t in tasks if t.get("Story points") is None)
    return count, len(tasks)


def _compute_carryover_rate(tasks, sprint_rows, epic_by_id, prior_sprint_tasks):
    if prior_sprint_tasks is None:
        return None  # signalled distinctly -- see compute_leading_indicators
    prior_ids = {t.get("ID") for t in prior_sprint_tasks}
    count = sum(1 for t in tasks if t.get("ID") in prior_ids)
    return count, len(tasks)


def _compute_mid_sprint_task_injection(tasks, sprint_rows, epic_by_id, prior_sprint_tasks):
    sprint_start = _parse_date(_sprint_field(sprint_rows, "Sprint Start Date"))
    if sprint_start is None:
        return 0, len(tasks)
    count = sum(
        1 for t in tasks
        if (created := _parse_date(t.get("CreatedDate"))) is not None and created > sprint_start
    )
    return count, len(tasks)


def _compute_bug_injection_rate(tasks, sprint_rows, epic_by_id, prior_sprint_tasks):
    sprint_start = _parse_date(_sprint_field(sprint_rows, "Sprint Start Date"))
    if sprint_start is None:
        return 0, len(tasks)
    count = sum(
        1 for t in tasks
        if t.get("Type") == "Bug"
        and (created := _parse_date(t.get("CreatedDate"))) is not None
        and created > sprint_start
    )
    return count, len(tasks)


def _compute_long_blocked_count(tasks, sprint_rows, epic_by_id, prior_sprint_tasks):
    count = sum(1 for t in tasks if (days := _numeric(t.get("Stage Blocked days"))) is not None and days > 0)
    return count, len(tasks)


def _compute_reopen_proxy_count(tasks, sprint_rows, epic_by_id, prior_sprint_tasks):
    count = sum(
        1 for t in tasks
        if (recurrence := _numeric(t.get("Stage Done recurrence"))) is not None and recurrence > 1
    )
    return count, len(tasks)


def _compute_stalled_wip_count(tasks, sprint_rows, epic_by_id, prior_sprint_tasks):
    count = 0
    for row, task in zip(sprint_rows, tasks):
        if row.get("Is Completed in Sprint") != "N":
            continue
        dev_days = _numeric(task.get("All Development Days"))
        if dev_days is None or dev_days == 0:
            count += 1
    return count, len(tasks)


def _compute_bug_feature_ratio(tasks, sprint_rows, epic_by_id, prior_sprint_tasks):
    count = sum(1 for t in tasks if t.get("Type") == "Bug")
    return count, len(tasks)


def _compute_late_completion_spike(tasks, sprint_rows, epic_by_id, prior_sprint_tasks):
    sprint_completed = _parse_date(_sprint_field(sprint_rows, "Sprint Completed Date"))
    completed_count = 0
    late_count = 0
    for row, task in zip(sprint_rows, tasks):
        if row.get("Is Completed in Sprint") != "Y":
            continue
        completed_count += 1
        completed_start = _parse_date(task.get("Completed Start Date"))
        if sprint_completed is None or completed_start is None:
            continue
        if (sprint_completed - completed_start).days <= LATE_COMPLETION_WINDOW_DAYS:
            late_count += 1
    return late_count, completed_count


_PROBABILISTIC_VALUE_FNS = {
    "MISSING_SP_RATIO": _compute_missing_sp_ratio,
    "CARRYOVER_RATE": _compute_carryover_rate,
    "MID_SPRINT_TASK_INJECTION": _compute_mid_sprint_task_injection,
    "BUG_INJECTION_RATE": _compute_bug_injection_rate,
    "LONG_BLOCKED_COUNT": _compute_long_blocked_count,
    "REOPEN_PROXY_COUNT": _compute_reopen_proxy_count,
    "STALLED_WIP_COUNT": _compute_stalled_wip_count,
    "BUG_FEATURE_RATIO": _compute_bug_feature_ratio,
    "LATE_COMPLETION_SPIKE": _compute_late_completion_spike,
}


# ---------------------------------------------------------------------------
# 4.1 — compute_leading_indicators
# ---------------------------------------------------------------------------

def _evaluate_one(indicator_id, spec, tasks, sprint_rows, epic_by_id, org_values, defaults, thresholds_cfg, prior_sprint_tasks):
    relationship_type = spec.get("relationship_type")

    if relationship_type in ("structural", "deterministic"):
        value = _STRUCTURAL_VALUE_FNS[indicator_id](tasks, sprint_rows, epic_by_id, prior_sprint_tasks)
        kpi_thresholds = resolve_kpi_thresholds(spec["preview_against_kpi"], org_values, defaults)
        if spec.get("invert_of_kpi"):
            kpi_thresholds = _invert_thresholds(kpi_thresholds)
        return evaluate_structural_indicator(indicator_id, value, kpi_thresholds)

    if relationship_type == "probabilistic":
        if indicator_id == "CARRYOVER_RATE" and prior_sprint_tasks is None:
            return {
                "risk_flag": "not_evaluated",
                "confidence": "hypothesis",
                "basis": "no_prior_sprint_data",
                "raw_count": None,
                "sprint_size": len(tasks),
            }
        count, sprint_size = _PROBABILISTIC_VALUE_FNS[indicator_id](tasks, sprint_rows, epic_by_id, prior_sprint_tasks)
        bands = thresholds_cfg.get(indicator_id.lower())
        return evaluate_probabilistic_indicator(indicator_id, count, sprint_size, bands)

    raise ValueError(f"Unknown relationship_type '{relationship_type}' for indicator '{indicator_id}'")


def compute_leading_indicators(tasks, sprint_rows, epic_by_id, indicator_specs, org_values, sprint_state, prior_sprint_tasks=None):
    """Returns {"planning_horizon": {...}, "in_sprint_horizon": {...}, "closure_horizon": {...}}.

    `tasks` and `sprint_rows` must be the same (team, Sprint ID) working
    set, index-aligned (tasks[i] is the task for sprint_rows[i]) -- the
    same alignment run_analysis.py::main already builds via
    `[task_by_id[row["ID"]] for row in team_rows]`.
    """
    defaults = _load_engine_defaults()
    thresholds_cfg = org_values.get("leading_indicator_thresholds") or {}

    result = {}
    for horizon in ("planning", "in_sprint", "closure"):
        horizon_mode = compute_mode_for(horizon, sprint_state)
        indicators = []
        for indicator_id, spec in indicator_specs.items():
            if spec.get("horizon") != horizon:
                continue

            available_at = set(spec.get("available_at") or HORIZON_AVAILABILITY[horizon])
            indicator_mode = "not_available" if sprint_state not in available_at else horizon_mode

            if indicator_mode == "not_available":
                confidence = "hypothesis" if spec.get("relationship_type") == "probabilistic" else "high"
                indicators.append({
                    "indicator_id": indicator_id,
                    "compute_mode": "not_available",
                    "risk_flag": "not_evaluated",
                    "confidence": confidence,
                    "basis": "horizon_not_available_for_sprint_state",
                })
                continue

            evaluated = _evaluate_one(
                indicator_id, spec, tasks, sprint_rows, epic_by_id, org_values, defaults, thresholds_cfg, prior_sprint_tasks
            )
            evaluated["indicator_id"] = indicator_id
            evaluated["compute_mode"] = indicator_mode
            indicators.append(evaluated)

        result[f"{horizon}_horizon"] = {"compute_mode": horizon_mode, "indicators": indicators}

    return result


# ---------------------------------------------------------------------------
# Leading-indicator-driven catalog routing.
#
# Whether this should exist at all was guardrails.md Rule 9's entire point
# until this version: routing an unvalidated, N=6-observation hypothesis
# into a management recommendation is the fabrication risk the guardrails
# file was built to prevent. This is now a deliberate, explicit exception --
# both `watch` and `concern` trigger, at *any* confidence level (high or
# hypothesis), per an explicit product decision to prioritize early
# coverage over the stricter high-confidence-only gate. The safety is moved
# from "don't trigger" to "never let the report blur a hypothesis-sourced
# recommendation with a verified one" -- see build_report_v2's separate
# `leading_indicators.recommendations` field (never merged into
# `kpi_evaluation.recommendations`) and guardrails.md Rule 9 (rewritten,
# not deleted).
# ---------------------------------------------------------------------------

TRIGGERING_RISK_FLAGS = {"watch", "concern"}


def _indicator_to_risk_id_map(defaults=None):
    defaults = defaults or _load_engine_defaults()
    risk_ids = defaults.get("leading_risk_ids", {})
    return {entry["indicator_id"]: risk_id for risk_id, entry in risk_ids.items()}


def triggered_leading_risks(leading_indicators_block, defaults=None):
    """Extracts every indicator across all three horizons whose risk_flag is
    `watch` or `concern` from a `compute_leading_indicators` result, and
    resolves each to its canonical risk ID (engine_defaults.json
    leading_risk_ids) for catalog matching.

    Returns a list of {risk_id, indicator_id, horizon, risk_flag, confidence}
    dicts -- never just a bare list of IDs, because a consumer must always
    be able to show which indicator and confidence level a match came from
    (guardrails.md Rule 9's reporting requirement). An indicator with no
    entry in leading_risk_ids (should not happen for the 12 shipped
    indicators, but defensive against a future indicator added to
    leading-indicator-rules.md without a corresponding engine_defaults.json
    entry) is skipped rather than raising -- routing is best-effort, unlike
    the hard KeyError semantics of the compute layer itself.
    """
    indicator_to_risk_id = _indicator_to_risk_id_map(defaults)
    triggered = []
    for horizon_key, horizon_name in (
        ("planning_horizon", "planning"),
        ("in_sprint_horizon", "in-progress"),
        ("closure_horizon", "closure"),
    ):
        for indicator in leading_indicators_block.get(horizon_key, {}).get("indicators", []):
            if indicator.get("risk_flag") not in TRIGGERING_RISK_FLAGS:
                continue
            indicator_id = indicator.get("indicator_id")
            risk_id = indicator_to_risk_id.get(indicator_id)
            if risk_id is None:
                continue
            triggered.append({
                "risk_id": risk_id,
                "indicator_id": indicator_id,
                "horizon": horizon_name,
                "risk_flag": indicator["risk_flag"],
                "confidence": indicator.get("confidence"),
            })
    return triggered
