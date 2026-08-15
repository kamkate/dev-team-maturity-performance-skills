# Leading Indicator Rules
definition_version: leading-indicator-rules-v1
source: thesis Sec.3.5.6 "Předstihové signály: rozšíření diagnostické vrstvy
  na plánovací a průběžný horizont" (Table 3.X)

> ⚠️ **Leading indicators are NOT KPIs.** They must never be presented,
> named, or visually styled in a way that could be confused with the final
> KPI evaluation (`kpi_evaluation` block). A leading indicator's
> `risk_flag` (`none | watch | concern | not_evaluated`) is a different
> vocabulary from a KPI's `level` (`GREEN | YELLOW | RED`) and the two are
> never interchangeable — see `guardrails.md` Rules 8–10.

This file is the single source of truth for the 12 leading indicators —
parsed directly by `maturity-core/leading_indicators.py::load_indicator_specs`
from the fenced ` ```indicator ` blocks below, the same way
`org-kpi-definitions.md`'s ` ```pipeline ` blocks are parsed by
`run_analysis.py::load_kpi_pipelines` (D2). Unlike KPI formulas, indicator
definitions here are engine-level and fixed across all 12 — not
per-organization — so this file is loaded from the engine's own directory
tree (`maturity-engine/references/`), not from a workspace, the same way
`maturity-core/engine_defaults.json` is loaded relative to the script
rather than the workspace root.

The actual arithmetic for each indicator's raw value/count is implemented
in `leading_indicators.py` (Python, not a DSL pipeline) — see that file's
module docstring for why indicators don't go through the KPI DSL (D2 scopes
the DSL to the 5 known KPIs only; D15 keeps it minimal-first).

---

## Relationship types

- **deterministic** — the indicator IS a KPI-derived value (e.g. a
  mathematical identity with `1 - kpi_value`). Always `confidence: high`.
- **structural** — the indicator makes a KPI outcome structurally
  predictable or impossible, independent of delivery effort. Evaluated
  against a preview of the affected KPI's own RED/YELLOW/GREEN thresholds.
  Always `confidence: high` (the preview logic itself is deterministic,
  even though what it predicts has not happened yet).
- **probabilistic** — the indicator historically co-occurs with KPI
  degradation, per a **directional finding validated only on N = 6
  observations** (see `TODO_projekt.md` "Historický backtesting"). Always
  `confidence: hypothesis` (or `not_evaluated` if no threshold is defined
  yet — see below). Never presented as if it were confirmed.

## Horizons

- **planning** — computable before or during the sprint from committed
  scope (`available_at: [future, active, closed]`).
- **in_sprint** — computable only once the sprint has actually started
  (`available_at: [active, closed]`); meaningless for a `future` sprint
  because there is no in-flight behavior yet to observe.
- **closure** — computable only once the sprint has closed
  (`available_at: [closed]`); depends on final completion state.

## Compute mode

Governed centrally by `leading_indicators.py::compute_mode_for` /
`HORIZON_AVAILABILITY` — see that module. No other part of the codebase
duplicates this availability logic. Values: `not_available | provisional |
verified`. This is a distinct field from `risk_flag` — a `verified`
indicator can still have `risk_flag: not_evaluated` if its threshold is
undefined.

## Threshold status — 7 of 9 populated from market benchmarks

The `watch_threshold` / `concern_threshold` values for 7 of the 9
probabilistic indicators are populated in `org-config.md`'s
`leading_indicator_thresholds` block with market-benchmark-informed
starting points — see `leading-indicator-market-benchmarks.md` for full
sourcing. Each populated entry also carries a `confidence_basis`, surfaced
verbatim as the report's `basis` field (never a hardcoded generic value —
see `leading_indicators.py::evaluate_probabilistic_indicator`):

- `market_benchmark_convergent` — multiple independent industry sources
  converge on a similar value.
- `market_benchmark_proxy` — a market benchmark exists for a closely
  related metric, adapted here as a proxy for this indicator.
- `market_benchmark_proxy_different_metric` — the benchmark measures a
  meaningfully different metric than this indicator; treat with more
  caution than a same-metric proxy.
- `qualitative_pattern_operationalized` — no numeric market benchmark;
  the threshold operationalizes a qualitative pattern described in
  industry sources (e.g. "end-loading") into a concrete band.
