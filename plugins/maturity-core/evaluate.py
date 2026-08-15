"""Deterministic pipeline evaluator for org-defined KPI specs.

Implements the minimal-first DSL from ZADANI-claude-code-maturity-rework.md
Sec.4 (D2/D15): each KPI is a declarative
scope -> select -> filter -> project -> aggregate -> classify pipeline,
interpreted here rather than hardcoded per-org in Python. Extending the
vocabulary (a new predicate or aggregate) is a new engine version, not a
silent fallback — unknown primitives are a hard error.

Threshold values (green/yellow) are resolved with org-config.md taking
priority over the classify block embedded in the org's own pipeline spec;
there is no implicit fallback to engine_defaults.json here — that fallback
happens one layer up, when onboarding generates a new org's pipeline specs.
"""

from statistics import mean, median


def _numeric(value):
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _resolve_link(row, field, tables, table_name, target_field):
    """linked_to predicate: row[field] is a key into `table_name`; read target_field off the linked row."""
    key = row.get(field)
    if key is None:
        return None
    index = tables.get(f"__index__{table_name}")
    if index is None:
        raise ValueError(f"linked_to references table '{table_name}' but no __index__{table_name} was provided")
    linked_row = index.get(key)
    if linked_row is None:
        return None
    return linked_row.get(target_field)


def match_predicate(row, pred, tables):
    op = pred["op"]
    field = pred.get("field")

    if op == "not_null":
        value = row.get(field)
        return value is not None and value != ""
    if op == "is_null":
        value = row.get(field)
        return value is None or value == ""
    if op == "exists":
        return row.get(field) is not None
    if op == "eq":
        return row.get(field) == pred["value"]
    if op == "neq":
        return row.get(field) != pred["value"]
    if op == "in":
        return row.get(field) in pred["values"]
    if op == "not_in":
        return row.get(field) not in pred["values"]
    if op == "linked_to":
        value = _resolve_link(row, field, tables, pred["table"], pred["target_field"])
        if "value" in pred:
            return value == pred["value"]
        return value is not None
    if op == "all_of":
        return all(match_predicate(row, sub, tables) for sub in pred["predicates"])
    if op == "any_of":
        return any(match_predicate(row, sub, tables) for sub in pred["predicates"])

    raise ValueError(
        f"Unknown filter predicate '{op}' — not defined in the minimal-first DSL "
        "vocabulary (engine-defaults-v1). Extending the vocabulary requires a new "
        "engine version, not a silent fallback."
    )


def apply_filters(rows, filters, tables):
    if not filters:
        return list(rows)
    return [row for row in rows if all(match_predicate(row, pred, tables) for pred in filters)]


def _aggregate_scalar(rows, spec):
    kind = spec["aggregate"]
    if kind == "count":
        return len(rows)
    if kind == "count_distinct":
        field = spec["project"]["field"]
        values = {row.get(field) for row in rows if row.get(field) is not None}
        return len(values)
    if kind in ("median", "mean", "sum"):
        field = spec["project"]["field"]
        values = [v for v in (_numeric(row.get(field)) for row in rows) if v is not None]
        if not values:
            return None
        if kind == "median":
            return median(values)
        if kind == "mean":
            return mean(values)
        return sum(values)
    raise ValueError(f"Unknown scalar aggregate '{kind}' — not defined in the minimal-first DSL vocabulary.")


def _aggregate_ratio(rows, spec, tables):
    params = spec["aggregate_params"]
    denominator = rows
    numerator = apply_filters(rows, params["numerator_filter"], tables)
    if not denominator:
        return None
    return len(numerator) / len(denominator)


def _aggregate_group_mean_of_means(rows, spec):
    """Two-level aggregate: mean(value_field) per group_field, then mean of those group means.

    This is the one KPI-specific aggregate outside the generic vocabulary
    (Epic Development Time — mean epic duration across epics). D15 keeps the
    DSL minimal-first: rather than invent a generic group-by primitive for a
    single caller, this aggregate is named for what it computes.
    """
    params = spec["aggregate_params"]
    group_field = params["group_field"]
    value_field = params["value_field"]
    scale_divisor = params.get("scale_divisor", 1)
    by_group = {}
    for row in rows:
        key = row.get(group_field)
        value = _numeric(row.get(value_field))
        if key is None or value is None:
            continue
        by_group.setdefault(key, []).append(value)
    if not by_group:
        return None
    group_means = [mean(values) / scale_divisor for values in by_group.values() if values]
    if not group_means:
        return None
    return mean(group_means)


def aggregate(rows, spec, tables):
    kind = spec["aggregate"]
    if kind == "ratio":
        return _aggregate_ratio(rows, spec, tables)
    if kind == "group_mean_of_means":
        return _aggregate_group_mean_of_means(rows, spec)
    return _aggregate_scalar(rows, spec)


def classify(value, spec, org_thresholds, threshold_prefix):
    if value is None:
        return None
    classify_spec = spec["classify"]
    direction = classify_spec["direction"]
    green = org_thresholds.get(f"{threshold_prefix}_green", classify_spec["green"])
    yellow = org_thresholds.get(f"{threshold_prefix}_yellow", classify_spec["yellow"])

    if direction == "higher_is_better":
        if value > green:
            return 1
        if value >= yellow:
            return 0.5
        return 0
    if direction == "lower_is_better":
        if value <= green:
            return 1
        if value <= yellow:
            return 0.5
        return 0

    raise ValueError(f"Unknown classify direction '{direction}' — not defined in the minimal-first DSL vocabulary.")


def evaluate_kpi(kpi_id, spec, tables, org_thresholds, threshold_prefix):
    """Pure function: (kpi_id, spec, tables, org_thresholds, threshold_prefix) -> {value, level, unit, trace}."""
    table_name = spec["select"]["table"]
    rows = tables.get(table_name, [])

    if spec["aggregate"] == "ratio":
        # Denominator is the unfiltered scope; the numerator is carved out by
        # aggregate_params.numerator_filter, not the top-level filter.
        working_rows = rows
    else:
        working_rows = apply_filters(rows, spec.get("filter"), tables)

    value = aggregate(working_rows, spec, tables)
    level = classify(value, spec, org_thresholds, threshold_prefix)

    trace = {
        "kpi_id": kpi_id,
        "source_table": table_name,
        "scope_row_count": len(rows),
        "working_row_count": len(working_rows),
        "aggregate": spec["aggregate"],
        "value": value,
        "level": level,
    }
    return {
        "value": value,
        "level": level,
        "unit": spec.get("unit"),
        "trace": trace,
    }
