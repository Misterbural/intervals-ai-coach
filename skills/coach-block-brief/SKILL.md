---
name: coach-block-brief
description: "Builds an endurance training block: science watch if due, brief (schedule, constraints, volume), week-by-week plan, ATP loads, and week 1 workouts written to intervals.icu."
---
# Block Brief & Construction

Principle: the entire block is designed upfront (structure, key sessions, weekly target loads in the ATP), but **only Week 1 workouts are written to the calendar**. Subsequent weeks are written each Sunday by `coach-weekly-review`, adapted to actual training response.

## 1. Current Status
- Read `season-goals.md`, the latest entry in `coaching-journal.md`, `science-watch.md`, `endurance-methodology.md`, and the active sport module(s).
- Pull from intervals.icu: CTL, ATL, TSB, 7-day HRV/RHR, prior block compliance, and actual average weekly load over the last 4 weeks (plus weekly km / vertical gain if running/trail). Compare external load vs HR-based load (HRSS) if thresholds are uncalibrated.
- Ask for upcoming on-call rotations, travel, races, **planned training camps (`camp` weeks)**, and schedule or terrain constraints across the block.

## 2. Science Watch (when due)
- Run a targeted literature check if: (a) `science-watch.md` is still on baseline v0, (b) it has been more than 3–6 months since the last full review, or (c) the athlete is entering a new sport/event modality. Otherwise, briefly confirm existing benchmarks remain current.
- When reviewing literature (meta-analyses, reviews, consensus from the last 2–3 years): state evidence level, what changed since the last watch, and concrete impact on the block. Never overhaul the method on a single isolated study; flag papers where only the abstract was read.
- Propose updated `science-watch.md` (and `endurance-methodology.md` / sport module only if a benchmark changes).

## 3. Block Brief
Ask any missing questions, then present the brief for validation:
- place in the season (target race or general development) and primary objective of the block;
- week-by-week availability and known constraints (aligning recovery weeks with heavy work/on-call weeks where possible);
- target weekly volume, load (and km/vert by sport if applicable), and starting readiness;
- lessons carried over from the previous block;
- end-of-block tests planned (if any).

## 4. Block Plan
Build per `endurance-methodology.md` and active sport modules, then present clearly week-by-week for validation:
- weekly targets computed with `coach_tools.py targets` (using `--camp-weeks` if a planned training camp falls in this block) in a summary table: phase (`load`, `camp`, or `recovery`), target load with `▇` bar, hours, sessions, delta %, projected CTL & TSB;
- CTL/TSB targets, zone distribution, max hard days per week (across all sports combined in multisport);
- key sessions each week with rationale and progression (one variable at a time);
- strength and mobility placement;
- 2–3 standardized benchmark sessions and which weeks they occur;
- run `coach_tools.py check-plan` and resolve any failures (discuss warnings);
- explicit adaptation criteria (what triggers lightening, shifting, or progressing faster).
If the athlete modifies the plan, show the impact on targets before updating.

## 5. Writing to intervals.icu
Only after explicit approval:
- write planned weekly loads for the whole block to the ATP;
- check the MCP server's workout syntax resource;
- validate Week 1 with `coach_tools.py rebalance` (±5% of target load and duration, adjusting an easy session only) and lint every single workout with `coach_tools.py lint --type <sport> --expected-duration <min>`;
- write Week 1 workouts only, following "Writing to intervals.icu" (read range first, no duplicates, leave unrelated events untouched), using the clean 🎯 / 🍌 / 📋 header format, `VirtualRide` for indoor cycling, `mtr` for swimming distances, explicit `HR`/`Pace` on run/trail/swim zones, and separate `WeightTraining` events for strength;
- immediately read back the written Week 1 range from intervals.icu to verify stored dates, parsed durations/loads, and absence of duplicates, then summarize the verified events (date + title);
- propose the "Block Opening" entry for `coaching-journal.md` containing the validated week-by-week plan (which `coach-weekly-review` will follow each Sunday).
