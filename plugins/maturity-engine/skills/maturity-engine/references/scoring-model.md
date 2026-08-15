# Maturity Scoring Model
definition_version: maturity_v1
depends_on: kpi_v2_aligned, pattern-rules-v1

> ⚠️ **DEPRECATED — not read by the engine or SKILL.md.** As of engine-v2,
> the single source of truth for the scoring formula and bands is
> `maturity-core/engine_defaults.json` (`scoring` block, version `maturity_v1`).
> This file is kept for historical and thesis reference only. Do not edit
> this file expecting it to change engine behavior — edit
> `engine_defaults.json` instead.

This file previously defined how 5 KPI levels aggregate into one maturity
score, retained below for narrative/thesis context. The formula is fixed
and cannot be changed during a conversation; changes to weighting or
aggregation require a new definition_version in engine_defaults.json.

---

## Input

Five KPI levels, each ∈ {0, 0.5, 1, null}

L1 = roadmap_contribution.level
L2 = sprint_completion.level
L3 = cycle_time_p50.level
L4 = parallel_epics.level
L5 = epic_dev_time.level

---

## Aggregation rule

Equal weighting — no KPI is more important than another in v1.
This is intentional: it prevents gaming and supports transparency.

Maturity_Index_Raw = sum(non-null levels) / 5

Note: denominator is always 5, even if some KPIs are null.
A null KPI contributes 0 to the numerator and reduces the score.
This penalises missing data, which is appropriate — missing data
is itself an information quality problem.

Maturity_Score = round(Maturity_Index_Raw × 100)
Range: 0–100

---

## Score bands

| Score | Band | Interpretation |
|-------|------|----------------|
| 0–39 | Low maturity | Reactive and ad-hoc delivery management |
| 40–69 | Developing maturity | Managed but unstable process |
| 70–100 | High maturity | Predictable and consistent delivery |

---

## Dimension breakdown (optional, load on request)

For deeper explainability, KPIs map to four dimensions:

**Flow Efficiency**
- cycle_time_p50
- epic_dev_time

**Delivery Reliability**
- sprint_completion

**Strategic Alignment**
- roadmap_contribution

**Focus**
- parallel_epics

When a CTO asks "why is the score low" or "what is driving this",
use dimension breakdown to explain contribution per area.

---

## Determinism requirements

- Same KPI input → same score always
- No hidden weights
- No smoothing across sprints
- No ML adjustments
- No implicit penalties outside the formula above

---

## Score output format

Report:
- maturity_score (integer 0–100)
- maturity_band (Low / Developing / High maturity)
- one_sentence_verdict (plain language summary for CTO)
- kpi_levels (table showing each KPI value, level, status)
- score_formula_note: "Equal weighting of 5 KPIs. maturity_v1."

**One-sentence verdict examples by band:**

Low maturity (0–39):
"The team's delivery process is reactive — multiple critical signals
require immediate management attention."

Developing maturity (40–69):
"The team shows some delivery capability but has significant gaps
that are limiting predictability and strategic alignment."

High maturity (70–100):
"The team demonstrates consistent, predictable delivery with strong
alignment to strategic priorities."

Adapt the verdict to the specific pattern context — mention the
dominant pattern if one compound pattern is triggered.

---

## Versioning policy

If any of the following change, increment definition_version:
- KPI set (add or remove a KPI)
- Weighting (move from equal to weighted)
- Thresholds (change RED/YELLOW/GREEN boundaries)
- Score formula (change aggregation method)

Do not overwrite historical scores computed with previous versions.
Historical scores are valid under the version that produced them.
