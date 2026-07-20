# Dev Team Maturity & Performance — Claude Skills

[![Claude Skill](https://img.shields.io/badge/Claude-Agent%20Skill-D97757?logo=anthropic&logoColor=white)](https://docs.claude.com/en/docs/claude-code/skills)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Two [Claude Agent Skills](https://docs.claude.com/en/docs/claude-code/skills) that turn raw Jira export data into governed, explainable engineering-maturity analysis for CTOs and Engineering Managers — no dashboards, no BI tooling, just Claude and your data.

> Built as part of an MBA thesis prototype on AI-assisted engineering management. The skills are generic and reusable — no organization-specific data is included in this repo.

---

## What's inside

| Skill | Purpose |
|---|---|
| [`maturity-engine/`](maturity-engine) | Computes 5 deterministic delivery KPIs from Jira data, detects diagnostic patterns, scores team maturity (0–100), and recommends interventions from a fixed catalog. |
| [`maturity-onboarding/`](maturity-onboarding) | Guides a CTO or consultant through configuring the engine for a new organization — KPI definitions, thresholds, active patterns, and data-quality notes. |

The two skills are designed to be used together: **onboarding** produces the `org-config.md` and `org-kpi-definitions.md` files that the **engine** consumes at analysis time.

---

## Why this exists

Most "AI for engineering metrics" tools either:
- invent numbers when data is messy, or
- let the LLM freelance on what counts as a good intervention.

This skill pair is built around governance instead:

- **Deterministic KPIs** — every number is computed from your Jira export, never estimated ([`references/kpi-definitions.md`](maturity-engine/references/kpi-definitions.md))
- **Rule-based pattern detection** — same inputs always produce the same signals, no LLM judgment calls ([`references/pattern-rules.md`](maturity-engine/references/pattern-rules.md))
- **Fixed intervention catalog** — recommendations only ever come from a catalog you control, never invented on the fly
- **Hard guardrails** — no individual (people-level) evaluation, no causal claims, no silent data gaps ([`references/guardrails.md`](maturity-engine/references/guardrails.md))

See [`maturity-engine/references/guardrails.md`](maturity-engine/references/guardrails.md) for the full list of hard and soft rules the engine will not break, even if asked.

---

## Requirements

- [Claude Code](https://docs.claude.com/en/docs/claude-code/overview), a Claude Project, or any Claude surface that supports [Agent Skills](https://docs.claude.com/en/docs/claude-code/skills)
- Your own data files at analysis time:
  - `jira_db.json` — exported Jira data (tasks, epics, initiatives, sprints)
  - `catalog.json` — your intervention catalog
  - `org-config.md` + `org-kpi-definitions.md` — produced by the onboarding skill

## Installation

Clone or copy the two skill folders into your Claude Skills directory:

```bash
git clone https://github.com/<your-username>/dev-team-maturity-performance-skills.git
cp -r dev-team-maturity-performance-skills/maturity-engine ~/.claude/skills/
cp -r dev-team-maturity-performance-skills/maturity-onboarding ~/.claude/skills/
```

Claude Code discovers skills automatically from `~/.claude/skills/` — no restart required for a new session.

## Usage

**1. Onboard a new organization** (first time only, or when KPI definitions change):

> "Set up the maturity engine for my organization"

The onboarding skill walks through organization context, KPI customization, thresholds, active patterns, and data-quality notes, then generates `org-config.md`, `org-kpi-definitions.md`, and an `onboarding-report.md`.

**2. Run an analysis:**

> "Analyse Team Alpha's last sprint"
> "Compare all teams in sprint 2025-S22"
> "Show me Team Alpha's maturity trend over the last 3 sprints"
> "Which team needs the most attention right now?"

The engine loads your config files, computes KPIs, detects patterns, scores maturity, and returns a structured report — facts, signals, and catalog-sourced interventions kept clearly separated. See [`maturity-engine/references/output-template.md`](maturity-engine/references/output-template.md) for the exact output structure.

---

## Repo structure

```
maturity-engine/
  SKILL.md                      entry point — governance, session startup, data model
  references/
    kpi-definitions.md          full KPI formulas, null handling, edge cases
    pattern-rules.md            atomic + compound pattern detection logic
    scoring-model.md            maturity score aggregation formula
    output-template.md          required output structure for every response
    guardrails.md               hard/soft rules the engine cannot break
  org-configs/
    template.md                 copy this to configure a new organization

maturity-onboarding/
  SKILL.md                      entry point — 8-step onboarding flow
  references/
    kpi-walkthrough.md          per-KPI customization dialogue
    threshold-guide.md          threshold calibration guidance per KPI
    output-generator.md         exact file formats for onboarding outputs
```

---

## License

[MIT](LICENSE) — use, adapt, and redistribute freely.
