# Sport Module: Triathlon & Multisport

Upload this file to your Claude Project Library alongside `endurance-methodology.md`, `cycling.md`, and `running.md` if you train for triathlon (Sprint, Olympic, 70.3, Ironman) or duathlon.

## Core Constraint: Three Sports, One Nervous System
The #1 mistake in triathlon planning is stacking three separate single-sport plans. The athlete recovers from **one combined systemic load** while absorbing **three very different local stress profiles**:
- **Swimming**: minimal lower-body impact, high technical and shoulder demand; tolerates high frequency (2–4×/week) even when legs are tired.
- **Cycling**: high metabolic load, low impact; the safest engine for building large aerobic volume and durability.
- **Running**: high mechanical impact; must progress conservatively (`run_km` rules in `running.md`) even when overall CTL (driven by cycling) is high.

## Separate Thresholds by Discipline
Keep thresholds and zones strictly separate in intervals.icu:
- **Swimming**: **CSS (Critical Swim Speed)** in `min:sec/100m`, measured via a 400 m + 200 m time trial in one session (full warmup, 5–10 min easy recovery between efforts) with `coach_tools.py css --t400 ... --t200 ...`.
- **Cycling**: CP/W' and outdoor/indoor FTP — see `cycling.md`.
- **Running**: CS/D', threshold pace, and LTHR (typically 5–10 bpm higher in running than cycling) — see `running.md`.

## Cross-Sport Load & Weekly Structure
- **Global intensity density**: count **hard days across all sports combined** (typically 2–3 key sessions/week total, *not* 2 per discipline). Example: 1 bike key session + 1 run key session + 1 swim threshold/technique session (lower systemic cost on legs).
- **Prioritize race limiters by distance**:
  - Sprint / Olympic: swim efficiency + bike/run threshold & VO2max + fast transitions.
  - 70.3 / Ironman: **smart bike pacing & durability** unlock the run off the bike; bike durability and on-bike fueling come first.
- **Sequencing**:
  - Avoid intense running the day after a heavy, leg-draining bike workout (unless a specific brick is planned).
  - Easy/technical swimming fits well the day after a heavy bike or run day.
  - Two-a-days: separate by as many hours as practical (AM/PM) and place the priority session first (unless doing an intentional bike → run brick).

## Brick Workouts (Bike → Run)
- **Purpose**: dial in proprioception, cadence, and pacing control during the first 10–20 min off the bike (classic error: going out far too fast).
- **Frequency**:
  - Base: unnecessary or rare (max once/month).
  - Build / Specialty: 1 brick every 1–2 weeks; **15–30 min of easy-to-race-pace running** right off the bike delivers almost all the neuromuscular adaptation without excessive injury risk. Avoid weekly long fatigued runs off the bike.
- **Fueling rehearsal**: in 70.3/Ironman specialty blocks, practice on-bike carbohydrate intake (building toward 60–90 g/h as tolerated) that leaves your stomach settled for the run.

## intervals.icu Workout Syntax (Swimming)
- Event type: `Swim`.
- **Critical intervals.icu gotcha**: write distances with **`mtr`** (e.g. `400mtr`, `100mtr`), **never `400m`** (which intervals.icu parses as 400 minutes!). `coach_tools.py lint --type swimming` catches this automatically.
- Intensities: `% Pace` (% of CSS), `Z1`–`Z5`, or `rest` for recovery intervals.
- Example steps:
  ```text
  Warmup
  - 300mtr Z1

  Drills 4x
  - 50mtr Z2
  - 15s rest

  Main set 6x
  - 200mtr 100% Pace
  - 30s rest

  Cooldown
  - 200mtr Z1
  ```

## Triathlon-Specific Strength & Mobility
- Respect total training volume: 1–2 concise sessions (25–35 min) in base, 1 maintenance session in specialty.
- Blend hip/calf durability (running), lower-body force (cycling), and **rotator-cuff / scapular stability + core** (swimming & aero position).
