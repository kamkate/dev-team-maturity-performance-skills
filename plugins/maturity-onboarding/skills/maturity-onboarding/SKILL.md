---
name: maturity-onboarding
description: >
  Use this skill when setting up a new organization for the Team Maturity
  Engine, when configuring KPI definitions for a specific company, when
  calibrating thresholds for a new Jira environment, or when rerunning setup
  after a definition or threshold change. It prepares the manifest, the org
  config, and the KPI definitions files used by the engine.
version: onboarding-v2
---

# Team Maturity Onboarding

Use this workflow to produce the machine-readable configuration files needed by the engine.
The onboarding flow is intentionally lightweight and should generate the manifest, the org config, and the KPI definitions files in a format the shared runner can consume.

## Required workflow

1. Collect the organization context and the sprint assumptions.
2. Produce a manifest at [maturity/manifest.json](maturity/manifest.json) that references the data and config files.
3. Produce [maturity/org-config.md](maturity/org-config.md) with the threshold values and active patterns.
   - KPI threshold calibration: [references/threshold-guide.md](references/threshold-guide.md).
   - Leading indicator applicability (which of the 9 probabilistic leading
     indicators apply to this org's workflow, and why not for any that
     don't): [references/leading-indicator-applicability.md](references/leading-indicator-applicability.md).
     Runs right after threshold calibration — same file, same
     `leading_indicator_thresholds` block, a different question.
4. Produce [maturity/org-kpi-definitions.md](maturity/org-kpi-definitions.md) with the KPI definitions for the organization.
5. Validate the files against the schemas in [maturity-core/schemas](maturity-core/schemas).

## Output files

At the end of onboarding you should have:

1. [maturity/manifest.json](maturity/manifest.json)
2. [maturity/org-config.md](maturity/org-config.md)
3. [maturity/org-kpi-definitions.md](maturity/org-kpi-definitions.md)

These files plus the Jira export and catalog are sufficient for the engine runner.

## Guidance

- Prefer a config-driven workflow over verbose chat-only instructions.
- Reuse engine defaults from [maturity-core/engine_defaults.json](maturity-core/engine_defaults.json) when the organization does not need a custom value.
- Keep the outputs deterministic and easy to audit.
- If the org does not need a custom KPI definition, copy the default logic from the engine defaults and note that it is inherited.
