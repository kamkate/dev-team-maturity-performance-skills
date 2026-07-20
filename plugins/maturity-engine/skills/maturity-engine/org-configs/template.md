# Org Config Template
# Copy this file, rename to [org-name].md, fill in all sections.
# This file is loaded by the maturity engine at session start.
# Values defined here override engine defaults.
# Sections left blank fall back to engine defaults.

config_version: org-config-v1
created_at: [YYYY-MM-DD]
created_by: [consultant name]
org_name: [organization name — anonymized if needed]
last_updated: [YYYY-MM-DD]

---

## Organization context

# Describe the organization so Claude can give contextually appropriate responses.
# This section is used for language and framing only — not for computation.

industry: [e.g. internal product development / fintech / e-commerce]
team_model: [e.g. cross-functional squads / feature teams / platform teams]
sprint_length_weeks: [1 / 2 / 3 / 4]
jira_workflow: [standard / custom]
org_context_notes: |
  [Free text — anything Claude should know about this organization's
  delivery model, known constraints, or context that affects interpretation.
  Example: "Teams are shared between product and maintenance work.
  Roadmap contribution below 40% is expected and acceptable here."]

---

## Threshold calibrations

# Override engine defaults where this organization's context differs.
# Leave blank to use engine defaults.
# All values must match the unit defined in kpi-definitions.md.

# Roadmap Contribution (ratio thresholds — higher is better)
# Engine defaults: green > 0.50, yellow 0.35–0.50, red < 0.35
roadmap_contribution_green: # e.g. 0.45
roadmap_contribution_yellow: # e.g. 0.30

# Sprint Completion (ratio thresholds — higher is better)
# Engine defaults: green > 0.80, yellow 0.50–0.80, red < 0.50
sprint_completion_green: # e.g. 0.75
sprint_completion_yellow: # e.g. 0.45

# Cycle Time p50 (day thresholds — lower is better)
# Engine defaults: green ≤ 6, yellow 7–9, red > 9
cycle_time_green_days: # e.g. 5
cycle_time_yellow_days: # e.g. 8

# Parallel Epics (count thresholds — lower is better)
# Engine defaults: green ≤ 3, yellow 4–5, red ≥ 6
parallel_epics_green: # e.g. 4
parallel_epics_yellow: # e.g. 6

# Epic Dev Time (week thresholds — lower is better)
# Engine defaults: green ≤ 5, yellow 6–8, red > 8
epic_dev_time_green_weeks: # e.g. 4
epic_dev_time_yellow_weeks: # e.g. 7

---

## Active patterns

# List which patterns are relevant for this organization.
# Leave blank to enable all patterns defined in pattern-rules.md.
# Comment out patterns that are not applicable.

active_patterns:
  - HIGH_EPIC_WIP
  - LOW_SPRINT_COMPLETION
  - LONG_CYCLE_TIME
  - LONG_EPIC_DEVELOPMENT_TIME
  - LOW_ROADMAP_CONTRIBUTION
  - WIP_DEATH_SPIRAL
  - ROADMAP_DRIFT

---

## Roadmap depth logic

# Describe how this organization defines strategic work in Jira.
# Used to help Claude interpret roadmap contribution correctly.

roadmap_committed_definition: |
  [How this org classifies work as roadmap committed.
  Example: "Epic is linked to an Initiative that has a Quarter defined."]

roadmap_stretched_definition: |
  [How this org classifies stretched roadmap work.
  Example: "Epic is linked to an Initiative without a Quarter."]

roadmap_data_quality_note: |
  [Known data quality issues affecting roadmap contribution.
  Example: "Not all epics are linked to initiatives. Roadmap 0% likely
  reflects missing linkage rather than zero strategic work."]

---

## Token efficiency settings

# Controls how the engine manages expensive queries.
# Leave blank to use engine defaults.

max_teams_per_compare: # default 6 — warn if more teams requested
default_trend_sprints: # default 3 — sprints to use for trend analysis
warn_above_tokens: # default 3000 — estimated tokens before warning user

---

## Data notes

# Document known data quality issues specific to this organization.
# Claude will include these in the Assumptions & Limitations section.

known_data_issues:
  - [e.g. "Roadmap linkage not maintained — Initiative keys missing on most epics"]
  - [e.g. "Some teams use non-standard workflow states — stage names may not normalize correctly"]
  - [e.g. "Sprint data before 2025-S15 is incomplete"]

# Proxy mode flags — set true if these conditions apply
epic_dev_time_proxy_mode: true # almost always true — set false only if stage timestamps available
roadmap_zero_warning: true # set true if 0% roadmap is expected to be a data gap, not reality

---

## Catalog version

# Specify which catalog version this org config is designed for.
# If catalog is updated, review this config for compatibility.

catalog_version: recommendation_catalog_v1
