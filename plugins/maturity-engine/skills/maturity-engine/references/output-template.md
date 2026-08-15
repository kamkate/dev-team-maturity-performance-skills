# Output Template
definition_version: output-template-v8

This file defines the required output structure for every analysis response.
Follow it exactly. Do not skip sections. Do not add sections not defined here.

**Chat-only.** The CTO reads this directly in the conversation — no artifact,
no document, no custom CSS. Plain markdown can't set color, so **emoji are
doing the color work** in this template — they're not decoration, they're
the only "color" a chat window has. Every emoji below is assigned to exactly
one meaning and reused consistently; that's what keeps a colorful report
readable instead of noisy.

> **Convention:** *[italic bracketed text]* is an instruction — never render
> it. Plain markdown is the literal shape of the output, verbatim except for
> the `[VALUE]` placeholders inside it.

The structure serves three purposes:
1. **Consistency** — the CTO always knows where to find information
2. **Auditability** — facts, signals, and hypotheses are always separated
3. **Defensibility** — for MBA thesis, every output is traceable

---

## 1. The icon legend

Two devices run through every section, and they do different jobs — don't
mix them:

- **Emoji = color, at a glance.** KPI status, pattern urgency, pattern type,
  band, effort/impact — anything the CTO should read in half a second from
  across the room. Fixed vocabulary, never improvised:

  | Meaning | Glyph |
  |---|---|
  | KPI / band status | 🔴 RED · 🟡 YELLOW · 🟢 GREEN |
  | Compound pattern (HIGH urgency) | 🚨 |
  | Pattern type — Predictability | 🎯 |
  | Pattern type — Flow | 🔁 |
  | Pattern type — Delivery | 📦 |
  | Pattern type — Strategic | 🧭 |
  | Sprint not yet closed | 🚧 |
  | Effort (repeat 1–3×, low→high) | 🔧 |
  | Impact (repeat 1–3×, low→high) | ⭐ |
  | Section: KPI Facts | 📊 |
  | Section: Signals | 🚦 |
  | Section: Interventions (from catalog, KPI-triggered) | 🛠️ |
  | Section: Interventions (from catalog, leading-indicator-triggered) | 🌱 |
  | Section: Leading Indicators | 🔭 |
  | Section: Assumptions & Limitations | 📝 |
  | Section: Next Step | 👉 |
  | Leading indicator flagged `watch` | 👀 |
  | Leading indicator flagged `concern` | 🔶 |
  | Trend direction | 📈 improving · ➖ stable · 📉 declining |

- **Code spans = precision, on demand.** Every exact computed value — scores,
  percentages, sprint IDs, pattern IDs, catalog IDs — goes in `` `backticks` ``.
  Monospace is the one thing plain markdown renders for free, and it marks
  "this number came from the engine, not from me." Never put prose in a code span.

---

## 2. Pick the structure

One report = one structure, chosen by what was actually run. Never blend two
structures into one response, and never invent a fourth.

| What you ran | Structure |
|---|---|
| One team, one sprint | §3 Full Sprint Analysis |
| One team, several sprints (a window over time) | §5 Trend Analysis |
| Several teams, one sprint | §6 Team Comparison |

*If the user's question spans two contexts — e.g. "how did this team do, and
how does it compare to the others" — run both and stack the two complete
sections back to back. Each keeps its own heading and its own Next Step.
Do not merge their tables into a hybrid layout.*

Every §3 report is scoped to one real `sprint_id`, never one calendar period.
*If the engine returns more than one report for the same team under the same
requested period (the team spans more than one board/squad), repeat §3 once
per report — never merge or average them. Put `sprint_id` in the header
whenever a team has more than one report, so the CTO can tell them apart.*

---

## 3. Full Sprint Analysis

*Use for one team, one sprint.*

### 🧭 [TEAM ID] · Sprint [SPRINT LABEL][ · SPRINT ID, only if this team has more than one report]

*If `sprint_closed_for_team` is `false`, this banner comes first — before the
score, as a blockquote, not a footnote:*
> 🚧 **Not yet closed for this team.** [sprint_state_warning text, verbatim]

**🎯 Score: `[score]/100`** — 🔴/🟡/🟢 [band]
[one-sentence verdict, human voice]

`[sprint_id]` · [org name] · [N] tasks analysed

### 📊 KPI Facts

*One emoji row at a glance — one glyph per KPI, same order as the table below
— then the table itself:*
🔴🔴🔴🔴🟢 *(4 red · 0 yellow · 1 green)*

