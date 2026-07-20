# Pattern Rules
definition_version: pattern-rules-v1
depends_on: kpi_v2_aligned

This file defines how KPI levels map to diagnostic patterns.
Patterns are the bridge between measured KPI values and catalog interventions.
All pattern detection is deterministic — same KPI levels always produce
same patterns. No LLM judgment in pattern detection.

---

## How pattern detection works

1. Compute all 5 KPI values
2. Apply thresholds (from org-config or engine defaults) → get level for each KPI
3. Apply rules below → get triggered patterns
4. Combine atomic patterns → check for compound patterns
5. Pass triggered pattern IDs to catalog lookup

A pattern is either triggered (true) or not triggered (false).
There is no partial triggering or confidence score in v1.

---

## Atomic patterns — triggered by single KPI

**LOW_SPRINT_COMPLETION**
Trigger: sprint_completion level = 0 (RED)
Type: Predictability
Business impact: Stakeholders cannot rely on sprint commitments.
  Teams consistently miss sprint goals, making planning unreliable
  and eroding confidence in delivery estimates.

**HIGH_EPIC_WIP**
Trigger: parallel_epics level = 0 (RED)
Type: Flow
Business impact: Excessive parallelisation slows throughput.
  Too many epics active simultaneously creates context switching,
  increases coordination overhead, and extends delivery timelines.

**LONG_CYCLE_TIME**
Trigger: cycle_time_p50 level = 0 (RED)
Type: Flow
Business impact: Slow task throughput — feedback loops are long.
  Tasks take too long to move through development, reducing
  the team's ability to respond to change and slowing learning.

**LONG_EPIC_DEVELOPMENT_TIME**
Trigger: epic_dev_time level = 0 (RED)
Type: Delivery
Business impact: Epics take too long to close — high delivery risk.
  Long-running epics increase the probability of scope drift,
  stakeholder misalignment, and delayed business value realisation.

**LOW_ROADMAP_CONTRIBUTION**
Trigger: roadmap_contribution level = 0 (RED)
Type: Strategic
Business impact: Team capacity not aligned with strategic priorities.
  Sprint work is not connected to roadmap objectives, meaning
  the team may be delivering output without strategic impact.
  Note: always check data quality before interpreting this pattern —
  0% roadmap contribution may reflect missing Jira linkage, not
  actual misalignment.

---

## Compound patterns — triggered by combination of atomic patterns

Compound patterns are checked AFTER atomic patterns.
They represent systemic problems more serious than individual KPI failures.

**WIP_DEATH_SPIRAL**
Trigger: HIGH_EPIC_WIP AND LONG_CYCLE_TIME both triggered
Type: Systemic
Business impact: WIP overload is creating queues that slow the entire system.
  High epic WIP increases cycle time, which prevents completion,
  which creates pressure to start new work, which increases WIP further.
  This is a self-reinforcing negative loop requiring systemic intervention,
  not a single fix.
Urgency: HIGH — escalate to leadership attention

**ROADMAP_DRIFT**
Trigger: LOW_ROADMAP_CONTRIBUTION AND LOW_SPRINT_COMPLETION both triggered
Type: Strategic/Systemic
Business impact: Low strategic alignment combined with low execution.
  The team is neither working on the right things nor completing
  what it commits to. This combination requires management attention
  at both the prioritisation and execution level.
Urgency: HIGH — escalate to leadership attention

---

## Pattern output format

For each triggered pattern report:
- pattern_id (e.g. HIGH_EPIC_WIP)
- triggered: true
- type (Predictability / Flow / Delivery / Strategic / Systemic / Strategic/Systemic)
- business_impact (from definitions above)
- urgency (HIGH only for compound patterns)
- triggered_by (which KPI and its value)

For compound patterns also report:
- component_patterns (list of atomic pattern IDs that triggered it)

---

## Patterns that are NOT triggered

Do not list untriggered patterns in output.
Only triggered patterns appear in the Signals section.
This keeps output focused and avoids overwhelming the CTO
with a long list of things that are fine.

---

## YELLOW signal — advisory note (not a pattern)

If a KPI is YELLOW (level = 0.5), it does not trigger a pattern.
However, if two or more KPIs are YELLOW, add an advisory note:

> "Advisory: [list of YELLOW KPIs] are in the warning zone.
> No pattern triggered yet, but monitor in the next sprint."

This is not a formal pattern — it is a forward-looking signal.

---

## Org-config overrides

If org-config.md specifies which patterns are active for this organisation,
only detect and report those patterns.
If org-config is silent on patterns, detect all patterns defined above.

Example org-config entry that would limit patterns:
```
active_patterns:
  - HIGH_EPIC_WIP
  - LOW_SPRINT_COMPLETION
  - WIP_DEATH_SPIRAL
```
In this case, LONG_CYCLE_TIME, LONG_EPIC_DEVELOPMENT_TIME,
LOW_ROADMAP_CONTRIBUTION, and ROADMAP_DRIFT would not be detected.
