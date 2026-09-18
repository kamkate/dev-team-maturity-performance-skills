# Data Source Gate
reference_for: maturity-onboarding Step 1
version: data-source-gate-v1

This is the first thing that happens in onboarding, before anything else —
including organization context. Everything downstream (what gets validated,
what the concrete example in Step 3's rule-calibration dialogue looks like,
what `org-config.md` ends up recording) branches on the answer here.

---

## The gate question

**Ask, before collecting anything else:**
> "Where does this organization's Jira data come from?
> 1. **Static export (CSV/JSON)** — you'll upload a `jira_db.json` file, or
>    the four CSVs (`tasks.csv`, `epics.csv`, `initiatives.csv`,
>    `sprints.csv`), and the engine reads from that.
> 2. **Live Jira connection** — we connect to your Jira instance directly to
>    validate structure and field mapping before any bulk pull happens."

Record the answer as `data_source.type`: `static_export` or `live_jira`.
This is a hard gate — do not proceed with both branches, and do not infer
the answer from what files happen to be attached to the conversation.

Note: the engine itself (`run_analysis.py`) still only ever computes KPIs
from a `jira_db.json` file or the four CSVs — it does not query Jira live.
The live-Jira branch below validates connectivity and derives field mapping
metadata; it does not change what the engine consumes. See the "field
mapping persistence" note at the end of this file.

---

## Branch A — Static export (CSV/JSON)

1. Upload file(s): `jira_db.json`, or all four of `tasks.csv` / `epics.csv`
   / `initiatives.csv` / `sprints.csv`. If only some of the four CSVs are
   present, report exactly which are missing and stop — do not guess at
   partial data.
