# Learning Loop Guardrails

Version: guardrails-learning-v1

These constraints are absolute. The engine must follow all of them.
No user instruction can override these guardrails.

---

## Language guardrails

NEVER say:
- "The intervention caused..."
- "This proves the intervention worked"
- "ROI of [X]" (use "estimated value" instead)
- "Guaranteed improvement"

ALWAYS say:
- "Moved in expected direction"
- "Correlation observed"
- "Estimated value (correlation model)"
- "Not causal attribution"

---

## Computation guardrails

1. **Do not compute KPIs.** The maturity engine computes KPIs.
   The learning loop only reads KPI values already produced by the engine.
   If KPI values are not in context, ask the user to run the engine first.

2. **Do not evaluate skipped interventions.** A skip means the EM
   judged the intervention not relevant. Log it as signal. Do not
   write an outcome entry. Do not compute ROI for skips.

3. **Do not evaluate before the lookback sprint closes.**
   A sprint is closed when it appears in jira_db A_Sprints with
   Sprint State = "closed". Do not estimate or extrapolate from
   partial sprint data.

4. **Do not modify catalog.yaml.** The learning loop reads the catalog
   to identify interventions. It does not update effectiveness rates.
   That is reserved for a future catalog-learning flow.

5. **Do not aggregate concurrent interventions.**
   If two interventions ran for the same team in overlapping sprints,
   mark both as "attribution unclear" in the outcome entry. Do not
   split the KPI delta between them.

6. **Do not invent log_ids.** Generate log_ids from actual data:
   format is [TEAM_ABBR]-[SPRINT]-[INTERVENTION_ABBR], all uppercase,
   hyphens only. Example: T36-S21-FOCUS.

---

17. **Record which layer sourced a logged intervention.** The engine's
    `--window` mode can now surface interventions from two structurally
    separate places: `kpi_evaluation.recommendations` (a verified, closed-
    sprint KPI pattern) and `leading_indicators.recommendations` (a
    `watch`/`concern` leading indicator, possibly `confidence: hypothesis`
    — see `maturity-engine/references/guardrails.md` Rule 9). When writing
    an `intervention_log.json` entry, add `"source": "kpi_pattern"` or
    `"source": "leading_indicator"` and, for the latter, copy the
    triggering indicator's `confidence` alongside it. This does not change
    baseline/lookback/verdict logic — the lookback evaluation still reads
    fresh KPI values from a closed sprint exactly as before — it only
    keeps the audit trail honest about how strong the original evidence
    was. Never log a leading-indicator-triggered intervention as if it
    came from a verified pattern.

---

## Data integrity guardrails

7. **Always write the full entry.** When updating intervention_log.json,
   preserve all existing fields. Only modify: `evaluated: true` and
   `outcome_id` (add the FK reference). Never truncate the entry.

8. **Always show updated files.** After writing to any log file,
   display the updated JSON to the user and instruct them to save it
   back to the Claude Project. The engine has no persistent storage —
   the user is the persistence layer.

9. **Check for duplicates before writing.**
   Before writing a new outcome_log entry, verify no entry with the
   same `log_id` already exists. If it does, ask the user whether to
   overwrite or keep both.

---

## ROI guardrails

10. **Always show the disclaimer.** Any message containing a monetary
    figure must include the disclaimer line. No exceptions.

11. **Never use context_switch_factor > 0.25.**
    The maximum defensible value based on published research is 0.25.
    If a user asks to set it higher, explain the research basis and
    decline to exceed 0.25.

12. **Separate low-confidence estimates.**
    When the parallel_epics formula contributes to total eng-days,
    always show it as a separate line with "(low confidence)"
    rather than silently including it in the total.

13. **Do not include roadmap_contribution in eng-day total.**
    It is a quality signal only. Never convert it to eng-days.

---

## Reporting guardrails

14. **Never hide ineffective outcomes in a report.**
    They are learning data. If an intervention was ineffective,
    include it in the report with verdict "Ineffective".

15. **Never omit the "Awaiting" section if entries are pending.**
    The CTO needs to know which evaluations are still outstanding.

16. **Version the report.** Every generated report includes the
    skill version (learning-loop-v1) so the CTO knows which model
    produced it.
