# Output Template
definition_version: output-template-v1

This file defines the required output structure for every analysis response.
Follow this structure exactly. Do not skip sections.
Do not add sections not defined here.

The structure serves three purposes:
1. Consistency — CTO always knows where to find information
2. Auditability — facts and hypotheses are always separated
3. Defensibility — for MBA thesis, every output is traceable

---

## Full sprint analysis output

Use this structure when running run_sprint_analysis (one team, one sprint).

---

### [TEAM ID] · Sprint [SPRINT ID]

**Maturity Score: [score]/100 — [band]**
[one-sentence verdict]

---

### KPI Facts

| KPI | Value | Status |
|-----|-------|--------|
| Roadmap Contribution | [value]% | 🔴/🟡/🟢 RED/YELLOW/GREEN |
| Sprint Completion | [value]% | 🔴/🟡/🟢 |
| Cycle Time p50 | [value] days | 🔴/🟡/🟢 |
| Parallel Epics | [value] epics | 🔴/🟡/🟢 |
| Epic Dev Time | [value] weeks (proxy) | 🔴/🟡/🟢 |

Tasks analysed: [N]

---

### Signals — Triggered Patterns

[If no patterns triggered: "No critical patterns detected. All KPIs within acceptable range."]

[For each triggered pattern:]
**[PATTERN_ID]** · [Type]
[Business impact text]

[If compound pattern triggered, add:]
⚠️ [PATTERN_ID] — [urgency note]
[Compound pattern description]

[If YELLOW advisory applies:]
Advisory: [KPI names] are in the warning zone. Monitor next sprint.

---

### Interventions — From Catalog

[Present top 3 interventions from catalog lookup only]

| Field | 1. [Intervention Name] · [INT-XXX] | 2. [Intervention Name] · [INT-XXX] | 3. [Intervention Name] · [INT-XXX] |
|---|---|---|---|
| Why it fits | [which pattern triggered this] | | |
| **Action** | **[intervention field from catalog]** | | |
| Expected outcome | [expected_outcome from catalog] | | |
| **Effort** | **[effort]** | | |
| **Impact** | **[impact]** | | |
| Owner | [owner_role] | | |
| Preconditions | [preconditions from catalog] | | |
| Risk | [risks from catalog] | | |
| Review | [review_cycle from catalog] | | |

---

### Assumptions & Limitations

[Always include — never skip this section]

- [List data quality warnings from KPI computation]
- [Include proxy warning if Epic Dev Time used]
- [Include roadmap 0% warning if applicable]
- [Any other data gaps observed]

Versions: kpi_v2_aligned · maturity_v1 · [catalog version] · [org-config version]

---

### Next Step

[One specific question to guide the CTO — not generic]

Examples:
- "Would you like to compare this team against others in the same sprint?"
- "This team's cycle time is GREEN but WIP is critical — want to see the trend over last 3 sprints to check if WIP is getting worse?"
- "The roadmap contribution warning may be a data quality issue — should we check which epics are linked to initiatives?"

---

## Team comparison output

Use this structure for compare_teams (multiple teams, one sprint).

---

### Team Comparison · Sprint [SPRINT ID]

Ranked by maturity score (lowest first — highest attention needed).

| Rank | Team | Score | Band | RED KPIs | Top Pattern |
|------|------|-------|------|----------|-------------|
| 1 | [TEAM] | [N]/100 | [band] | [list] | [pattern] |
| 2 | ... | | | | |

**Teams requiring immediate attention:** [teams with score < 40]
**Teams to monitor:** [teams with score 40–59]
**Teams performing well:** [teams with score ≥ 60]

---

### Next Step

"Which team would you like to analyse in detail?"

---

## Trend output

Use this structure for get_trend (one team, multiple sprints).

---

### Trend · [TEAM ID] · [SPRINT range]

Overall trend: **[improving / stable / declining]**
Score change: [first sprint score] → [last sprint score] (Δ [delta])

| Sprint | Score | Band | Active Patterns |
|--------|-------|------|-----------------|
| [S1] | [N] | [band] | [pattern IDs] |
| [S2] | [N] | [band] | [pattern IDs] |
| [S3] | [N] | [band] | [pattern IDs] |

**KPI movement:**
| KPI | [S1] | [S2] | [S3] | Direction |
|-----|------|------|------|-----------|
| Roadmap | | | | ↑/→/↓ |
| Completion | | | | |
| Cycle Time | | | | |
| WIP | | | | |
| Epic Time | | | | |

**Interpretation:**
[2-3 sentences describing what the trend means for the business]

---

### Next Step

[Specific follow-up based on trend direction]

---

## Formatting rules

- Use markdown tables for KPI data — always
- Use a markdown table (fields as rows, interventions as columns) for the Interventions section — never bullet/paragraph format
- Bold the Action, Effort, and Impact row values in the Interventions table (row label and cell content) for all three interventions
- Use emoji for status: 🔴 RED, 🟡 YELLOW, 🟢 GREEN
- Bold pattern IDs and intervention names
- Never use bullet points for KPI data — use tables
- Keep verdict and next step in plain language — no Jira jargon
- Maximum response length: concise enough for a CTO to read in 2 minutes
- If a section has no content (e.g. no patterns triggered), say so explicitly
  — never silently omit a section