- `no_market_benchmark_found` — no usable benchmark exists (the 2
  remaining indicators, `LONG_BLOCKED_COUNT` and `STALLED_WIP_COUNT`);
  `watch_threshold`/`concern_threshold` stay `null` on purpose.

These remain starting points, not confirmed thresholds — none are yet
validated against this org's own sprint history. Re-calibrating them
(historical backtesting against more sprints) is out of scope for this
version — see `TODO_projekt.md` "Historický backtesting předstihových
signálů". Until an indicator has a real, non-null `watch_threshold`, it
reports `risk_flag: "not_evaluated"`, never a silent fallback to `"none"`.

This is a separate axis from **applicability** — whether an indicator
makes sense for a given org's workflow at all (e.g. no story points →
`MISSING_SP_RATIO` is not applicable). See
`maturity-onboarding/references/leading-indicator-applicability.md` and
`output-template.md` §4 for how `not_applicable` (excluded before
computation) differs from `not_evaluated` (computed, no threshold yet).

---

## The 12 indicators

### 1. SOLO_TASK_RATIO

```indicator
indicator_id: SOLO_TASK_RATIO
horizon: planning
affected_kpis: [roadmap_contribution, parallel_epics]
relationship_type: structural
available_at: [future, active, closed]
evaluation_mode: reuse_kpi_threshold
preview_against_kpi: roadmap_contribution
invert_of_kpi: true
source_fields: ["Parent key"]
formula: >
  Share of committed sprint tasks with no Parent key (no epic link at
  all). A solo task cannot be roadmap-linked under any org's
  roadmap-linkage rule (Parent key -> Epic -> Initiative key), so a rising
  solo-task share structurally caps how high Roadmap Contribution can go
  this sprint, before a single task is delivered. Solo tasks are always a
  subset of "not initiative-linked" tasks (solo_task_ratio <=
  1 - roadmap_contribution), so if solo_task_ratio alone already crosses
  a RED boundary under the same inverted-threshold preview used for
  INITIATIVE_LINK_RATIO_TASK_WEIGHTED (invert_of_kpi), roadmap_contribution
  is structurally guaranteed to be at least as bad. Uses the same
  invert_of_kpi transform for that reason, even though (unlike indicator 2)
  this is not itself a mathematical identity with roadmap_contribution --
  hence relationship_type stays "structural", not "deterministic".
  value = count(tasks where Parent key is null) / count(tasks)
```

### 2. INITIATIVE_LINK_RATIO_TASK_WEIGHTED

```indicator
indicator_id: INITIATIVE_LINK_RATIO_TASK_WEIGHTED
horizon: planning
affected_kpis: [roadmap_contribution]
relationship_type: deterministic
available_at: [future, active, closed]
evaluation_mode: reuse_kpi_threshold
preview_against_kpi: roadmap_contribution
invert_of_kpi: true
source_fields: ["Parent key", "A_Epic.Initiative key"]
formula: >
  Mathematical identity: value = 1 - roadmap_contribution (task-weighted,
  same tasks/epics as the KPI 1 formula). Always confidence: high, never
  "hypothesis" -- this is not a co-occurrence finding, it is the same
  computation as roadmap_contribution read from the other side. Evaluated
  against roadmap_contribution's own thresholds with the direction and
  green/yellow boundaries inverted around 1 (since value = 1 - kpi_value
  exactly), per invert_of_kpi.
  value = 1 - (count(tasks where Parent key -> Epic -> Initiative key is
  not null) / count(tasks))
```

### 3. MISSING_SP_RATIO

```indicator
indicator_id: MISSING_SP_RATIO
horizon: planning
affected_kpis: [sprint_completion, cycle_time_p50]
relationship_type: probabilistic
available_at: [future, active, closed]
evaluation_mode: probabilistic_band
confidence_basis: market_benchmark_proxy
source_fields: ["Story points"]
formula: >
  Share of committed tasks with no Story points recorded. Unestimated
  work correlates (directional, N=6) with worse predictability -- it
  cannot be sized during planning, which historically co-occurs with
  lower sprint completion and longer cycle time.
  raw_count = count(tasks where Story points is null)
  sprint_size = count(tasks)
```

### 4. CARRYOVER_RATE

