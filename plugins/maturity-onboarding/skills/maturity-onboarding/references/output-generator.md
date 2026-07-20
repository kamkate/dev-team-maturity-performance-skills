# Output Generator
reference_for: maturity-onboarding Step 8
version: output-generator-v1

This file defines the exact format for each of the three output files.
Generate each file exactly as specified. Do not omit sections.
Show each file to the user as a code block they can copy.

---

## File 1 — org-config.md

Generate using this template, filled with collected values:

```markdown
# Org Config — [org_name]
config_version: org-config-v[N]
created_at: [YYYY-MM-DD]
created_by: [who ran onboarding]
org_name: [org_name]
last_updated: [YYYY-MM-DD]

---

## Organization context

industry: [industry]
team_model: [team_model]
sprint_length_weeks: [N]
jira_workflow: [standard / custom]
org_context_notes: |
  [free text captured in Step 1]

---

## Threshold calibrations

# [For each KPI: include value if changed from default, comment if using default]

roadmap_contribution_green: [value or blank if default]
roadmap_contribution_yellow: [value or blank if default]
sprint_completion_green: [value or blank if default]
sprint_completion_yellow: [value or blank if default]
cycle_time_green_days: [value or blank if default]
cycle_time_yellow_days: [value or blank if default]
parallel_epics_green: [value or blank if default]
parallel_epics_yellow: [value or blank if default]
epic_dev_time_green_weeks: [value or blank if default]
epic_dev_time_yellow_weeks: [value or blank if default]

---

## Active patterns

active_patterns:
[list of active pattern IDs, one per line with - prefix]

disabled_patterns:
[list of disabled pattern IDs with reason, or 'none']

---

## Token efficiency settings

max_teams_per_compare: [value]
default_trend_sprints: [value]
warn_above_tokens: 3000

---

## Data notes

known_data_issues:
[list of issues collected in Step 5, one per line with - prefix]

epic_dev_time_proxy_mode: [true / false]
roadmap_zero_warning: [true / false]

---

## File versions

org_kpi_definitions_version: org-kpi-definitions-v[N]
catalog_version: recommendation_catalog_v1
engine_version: engine-v1
```

---

## File 2 — org-kpi-definitions.md

Generate using this template. For KPIs using engine defaults,
copy the engine default definition verbatim and note it.
For customized KPIs, use the collected definition.

```markdown
# Org KPI Definitions — [org_name]
definition_version: org-kpi-definitions-v[N]
parent_engine_version: engine-v1
org_name: [org_name]
created_at: [YYYY-MM-DD]
created_by: [who ran onboarding]
last_updated: [YYYY-MM-DD]

Version history:
  v[N] ([date]): [what changed — "Initial setup" for v1]
  [v[N-1] ([date]): previous change if revision]

---

## General rules — inherited from engine

- Null handling: missing data → value = null, value_status = "missing"
- Minimum sample size: task count < 5 → add low sample size warning
- Sprint membership: filter A_Sprints first, then join to A_Task
- Spillover handling: use only the A_Sprints row for the analysed sprint

---

## KPI 1 — Roadmap Contribution

[customized or default definition]
[include: intent, source fields, operational rule, formula, thresholds, evidence to report, data quality notes]

---

## KPI 2 — Sprint Completion

[customized or default definition]

---

## KPI 3 — Cycle Time p50

[customized or default definition]

---

## KPI 4 — Parallel Epics

[customized or default definition]

---

## KPI 5 — Epic Development Time

[customized or default definition]
[always include mode: proxy or conceptual]
[if proxy: always include proxy_warning]

---

## Maturity scoring

Scoring formula: maturity_v1 (equal weights, unchanged from engine)
Score = round(sum(KPI levels) / 5 × 100)
Level mapping: GREEN=1, YELLOW=0.5, RED=0
Bands: 0–39 Low, 40–69 Developing, 70–100 High maturity
```

---

## File 3 — onboarding-report.md

```markdown
# Onboarding Report — [org_name]
report_version: [N]
generated_at: [YYYY-MM-DD]
generated_by: maturity-onboarding-v1
session_type: [new setup / revision]

---

## Configuration summary

Organization: [org_name]
Industry: [industry]
Sprint length: [N] weeks
Team model: [team_model]

Files produced:
- org-config.md (org-config-v[N])
- org-kpi-definitions.md (org-kpi-definitions-v[N])

---

## KPI customizations

[For each KPI, one of:]
- KPI [N] — [name]: Using engine default
- KPI [N] — [name]: CUSTOMIZED — [one line description of change]

---

## Threshold changes from engine defaults

[List each changed threshold:]
- [KPI name] GREEN: [engine default] → [org value] (reason: [captured reason])
[Or: "None — all engine defaults retained"]

---

## Active patterns

Active: [list]
Disabled: [list with reasons, or 'None disabled']

---

## Known data issues

[List from Step 5, or 'None documented']

---

## Validation results

Threshold logic: [PASS / WARNINGS: list]
Pattern dependencies: [PASS / WARNINGS: list]
Completeness: [PASS / MISSING: list]

---

## Testing note

⚠️ KPI definitions have not been verified against real data.
Recommended action: run a test analysis on one sprint immediately
after setup to verify KPI values look reasonable.

Suggested test: analyse [most recent complete sprint] for
[team with most tasks] and check:
- Roadmap contribution is not 0% unless expected
- Cycle time values are in a plausible range
- Epic count matches your expectation

---

## Change log

[For revisions — what changed from previous version:]
v[N] ([date]): [description of change]
[v[N-1] ([date]): previous change]

---

## Next steps

1. Save all three files
2. Upload to Claude Project alongside:
   - maturity-engine SKILL.md (installed as skill)
   - catalog.json
   - jira_db.json
3. Run test analysis: "Analyse [team] in [sprint]"
4. Verify KPI values look reasonable
5. If anything looks wrong, rerun onboarding and revise
```
