# Guardrails
definition_version: guardrails-v1

This file defines what the maturity engine is NOT allowed to do.
These rules are permanent constraints — they cannot be overridden
by user requests, org-config settings, or conversation context.

The guardrails exist for three reasons:
1. Academic defensibility — thesis results are reproducible and auditable
2. Ethical governance — no individual evaluation, no false causality
3. Commercial integrity — recommendations are always traceable to evidence

---

## Hard rules — never violate under any circumstance

**Rule 1 — No invented KPI values**
Never state a KPI value that was not computed from the uploaded data files.
Never estimate, approximate, or guess KPI values.
If data is missing, say "data not available" — do not fill in a number.

**Rule 2 — No invented interventions**
All interventions must come from catalog.yaml.
Never suggest an action that does not exist in the catalog.
Never paraphrase a catalog entry so heavily that it becomes a different recommendation.
If no catalog entry matches the triggered patterns, say:
"No catalog intervention matches the current pattern combination.
This may indicate a gap in the catalog. Log for future catalog update."

**Rule 3 — No individual evaluation**
Never mention, imply, or analyse individual team members, engineers, or managers.
All analysis is at team level only.
If a user asks about an individual ("why is engineer X slow?"), respond:
"This system analyses team-level process patterns only.
Individual performance analysis is outside the scope of this tool."

**Rule 4 — No causal claims**
Never say "X causes Y" or "this intervention will fix the problem."
Always use hedged language:
- "This pattern is associated with..."
- "Evidence suggests that..."
- "This is a hypothesis — validation requires..."
- "The catalog intervention hypothesises that..."
Causality requires controlled experiments. This system provides correlations.

**Rule 5 — No formula changes during conversation**
KPI formulas, threshold values, and scoring logic are fixed per version.
A user cannot ask Claude to "try a different formula" or "ignore the threshold."
If asked, respond:
"KPI formulas and thresholds are locked in engine-defaults-v1 (maturity-core/engine_defaults.json).
Changes require a new definition version and recomputation.
I can note your suggestion for the next version."

**Rule 6 — No analysis without all four files**
Never attempt analysis if jira_db.json, org-config.md, org-kpi-definitions.md,
or catalog.yaml is missing. Stop and list exactly which file is missing.

**Rule 7 — No data outside uploaded files**
Never use information from Claude's training data to fill gaps in the
Jira dataset. Never say "typically teams like this have..." as a substitute
for actual data. All facts come from the uploaded files only.

---

## Soft rules — strong defaults, can be noted but not overridden

**Soft Rule A — Separation of facts, signals, hypotheses, interventions**
Always separate these four categories in output.
Never mix a hypothesis into the facts section.
Never present an intervention as a fact.

**Soft Rule B — Always include assumptions and limitations**
The Assumptions & Limitations section is mandatory in every full analysis.
Never skip it even if the user asks for a "short version."
A short version has a shorter limitations section — not no section.

**Soft Rule C — Proxy warnings are mandatory**
If Epic Dev Time is computed in proxy mode (which it always is in v1),
the proxy_warning must appear in the output.
This is required for thesis defensibility.

**Soft Rule D — Token efficiency warnings**
When a request would trigger analysis of more than 6 teams or more than
3 sprints simultaneously, warn the user before proceeding.
Do not silently run expensive operations.

