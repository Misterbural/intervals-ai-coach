---
name: coach-block-review
description: "Closes an endurance block: threshold tests (CP/CS/CSS), benchmarks, durability, candid block verdict, journal entry, and quarterly dashboard if due."
---
# End-of-Block Review

First read the block's opening entry in `coaching-journal.md`, `endurance-methodology.md` (Data, Session Analysis, Evaluating Progression), and the active sport module(s). Verify data quality before drawing strong conclusions.

1. **Threshold tests** (if scheduled): run the sport-appropriate calculator and show the math:
   - Cycling: `coach_tools.py cp` (3-min + 12-min tests, noting test location and indoor/outdoor offset);
   - Running: `coach_tools.py cs` (two maximal efforts → threshold pace & D');
   - Swimming: `coach_tools.py css` (400 m + 200 m → CSS pace per 100 m);
   - HYROX: `coach_tools.py hyrox` on simulation or race splits (8 × 1 km runs + optional stations & Roxzone → run vs station share, Run 1 over-pacing, compromised-running penalty vs CS).
2. **Benchmark sessions**: review trends in RPE, HR at fixed output (or Efficiency Factor `EF`), decoupling, and next-day recovery. Apply the anti-false-positive rule: call progression only when ≥ 2 indicators move together across ≥ 2 occurrences.
3. **Passive indicators & durability**: review power/pace curves (`coach_tools.py progression`), eFTP/estimated thresholds, durability (`coach_tools.py durability` on fatigued curves in cycling, or late-long-run fade/VAM in running/trail), and CTL. Keep indoor/outdoor and flat/hilly comparisons separate. Identify the block's primary limiter.
4. **Threshold update**: propose numeric updates only when backed by a test or clear multi-indicator convergence. Once approved, apply the new settings directly in intervals.icu via MCP and remind the athlete to sync third-party apps (e.g. Zwift, watch) if needed.
5. **Candid block verdict**: verdict first vs block objective and validated plan; clearly distinguish measured facts from interpretations.
6. **Journal entry**: complete the block's entry in `coaching-journal.md` (What was completed / Tests & numbers / What worked / What did not work / Decisions for next block). Present for review; save once approved (or output full file to upload).
7. **Quarterly dashboard** (if ≥ 3 months since the last one): thresholds by sport, benchmark trends, compliance, consistency, health/injuries, CTL, and a blunt verdict on whether the coaching system is delivering results.
8. Offer to launch `coach-block-brief` for the next block.
