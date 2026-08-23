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

## Step 0 — Offer the entry menu

At the start of an analysis conversation, before doing anything else, offer
these five modes as a plain numbered list (must render identically in
claude.ai, the desktop app, Claude Code, and Cowork — a structured choice UI
like Cowork's AskUserQuestion may layer on top, but the numbered list is the
spec):

1. **Team comparison** — compare all teams in a specific sprint window → §6 Team Comparison
2. **Morning brief** — a short status scan across teams: state + top priorities, no extra narration → Morning Brief (see [references/morning-brief-template.md](references/morning-brief-template.md))
3. **Full team analysis** — one team, one sprint window, in depth → §3 Full Sprint Analysis
4. **Trend analysis** — one team across the last 3 (or N) sprint windows → §5 Trend Analysis
5. **Last open sprint** — in-progress risk signal for one team's current sprint → §4 Leading Indicators, from a `--window` run (`mid_sprint_drift_check` / `sprint_start_risk_flag`)

**Soft default, never a gate.** If the user's first message already states
enough to proceed directly (a mode, or enough of team/sprint/window to
reasonably infer one), skip the menu and proceed. If the user answers
something other than 1–5, or asks a different question entirely — mid-menu
or mid-report — follow that instead. Never insist the user pick from the
menu before answering a clear, differently-phrased request.

## Required workflow

1. Read the mandatory files first:
   - [maturity/manifest.json](maturity/manifest.json)
   - [maturity/org-config.md](maturity/org-config.md)
   - [maturity/org-kpi-definitions.md](maturity/org-kpi-definitions.md)
   - [catalog.yaml](catalog.yaml)
2. Follow the output template in [maturity-engine/references/output-template.md](maturity-engine/references/output-template.md).
3. Use the shared runner at [maturity-core/run_analysis.py](maturity-core/run_analysis.py) for Tier A execution.
4. If the runner cannot execute, degrade gracefully and mark the output as unverified rather than fabricating numbers.
5. For every report's `👉 Next Step` section, select exactly one question —
   the single highest-priority match via
   [references/next-step-routing.md](references/next-step-routing.md) —
   never invented. When it routes to "which tasks/epics are behind this,"
   run `run_analysis.py --drill-down TEAM SPRINT_ID INDICATOR_ID`
   (read-only — see [references/guardrails.md](references/guardrails.md)
   Rule 11) rather than guessing.

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