```indicator
indicator_id: CARRYOVER_RATE
horizon: planning
affected_kpis: [sprint_completion, cycle_time_p50]
relationship_type: probabilistic
available_at: [future, active, closed]
evaluation_mode: probabilistic_band
confidence_basis: market_benchmark_convergent
source_fields: ["ID", "prior_sprint_tasks (same team's previous sprint)"]
formula: >
  The one Tier-0 signal that reads beyond the current sprint. Share of
  this sprint's committed tasks whose task ID also appeared in the same
  team's immediately preceding sprint (prior_sprint_tasks). High carryover
  co-occurs (directional, N=6) with lower completion and longer cycle
  time in the sprint it lands in. Requires prior_sprint_tasks; if that
  is not available (e.g. this is the team's first observed sprint),
  the indicator reports risk_flag "not_evaluated" with
  basis "no_prior_sprint_data", not a fabricated raw_count of 0.
  raw_count = count(tasks where ID in {t.ID for t in prior_sprint_tasks})
  sprint_size = count(tasks)
```

### 5. EPIC_SPRAWL

```indicator
indicator_id: EPIC_SPRAWL
horizon: planning
affected_kpis: [sprint_completion, parallel_epics]
relationship_type: structural
available_at: [future, active, closed]
evaluation_mode: reuse_kpi_threshold
preview_against_kpi: parallel_epics
source_fields: ["Parent key"]
formula: >
  Count of distinct epics already represented in the committed task set --
  the same formula as the parallel_epics KPI itself, but available at
  planning horizon (before the sprint closes, even for a future sprint)
  as an early preview of what parallel_epics will resolve to. Structural
  because the epic count is already fixed by what was committed; no
  amount of delivery effort during the sprint changes it.
  value = count_distinct(Parent key among tasks where Parent key is not null)
```

### 6. MID_SPRINT_TASK_INJECTION

```indicator
indicator_id: MID_SPRINT_TASK_INJECTION
horizon: in_sprint
affected_kpis: [roadmap_contribution, sprint_completion, parallel_epics]
relationship_type: probabilistic
available_at: [active, closed]
evaluation_mode: probabilistic_band
confidence_basis: market_benchmark_proxy
source_fields: ["CreatedDate", "A_Sprints.Sprint Start Date"]
formula: >
  Share of tasks in the sprint whose CreatedDate is after this Sprint
  ID's own Sprint Start Date -- work added after the sprint had already
  started, not planned at commitment time. Historically co-occurs with
  scope pressure degrading completion and roadmap contribution.
  raw_count = count(tasks where CreatedDate > sprint_start_date)
  sprint_size = count(tasks)
```

### 7. BUG_INJECTION_RATE

```indicator
indicator_id: BUG_INJECTION_RATE
horizon: in_sprint
affected_kpis: [roadmap_contribution, cycle_time_p50, parallel_epics]
relationship_type: probabilistic
available_at: [active, closed]
evaluation_mode: probabilistic_band
confidence_basis: market_benchmark_proxy_different_metric
source_fields: ["Type", "CreatedDate", "A_Sprints.Sprint Start Date"]
formula: >
  Share of tasks in the sprint that are Type = "Bug" AND created after
  the sprint's own Sprint Start Date -- reactive bug work entering mid
  sprint, a narrower and more specific case of MID_SPRINT_TASK_INJECTION.
  raw_count = count(tasks where Type == "Bug" AND CreatedDate > sprint_start_date)
  sprint_size = count(tasks)
```

### 8. LONG_BLOCKED_COUNT

```indicator
indicator_id: LONG_BLOCKED_COUNT
horizon: in_sprint
affected_kpis: [cycle_time_p50, parallel_epics]
relationship_type: probabilistic
available_at: [active, closed]
evaluation_mode: probabilistic_band
confidence_basis: no_market_benchmark_found
source_fields: ["Stage Blocked days"]
formula: >
  Count of tasks in the sprint that have recorded any time in the
  Blocked stage (Stage Blocked days > 0). The "how many days counts as
  long" cutoff is itself one of the deferred thresholds (see
  TODO_projekt.md) -- this raw_count intentionally does not embed an
  arbitrary day cutoff of its own; it counts "was blocked at all" as the
  base signal, and watch/concern bands (once defined) apply to the ratio.
  raw_count = count(tasks where Stage Blocked days is not null AND > 0)
  sprint_size = count(tasks)
```

### 9. REOPEN_PROXY_COUNT

