import argparse
import json
import sys
from collections import Counter
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import evaluate  # noqa: E402  (maturity-core/evaluate.py — the DSL pipeline interpreter)
import leading_indicators  # noqa: E402  (maturity-core/leading_indicators.py — the leading indicator layer, Sec.3.5.6)


ROOT = Path(__file__).resolve().parents[1]

# Org-config.md threshold keys don't all match the KPI id 1:1 (legacy naming);
# this is the one mapping table that bridges that, kept here rather than in
# evaluate.py because it is about *our* org-config file convention, not the
# DSL itself.
THRESHOLD_PREFIX = {
    "roadmap_contribution": "roadmap_contribution",
    "sprint_completion": "sprint_completion",
    "cycle_time_p50": "cycle_time",
    "parallel_epics": "parallel_epics",
    "epic_dev_time": "epic_dev_time",
}


def resolve_workspace_root(start: Path) -> Path:
    for candidate in [start, *start.parents]:
        if (candidate / "maturity" / "manifest.json").exists() or (candidate / "DATA" / "jira_db.json").exists():
            return candidate
    return start


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_catalog(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle) or {}
    return list(payload.get("recommendation_catalog", {}).values())


def parse_markdown_kv(text: str):
    """Parse org-config.md's flat `key: value` lines, plus a block form for
    both a list and a nested mapping:

        active_patterns:
          - HIGH_EPIC_WIP
          - LOW_SPRINT_COMPLETION

        leading_indicator_thresholds:
          carryover_rate:
            watch_threshold: null
            concern_threshold: null

    A `key:` line with nothing after the colon, followed by one or more
    lines indented relative to column 0, becomes `values[key] = <parsed>`,
    where `<parsed>` is that indented block fed through `yaml.safe_load` --
    which naturally produces a list for `- item` lines (as before) or a
    nested dict for further `key: value` / `key:` lines (needed for
    org-config.md's `leading_indicator_thresholds` block, whose
    watch/concern values are intentionally `null` placeholders in this
    version -- see leading-indicator-rules.md). This was previously
    silently dropped for the list case (the empty-value line and the
    `- item` lines both failed the plain `key: value` shape and were
    skipped), which meant org-config.md's documented `active_patterns`
    restriction was parsed but never actually reached the engine — see
    `pattern-rules.md`'s "Org-config overrides" section for the behavior
    this now actually implements.
    """
    values = {}
    lines = text.splitlines()
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i].strip()
        if not line or line.startswith("#") or line in {"---", "```"}:
            i += 1
            continue
        if ":" not in line:
            i += 1
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if not value:
            block_lines = []
            j = i + 1
            while j < n and lines[j].strip() and lines[j][:1] in (" ", "\t"):
                block_lines.append(lines[j])
                j += 1
            if block_lines:
                values[key] = yaml.safe_load("\n".join(block_lines))
                i = j
                continue
            i += 1
            continue
        lowered = value.lower()
        if lowered in {"true", "false"}:
            values[key] = lowered == "true"
        else:
            try:
                values[key] = float(value)
            except ValueError:
                values[key] = value
        i += 1
    return values


def load_org_config(path: Path):
    return parse_markdown_kv(path.read_text(encoding="utf-8"))


def normalize_table(table):
    if isinstance(table, dict):
        return list(table.values())
    if isinstance(table, list):
        return table
    return []


def load_kpi_pipelines(text):
    """Extract fenced ```pipeline blocks from org-kpi-definitions.md.

    Each block is a YAML mapping with a required `kpi_id` key. This is the
    machine-readable half of the file; the surrounding prose is for humans
    and is not parsed. Per D2, an org's KPI logic lives here — the engine
    never hardcodes formulas in Python.
    """
    specs = {}
    in_block = False
    buf = []
    for raw_line in text.splitlines():
        stripped = raw_line.strip()
        if not in_block and stripped == "```pipeline":
            in_block = True
            buf = []
            continue
        if in_block and stripped == "```":
            in_block = False
            spec = yaml.safe_load("\n".join(buf)) or {}
            kpi_id = spec.get("kpi_id")
            if not kpi_id:
                raise ValueError("A ```pipeline block is missing its required 'kpi_id' field.")
            specs[kpi_id] = spec
            continue
        if in_block:
            buf.append(raw_line)
    return specs


