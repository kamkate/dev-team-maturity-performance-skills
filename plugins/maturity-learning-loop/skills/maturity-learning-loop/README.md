# Team Maturity Learning Loop — Install Guide

## What this is

An add-on skill for the Team Maturity Engine.
It tracks whether intervention recommendations were tried,
evaluates whether they worked, and generates ROI reports for CTOs.

No app. No infrastructure. No database. Everything runs in the
Claude Project alongside your existing engine files.

---

## Prerequisites

- Team Maturity Engine skill already installed and working
- At least one completed maturity analysis session (to have KPI baselines)
- org-config.md updated with cost_per_eng_day (for monetary ROI)

---

## Files in this package

```
SKILL.md                          ← install this as a skill
intervention_log.json             ← starts empty, grows over time
outcome_log.json                  ← starts empty, grows over time
references/
  roi-model.md                    ← ROI conversion formulas
  verdict-rules.md                ← effective / partial / ineffective logic
  report-template.md              ← CTO report format
  guardrails-learning.md          ← constraints the engine always follows
```

---

## Install steps

**Step 1 — Add the skill**

Upload `SKILL.md` to your Claude Project as a skill,
or add it alongside your other skills with the filename
`maturity-learning-loop.md`.

**Step 2 — Upload the data files**

Upload to the same Claude Project:
- `intervention_log.json` (empty to start)
- `outcome_log.json` (empty to start)
- All four files in `references/`

**Step 3 — Update org-config.md**

Add these fields to your existing org-config.md:

```
# ROI model parameters
cost_per_eng_day: [your fully loaded daily cost per engineer]
cost_currency: [EUR / USD / GBP / etc]
context_switch_factor: 0.15
```

Leave `context_switch_factor` at 0.15 unless you have a specific reason
to adjust it. See references/roi-model.md for the research basis.

**Step 4 — Verify**

Start a new session. The engine should load both skills.
Say: "show me the learning loop status"

Expected response:
> "intervention_log.json: 0 entries.
> outcome_log.json: 0 entries.
> No pending lookbacks. Ready to record intervention decisions."

---

## How it works in practice

**After an engine analysis session:**

The engine recommends interventions. You decide what to do.
Tell the engine: "Accept the focus sprint recommendation" or "Skip all."
The skill writes a log entry with the baseline KPIs and lookback sprint.
Save the updated `intervention_log.json` back to the Project.

**Two sprints later:**

Upload the new `jira_db.json` (with the lookback sprint data).
The skill detects the pending evaluation automatically at session start.
It asks you to run the engine for that team × sprint to get fresh KPIs.
Once you paste the KPI output, it computes the delta, assigns a verdict,
and writes to `outcome_log.json`.
Save both updated files back to the Project.

**Each quarter:**

Say: "Generate ROI report for Q2 2025."
The skill reads outcome_log.json, aggregates, applies the ROI model,
and produces a formatted report you can copy into a board update.

---

## Important: the user is the persistence layer

Claude Projects have no database. The log files are your database.
Every time the skill writes to a log file, it shows you the updated
JSON and tells you to save it back to the Project.

This is a feature, not a limitation — you always have a local copy,
and you can audit every entry.

---

## Updating catalog.yaml for effectiveness rates (manual, v1)

The skill records effectiveness data in outcome_log.json but does not
yet automatically update catalog.yaml. To manually enrich a catalog entry:

1. Count outcome_log entries for a given intervention_id
2. Count how many have verdict = "effective"
3. effectiveness_rate = effective_count / total_count
4. Add to catalog.yaml: `effectiveness_rate: [value]` and `sample_size: [N]`

A future catalog-learning skill will automate this.
