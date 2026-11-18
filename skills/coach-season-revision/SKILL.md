---
name: coach-season-revision
description: "Revises the endurance season when a goal is added, changed, or dropped: feasibility check, reverse-planned blocks, taper, transition, and season-goals.md + ATP update."
---
# Season Revision

When to use: a race goal is added, rescheduled, or dropped, or a major disruption changes the season (new injury, long layoff, lasting schedule change). This workflow sets the macro-plan; `coach-block-brief` builds each individual block afterward.

1. Read `season-goals.md`, `athlete-profile.md`, `coaching-journal.md`, `science-watch.md`, `endurance-methodology.md`, and the active sport module(s).
2. Check current status on intervals.icu: CTL, ATL, TSB, 6-week trend by sport, benchmark sessions, latest threshold tests, and 7-day HRV/RHR.
3. Clarify the goal in short rounds (3–5 questions per message): event, date, sport/distance/elevation/format, expected conditions (heat, night, altitude, open water), success criteria, secondary B/C events, planned training camps (`camp` weeks), and known constraints until race day.
4. Feasibility check with real numbers: weeks available, starting CTL vs target CTL using CTL ramp guardrails from `endurance-methodology.md` (and mechanical mileage/vert caps from `running.md`/`trail.md` where applicable). If the target is unrealistic for that date, state it candidly and propose concrete alternatives (adjusted target, different distance, later date).
5. Reverse-plan the season from race day: sequential blocks (return if needed, base, build, specialty, taper), duration and focus of each; threshold tests and benchmark sessions; gut training, bricks, or vertical/terrain specificity if required; and a **planned active post-race transition** (never an unplanned total stop). Project race-day TSB with `coach_tools.py project` and sanity-check the macro-plan with `coach_tools.py check-plan`.
6. Current block decision: clearly recommend whether to finish it as planned, adjust it, or stop it immediately, and explain why.
7. Only after approval: output the updated `season-goals.md`; create/update the race event in intervals.icu (`RACE_A`, `RACE_B`, or `RACE_C`) and update planned weekly loads in the ATP; immediately read back the written race event and ATP range to confirm they saved cleanly; summarize the verified changes; draft a "Season Revision" entry for `coaching-journal.md`.
8. Offer to launch `coach-block-brief` for the next block.