def compute_kpis(tasks, sprint_rows, epic_by_id, kpi_specs, org_values):
    tables = {
        "A_Task": tasks,
        "A_Sprints": sprint_rows,
        "__index__A_Epic": epic_by_id,
    }
    kpis = {}
    for kpi_id, threshold_prefix in THRESHOLD_PREFIX.items():
        spec = kpi_specs.get(kpi_id)
        if spec is None:
            raise ValueError(
                f"org-kpi-definitions.md has no ```pipeline block for '{kpi_id}'. "
                "All 5 KPIs must be defined — no silent fallback to engine defaults (D2)."
            )
        result = evaluate.evaluate_kpi(kpi_id, spec, tables, org_values, threshold_prefix)
        kpis[kpi_id] = {"value": result["value"], "level": result["level"], "unit": result["unit"]}
    return kpis


def detect_patterns(kpis, active_patterns=None):
    """Detect triggered patterns; optionally restrict to org-config's active_patterns.

    Per pattern-rules.md "Org-config overrides": if org-config.md specifies
    active_patterns, only those are detected/reported, even if a KPI's
    level would otherwise trigger a pattern outside that set. If
    active_patterns is absent (None), all patterns are eligible.
    """
    triggered = []
    if kpis["sprint_completion"]["level"] == 0:
        triggered.append("LOW_SPRINT_COMPLETION")
    if kpis["parallel_epics"]["level"] == 0:
        triggered.append("HIGH_EPIC_WIP")
    if kpis["cycle_time_p50"]["level"] == 0:
        triggered.append("LONG_CYCLE_TIME")
    if kpis["epic_dev_time"]["level"] == 0:
        triggered.append("LONG_EPIC_DEVELOPMENT_TIME")
    if kpis["roadmap_contribution"]["level"] == 0:
        triggered.append("LOW_ROADMAP_CONTRIBUTION")
    if "HIGH_EPIC_WIP" in triggered and "LONG_CYCLE_TIME" in triggered:
        triggered.append("WIP_DEATH_SPIRAL")
    if "LOW_ROADMAP_CONTRIBUTION" in triggered and "LOW_SPRINT_COMPLETION" in triggered:
        triggered.append("ROADMAP_DRIFT")
    if active_patterns is not None:
        triggered = [p for p in triggered if p in active_patterns]
    return triggered


IMPACT_RANK = {"high": 0, "medium": 1, "low": 2}
EFFORT_RANK = {"low": 0, "medium": 1, "high": 2}


def recommend_interventions(triggered_patterns, catalog):
    seen = []
    for item in catalog:
        applicable = set(item.get("applicable_pattern_ids", []))
        match_count = len(applicable & set(triggered_patterns))
        if match_count:
            seen.append((match_count, item))
    if not seen:
        return []
    seen.sort(
        key=lambda entry: (
            -entry[0],
            IMPACT_RANK.get(entry[1].get("impact"), len(IMPACT_RANK)),
            EFFORT_RANK.get(entry[1].get("effort"), len(EFFORT_RANK)),
            entry[1].get("recommendation_id", ""),
        )
    )
    return [
        {
            "recommendation_id": item.get("recommendation_id"),
            "recommendation_name": item.get("recommendation_name"),
            "applicable_pattern_ids": item.get("applicable_pattern_ids", []),
            "intervention": item.get("intervention"),
            "expected_outcome": item.get("expected_outcome"),
            "effort": item.get("effort"),
            "impact": item.get("impact"),
            "owner_role": item.get("owner_role"),
            "preconditions": item.get("preconditions"),
            "risks": item.get("risks"),
            "review_cycle": item.get("review_cycle"),
        }
        for _, item in seen[:3]
    ]