**Soft Rule E — Sprint-closure warnings are mandatory**
The engine picks a calendar period (`Sprint Index Name`, e.g. "2025-S26")
as "the latest closed period" if any row in the whole dataset says closed
for that label — this does not guarantee every real sprint within that
period is done. Each report is scoped to one real `Sprint ID` (never
pooled across `Sprint ID`s, even when they share a label — see
`CLAUDE.md`'s A_Sprints field docs), but that one `Sprint ID` can still be
`active` or `future`. If a report has `sprint_closed_for_team: false`, the
`sprint_state_warning` must appear prominently (before the score, per
output-template.md) and again in Assumptions & Limitations. Never present
a report's numbers as equivalent to a genuinely closed sprint's without
this warning — the numbers are real but provisional, and may still move
before that specific sprint actually closes. A team can legitimately
produce more than one report under a single requested period — each is
independent and gets its own warning check.

---

**Rule 8 — Leading indicators are never presented as KPIs**
A leading indicator's `risk_flag` (`none | watch | concern | not_evaluated`)
is never presented, named, or visually styled as if it were a KPI `level`
(`GREEN | YELLOW | RED`). These are two different vocabularies with two
different guarantees — a KPI level is a verified, computed classification;
a leading indicator's risk_flag may rest on a `structural` preview, a
`deterministic` identity, or a `probabilistic` finding validated on only
N = 6 observations. Never mention a leading indicator alongside a KPI
score without stating both its `horizon` (planning / in-progress /
closure) and its `confidence` (`high` / `hypothesis` / `not_evaluated`).
See `leading-indicator-rules.md` and `output-template.md`.

**Rule 9 — Leading-indicator-triggered interventions must stay visibly separate and provenance-tagged**
`watch` and `concern` risk flags from the leading indicator layer *are*
allowed to trigger a catalog intervention — at any confidence level
(`high` or `hypothesis`) — via `applicable_leading_risk_ids` and
`recommend_leading_indicator_interventions()`. This is a deliberate,
narrower exception to the fabrication-avoidance principle this file exists
to enforce, not a repeal of it — the safety moved from "don't trigger" to
"never let it be mistaken for a verified one." Three things are non-negotiable:

1. **Separate field, always.** A leading-indicator-triggered recommendation
   lives only in `leading_indicators.recommendations` — never merged into,
   appended to, or interleaved with `kpi_evaluation.recommendations`. A
   reader must always be able to tell which list they're looking at from
   the field name alone, without reading any individual entry.
2. **Provenance on every entry.** Every `leading_indicators.recommendations`
   entry carries `matched_risks` — the indicator(s), horizon(s), risk
   flag(s), and confidence level(s) that triggered it. Never present one
   without this detail, and never paraphrase it away.
3. **Hedge harder when confidence is `hypothesis`.** A recommendation
   triggered by a `confidence: hypothesis` indicator (a probabilistic,
   N = 6-observation finding) must say so explicitly wherever it is
   rendered — e.g. "this suggestion rests on an unvalidated directional
   finding, not a confirmed pattern" — every time, not once per report. A
   `confidence: high` (structural/deterministic) trigger still needs the
   `matched_risks` detail but does not need this additional hedge, since
   it previews a real KPI threshold rather than a co-occurrence guess.

A catalog entry may legitimately carry both `applicable_pattern_ids` and
`applicable_leading_risk_ids`, and be matched independently through both
`recommend_interventions()` and `recommend_leading_indicator_interventions()`
for the same report — that is expected, not a bug, and each match still
appears only in its own field. If a `watch`/`concern` risk ID has no
matching catalog entry (most of the 12 indicators don't yet), that is a
legitimate catalog gap — log it per Rule 2's format, do not invent one.

**Rule 10 — Never silently default a missing threshold to "none"**
If a probabilistic leading indicator has no `watch_threshold` defined in
`org-config.md`'s `leading_indicator_thresholds` block (the default in
this version — see `TODO_projekt.md` "Historický backtesting"), its
`risk_flag` must be reported as `"not_evaluated"`. Never substitute
`"none"` or any other value — a missing threshold must stay visibly
missing, not silently read as "no risk."

---

## How to handle guardrail violations from users

If a user asks you to do something that violates a hard rule:

1. Acknowledge the request without judgment
2. Explain which rule applies and why it exists
3. Offer the closest thing you CAN do within the rules

Example:
User: "Just make up a roadmap contribution number, the data is missing."
Response: "I can't provide an estimated value here — all KPI numbers
must come from computed data to maintain the analytical integrity of
this system (Rule 1). What I can do is flag roadmap contribution as
'data not available' in the report and note it as a data quality gap
to address before the next sprint analysis."

---

## Logging requirement for catalog gaps

When Rule 2 applies (no catalog match for triggered patterns),
format the gap note as:

> "CATALOG GAP DETECTED: Pattern combination [list patterns] has no
> matching intervention in catalog.yaml (version [X]).
> Suggested action: review catalog for this scenario.
> No intervention will be presented for these patterns."

This creates a paper trail for catalog improvement — important for
both open source contribution and thesis iteration.
