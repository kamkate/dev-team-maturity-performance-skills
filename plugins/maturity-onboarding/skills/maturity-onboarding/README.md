# Team Maturity Onboarding — Install Guide

## What this is

A configuration wizard for the Team Maturity Engine. It walks a CTO or
consultant through a conversation and produces three machine-readable
files — `manifest.json`, `org-config.md`, `org-kpi-definitions.md` — that
tell the engine how *this specific organization's* Jira data should be
read and scored.

No app. No infrastructure. No database. It runs entirely inside a Claude
conversation (Claude Code or a Claude Project) alongside your other Team
Maturity Engine files.

This package is **onboarding only**. It does not compute KPIs or detect
patterns itself — see "What you still need" below.

---

## What you still need

Onboarding cannot run standalone — it depends on the **maturity-core**
package for its schemas and engine defaults (`SKILL.md` links directly to
`maturity-core/schemas/*.json` and `maturity-core/engine_defaults.json`).
This zip includes a copy of `maturity-core` for that reason.

To actually *analyze* a team after onboarding finishes, you separately need
the **maturity-engine** skill (not included in this package — it's the
one that reads `jira_db.json`/CSVs plus the files onboarding produces, and
computes the 5 KPIs, patterns, and intervention recommendations). Ask
whoever gave you this package for it, or request it separately.

---

## Files in this package

```
README.md                                  ← this file
.claude-plugin/
  marketplace.json                         ← lets `claude plugin` install both plugins below directly
plugins/
  maturity-onboarding/
    .claude-plugin/plugin.json
    skills/maturity-onboarding/
      SKILL.md                             ← install this as a skill (Option B: upload this file)
      README.md                            ← same content as this file
      references/
        data-source-gate.md                ← Step 1: static export vs. live Jira
        kpi-walkthrough.md                 ← Step 3: what each KPI means for this org
        threshold-guide.md                 ← Step 4: per-KPI numeric thresholds
        leading-indicator-applicability.md ← Step 4b: which leading indicators apply
        output-generator.md                ← Step 5: exact output file formats
  maturity-core/
    .claude-plugin/plugin.json
    engine_defaults.json                   ← default KPI thresholds/formulas
    run_analysis.py, evaluate.py, leading_indicators.py   ← the deterministic engine (used by maturity-engine, referenced by onboarding for validation)
    schemas/                               ← JSON Schemas onboarding validates its output against
```

---

## Install steps

**Option A — Claude Code plugin system**

If your organization uses Claude Code with plugin support, point it at
this unzipped folder as a marketplace source (it contains a
`marketplace.json` listing both `maturity-core` and `maturity-onboarding`)
and install both plugins from it. `maturity-onboarding` declares
`maturity-core` as a dependency — install `maturity-core` first.

**Option B — Manual upload to a Claude Project**

1. Upload `plugins/maturity-onboarding/skills/maturity-onboarding/SKILL.md`
   to your Claude Project as a skill (or add it as `maturity-onboarding.md`
   alongside your other skills).
2. Upload every file under
   `plugins/maturity-onboarding/skills/maturity-onboarding/references/`.
3. Upload `plugins/maturity-core/engine_defaults.json` and everything under
   `plugins/maturity-core/schemas/`. (`run_analysis.py`, `evaluate.py`, and
   `leading_indicators.py` are only needed once you also install
   maturity-engine — safe to upload now or skip until then.)

**Verify**

Start a new session and say: **"Set up a new organization for the Team
Maturity Engine."** The very first thing it should do is ask you whether
your data comes from a static export (CSV/JSON) or a live Jira connection
— that's the Step 1 gate. If it skips straight to asking about industry
or team model instead, the skill didn't load correctly — check that
`SKILL.md` and all five `references/*.md` files were uploaded.

---

## How it works in practice

**Step 1 — Data source gate.** Static export (upload `jira_db.json` or
four CSVs) or live Jira connection (Atlassian connector, a single test
task you supply, its epic/sprint/initiative/changelog). Either way you end
up with one concrete, fully-linked example on screen before anything else
happens. For live Jira, this step also derives and records a
`field_mapping` (which custom field IDs mean story points, sprint, epic
link, initiative link on *your* instance) — Jira custom field IDs are
per-instance, so this can't be hardcoded.

**Steps 2–4 — Context and calibration.** Organization context, then what
each KPI means for your teams and which leading indicators apply
(grounded in the Step 1 example, not asked abstractly), then the numeric
GREEN/YELLOW/RED thresholds for each.

**Step 5 — Write, freeze, version.** Produces `manifest.json`,
`org-config.md` (thresholds, active patterns, data source, field mapping),
and `org-kpi-definitions.md`, then validates all three against the schemas
in `maturity-core/schemas/`.

---

## Important caveats

- **The live-Jira branch validates and maps fields — it does not make the
  engine query Jira live.** `run_analysis.py` (in `maturity-core`, used by
  the separate maturity-engine skill) still only ever computes KPIs from
  an uploaded `jira_db.json` or the four CSVs. The `field_mapping`
  artifact this package produces is recorded for a future live-ingest
  pipeline to consume — it is not consumed by anything yet.
- **Per-team threshold overrides are declared but not enforced.**
  `org-config.md`'s `team_overrides` field is schema-validated but not
  currently read by `run_analysis.py` — thresholds are org-level only for
  now, regardless of what onboarding records there.
- **The user is the persistence layer.** There's no database — after
  onboarding writes the three output files, save them back to your Claude
  Project (or repo) yourself. Re-run onboarding any time a KPI definition
  or threshold needs to change; it versions and preserves prior definitions
  rather than overwriting them.