def recommend_leading_indicator_interventions(triggered_risks, catalog):
    """Mirrors recommend_interventions()'s ranking exactly (match count desc,
    impact desc, effort asc, recommendation_id), but keyed on
    `applicable_leading_risk_ids` instead of `applicable_pattern_ids`.

    `triggered_risks` is leading_indicators.triggered_leading_risks()'s
    output -- {risk_id, indicator_id, horizon, risk_flag, confidence} dicts.
    A catalog entry can carry both applicable_pattern_ids and
    applicable_leading_risk_ids and be matched independently by both this
    function and recommend_interventions() -- the two paths are not
    mutually exclusive (confirmed: e.g. INT-008 matches LONG_CYCLE_TIME via
    the KPI path and LONG_BLOCKED_TASKS/STALLED_WIP via this one).

    Per guardrails.md Rule 9, every returned entry carries `matched_risks`
    -- the full triggering detail (indicator, horizon, risk_flag,
    confidence) -- so a leading-indicator-sourced recommendation can never
    be rendered without visible provenance, unlike a KPI-pattern-sourced
    one which is always confidence: verified by construction.
    """
    triggered_risk_ids = {risk["risk_id"] for risk in triggered_risks}
    risk_detail_by_id = {risk["risk_id"]: risk for risk in triggered_risks}
    seen = []
    for item in catalog:
        applicable = set(item.get("applicable_leading_risk_ids", []))
        matched = applicable & triggered_risk_ids
        if matched:
            seen.append((len(matched), item, matched))
    if not seen:
        return []
    seen.sort(
        key=lambda entry: (
            -entry[0],
            IMPACT_RANK.get(entry[1].get("impact"), len(IMPACT_RANK)),
            EFFORT_RANK.get(entry[1].get("effort"), len(EFFORT_RANK)),
            entry[1].get("recommendation_id", ""),
        )
    )
    return [
        {
            "recommendation_id": item.get("recommendation_id"),
            "recommendation_name": item.get("recommendation_name"),
            "applicable_leading_risk_ids": item.get("applicable_leading_risk_ids", []),
            "matched_risks": [risk_detail_by_id[rid] for rid in sorted(matched)],
            "intervention": item.get("intervention"),
            "expected_outcome": item.get("expected_outcome"),
            "effort": item.get("effort"),
            "impact": item.get("impact"),
            "owner_role": item.get("owner_role"),
            "preconditions": item.get("preconditions"),
            "risks": item.get("risks"),
            "review_cycle": item.get("review_cycle"),
        }
        for _, item, matched in seen[:3]
    ]


def band_for_score(score, bands):
    for band in bands:
        if band["min"] <= score <= band["max"]:
            return band["label"]
    return None


def sprint_closed_for_team(team_sprint_rows):
    """True only if every row in this (team, Sprint ID) group says closed.

    `Sprint ID` is the real, stable sprint identifier (confirmed: every
    distinct Sprint ID in the real dataset has exactly one Sprint State,
    with zero exceptions). Rows reaching this function are already grouped
    by (team, Sprint ID) in main(), so in practice this set will always
    have exactly one member -- the check stays explicit rather than
    assuming that invariant, since a caller could pass an unfiltered group.
    """
    states = {row.get("Sprint State") for row in team_sprint_rows}
    return states == {"closed"}


def build_report(team, sprint_label, sprint_id, kpis, patterns, recommendations, tasks, sprint_rows, org_name, defaults):
    levels = [kpis[key]["level"] for key in ["roadmap_contribution", "sprint_completion", "cycle_time_p50", "parallel_epics", "epic_dev_time"]]
    score = round(sum(level or 0 for level in levels) / 5 * 100)
    band = band_for_score(score, defaults["scoring"]["bands"])
    closed = sprint_closed_for_team(sprint_rows)
    report = {
        "team": team,
        "sprint": sprint_label,
        "sprint_id": sprint_id,
        "org_name": org_name,
        "compute_mode": "verified",
        "sprint_closed_for_team": closed,
        "score": score,
        "band": band,
        "tasks_analyzed": len(tasks),
        "kpis": kpis,
        "patterns": patterns,
        "recommendations": recommendations,
    }
    if not closed:
        state_counts = Counter(row.get("Sprint State") for row in sprint_rows)
        non_closed = {state: count for state, count in state_counts.items() if state != "closed"}
        non_closed_count = sum(non_closed.values())
        report["sprint_state_warning"] = (
            f"{non_closed_count} of {len(sprint_rows)} rows for sprint {sprint_id!r} "
            f"(one of this team's own sprints within the {sprint_label!r} period) are not "
            f"marked closed (states: {non_closed}). This specific sprint is still in "
            f"progress; figures reflect a snapshot, not a final result, and may still "
            f"change."
        )
    return report