| KPI | Value | Status |
|-----|-------|--------|
| Roadmap Contribution | `[value]%` | 🔴/🟡/🟢 RED/YELLOW/GREEN |
| Sprint Completion | `[value]%` | 🔴/🟡/🟢 |
| Cycle Time p50 | `[value] days` | 🔴/🟡/🟢 |
| Parallel Epics | `[value] epics` | 🔴/🟡/🟢 |
| Epic Dev Time | `[value] weeks` (proxy) | 🔴/🟡/🟢 |

### 🚦 Signals — Triggered Patterns

*If no patterns triggered:* "No critical patterns detected. All KPIs within acceptable range."

*If a compound pattern triggered, lead with it — 🚨, blockquoted — then list
the atomic patterns feeding it directly underneath, indented with `↳` and
their type glyph. The nesting is the point: it's the difference between
"5 things are wrong" and "these 2 things are wrong, and together they cause
a 3rd, worse thing."*

> 🚨 **`[PATTERN_ID]`** — HIGH urgency
> [compound pattern description: what self-reinforcing loop this is, human voice]

　↳ 🔁 **`[PATTERN_ID]`** · Flow — [business impact, one line]
　↳ 🎯 **`[PATTERN_ID]`** · Predictability — [business impact, one line]

*Any atomic pattern not feeding a compound gets its own flat line, same shape, no `↳`:*
🧭 **`[PATTERN_ID]`** · Strategic — [business impact, one line]

*If a KPI is YELLOW but didn't trigger a pattern, add one italic line:*
*Advisory: [KPI names] in the warning zone — monitor next sprint.*

### 🛠️ Interventions — From Catalog

*Top 3 from catalog lookup only, ranked pattern-match count DESC, impact DESC,
effort ASC. One numbered block per intervention — not a wide table; a
3-column table this dense needs horizontal scrolling in a chat pane and
defeats the point.*

1️⃣ **[Intervention Name]** `[INT-XXX]`
🔧 Effort: [LOW/MEDIUM/HIGH] · ⭐ Impact: [LOW/MEDIUM/HIGH]
Fits `[PATTERN_ID]` · `[PATTERN_ID]`

→ [intervention field from catalog, human voice]

**Expected:** [expected_outcome from catalog]

- Preconditions: [preconditions from catalog]
- Risk: [risks from catalog]
- Owner: [owner_role] · Review: [review_cycle]

*Repeat as 2️⃣ and 3️⃣, each block separated by a blank line. Draw the 🔧 and
⭐ glyphs 1×, 2×, or 3× to match low/medium/high — e.g. `🔧🔧` for medium
effort, `⭐⭐⭐` for high impact. Never collapse the four parts (header →
action → expected → fine print) onto consecutive lines with no break —
a blank line between each is what makes it read as distinct fields instead
of one paragraph.*

### 📝 Assumptions & Limitations

*Always include — never skip this section, even in a short version (a short
version has a shorter list here, not no section):*

