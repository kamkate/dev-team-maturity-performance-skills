# Next-Step Routing Table
definition_version: next-step-routing-v1

Every report's `👉 Next Step` section (see `output-template.md` §3, §4
standalone, §5, §6, and `morning-brief-template.md`) shows **exactly one
question — the single most important follow-up for this moment**, not a
menu of options. This file is the single source of truth for which
questions are allowed, and when — a lookup of *what's allowed to be asked
given what actually triggered*, not a script to recite in full.

---

## Routing principle

Before writing a Next Step section:

1. Identify every `pattern_id` / leading-indicator `risk_id` / KPI `level` /
   trend direction that **actually triggered in this specific report**.
2. Match against the table below (§2).
3. Pick the single highest-priority match. Priority order:
   **compound pattern > atomic pattern > leading-indicator `concern` >
   leading-indicator `watch` > trend direction.** If two rows tie on
   priority, prefer whichever points at the more specific, more actionable
   next move for this report over a broader "see more context" question.
4. If nothing matched, use the fallback tier (§3), in order, taking the
   first one that applies.

**Never present a question whose trigger condition did not actually occur
in this report.** Never invent a question. Never show more than one — the
fallback tier exists precisely so a report never has zero grounded options
to fall back to.

---

## §2 — Routing table

| From (report) | Trigger condition | Question | Routes to |
|---|---|---|---|
| Morning Brief | a team has score < 40 or a compound pattern | "Team [X] is 🔴 [score]/100 with [pattern] — run a Full Sprint Analysis on it?" | Mode 3 (§3 Full Sprint Analysis) |
| Morning Brief | 2+ teams share the same triggered pattern | "[N] teams share [pattern] this brief — want the Team Comparison view to see the full spread?" | Mode 1 (§6 Team Comparison) |
| Full Sprint Analysis | `WIP_DEATH_SPIRAL` or `ROADMAP_DRIFT` triggered | "Want the trend over the last 3 sprints to check if [driving KPI] has been climbing, or if this sprint is an outlier?" | Mode 4 (§5 Trend Analysis) |
| Full Sprint Analysis | any compound pattern triggered | "Want to see if other teams show the same pattern this sprint — Team Comparison?" | Mode 1 (§6 Team Comparison) |
| Full Sprint Analysis | `LOW_ROADMAP_CONTRIBUTION` triggered | "0% roadmap contribution can also mean missing Jira linkage rather than real drift — want to check which epics lack an initiative link before treating this as fact?" | Task-level drill-down (§4 of this doc) |
| Full Sprint Analysis / §4 Leading Indicators | `BUG_INJECTION_RATE` or `MID_SPRINT_TASK_INJECTION` at `watch`/`concern` | "[N] bug tasks were injected mid-sprint — want to see which tasks, and when they were created?" | Task-level drill-down |
| Full Sprint Analysis / §4 Leading Indicators | a catalog recommendation was shown (e.g. `INT-013` triggered by a leading-indicator risk) | "Want to record a decision (accept/defer/skip) on [INT-XXX] for the learning loop?" | `maturity-learning-loop` skill |
| Task-level drill-down | a task list was returned | "Want to search Slack for context on why these tasks were created?" | `jira-slack-context` skill (§5 of this doc) |
| Task-level drill-down | a task list was returned | "Or go back to the full sprint picture for this team?" | Mode 3 (§3 Full Sprint Analysis) |
| Trend Analysis | direction is `📉 declining` and the same pattern recurs across 2+ sprints in the window | "This decline is recurring, not a one-off — want Team Comparison to check if it's isolated to this team or wider?" | Mode 1 (§6 Team Comparison) |
| Trend Analysis | direction is `📉 declining` | "Want the most recent sprint's Full Sprint Analysis for the specific numbers behind this trend?" | Mode 3 (§3 Full Sprint Analysis) |
| Team Comparison | 2+ teams share the same "Top Pattern" | "[N] teams share [pattern] — could be a systemic/org-level issue rather than one team's problem. Want to look at the lowest-scoring one first?" | Mode 3 (§3 Full Sprint Analysis) |
| Team Comparison | any team scores < 40 | "Want the Trend view for [lowest team] to see if this is new or ongoing?" | Mode 4 (§5 Trend Analysis) |
| §4 Leading Indicators (Mode 5 — last open sprint) | structural indicator (`INITIATIVE_LINK_RATIO_TASK_WEIGHTED`, `EPIC_SPRAWL`) flags risk | "This sprint's Roadmap Contribution is already structurally close to [X]% based on the epics committed — want to see which epics lack an initiative link, while there's still time to replan?" | Task-level drill-down |
| §4 Leading Indicators (Mode 5) | any probabilistic indicator at `concern` | "Want to see the full leading-indicator breakdown, including indicators with no signal, for full context?" | §4 full breakdown (existing capability) |
| Any report | recommendations were shown and no decision has been recorded yet this session | "Want to record a decision on any of these for the learning loop?" | `maturity-learning-loop` skill |

---

## §3 — Fallback tier

Used only when nothing in §2 matched (e.g. a clean, all-GREEN Full Sprint
Analysis). Take the first one that applies, in order:

1. "Want the Trend view to confirm this is a stable pattern, not a one-sprint snapshot?" → Mode 4 (§5 Trend Analysis)
2. "Want to see how this team compares to others this sprint?" → Mode 1 (§6 Team Comparison)
3. "Want the Morning Brief for a quick scan across all teams?" → Morning Brief

Never invent a question that has no basis in the current report — the
fallback tier is still grounded (it always names the report just
produced), it's just less specific than a triggered-pattern match.

---

## §4 — Task-level drill-down

A read-only lookup of the individual tasks (or, for
`LOW_ROADMAP_CONTRIBUTION`, epics) behind an aggregate signal — "show me
the receipts." Exposed via `maturity-core/run_analysis.py --drill-down
TEAM SPRINT_ID INDICATOR_ID`. Never touches KPI computation, pattern
detection, or scoring (see `guardrails.md` Rule 11). The result is a short
list presented inline in the response — not a new report type, not run
through `output-template.md`'s §3/§5/§6 structures.

Supported `INDICATOR_ID` values and what they return:

| Indicator | Returns |
|---|---|
| `BUG_INJECTION_RATE` | Tasks where `Type == "Bug"` and `CreatedDate` is after the sprint's own start date — `ID`, `Type`, `CreatedDate` |
| `MID_SPRINT_TASK_INJECTION` | Tasks where `CreatedDate` is after the sprint's own start date — `ID`, `Type`, `CreatedDate` |
| `LOW_ROADMAP_CONTRIBUTION` | Epics in the working set with no `Initiative key`, with their task counts — `epic_id`, `task_count` |

Filter logic mirrors the corresponding indicator's `formula` in
`leading-indicator-rules.md` exactly, scoped to the same team × `Sprint ID`
working set as the rest of the engine (never `Sprint Index Name` — see
`CLAUDE.md`'s A_Sprints field docs).

---

## §5 — Handoff to `jira-slack-context`

After a task-level drill-down returns task IDs, the first drill-down Next
Step question (§2 above) offers a Slack-context search. If accepted, hand
off to the `jira-slack-context` skill using the task key(s) the drill-down
just returned, passed as-is. **Omit the optional "creator name" parameter**
— the offline Jira export used by this engine does not carry a
creator/reporter field (see `guardrails.md` Rule 11 and
`docs/data-model.md`), and `jira-slack-context`'s own instructions already
treat creator name as "helpful," not required, and say to proceed without
blocking on it.
