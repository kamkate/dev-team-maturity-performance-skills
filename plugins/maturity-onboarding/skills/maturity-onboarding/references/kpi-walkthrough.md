# KPI Walkthrough Guide
reference_for: maturity-onboarding Step 2
version: kpi-walkthrough-v1

This file defines the dialogue for each of the 5 KPIs during onboarding.
For each KPI: show default, ask if it fits, capture custom definition if not.

---

## KPI 1 — Roadmap Contribution

**Show to user:**
> "**KPI 1 — Roadmap Contribution**
> Measures what share of sprint work is connected to strategic priorities.
>
> **Engine default definition:**
> A task counts as roadmap-linked if its parent epic has a non-null
> Initiative key (i.e. the epic is linked to a strategic initiative).
>
> **Does this match how your organization tracks strategic work in Jira?**
> (yes / no)"

**If yes:** use engine default. Ask threshold question only.

**Important — one-hop limit:** the engine's `linked_to` predicate can only
resolve one join hop (e.g. Task → Epic). It cannot currently chase a
second hop (e.g. Epic → Initiative → Initiative's own Quarter field) in a
single pipeline condition. Do not translate a rule like "epic's initiative
has a Quarter defined" into `linked_to` targeting a field that only exists
on the *initiative*, not the epic — that field will always read null off
the epic row and silently produce 0% for every team. If a rule genuinely
needs a second hop, say so explicitly and either use the epic's own
`Initiative key` as a proxy (the default above — matches ~96% of cases
where quarter-based linkage was tested) or flag it as a known engine
limitation rather than encoding something the DSL can't actually run.

**If no:** ask these questions in order:

1. "How does your organization track which work is strategic?
   Describe in plain language — I will translate it into a formula."

2. "Which Jira fields are involved?
   For example: Epic field 'Initiative key', Task field 'Labels',
   Initiative field 'Quarter', custom fields, etc."

3. "What is the simplest rule that correctly identifies roadmap work
   in your Jira? For example:
   - 'Task has a parent epic AND that epic has an Initiative key set'
   - 'Task has label ROADMAP'
   Tell me your rule." (If the rule needs a field that lives on the
   Initiative record rather than the Epic record, see the one-hop
   limit note above before translating it into a formula.)

4. After receiving the rule, translate it into formal definition:
   > "Based on what you described, the formula would be:
   > [formal definition]
   > Source fields: [list fields]
   > Operational rule: [plain language rule]
   >
   > Is this correct?"

5. Ask: "Are there edge cases? For example, tasks without epics — should
   they always count as non-roadmap, or is there another rule?"

**Capture:**
- source_fields: list of Jira fields used
- operational_rule: plain language
- formal_formula: R / N definition
- edge_cases: any special handling

---

## KPI 2 — Sprint Completion

**Show to user:**
> "**KPI 2 — Sprint Completion**
> Measures the team's ability to complete sprint commitments.
>
> **Engine default definition:**
> Count of tasks marked 'Completed in Sprint' (Is Completed in Sprint = Y)
> divided by total tasks in sprint.
>
> Source field: A_Sprints['Is Completed in Sprint'] — 'Y' or 'N'
>
> **Does this field exist and work correctly in your Jira?**
> (yes / no)"

**If yes:** use engine default.

**If no:** ask:
1. "How does your Jira track whether a task was completed within the sprint?
   Is there a different field or status we should use?"
2. Capture alternative field and rule.

---

## KPI 3 — Cycle Time p50

**Show to user:**
> "**KPI 3 — Cycle Time p50**
> Measures the median time tasks spend in active development.
>
> **Engine default definition:**
> Median of 'All Development Days Round Up to 50' field across all tasks
> in the sprint. This field is pre-capped at 50 days.
>
> Source field: A_Task['All Development Days Round Up to 50']
>
> **Two questions:**
> 1. Is the 'All Development Days Round Up to 50' field populated
>    for most tasks in your Jira? (yes / no / partially)
> 2. Is a 50-day cap appropriate, or would a different cap make more
>    sense for your sprint length and work type?"

**If field missing:** ask what alternative field tracks development time.

**If cap should change:** capture the new cap value.

---

## KPI 4 — Parallel Epics

**Show to user:**
> "**KPI 4 — Parallel Epics (WIP)**
> Measures how many epics are active in a single sprint.
> Higher values mean more parallelisation and more context switching.
>
> **Engine default definition:**
> Count of distinct non-null Parent key values across all tasks in sprint.
> (i.e. how many different epics the team's tasks belong to)
>
> Source field: A_Task['Parent key']
>
> **Does this make sense for your organization?**
> For example: if your teams intentionally run many small epics in parallel,
> the default thresholds may need adjustment even if the formula is correct.
> (yes — formula and thresholds make sense / yes formula but need threshold adjustment / no)"

**If no:** ask what a better WIP measure would be for this organization.

---

## KPI 5 — Epic Development Time

**Show to user:**
> "**KPI 5 — Epic Development Time**
> Measures how long epics take to develop — a proxy for delivery throughput.
>
> **Engine default definition (proxy mode):**
> For each epic: average the 'All Development Days' (uncapped) of its tasks,
> then divide by 7 to get weeks. Then average across all epics in the sprint.
>
> Source field: A_Task['All Development Days'] (uncapped)
>
> ⚠️ This is a proxy — the conceptual definition would use timestamps
> (first task In Progress → last task Done) but stage history is often
> unavailable in Jira.
>
> **Two questions:**
> 1. Does your Jira have reliable stage timestamps at epic level?
>    (first In Progress date, last Done date per epic)
>    If yes, we can use the conceptual definition instead of the proxy.
> 2. Is the 'All Development Days' field populated for most tasks?"

**If stage timestamps available:** capture fields and switch to conceptual mode.
Document as mode: 'conceptual' in org-kpi-definitions.md.

**If proxy only:** confirm proxy mode. Remind user proxy_warning will appear
in every analysis output.