- [Data quality warnings from KPI computation]
- [Proxy warning if Epic Dev Time used]
- [Roadmap 0% warning if applicable]
- [If `sprint_closed_for_team` is false: restate that this sprint is still in progress for this team — don't let the banner above be the only mention]
- [Any other data gaps observed]

`Versions: engine-defaults-v1 · maturity_v1 · [catalog version] · [org-config version]`

### 👉 Next Step

*Two parts, blank line between them inside the same blockquote: the specific
fact that prompted the question, then the question itself — never the
question alone with no grounding, and never the grounding without a
concrete question at the end.*

> [one line: the specific number or pattern above that this question follows from]
>
> **[the question itself]?**

Examples of the question line — always this concrete, never generic:
- "Cycle time is 🟢 GREEN but Parallel Epics is 🔴 RED, and the compound pattern says WIP is the driver — want the trend over the last 3 sprints to check if it's climbing?"
- "Roadmap Contribution is 🔴 RED at 28.6%, which can also mean missing Jira linkage rather than real drift — want to check which epics are linked to initiatives before treating this as a fact?"
- "This is one of 4 teams reporting this sprint — want the Team Comparison view to see where it ranks?"

---

### Worked example

*A complete §3 report, illustrative numbers, so the shape above is unambiguous:*

> ### 🧭 TEAMPRJ-DEMO01 · Sprint 2099-S01
>
> **🎯 Score: `20/100`** — 🔴 Low maturity
> Delivery is unpredictable and strategically adrift this sprint — four of five KPIs are red, and the two compound patterns below point to the same root cause: too much started, not enough finished.
>
> `SPRINT-DEMO01` · Demo Org · 31 tasks analysed
>
> **📊 KPI Facts**
> 🔴🔴🔴🔴🟢 *(4 red · 0 yellow · 1 green)*
>
> | KPI | Value | Status |
> |-----|-------|--------|
> | Roadmap Contribution | `24.1%` | 🔴 RED |
> | Sprint Completion | `43.8%` | 🔴 RED |
> | Cycle Time p50 | `12.5 days` | 🔴 RED |
> | Parallel Epics | `6 epics` | 🔴 RED |
> | Epic Dev Time | `4.2 weeks` (proxy) | 🟢 GREEN |
>
> **🚦 Signals — Triggered Patterns**
>
> 🚨 **`WIP_DEATH_SPIRAL`** — HIGH urgency
> WIP overload is creating queues that slow the entire system: high epic WIP increases cycle time, which prevents completion, which creates pressure to start new work, which increases WIP further — a self-reinforcing loop requiring systemic intervention, not a single fix.
>
> 　↳ 🔁 **`HIGH_EPIC_WIP`** · Flow — Excessive parallelisation slows throughput; too many epics active at once creates context switching and coordination overhead.
> 　↳ 🔁 **`LONG_CYCLE_TIME`** · Flow — Slow task throughput; tasks take too long to move through development, reducing the team's ability to respond to change.
>
> 🚨 **`ROADMAP_DRIFT`** — HIGH urgency
> Low strategic alignment combined with low execution: the team is neither working on the right things nor completing what it commits to.
>
> 　↳ 🧭 **`LOW_ROADMAP_CONTRIBUTION`** · Strategic — Sprint work is not connected to roadmap objectives; check Initiative-key linkage before treating this as actual misalignment.
> 　↳ 🎯 **`LOW_SPRINT_COMPLETION`** · Predictability — Stakeholders cannot rely on sprint commitments; the team consistently misses sprint goals.
>
> **🛠️ Interventions — From Catalog**
>
> 1️⃣ **Enforce WIP Limits** `INT-001`
> 🔧 Effort: LOW · ⭐⭐⭐ Impact: HIGH
> Fits `HIGH_EPIC_WIP` · `LONG_CYCLE_TIME` · `WIP_DEATH_SPIRAL`
>
> → Set an explicit team-level WIP limit for active epics and review it during sprint planning and weekly delivery checkpoints.
>
> **Expected:** lower active epic count, shorter cycle time, more predictable completion.
>
> - Preconditions: leadership must agree which epics are truly active
> - Risk: unmanaged exceptions may let the limit be bypassed
> - Owner: Engineering Manager · Review: 2 sprints
>
> 2️⃣ **Create Roadmap Capacity Guardrail** `INT-009`
> 🔧🔧 Effort: MEDIUM · ⭐⭐ Impact: MEDIUM
> Fits `HIGH_EPIC_WIP` · `LOW_ROADMAP_CONTRIBUTION` · `ROADMAP_DRIFT`
>
> → Set a target range for roadmap-linked sprint work and review exceptions during planning.
>
> **Expected:** higher roadmap contribution, stronger alignment between execution and strategy.
>
> - Preconditions: roadmap-linked work must be classified consistently
> - Risk: a fixed percentage target may be harmful during incidents
> - Owner: Product Director · Review: 2 sprints
>
> 3️⃣ **Focus on One Primary Epic per Team** `INT-012`
> 🔧 Effort: LOW · ⭐⭐⭐ Impact: HIGH
> Fits `HIGH_EPIC_WIP` · `WIP_DEATH_SPIRAL`
>
> → For the next sprint, select one primary epic focus and limit secondary epic work to explicitly justified exceptions.
>
> **Expected:** faster progress on priority epic work, lower story cycle time.
>
> - Preconditions: leadership must agree which epic has highest priority
> - Risk: frequent priority changes may create confusion instead of focus
> - Owner: VP Engineering · Review: 1 sprint
>
> **📝 Assumptions & Limitations**
> - Epic Dev Time is computed in `proxy_avg_dev_days` mode — mean task-level development days ÷ 7, per epic. Conceptual (stage-timestamp) mode is not available for this Jira instance.
> - Roadmap Contribution of 24.1% may partly reflect missing Initiative-key linkage in A_Epic rather than true strategic misalignment.
> - `SPRINT-DEMO01` is closed for this team — these figures are final for this reporting period.
>
> `Versions: engine-defaults-v1 · maturity_v1 · recommendation_catalog_v1 · org-config-v1`
>
> **👉 Next Step**
>
> Both compound patterns trace back to epic WIP being the shared driver.
>
> **Want to see the trend over the last 3 sprints, to check whether WIP has been climbing or this sprint is an outlier?**

---

## 4. Leading Indicators

*Applies whenever the engine ran in `--window` mode
(`build_sprint_window_reports`) and a report's `leading_indicators` block is
being presented — e.g. a `sprint_start_risk_flag` (future sprint), a
`mid_sprint_drift_check` (active sprint), or a closed sprint's leading
indicators alongside its `kpi_evaluation`. This is a within-sprint layer
(planning → in-progress → closure), separate from §5's across-sprint trend.*

**Same rule as Signals (§3): only show what has a signal.** Of up to 9
probabilistic + 3 structural indicators across 3 horizons, most will read
`none` or `not_evaluated` in any given report — that is expected, not
interesting, and listing all of them (the old behavior of this section) is
exactly what buries the 1–2 that actually matter. Show flagged indicators
individually; fold everything else into one tally line. This is the same
"don't overwhelm the CTO with a long list of things that are fine" principle
`pattern-rules.md` already applies to atomic patterns — applied here to a
much noisier layer where it matters more, not less.

### 🔭 Leading Indicators

*One bold line, always — this is the whole section if nothing is flagged:*
**[N] 👀 to watch · [N] 🔶 of concern** *(of [N] indicators checked — [N] no signal, [N] not yet evaluated)*

*If both flagged counts are 0, stop there:* "No leading indicator concerns this sprint."

*If either count is nonzero, one line per flagged indicator — horizon and
confidence inline, never a separate paragraph per horizon:*

👀 **[Indicator name]** ([planning/in-progress/closure] · confidence: [high/hypothesis]) — [one sentence: what it structurally previews, or what it hypothesises — per leading-indicator-rules.md]

🔶 **[Indicator name]** ([planning/in-progress/closure] · confidence: [high/hypothesis]) — [one sentence, same rule]

*Only reach for a table (indicator rows × horizon columns) when 2+ flagged
indicators need comparing across horizons — e.g. the same indicator moving
watch → concern as the sprint progresses. A table that's mostly "—" for
indicators nobody flagged is the noise this redesign removes; don't bring
it back for the common case of 0–2 flagged indicators.*

*If the CTO wants the full picture — every indicator, including the
`none`/`not_evaluated` ones — that's a deliberate ask, not the default:
offer it in Next Step rather than dumping it unprompted, e.g. "Want the
full leading-indicator breakdown, including the ones with no signal?"*

**Hard rule — never name a flagged indicator without its horizon and confidence**, inline as shown above:
- **Horizon** — map `planning_horizon` → "planning", `in_sprint_horizon` →
  "in-progress", `closure_horizon` → "closure"
- **Confidence** — `high` (structural/deterministic — previews a KPI
  threshold or a mathematical identity) or `hypothesis` (probabilistic —
  directional, validated on only 6 observations)

Never show a `risk_flag` next to a KPI's `level` without this distinction in
the same breath — the reader must never be able to mistake one for the other.

**🌱 Interventions — From Leading Indicators**

*A `watch`/`concern` leading indicator can now trigger a catalog match
(guardrails.md Rule 9, rewritten) — but this is a structurally different
kind of recommendation from §3's `🛠️ Interventions — From Catalog`, and
must never be presented the same way or in the same list. Read from
`leading_indicators.recommendations` (a sibling field inside
`leading_indicators`, never merged into `kpi_evaluation.recommendations`).
If it's empty, say so in one line — "No leading-indicator-triggered
interventions this sprint" — do not omit the subsection.*

*Same card shape as §3, plus two things §3 never needs: which indicator(s)
triggered it, and a mandatory hedge line whenever any triggering indicator
has `confidence: hypothesis`:*

1️⃣ **[Intervention Name]** `[INT-XXX]`
🔧 Effort: [LOW/MEDIUM/HIGH] · ⭐ Impact: [LOW/MEDIUM/HIGH]
Triggered by: `[risk_id]` — [indicator name] ([horizon] horizon), 👀/🔶 [watch/concern], confidence: [high/hypothesis]

→ [intervention field from catalog, human voice]

**Expected:** [expected_outcome from catalog]

- Preconditions: [preconditions from catalog]
- Risk: [risks from catalog]
- Owner: [owner_role] · Review: [review_cycle]

*If any `matched_risks` entry has `confidence: hypothesis`, add this line, every time — never skip it once "already said above":*
*⚠️ This suggestion rests on [an unvalidated directional finding / unvalidated directional findings] (N = 6 observations), not a confirmed pattern — treat as a lead to investigate, not a verified diagnosis.*

*If `leading_indicators.recommendations` has entries but no catalog entry
matches a `watch`/`concern` risk that seems significant, do not invent one
— name it as a catalog gap per guardrails.md Rule 2's format instead.*

**Excluded (not applicable) indicators — a different thing from `not_evaluated`.**

`not_evaluated` (folded into the tally line above) means "this indicator
applies to this org, there's just no confirmed threshold yet, or a
dependency like the prior sprint's data is missing." `not_applicable`
means "this indicator does not apply to this org's workflow at all" (e.g.
no story points → `MISSING_SP_RATIO`) — it was excluded from
`indicator_specs` before `compute_leading_indicators` ever ran (see
`leading_indicators.py::filter_applicable_indicators`), so it is simply
**absent**, and does not count toward the "[N] indicators checked" tally
either. Never conflate the two:

- Never mention an indicator that isn't present in the report at all —
  there is no need to say "we didn't check X"; the absence is already
  the signal.
- If the report's top-level `excluded_indicators` field is present, add
  **at most one short line**, once, summarizing the count and pointing to
  the onboarding record — never narrate each excluded indicator's
  `reason` inline, and never turn it into a bulleted list. Example tone:
  "3 leading indicators aren't shown because they don't apply to this
  organization's workflow (see onboarding record for details)." Do not
  repeat this line elsewhere in the same report.
- If `excluded_indicators` is absent, say nothing about exclusions at
  all — omitting the field is itself the signal that nothing was excluded;
  don't manufacture a "0 excluded" line.
- A `not_applicable` (excluded) indicator must never be described with
  `not_evaluated`'s vocabulary or sentence templates — they answer
  different questions ("does this apply at all" vs. "is there a confirmed
  threshold").

**Formatting rules specific to this section:**

- Never use 🔴/🟡/🟢 (reserved for KPI/band status, §1) or the `watch`/`concern`
  glyphs above for anything except a leading indicator's `risk_flag` — never
  mix the three vocabularies.
- Never phrase a `watch`/`concern` risk_flag as a recommendation ("you
  should..."). Leading indicators report; only `kpi_evaluation.recommendations`
  (catalog-sourced) may prescribe action — see `guardrails.md` Rule 9.
- If `kpi_evaluation.available` is `false` (sprint not closed), say so before
  showing leading indicators — don't let their presence imply a KPI score exists.

---

## 5. Trend Analysis

*Use for one team, several sprints — comparing sprint windows over time to
see whether the team is improving, stable, or declining.*

### 📈 Trend · [TEAM ID] · [SPRINT range]

**[N] sprints · trend: 📈 improving / ➖ stable / 📉 declining · `[first score]` → `[last score]` (Δ `[delta]`)**

| Sprint | Score | Band | Active Patterns |
|--------|-------|------|-----------------|
| `[S1]` | `[N]` | 🔴/🟡/🟢 [band] | `[pattern IDs]`, or "none" |
| `[S2]` | `[N]` | 🔴/🟡/🟢 [band] | `[pattern IDs]`, or "none" |
| `[S3]` | `[N]` | 🔴/🟡/🟢 [band] | `[pattern IDs]`, or "none" |

**KPI movement**

| KPI | `[S1]` | `[S2]` | `[S3]` | Direction |
|-----|------|------|------|-----------|
| Roadmap Contribution | | | | 📈/➖/📉 |
| Sprint Completion | | | | 📈/➖/📉 |
| Cycle Time p50 | | | | 📈/➖/📉 |
| Parallel Epics | | | | 📈/➖/📉 |
| Epic Dev Time | | | | 📈/➖/📉 |

**Interpretation**

*Three short labeled lines, not one dense paragraph — each is one sentence,
human voice, hedged (never "caused"; "is associated with", "coincides with"):*

**What moved:** [which KPI(s) or pattern(s) actually changed across the window, and in which direction]

**Why it matters:** [the business implication of that specific movement]

**Watch:** [what to check next sprint if the trend continues in the same direction]

### 👉 Next Step

*Grounding line, then the question — blank line between them:*

> [one line: the specific sprint-over-sprint movement above that this question follows from]
>
> **[the follow-up question, specific to that movement]?**

---

## 6. Team Comparison

*Use for several teams, one sprint.*

### 🧭 Team Comparison · Sprint `[SPRINT ID]`

**[N] teams · lowest: [team] (`[score]`) · highest: [team] (`[score]`)**

*Ranked by maturity score, lowest first — lowest score needs the most
attention. A full matrix earns its place here because every team has all 5
KPIs, always — one row per team, one column per KPI, so the CTO can scan
down a column and see who's red on, say, Cycle Time, instead of reading
five separate "RED KPIs" lists. (§4's leading indicators don't get this
treatment by default — most read no signal at all, so a full matrix would
be mostly empty; see §4 for why that section shows only what's flagged.)*

| Rank | Team | Score | Band | Roadmap | Completion | Cycle Time | WIP | Epic Time | Top Pattern |
|------|------|-------|------|---------|------------|------------|-----|-----------|-------------|
| 1 | `[TEAM]` | `[N]/100` | 🔴/🟡/🟢 [band] | 🔴/🟡/🟢 | 🔴/🟡/🟢 | 🔴/🟡/🟢 | 🔴/🟡/🟢 | 🔴/🟡/🟢 | `[pattern]`, or "—" |
| 2 | ... | | | | | | | | |

*"Top Pattern" is the highest-urgency triggered pattern for that team (a
compound pattern outranks an atomic one); "—" if none triggered.*

🚨 **Immediate attention** (score < 40): [teams, or "none"]
👀 **Monitor** (score 40–59): [teams, or "none"]
✅ **Performing well** (score ≥ 60): [teams, or "none"]

### 👉 Next Step

> [one line: which team(s) stand out from the table above and why — lowest score, a shared pattern across several teams, or a surprising outlier]
>
> **Which team would you like to analyse in detail?**

---

## 7. Formatting rules

- Blank line between every distinct field in a block (intervention header →
  action → expected → fine-print bullets; §3's Interventions). Consecutive
  lines with no blank line between them render as one dense paragraph in
  chat — that's what makes a block unreadable, not the content length.
- Show only what's flagged (§3 Signals, §4 Leading Indicators): a fixed,
  always-5 set like the KPI table is always shown in full; an open-ended
  set like patterns or leading indicators is not — list only the ones with
  a signal, fold the rest into one tally line. This is what keeps a
  12-indicator layer from burying the 1–2 that matter.
- Teams across KPIs (§6) get a full matrix table because the set is fixed
  (5 KPIs, every team, always) — that's the one case in this template
  where showing everything is the readable choice, not the noisy one.
- Interpretation (§5) is three labeled one-sentence lines (**What moved:** /
  **Why it matters:** / **Watch:**), never one 2-3 sentence paragraph — same
  reasoning as the intervention blocks: labeled short fields beat a dense block.
- Every Next Step (§3, §5, §6) is two parts inside its blockquote, blank line
  between them: a grounding line naming the specific number or pattern it
  follows from, then the bolded question. Never the question alone with no
  grounding — the CTO should never have to ask "why are you asking me this?"
- Markdown tables for all KPI and score data — never bullet points for numbers
- Emoji carry status, urgency, type, and direction (§1's fixed vocabulary) — never improvise a new emoji meaning mid-report
- Code spans (`` ` `` `` ` ``) for every computed value: scores, IDs, pattern names, KPI values — never for prose
- Intervention blocks (§3, §4's 🌱 subsection), not wide tables — a 3-column table with 8+ rows needs horizontal scrolling in a chat pane
- 🔴🟡🟢 for KPI/band status only — never for leading-indicator risk flags (§4), which use 👀/🔶 instead
- §4's 🌱 Interventions never merge into or sit inside §3's 🛠️ Interventions — two separate subsections, even when both are non-empty for the same report; a `matched_risks` entry with `confidence: hypothesis` always carries its hedge line, every single time it's shown, never only on first mention
- Blockquotes reserved for callouts that must not be skimmed past: the not-closed banner, a compound pattern, the Next Step — not for routine content, or they stop standing out
- `↳` only under a compound pattern, to mark the atomic patterns feeding it — never elsewhere
- 🔧/⭐ repeated 1–3× for effort/impact — count must match low/medium/high, never a flat single glyph regardless of level
- If a section has no content (e.g. no patterns triggered), say so explicitly — never silently omit a section
- Keep verdicts, interpretations, and Next Step in plain language — no Jira jargon
- Target length: readable by a CTO in under 2 minutes per structure