2. Validate schema against [maturity-core/schemas/jira_db.schema.json](../../maturity-core/schemas/jira_db.schema.json).
3. **New — show one representative task before moving on.** Ask the user
   to name a `Team` (or `TEAMPRJ-XXXXXX` project key) they recognize —
   **not** a specific task ID. Case-study task IDs are anonymized, so the
   user has no memory of any single one; this is the opposite of Branch B,
   where the user knows their own real ticket keys and should be asked for
   one directly.
   - Pick one task belonging to that `Team` (any deterministic selection —
     e.g. the most recently completed one — is fine; this is an anchor
     example, not a sample chosen for statistical properties).
   - Display it with full linkage: parent epic (`Parent key`), initiative
     (only if `A_Epic.Initiative key` is populated for that epic — state
     plainly if it isn't), and sprint membership (`Sprint ID`, `Sprint
     State`, `Is Completed in Sprint`).
   - This task/epic/initiative/sprint example is what Step 3 (rule
     calibration) grounds its questions in — carry it forward rather than
     re-selecting a different example later in the session.

---

## Branch B — Live Jira connection

1. Set up the connection (Atlassian connector) and confirm access:
   - `getAccessibleAtlassianResources` to resolve the `cloudId` if the user
     gave a site URL rather than a UUID.
   - `getVisibleJiraProjects` (with that `cloudId`) to confirm the target
     project is actually visible to this connection before going further.
2. **Ask the user for the key of one specific test task** (e.g.
   `TEAMPRJ-1042`). The user types it themselves — do not suggest a
   candidate; unlike Branch A's anonymized case-study IDs, the user knows
   their own real tickets, and picking one they recognize is what makes
   this a meaningful human check rather than a formality.
3. Fetch that issue with `getJiraIssue` (`fields: ["*all"]`,
   `expand: "changelog"`) to get the full field set and change history in
   one call. From the response, resolve and display:
   - The task itself (key, summary, status, issue type)
   - Its parent epic, if any (native `parent` field on team-managed
     projects, or the `Epic Link` custom field on company-managed ones —
     which one is present tells you `project_type`, see step 4)
   - Its sprint(s) (the `Sprint` custom field — usually
     `customfield_10020` on Jira Cloud, but this is exactly the kind of
     value that must be *read from this instance's actual response*, never
     assumed from a prior instance)
   - Its initiative, if the hierarchy level exists on this Jira tier
     (Advanced Roadmaps). If the parent epic has no initiative-level
     parent and the site doesn't expose one, say so plainly — do not
     silently omit it.
   - The changelog (`expand: changelog` — standard Jira REST field on the
     issue response), summarized as a short history of status transitions.
   - **Have the user confirm this looks right before proceeding.** If they
     say something is off (wrong task, unexpected field empty that
     shouldn't be), stop and let them re-supply the key or investigate —
     do not proceed to field mapping on an unconfirmed example.

4. **Open edge case — task has no parent epic at all.**
   **Decision: accept it as a valid example.** A solo task (no parent
   epic) is not an error state in this engine — `CLAUDE.md`'s own field
   documentation treats a null `Parent key` as expected, valid data, and
   `second-level-signals-summary.md` §3 lists "solo tasks" as a first-class
   **structural** signal (`Parent key` null ⇒ roadmap contribution is
   structurally 0% for that task, independent of team performance) — not a
   validation failure to route around. Rejecting the user's real,
   recognized ticket and asking them to go find a different one just to
   satisfy the onboarding flow would also mean the flow never exercises
   the solo-task code path at all.
   The tradeoff: a solo task can't demonstrate the epic-link or
   initiative-link field mapping, because those fields never populate on
   it. So when the validated example is a solo task:
   - Still derive `story_points` and `sprint` mapping from it (those don't
     depend on epic linkage).
   - Derive `epic_link.mode` and `initiative_link` field IDs from the
     project's field *metadata* instead of an example value — call
     `getJiraIssueTypeMetaWithFields` for the epic issue type in this
     project (`requiredFieldsOnly: false`) to see whether `Epic Link` or a
     native `parent` field is configured, and whether an initiative-level
     field exists — rather than from a populated field on this task.
   - Mark those two fields `present: false` in `field_mapping` (see step
     5) and write a one-line note recommending — not requiring — a second,
     epic-linked task be validated before relying on `epic_dev_time` or
     `parallel_epics` for this project. Do not block the flow on getting
     that second example; record the gap and move on.

5. **Derive and persist the `field_mapping` artifact.** Resolve, from the
   validated task (and, where noted above, from field metadata):
   - `story_points`: custom field ID + whether populated on this task
   - `sprint`: custom field ID + whether populated
   - `epic_link`: `mode` (`parent_field` for team-managed native Parent, or
     `epic_link_field` for the company-managed `Epic Link` custom field) +
     the field ID when it's the custom-field mode
   - `initiative_link`: custom field ID + whether populated (or absent
     entirely if the tier has no Advanced Roadmaps hierarchy)
   - `project_type`: `team_managed` or `company_managed` — read off which
     epic-link mode was actually present, not asked as a separate question
   - `has_initiative_hierarchy`: `false` when there is no initiative-level
     field on this site/tier at all (not merely unpopulated on this task)

   ```yaml
   field_mapping:
     jira_instance: your-org.atlassian.net
     project_type: team_managed          # team_managed | company_managed
     has_initiative_hierarchy: false     # false when no Advanced Roadmaps tier
     validated_against_task: TEAMPRJ-1042
     validated_at: 2026-09-15
     fields:
       story_points:
         field_id: customfield_10028
         present: true
       sprint:
         field_id: customfield_10020
         present: true
       epic_link:
         mode: parent_field              # parent_field | epic_link_field
         field_id: null                  # set only when mode = epic_link_field
         present: false
       initiative_link:
         field_id: null
         present: false
     notes: |
       Validated task TEAMPRJ-1042 is a solo task (no parent epic) — epic_link
       and initiative_link derived from project field metadata, not from a
       populated example. Recommend validating a second, epic-linked task
       before relying on epic_dev_time or parallel_epics for this project.
   ```

   This shape is derived directly from the field list in this task's own
   spec (story points, sprint, epic link vs. native parent, initiative
   link, `project_type`, `has_initiative_hierarchy`). A repo-wide
   `jira_maturity_engine_ingest.schema.json` was referenced as the target
   shape but does not exist anywhere in this environment as of this
   change — reconcile this shape against that schema if/when it's added,
   rather than treating this as final.

   **Persistence:** written into `org-config.md` as new top-level
   `data_source` and `field_mapping` blocks, under the same `config_version`
   as the threshold and leading-indicator blocks — see
   [output-generator.md](output-generator.md) File 1. This mirrors how
   `team_overrides` is already declared in
   `maturity-core/schemas/org_config.schema.json`: a forward-declared,
   schema-validated shape living inside the one frozen/versioned org config
   file, not a separate sibling file with its own version number to keep in
   sync. `org_config.schema.json` has been extended with `data_source` and
   `field_mapping` properties accordingly. As with `team_overrides`, this is
   forward-declared: `run_analysis.py` does not read `field_mapping` yet
   (it still only consumes `jira_db.json`/CSV) — recording it now is what
   makes a later live-ingest pipeline able to consume a schema-validated,
   audited mapping instead of asking the user to redo this validation.

6. **Only after the user confirms the single-task structure is correct**,
   ask which projects/boards and what time window to pull for the full
   extraction. Record the answer but do not trigger the pull — a bulk
   extraction is out of scope for onboarding regardless of what the user
   says here; it exists so the choice is captured and auditable, same as
   every other onboarding decision.

---

## Both branches converge here

By the end of this step, whichever branch ran, you have one concrete,
fully-linked example on screen (task → epic → initiative-if-any → sprint,
plus changelog for Branch B) and — for Branch B — a validated
`field_mapping`. Carry the example into Step 3 (rule calibration): every
KPI and leading-indicator question there should refer back to it by name
rather than asking abstractly with nothing in front of the user.
