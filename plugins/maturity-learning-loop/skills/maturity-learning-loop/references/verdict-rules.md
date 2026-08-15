# Verdict Rules

Version: verdict-rules-v1

This file defines what "effective", "partial", and "ineffective" mean
for each intervention type. The engine applies these rules mechanically.

---

## Verdict definitions

**Effective**
All primary KPIs for this intervention moved in the expected direction.
Movement required: ≥ 5% relative change (or ≥ 0.5 for count KPIs).
Smaller movements are noise, not signal.

**Partial**
Some primary KPIs moved in the expected direction; at least one did not.
The engine flags the non-moving KPI and checks for a follow-on pattern.

**Ineffective**
Primary KPIs did not move, or moved in the wrong direction.
This is not a failure to report — it is a signal to learn from.
The engine notes the outcome and may suggest a different intervention.

**Awaiting**
The lookback sprint has not yet closed. No verdict possible.

---

## Primary KPIs per intervention type

Each intervention has 1–3 primary KPIs — the ones it is designed to move.
Secondary KPIs may also shift; they are noted but do not affect the verdict.

### FOCUS_SPRINT
Target pattern: WIP_DEATH_SPIRAL, HIGH_EPIC_WIP
Primary KPIs: sprint_completion (+), parallel_epics (−)
Secondary: cycle_time_p50 (may improve as side effect)
Minimum movement: completion +5pp, parallel_epics −1

### EPIC_SCOPING_WORKSHOP
Target pattern: LONG_EPIC_DEVELOPMENT_TIME, HIGH_EPIC_WIP
Primary KPIs: epic_dev_time_weeks (−), parallel_epics (−)
Secondary: sprint_completion (may improve as side effect)
Minimum movement: epic_dev_time −0.5 weeks, parallel_epics −1

### CYCLE_TIME_RETROSPECTIVE
Target pattern: LONG_CYCLE_TIME
Primary KPIs: cycle_time_p50 (−)
Secondary: sprint_completion (may improve)
Minimum movement: cycle_time −0.5 days

### ROADMAP_SYNC_CADENCE
Target pattern: ROADMAP_DRIFT, LOW_ROADMAP_CONTRIBUTION
Primary KPIs: roadmap_contribution (+)
Secondary: sprint_completion (may improve if scope was unfocused)
Minimum movement: roadmap_contribution +5pp

### SPRINT_COMMITMENT_CALIBRATION
Target pattern: LOW_SPRINT_COMPLETION
Primary KPIs: sprint_completion (+)
Secondary: parallel_epics (may decrease as team reduces scope)
Minimum movement: completion +5pp

### WIP_LIMIT_EXPERIMENT
Target pattern: HIGH_EPIC_WIP, WIP_DEATH_SPIRAL
Primary KPIs: parallel_epics (−), cycle_time_p50 (−)
Secondary: sprint_completion (may improve)
Minimum movement: parallel_epics −1, cycle_time −0.5 days

---

## Follow-on logic

When verdict is "partial", check which primary KPI did not move.

If the non-moving KPI still scores RED or YELLOW:
1. Identify the pattern that targets that KPI
2. Check catalog for interventions matching that pattern
3. Surface the top-ranked one as a follow-on recommendation

Example: ROADMAP_SYNC_CADENCE → roadmap improved (+26pp) but
sprint_completion unchanged (61% → 63%). Sprint completion still YELLOW.
Pattern LOW_SPRINT_COMPLETION is active. Suggest SPRINT_COMMITMENT_CALIBRATION.

---

## Edge cases

**KPI was already at GREEN at baseline**
If a primary KPI was already GREEN before the intervention, exclude it
from the verdict calculation. Partial verdict cannot be assigned for a
KPI that wasn't a problem to begin with.

**Data missing for lookback sprint**
If jira_db does not contain the lookback sprint, verdict = "awaiting".
Do not estimate or extrapolate.

**Team size changed between baseline and lookback**
Note the change. Compute KPIs using lookback team composition.
Flag that comparison may be affected.

**Multiple interventions for same team in overlapping sprints**
Do not attribute KPI movements to a single intervention when two
interventions were running concurrently. Verdict = "partial (concurrent
intervention — attribution unclear)". Note both log_ids.
