---
name: maturity-onboarding
description: >
  Use this skill when setting up a new organization for the Team Maturity
  Engine, when configuring KPI definitions for a specific company, when
  calibrating thresholds for a new Jira environment, or when rerunning setup
  after a definition or threshold change. It prepares the manifest, the org
  config, and the KPI definitions files used by the engine.
version: onboarding-v3
---

# Team Maturity Onboarding

Use this workflow to produce the machine-readable configuration files needed by the engine.
The onboarding flow is intentionally lightweight and should generate the manifest, the org config, and the KPI definitions files in a format the shared runner can consume.

## Required workflow

1. **Data source gate — ask first, before anything else.** Static export
   (CSV/JSON) or live Jira connection: [references/data-source-gate.md](references/data-source-gate.md).
   This is a hard gate everything else branches on. Both branches end with
   one concrete, fully-linked example (task → epic → initiative-if-any →
   sprint) on screen — for live Jira, also a validated `field_mapping`
   artifact. Carry that example into Step 3.
2. Collect the organization context and the sprint assumptions.
3. Rule calibration — what each KPI means for this org, grounded in the
   Step 1 example: [references/kpi-walkthrough.md](references/kpi-walkthrough.md).
4. Per-KPI threshold calibration: [references/threshold-guide.md](references/threshold-guide.md).
   (Per-team threshold overrides are a forward-declared shape in
   `org_config.schema.json` — not yet read by the engine; this step still
   calibrates org-level thresholds only.) Immediately followed by leading
   indicator applicability — which of the 9 probabilistic leading
   indicators apply to this org's workflow, and why not for any that
   don't, also grounded in the Step 1 example:
   [references/leading-indicator-applicability.md](references/leading-indicator-applicability.md).
   Same `org-config.md` `leading_indicator_thresholds` block as the
   threshold values, a different question.
5. Write, freeze, version:
   - Produce a manifest at [maturity/manifest.json](maturity/manifest.json) that references the data and config files.
   - Produce [maturity/org-config.md](maturity/org-config.md) with the data
     source choice, field mapping (live-Jira branch only), threshold
     values, and active patterns — see [references/output-generator.md](references/output-generator.md).
   - Produce [maturity/org-kpi-definitions.md](maturity/org-kpi-definitions.md) with the KPI definitions for the organization.
   - Validate the files against the schemas in [maturity-core/schemas](maturity-core/schemas).

## Output files

At the end of onboarding you should have:

1. [maturity/manifest.json](maturity/manifest.json)
2. [maturity/org-config.md](maturity/org-config.md) — now also carries the
   `data_source` choice and, for the live-Jira branch, the `field_mapping`
   artifact, alongside thresholds and active patterns.
3. [maturity/org-kpi-definitions.md](maturity/org-kpi-definitions.md)

These files plus the Jira export and catalog are sufficient for the engine runner.
(Note: the engine still only ever computes from `jira_db.json`/CSV — the
live-Jira branch validates connectivity and field mapping, it does not add
a live-query path to `run_analysis.py`. Bulk extraction scope captured at
the end of the live-Jira branch is recorded, not executed, by onboarding.)

## Guidance

- Prefer a config-driven workflow over verbose chat-only instructions.
- Reuse engine defaults from [maturity-core/engine_defaults.json](maturity-core/engine_defaults.json) when the organization does not need a custom value.
- Keep the outputs deterministic and easy to audit.
- If the org does not need a custom KPI definition, copy the default logic from the engine defaults and note that it is inherited.
- "CSV" always means "static export (CSV/JSON)" in this workflow — the
  real case-study data (`jira_db.json`) is JSON, not CSV, and prompts
  should say so rather than implying only CSV is supported.