REPORT_TYPE_BY_SPRINT_STATE = {
    "future": "sprint_start_risk_flag",
    "active": "mid_sprint_drift_check",
    "closed": "sprint_close_retrospective",
}


def build_report_v2(team, sprint_label, sprint_id, sprint_state, kpis, patterns, recommendations,
                     tasks, sprint_rows, org_name, defaults, leading_indicators_block):
    """Sec.5 report shape: `kpi_evaluation` and `leading_indicators` as
    always-sibling top-level keys, never merged into one number or field.

    Used only by build_sprint_window_reports (the new --window mode).
    build_report above is unchanged and remains what main()'s default,
    closed-sprint-only path produces -- this preserves backward
    compatibility for existing readers of analysis_output.json (in
    particular maturity-learning-loop) without requiring them to change.
    """
    closed = sprint_state == "closed"
    if closed:
        levels = [kpis[key]["level"] for key in ["roadmap_contribution", "sprint_completion", "cycle_time_p50", "parallel_epics", "epic_dev_time"]]
        score = round(sum(level or 0 for level in levels) / 5 * 100)
        band = band_for_score(score, defaults["scoring"]["bands"])
        kpi_evaluation = {
            "compute_mode": "verified",
            "available": True,
            "score": score,
            "band": band,
            "kpis": kpis,
            "patterns": patterns,
            "recommendations": recommendations,
        }
    else:
        # The engine must not compute KPIs from an incomplete sprint (today's
        # actual behavior for main(); this mode just names it explicitly).
        kpi_evaluation = {
            "compute_mode": "not_available",
            "available": False,
            "score": None,
            "band": None,
            "kpis": None,
            "patterns": [],
            "recommendations": [],
        }

    report = {
        "team": team,
        "sprint": sprint_label,
        "sprint_id": sprint_id,
        "sprint_state": sprint_state,
        "report_type": REPORT_TYPE_BY_SPRINT_STATE.get(sprint_state, "unknown"),
        "org_name": org_name,
        "tasks_analyzed": len(tasks),
        "kpi_evaluation": kpi_evaluation,
        "leading_indicators": leading_indicators_block,
    }

    if sprint_state == "future":
        report["sprint_state_warning"] = (
            f"Sprint {sprint_id!r} has not started yet (state: future). Only the planning "
            f"horizon of the leading indicator layer is meaningful here; kpi_evaluation is "
            f"not available and will not become available until this sprint closes."
        )
    elif sprint_state == "active":
        report["sprint_state_warning"] = (
            f"Sprint {sprint_id!r} is in progress (state: active). kpi_evaluation is not "
            f"available until this sprint closes; leading_indicators reflects a provisional, "
            f"in-flight snapshot that may still change."
        )

    return report


