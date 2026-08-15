---
name: maturity-engine
description: >
  Use this skill when the user asks about team maturity, sprint analysis,
  KPI computation, pattern detection, or intervention recommendations based
  on Jira data. The workflow is deterministic and uses the checked-in engine
  runner and catalog.
version: engine-v2
---

# Team Maturity Engine

Use this workflow for deterministic sprint analysis and intervention selection.
The engine is intentionally thin; the executable logic lives in the shared core runner.

## Required workflow

1. Read the mandatory files first:
   - [maturity/manifest.json](maturity/manifest.json)
   - [maturity/org-config.md](maturity/org-config.md)
   - [maturity/org-kpi-definitions.md](maturity/org-kpi-definitions.md)
   - [catalog.yaml](catalog.yaml)
2. Follow the output template in [maturity-engine/references/output-template.md](maturity-engine/references/output-template.md).
3. Use the shared runner at [maturity-core/run_analysis.py](maturity-core/run_analysis.py) for Tier A execution.
4. If the runner cannot execute, degrade gracefully and mark the output as unverified rather than fabricating numbers.

## Runtime behavior

- Tier A: run the shared runner and use the generated JSON output.
- Tier B: if code execution is unavailable, compute from the same rules in prose and mark the output as unverified.
- Tier C: if the data files are missing, stop and report the gap without inventing values.

## Guardrails

- Never invent KPI values.
- Never invent interventions.
- Never change formulas mid-session.
- Always separate facts, hypotheses, and interventions.
- Include the assumptions and limitations section.

## Analysis entry point

When the user asks for an analysis, run the shared runner and present the result in the output-template structure. The runner emits a JSON report with the computed KPIs, triggered patterns, recommended interventions, and a verified compute mode.
