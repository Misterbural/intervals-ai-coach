---
name: coach-weekly-review
description: "Sunday endurance review: analyzes the completed week on intervals.icu (load, compliance, HRV, RPE), writes next week from the block plan, plus monthly critical self-review."
---
# Weekly Review

Principle: the validated block plan ("Block Opening" entry in `coaching-journal.md` and planned ATP loads) sets the target; each Sunday you analyze actual execution and write the upcoming week's workouts accordingly.

1. Read the active block plan from `coaching-journal.md` and planned ATP loads on intervals.icu. Locate where the upcoming week sits in the block.
2. Pull the completed week from intervals.icu: planned vs actual, compliance, load (plus HR-based load HRSS if thresholds are uncalibrated), CTL/ATL/TSB, 7-day HRV/RHR (`coach_tools.py wellness`), sleep, RPE/notes, and any benchmark sessions. Check data quality first. Compute Foster monotony, strain, and consecutive hard days with `coach_tools.py monotony`; analyze durability on the long session per `endurance-methodology.md` (and km/vert mechanical trends if running/trail).
3. Ask for overall subjective feel, any soreness/pain, and schedule/constraints (or optional races) for the upcoming week.
4. Check all guardrails and adaptation criteria from `endurance-methodology.md` and active sport modules.
5. Deliver a concise 5–8 line review, **verdict first**: key supporting facts, main limiter or risk, what worked, what did not, and what changes next week.
6. Propose the upcoming week in a table (day, sport, workout title, duration, goal, planned load) grounded in the block plan. Verify totals with `coach_tools.py rebalance` (within ±5% of target load and duration, or explain any deliberate deviation). Key sessions progress by one variable vs the previous load week (unless recovery week or amber/red override; repeat poorly executed key sessions unchanged). Explain any deviation from the block plan, and propose ATP updates if downstream weeks are affected.
7. Only after explicit approval: lint every workout with `coach_tools.py lint --type <sport> --expected-duration <min>`, write the upcoming week to intervals.icu per "Writing to intervals.icu", update the ATP if approved, and summarize created/updated events (date + title).
8. **First Sunday of the month — Critical Self-Review**: critique your own coaching plan from the past month. What was weak, poorly justified, or overly cautious/aggressive? Which assumptions did actual data contradict? What would a demanding human coach change? End with concrete adjustments and propose an entry for `coaching-journal.md`.