def build_sprint_window_reports(sprint_rows, task_by_id, epic_by_id, kpi_specs, indicator_specs,
                                 org_values, catalog, defaults, window_labels=None,
                                 excluded_indicators=None):
    """One report per (team, Sprint ID), across ALL sprint states present in
    `window_labels` (future/active/closed) -- unlike main(), which filters
    to the latest closed calendar period only. `window_labels`: a list of
    `Sprint Index Name` values, or None for every label present in the data.

    `indicator_specs` must already be the per-org *applicable* subset (see
    leading_indicators.filter_applicable_indicators) -- this function does
    not filter, it only computes over whatever specs it is given, and
    attaches `excluded_indicators` (the same org-wide list on every report,
    if non-empty) for transparency. Omitted entirely when empty/None, so
    the common case (nothing excluded) carries no dead weight.

    Reports are sorted chronologically per team (by each group's own Sprint
    Start Date), so a leading indicator observed in sprint N and a KPI
    outcome in sprint N+1 are already in the right order for a later
    cross-sprint correlation analysis -- not implemented here (see
    leading-indicator-rules.md "What this file does NOT define").
    """
    if window_labels is None:
        window_labels = sorted({row.get("Sprint Index Name") for row in sprint_rows if row.get("Sprint Index Name")})

    period_rows = [row for row in sprint_rows if row.get("Sprint Index Name") in set(window_labels)]
    teams = sorted({task_by_id[row["ID"]]["Team"] for row in period_rows if task_by_id.get(row["ID"])})

    reports = []
    for team in teams:
        team_period_rows = [row for row in period_rows if task_by_id.get(row["ID"]) and task_by_id[row["ID"]].get("Team") == team]

        rows_by_sprint_id = {}
        for row in team_period_rows:
            rows_by_sprint_id.setdefault(row.get("Sprint ID"), []).append(row)

        def _start_date(sprint_id):
            rows = rows_by_sprint_id[sprint_id]
            return (rows[0].get("Sprint Start Date") or "", sprint_id or "")

        prior_tasks = None
        for sprint_id in sorted(rows_by_sprint_id, key=_start_date):
            team_rows = rows_by_sprint_id[sprint_id]
            tasks = [task_by_id[row["ID"]] for row in team_rows]
            sprint_label = team_rows[0].get("Sprint Index Name")
            sprint_state = team_rows[0].get("Sprint State")

            if sprint_state == "closed":
                kpis = compute_kpis(tasks, team_rows, epic_by_id, kpi_specs, org_values)
                patterns = detect_patterns(kpis, org_values.get("active_patterns"))
                recommendations = recommend_interventions(patterns, catalog)
            else:
                kpis, patterns, recommendations = None, [], []

            leading = leading_indicators.compute_leading_indicators(
                tasks, team_rows, epic_by_id, indicator_specs, org_values, sprint_state, prior_tasks
            )
            # Leading-indicator-driven catalog routing (guardrails.md Rule 9,
            # rewritten): watch/concern at any confidence can trigger a match,
            # but it always lands in this separate leading_indicators.recommendations
            # field -- never merged into kpi_evaluation.recommendations, so a
            # hypothesis-sourced suggestion can never be mistaken for a
            # verified-pattern one.
            triggered_risks = leading_indicators.triggered_leading_risks(leading)
            leading["recommendations"] = recommend_leading_indicator_interventions(triggered_risks, catalog)

            report = build_report_v2(
                team, sprint_label, sprint_id, sprint_state, kpis, patterns, recommendations,
                tasks, team_rows, org_values.get("org_name", "demo"), defaults, leading,
            )
            if excluded_indicators:
                report["excluded_indicators"] = excluded_indicators
            reports.append(report)
            prior_tasks = tasks

    return reports


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=None)
    parser.add_argument(
        "--window", "--all-sprint-states", dest="window", action="store_true",
        help=(
            "Compute across every sprint-state window (future/active/closed) for every "
            "team, instead of only the single latest closed calendar period. Adds the "
            "leading_indicators block to each report and does not change or overwrite "
            "the default analysis_output.json -- writes analysis_output_window.json "
            "instead."
        ),
    )
    args = parser.parse_args()
    workspace_root = resolve_workspace_root(Path(args.root or Path.cwd()))

    manifest_path = workspace_root / "maturity" / "manifest.json"
    if not manifest_path.exists():
        print("Missing manifest.json", file=sys.stderr)
        return 1
    manifest = load_json(manifest_path)

    jira_db_path = workspace_root / manifest.get("jira_db_path", "DATA/jira_db.json")
    catalog_path = workspace_root / manifest.get("catalog_path", "catalog.yaml")
    config_path = workspace_root / manifest.get("org_config_path", "maturity/org-config.md")
    definitions_path = workspace_root / manifest.get("org_kpi_definitions_path", "maturity/org-kpi-definitions.md")

    for required in [jira_db_path, catalog_path, config_path, definitions_path]:
        if not required.exists():
            print(f"Missing required input: {required}", file=sys.stderr)
            return 1

    data = load_json(jira_db_path)
    catalog = load_catalog(catalog_path)
    org_values = load_org_config(config_path)
    try:
        leading_indicators.validate_leading_indicator_thresholds(org_values)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    kpi_specs = load_kpi_pipelines(definitions_path.read_text(encoding="utf-8"))

    defaults = load_json(Path(__file__).resolve().with_name("engine_defaults.json"))

    task_rows = normalize_table(data.get("A_Task", []))
    epic_rows = normalize_table(data.get("A_Epic", []))
    sprint_rows = normalize_table(data.get("A_Sprints", []))

    task_by_id = {row.get("ID"): row for row in task_rows if isinstance(row, dict) and row.get("ID") is not None}
    epic_by_id = {row.get("ID"): row for row in epic_rows if isinstance(row, dict) and row.get("ID") is not None}

    if args.window:
        # Engine-level indicator definitions, resolved relative to this
        # script (like engine_defaults.json), not the workspace -- the 12
        # indicators are fixed, not per-org, unlike the KPI pipelines.
        indicator_specs = leading_indicators.load_indicator_specs(
            leading_indicators.DEFAULT_RULES_PATH.read_text(encoding="utf-8")
        )
        indicator_specs, excluded_indicators = leading_indicators.filter_applicable_indicators(
            indicator_specs, org_values
        )
        reports = build_sprint_window_reports(
            sprint_rows, task_by_id, epic_by_id, kpi_specs, indicator_specs, org_values, catalog, defaults,
            excluded_indicators=excluded_indicators,
        )
        output_path = workspace_root / "maturity" / "analysis_output_window.json"
        output_path.write_text(json.dumps(reports, indent=2), encoding="utf-8")
        print(json.dumps(reports, indent=2))
        return 0

    # "Sprint Index Name" (e.g. "2025-S26") is a shared calendar-period label,
    # NOT a unique sprint identifier -- confirmed empirically (every distinct
    # "Sprint ID" has exactly one "Sprint State", but a label can span many
    # Sprint IDs) and by the source data's own anonymization policy, which
    # documents "Sprint ID" as "the stable sprint identifier". It is used
    # here only to pick which calendar period to report on; the actual
    # team x sprint join below groups by Sprint ID, never by this label.
    sprint_names = sorted({row.get("Sprint Index Name") for row in sprint_rows if row.get("Sprint State") == "closed" and row.get("Sprint Index Name")})
    sprint_label = sprint_names[-1] if sprint_names else None
    if not sprint_label:
        print("No closed sprint found in Jira data", file=sys.stderr)
        return 1

    period_rows = [row for row in sprint_rows if row.get("Sprint Index Name") == sprint_label]
    teams = sorted({task_by_id[row["ID"]]["Team"] for row in period_rows if task_by_id.get(row["ID"])})
    reports = []
    for team in teams:
        team_period_rows = [row for row in period_rows if task_by_id.get(row["ID"]) and task_by_id[row["ID"]].get("Team") == team]

        # Group by the real sprint identity. A team can have more than one
        # distinct Sprint ID within the same calendar-label period (observed:
        # up to 7, for teams that are really several boards/squads sharing
        # one Team) -- pooling those together would silently blend
        # unrelated sprints' tasks into one KPI computation (e.g. Parallel
        # Epics counting epics across sprints that were never concurrent).
        # One report per (team, Sprint ID) instead; sorted by each group's
        # own Sprint Start Date so multiple reports for one team read
        # chronologically.
        rows_by_sprint_id = {}
        for row in team_period_rows:
            rows_by_sprint_id.setdefault(row.get("Sprint ID"), []).append(row)

        def _start_date(sprint_id):
            rows = rows_by_sprint_id[sprint_id]
            return (rows[0].get("Sprint Start Date") or "", sprint_id or "")

        for sprint_id in sorted(rows_by_sprint_id, key=_start_date):
            team_rows = rows_by_sprint_id[sprint_id]
            tasks = [task_by_id[row["ID"]] for row in team_rows]
            kpis = compute_kpis(tasks, team_rows, epic_by_id, kpi_specs, org_values)
            patterns = detect_patterns(kpis, org_values.get("active_patterns"))
            recommendations = recommend_interventions(patterns, catalog)
            reports.append(build_report(team, sprint_label, sprint_id, kpis, patterns, recommendations, tasks, team_rows, org_values.get("org_name", "demo"), defaults))

    output_path = workspace_root / "maturity" / "analysis_output.json"
    output_path.write_text(json.dumps(reports, indent=2), encoding="utf-8")
    print(json.dumps(reports, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