```indicator
indicator_id: REOPEN_PROXY_COUNT
horizon: in_sprint
affected_kpis: [sprint_completion, cycle_time_p50, parallel_epics]
relationship_type: probabilistic
available_at: [active, closed]
evaluation_mode: probabilistic_band
confidence_basis: market_benchmark_convergent
source_fields: ["Stage Done recurrence"]
formula: >
  Proxy for reopened work: no full status-transition changelog is
  available, but "Stage Done recurrence" > 1 means the task re-entered
  the Done stage more than once -- it left Done and came back, i.e. was
  reopened. This is a proxy, not a direct reopen-event count.
  raw_count = count(tasks where Stage Done recurrence is not null AND > 1)
  sprint_size = count(tasks)
```

### 10. STALLED_WIP_COUNT

```indicator
indicator_id: STALLED_WIP_COUNT
horizon: in_sprint
affected_kpis: [cycle_time_p50, parallel_epics]
relationship_type: probabilistic
available_at: [active, closed]
evaluation_mode: probabilistic_band
confidence_basis: no_market_benchmark_found
source_fields: ["Is Completed in Sprint", "All Development Days"]
formula: >
  Count of tasks still incomplete in the sprint (Is Completed in Sprint =
  "N") with no recorded development progress at all (All Development
  Days is null or 0) -- WIP that has not actually started moving.
  raw_count = count(tasks where Is Completed in Sprint == "N" AND
    (All Development Days is null OR All Development Days == 0))
  sprint_size = count(tasks)
```

### 11. BUG_FEATURE_RATIO

```indicator
indicator_id: BUG_FEATURE_RATIO
horizon: in_sprint
affected_kpis: [roadmap_contribution, sprint_completion]
relationship_type: probabilistic
available_at: [active, closed]
evaluation_mode: probabilistic_band
confidence_basis: market_benchmark_proxy
source_fields: ["Type"]
formula: >
  Share of the sprint's tasks that are Type = "Bug". A high bug share
  historically co-occurs with lower roadmap contribution (reactive work
  crowding out strategic work) and lower completion.
  raw_count = count(tasks where Type == "Bug")
  sprint_size = count(tasks)
```

Note: the table in Sec.3.5.6 lists this indicator's horizon as
"planning → in_sprint" (its value is meaningful at both). It is grouped
under the `in_sprint_horizon` report block here because bug composition of
committed scope is only fully known once bugs triaged mid-sprint are also
counted; `available_at` is `[active, closed]` accordingly (excludes
`future`, where bug/feature composition of not-yet-triaged backlog is not
yet meaningful).

### 12. LATE_COMPLETION_SPIKE

```indicator
indicator_id: LATE_COMPLETION_SPIKE
horizon: closure
affected_kpis: [sprint_completion, cycle_time_p50]
relationship_type: probabilistic
available_at: [closed]
evaluation_mode: probabilistic_band
confidence_basis: qualitative_pattern_operationalized
source_fields: ["Is Completed in Sprint", "Completed Start Date", "A_Sprints.Sprint Completed Date"]
formula: >
  Share of completed tasks whose Completed Start Date falls within the
  last 2 days before this Sprint ID's own Sprint Completed Date --
  "end-loading": work rushed through right before the sprint boundary
  rather than integrated steadily. The 2-day window is carried over
  unchanged from the prior signal-design draft (second-level-signals-
  summary.md Sec.6) as the working definition of "late"; it is a
  definitional constant, not one of the deferred watch/concern bands.
  raw_count = count(completed tasks where
    (Sprint Completed Date - Completed Start Date) <= 2 days)
  sprint_size = count(tasks where Is Completed in Sprint == "Y")
```

---

## What this file does NOT define

- *Final, org-validated* watch/concern threshold values for the
  probabilistic indicators — see `org-config.md`'s
  `leading_indicator_thresholds` block, now populated with
  market-benchmark-informed starting points for 7 of 9 (2 remain `null` —
  see "Threshold status" above).
- Per-org indicator applicability — see
  `maturity-onboarding/references/leading-indicator-applicability.md`.
- Any wiring into `recommend_interventions()` / the catalog. Leading
  indicators only report in this version — see `guardrails.md` Rule 9.
- Cross-sprint correlation analysis (indicator in sprint N vs. KPI outcome
  in sprint N+1). `run_analysis.py::build_sprint_window_reports` sorts
  reports chronologically per team specifically so this analysis is
  possible later without reshuffling data, but does not compute it.
