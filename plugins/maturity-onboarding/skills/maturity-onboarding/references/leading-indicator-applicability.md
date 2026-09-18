# Leading Indicator Applicability Guide
reference_for: maturity-onboarding Step 4b (runs immediately after Step 4 — threshold-guide.md)
version: leading-indicator-applicability-v1

This file defines the dialogue for confirming, per leading indicator,
whether it applies to this organization's workflow at all — distinct from
threshold-guide.md's Step 4, which calibrates *values* for KPI thresholds.
Same pattern as that step: show the indicator, ask if it applies, capture
a reason when it doesn't. Choice + reason are recorded into `org-config.md`
and are frozen and auditable from that point on, exactly like a KPI
threshold override.

Only the 9 **probabilistic** leading indicators go through this dialogue —
they are the only ones with entries in `leading_indicator_thresholds`. The
3 structural/deterministic indicators (`SOLO_TASK_RATIO`,
`INITIATIVE_LINK_RATIO_TASK_WEIGHTED`, `EPIC_SPRAWL`) reuse an existing
KPI's own thresholds and use fields (`Parent key`) that every org's Jira
export already has by definition — there is nothing to ask about.

**Ground each question in the Step 1 example**
([data-source-gate.md](data-source-gate.md)): where the example task has a
relevant field populated (or empty), point at it. E.g. for
`MISSING_SP_RATIO`, if the example task has no story points set, say so
before asking whether that's typical — a concrete "your example task [KEY]
has no story points" lands better than an abstract yes/no.

---

## How this differs from a threshold override

- **Threshold calibration** (Step 4): "this indicator applies here — what
  value counts as concerning?"
- **Applicability** (this step): "does this indicator apply here at all?"

An indicator can be inapplicable even with a perfectly good default
threshold — e.g. `MISSING_SP_RATIO`'s 20%/40% market-benchmark threshold
is fine in the abstract, but meaningless for an org that doesn't estimate
in story points at all. Marking it inapplicable stops the engine from
computing it and keeps it out of every report, rather than showing a
`not_evaluated` or a silently-meaningless value.

---

## The dialogue

**Show to user (once, before going indicator-by-indicator):**
> "Nine leading indicators use fields that not every Jira setup populates
> the same way — story points, bug typing, blocked-time tracking, and so
> on. For each one, I'll ask whether it fits how your teams actually work.
> If it doesn't, it's excluded from every report rather than shown with a
> meaningless or empty value."

**For each of the 9, ask:**

1. **MISSING_SP_RATIO** — uses `Story points`.
   > "Do your teams estimate tasks in story points before a sprint starts?
   > (yes / no — we don't use story points / no — we use a different unit)"

2. **CARRYOVER_RATE** — uses task IDs carried from the previous sprint.
   > "Do your teams run sequential sprints per team where 'this task was
   > also in last sprint' is a meaningful signal? (yes / no — e.g. kanban
   > flow with no discrete sprint boundaries)"

3. **MID_SPRINT_TASK_INJECTION** — uses `CreatedDate` vs. `Sprint Start Date`.
   > "Is scope typically locked at sprint start, so a task created after
   > that date is meaningfully 'added mid-sprint'? (yes / no — e.g.
   > continuous-flow teams where this framing doesn't apply)"

4. **BUG_INJECTION_RATE** — uses `Type = "Bug"` + `CreatedDate`.
   > "Do your teams use a distinct 'Bug' issue type in Jira? (yes / no —
   > e.g. bugs are just tasks with a label, or triaged in a separate system)"

5. **BUG_FEATURE_RATIO** — uses `Type = "Bug"`.
   > "Same question as above — same 'Bug' issue type dependency. (yes / no)"

6. **LONG_BLOCKED_COUNT** — uses `Stage Blocked days`.
   > "Does your Jira workflow have an explicit 'Blocked' status or stage
   > that gets tracked? (yes / no — e.g. blockers are only noted in comments)"

7. **REOPEN_PROXY_COUNT** — uses `Stage Done recurrence`.
   > "Can a task leave 'Done' and come back (reopened)? If your workflow
   > makes that structurally impossible or it's never actually used, this
   > proxy has nothing to measure. (yes it can happen / no)"

8. **STALLED_WIP_COUNT** — uses `Is Completed in Sprint` + `All Development Days`.
   > "Is `All Development Days` populated for in-progress work, not just
   > completed work? (yes / no — e.g. it's only backfilled on completion)"

9. **LATE_COMPLETION_SPIKE** — uses `Completed Start Date` vs. `Sprint Completed Date`.
   > "Do you track a per-task 'work started' timestamp distinct from when
   > it was marked done? (yes / no)"

**If yes:** mark `applicable: true` (or leave the field out — same effect).

**If no:** ask:
> "In a few words, why doesn't this apply? (e.g. 'Organization does not
> use story points for estimation.') This gets recorded in org-config.md
> so it's auditable later — it can't be left blank."

Capture the answer verbatim as `applicability_reason`. Do not paraphrase it
into something vaguer than what the user said — the reason is the audit
trail, not decoration.

---

## Recording the answer

Write into `org-config.md`'s `leading_indicator_thresholds` block, on the
same per-indicator entry as the watch/concern thresholds (see
`output-generator.md` File 1 template) — one lookup, not two:

```yaml
leading_indicator_thresholds:
  missing_sp_ratio:
    watch_threshold: 0.20
    concern_threshold: 0.40
    confidence_basis: market_benchmark_proxy
    applicable: false
    applicability_reason: "Organization does not use story points for estimation (confirmed at onboarding, [YYYY-MM-DD])."
```

If every indicator applies (the common case), omit `applicable` and
`applicability_reason` entirely rather than writing `applicable: true` on
every entry — the engine already defaults a missing field to applicable
(see `leading_indicators.py::filter_applicable_indicators`), and a config
free of unnecessary boilerplate is easier to audit.

**Validation:** `applicable: false` with a missing or empty
`applicability_reason` fails config loading with a clear error (see
`leading_indicators.py::validate_leading_indicator_thresholds`) — if this
happens while assembling the final file, go back and ask for the reason
rather than writing a placeholder.

Reflect every exclusion in the onboarding report (`onboarding-report.md`,
`output-generator.md` File 3) under a new "Leading indicator applicability"
section, the same way threshold changes are listed under "Threshold
changes from engine defaults" — so a later reviewer can see what was
excluded and why without re-deriving it from `org-config.md` alone.
