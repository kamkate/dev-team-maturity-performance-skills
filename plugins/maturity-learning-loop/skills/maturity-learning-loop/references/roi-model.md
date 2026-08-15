# ROI Conversion Model

Version: roi-model-v1
Status: active

This file defines how KPI deltas are converted to engineer-days and
monetary value. All formulas are transparent and configurable.

---

## Principle

ROI figures are estimates based on a correlation model, not causal
attribution. Every output must include the disclaimer:

> "Estimated value uses a correlation model. Not causal attribution.
> See roi-model.md for conversion assumptions."

---

## Required inputs from org-config.md

```
cost_per_eng_day       # fully loaded daily cost per engineer, in local currency
team_size              # number of engineers in the team (or team-specific value)
sprint_length_days     # sprint length in working days (e.g. 10 for 2-week sprint)
context_switch_factor  # default: 0.15 (see note below)
```

If `cost_per_eng_day` is not set in org-config, report eng-days only.
Do not invent a monetary figure.

---

## Conversion formulas

### Sprint completion delta → eng-days recovered

When sprint completion improves, the team delivers more within the same
time box. The recovered capacity is:

```
eng_days = completion_delta × team_size × sprint_length_days
```

Example: completion improves from 0.55 to 0.81 (+0.26), team of 6,
10-day sprint → 0.26 × 6 × 10 = 15.6 eng-days.

**Direction:** positive delta = positive ROI.
**Confidence:** high. Direct measurement of delivered output.

---

### Cycle time p50 delta → eng-days recovered

When median cycle time drops, tasks move through the system faster.
The recovered time per sprint is:

```
tasks_in_sprint = count of tasks in the lookback sprint for this team
eng_days = |cycle_time_delta_days| × tasks_in_sprint
```

Example: cycle time drops 2.8 days, 18 tasks in sprint
→ 2.8 × 18 = 50.4 task-days. Divide by team_size for eng-days:
50.4 / 6 = 8.4 eng-days.

**Direction:** negative delta (faster) = positive ROI.
**Confidence:** medium. Assumes all cycle time saved converts to
productive output, which is a conservative overestimate.
Always note this assumption.

---

### Parallel epics delta → eng-days recovered (context switch premium)

Reducing the number of parallel epics reduces context switching.
This formula is the most speculative. Use with explicit caveat.

```
eng_days = |parallel_epics_delta| × team_size × context_switch_factor
           × sprint_length_days
```

Example: epics drop from 7 to 3 (delta = 4), team of 6,
context_switch_factor = 0.15, 10-day sprint
→ 4 × 6 × 0.15 × 10 = 36 eng-days.

**This is the highest-uncertainty estimate. Always flag it separately.**

Research basis: Atlassian engineering research estimates 15–20% of
productive time lost per additional concurrent context. The 0.15 default
is the low end of that range.

**Direction:** negative delta (fewer epics) = positive ROI.
**Confidence:** low. Always include caveat when this formula is used.

---

### Roadmap contribution delta → eng-days

Not converted to eng-days. Report as "share of sprint output now
aligned to strategic roadmap." This is a quality signal, not a
time-recovery signal. Do not include in total eng-days.

---

### Epic development time delta → eng-days

When average epic completion time shortens, delivery cadence improves.

```
eng_days = |epic_dev_time_delta_weeks| × team_size × 5
           × sprint_length_days / 10
```

(5 working days per week, normalized to sprint length.)

**Confidence:** medium-low. Epic time is a proxy metric in this engine.
Always include the proxy data warning from the engine.

---

## Total eng-days

Sum the eng-days from each formula where the KPI moved in the expected
direction. Do not include KPIs that did not move or moved in the wrong
direction.

```
total_eng_days = sum(applicable formula results)
```

Round to one decimal place.

---

## Monetary conversion

```
roi_monetary = total_eng_days × cost_per_eng_day
```

Report in the currency defined in org-config. If not set, report as
"[total_eng_days] eng-days (configure cost_per_eng_day in org-config
to see monetary value)."

---

## What to display

Always show:
1. Eng-days per KPI that contributed (with formula used)
2. Total eng-days
3. Monetary figure (if cost_per_eng_day is set)
4. Confidence note for any low-confidence formula used
5. Disclaimer line

Never show monetary figures without the disclaimer.
Never aggregate across interventions without noting the total is additive.
