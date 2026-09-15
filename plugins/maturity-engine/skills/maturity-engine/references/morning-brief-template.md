# Morning Brief Template
definition_version: morning-brief-template-v1

A terse, multi-team status scan — mode 2 of the entry menu (see
`../SKILL.md` Step 0). Optimized for "what needs my attention right now,"
not for depth. Depth lives in §3/§5/§6 of `output-template.md`; a CTO who
wants it gets there via this brief's Next Step.

---

## Scope

The latest closed sprint per team, computed via the shared runner's
`--window` mode (`build_sprint_window_reports`) so every team's current
sprint state — `future`, `active`, or `closed` — is visible in one pass.

A team with **no closed sprint** (only `future`/`active`) is **included,
not skipped**, shown with a 🚧 marker and a leading-indicator preview
(`mid_sprint_drift_check` / `sprint_start_risk_flag`) instead of a final
score, since there isn't one yet.

---

## Shape

*One line per team. No interpretation. No per-team Assumptions & Limitations
or Next Step section — those are §3/§5/§6 things, not this one's.*

```
🔴 TEAMPRJ-000005 — 20/100 — WIP_DEATH_SPIRAL, ROADMAP_DRIFT
🟡 TEAMPRJ-000017 — 50/100 — LOW_SPRINT_COMPLETION
🟢 TEAMPRJ-000048 — 80/100 — LOW_ROADMAP_CONTRIBUTION
🚧 TEAMPRJ-000014 — sprint open (SPRINT-000117), no risk flagged yet — final score after close
```

- Band emoji (🔴/🟡/🟢) and pattern IDs follow the same fixed vocabulary as
  `output-template.md` §1 — no new glyphs invented here.
- A 🚧 team shows a leading-indicator preview instead of pattern IDs when
  one is flagged (e.g. `🚧 TEAMPRJ-000022 — sprint open (SPRINT-000203),
  👀 EPIC_SPRAWL (planning) — final score after close`), otherwise the
  "no risk flagged yet" wording above.
- Sort: 🔴 first, then 🟡, then 🟢, then 🚧 — worst news at the top, exactly
  like §6 Team Comparison's lowest-first ranking.

---

## Summary block

*One block at the end, across all teams — never repeated per team:*

- **"[N] teams need attention (score < 40): [team list]"**
- Up to 3–5 top-priority items: teams with a compound pattern, or a
  newly-flagged `concern`-level leading indicator
- If any team is 🚧: **one explicit sentence**, always, even though the
  per-team 🚧 marker already implies it — e.g. "3 teams still have an open
  sprint — their numbers above are provisional, not a final score."

---

## Explicitly excluded from this mode

- Verdict sentences (§3's "one-sentence verdict, human voice")
- The full KPI-facts table (§3 📊)
- Intervention catalog cards (§3 🛠️ / §4 🌱)
- A repeated 📝 Assumptions & Limitations section per team — at most one
  shared line across the whole brief, never one per team

If the CTO wants any of that for a specific team, that's what Next Step
routes to (§3 Full Sprint Analysis) — not something this mode inlines.

---

## 👉 Next Step

*Same rule as every other structure (see `next-step-routing.md`): exactly
one question — the single most important follow-up given what the brief
actually shows, e.g. the worst-scoring team, or a pattern shared by several
teams. Never more than one question, never an ungrounded one.*

> [grounding line: the specific team/score/pattern from the brief above]
>
> **[the question]?**

Example:

> 🔴 TEAMPRJ-000005 is the lowest score this brief at `20/100`, with the compound pattern `WIP_DEATH_SPIRAL`.
>
> **Run a Full Sprint Analysis on TEAMPRJ-000005?**
