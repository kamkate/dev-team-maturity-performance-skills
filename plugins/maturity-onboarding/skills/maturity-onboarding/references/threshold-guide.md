# Threshold Calibration Guide
reference_for: maturity-onboarding Step 3
version: threshold-guide-v1

This file guides the threshold calibration dialogue for each KPI.
Show the engine default, explain what it means, ask if it fits.

---

## How thresholds work

Each KPI has three zones: GREEN (good), YELLOW (warning), RED (critical).
Thresholds define the boundaries between zones.

For KPIs where higher is better (Roadmap Contribution, Sprint Completion):
- GREEN means value is above the green threshold
- YELLOW means value is between yellow and green thresholds
- RED means value is below the yellow threshold

For KPIs where lower is better (Cycle Time, Parallel Epics, Epic Dev Time):
- GREEN means value is below the green threshold
- YELLOW means value is between green and yellow thresholds
- RED means value is above the yellow threshold

---

## KPI 1 — Roadmap Contribution thresholds

**Engine defaults:**
- GREEN: > 50% (majority of sprint work is roadmap-linked)
- YELLOW: 35–50% (minority but meaningful share is roadmap-linked)
- RED: < 35% (most sprint work is not connected to strategic priorities)

**Explain to user:**
> "The 50% GREEN threshold means: if more than half your sprint tasks
> are connected to roadmap initiatives, the team gets a GREEN signal.
>
> This may be too high or too low depending on your organization.
> For example: if teams are expected to spend 40% on roadmap and 60%
> on operations/maintenance, you might set GREEN at 40% instead of 50%."

**Ask:**
> "Do these thresholds fit your organization, or would you like to adjust?
> (keep defaults / I want to change them)"

**If change:** ask for GREEN threshold, then derive YELLOW as halfway between
GREEN and 0 (or ask explicitly).

---

## KPI 2 — Sprint Completion thresholds

**Engine defaults:**
- GREEN: > 80%
- YELLOW: 50–80%
- RED: < 50%

**Explain to user:**
> "80% GREEN means: if the team completes more than 80% of their sprint
> commitment, that's a healthy signal. The Scrum Guide considers this
> a reasonable target for mature teams.
>
> For teams with unstable backlogs or frequent interruptions, 70% GREEN
> might be more realistic. For high-discipline teams, you might set 85%."

**Ask:**
> "Do the sprint completion thresholds fit your context?
> (keep defaults / I want to change them)"

---

## KPI 3 — Cycle Time p50 thresholds

**Engine defaults:**
- GREEN: ≤ 6 days
- YELLOW: 7–9 days
- RED: > 9 days

**Explain to user:**
> "These thresholds are based on 2-week sprints. A median cycle time
> of 6 days or less means most tasks complete in less than a week —
> healthy for a 2-week sprint.
>
> For 1-week sprints: consider GREEN ≤ 3 days.
> For 3-week sprints: GREEN ≤ 9 days may be appropriate.
> For teams doing large complex features: higher thresholds may apply."

**Ask:**
> "Given your sprint length of [X] weeks, do these cycle time thresholds
> make sense? (keep defaults / I want to change them)"

---

## KPI 4 — Parallel Epics thresholds

**Engine defaults:**
- GREEN: ≤ 3 epics
- YELLOW: 4–5 epics
- RED: ≥ 6 epics

**Explain to user:**
> "3 epics GREEN means: a team focused on 3 or fewer epics simultaneously
> has healthy focus. This is based on cognitive load research — beyond
> 3 parallel streams, context switching significantly reduces throughput.
>
> For larger teams (10+ people), 4 or 5 epics GREEN may be appropriate.
> For small teams (3–5 people), even 3 may be too many."

**Ask:**
> "How large are the teams in this organization (roughly)?
> Based on your answer, do the parallel epics thresholds make sense?
> (keep defaults / I want to change them)"

---

## KPI 5 — Epic Development Time thresholds

**Engine defaults:**
- GREEN: ≤ 5 weeks
- YELLOW: 6–8 weeks
- RED: > 8 weeks

**Explain to user:**
> "5 weeks GREEN means: epics that complete in 5 weeks or less are
> delivering value at a healthy pace. This roughly aligns with 2–3
> sprint cycles.
>
> For large platform epics or complex integrations, longer timelines
> may be unavoidable. For product feature teams, shorter is better.
> The proxy mode (averaging task dev days) may produce lower values
> than conceptual duration — calibrate accordingly."

**Ask:**
> "Given the type of work your teams do, do these epic development
> time thresholds make sense? (keep defaults / I want to change them)"

---

## Threshold validation rules

After collecting all thresholds, validate:

For higher-is-better KPIs (roadmap contribution, sprint completion):
- green_threshold must be > yellow_threshold
- yellow_threshold must be > 0
- green_threshold must be ≤ 1.0 (it is a ratio)

For lower-is-better KPIs (cycle time, parallel epics, epic dev time):
- green_threshold must be < yellow_threshold
- both must be > 0

If any validation fails:
> "⚠️ Threshold conflict detected: [describe issue].
> For [KPI], GREEN should be [direction] than YELLOW.
> Please correct: what should GREEN be? What should YELLOW be?"

---

## Next: leading indicator applicability

Once the 5 KPI thresholds are settled, continue immediately to
[leading-indicator-applicability.md](leading-indicator-applicability.md) —
a related but distinct question (does each of the 9 probabilistic leading
indicators even apply to this org's workflow, not what its threshold
value should be) that writes into the same `org-config.md`
`leading_indicator_thresholds` block.
