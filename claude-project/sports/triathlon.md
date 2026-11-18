# Sport Module: Triathlon & Multisport

Upload this file to your Claude Project Library alongside `endurance-methodology.md`, `swimming.md`, `cycling.md`, and `running.md` if you train for triathlon (Sprint, Olympic, 70.3, Ironman) or duathlon.

## Core Constraint: Three Sports, One Nervous System
The #1 mistake in triathlon planning is stacking three separate single-sport plans. The athlete recovers from **one combined systemic load** while absorbing **three very different local stress profiles**:
- **Swimming** (see `swimming.md`): minimal lower-body impact, high technical and shoulder demand; tolerates high frequency (2–4×/week) even when legs are tired.
- **Cycling** (see `cycling.md`): high metabolic load, low impact; the safest engine for building large aerobic volume and durability.
- **Running** (see `running.md`): high mechanical impact; must progress conservatively (`run_km` rules) even when overall CTL (driven by cycling) is high.

## Separate Thresholds by Discipline
Keep thresholds and zones strictly separate in intervals.icu:
- **Swimming**: **CSS (Critical Swim Speed)** in `min:sec/100m` (`coach_tools.py css`) — see `swimming.md`.
- **Cycling**: CP/W' and outdoor/indoor FTP (`coach_tools.py cp`) — see `cycling.md`.
- **Running**: CS/D', threshold pace (`coach_tools.py cs`), and LTHR (typically 5–10 bpm higher in running than cycling) — see `running.md`.

## Cross-Sport Load & Weekly Structure
- **Global intensity density**: count **hard days across all sports combined** (typically 2–3 key sessions/week total, *not* 2 per discipline). Example: 1 bike key session + 1 run key session + 1 swim threshold/technique session (lower systemic cost on legs).
- **Prioritize race limiters by distance**:
  - Sprint / Olympic: swim efficiency + bike/run threshold & VO2max + fast transitions.
  - 70.3 / Ironman: **smart bike pacing & durability** unlock the run off the bike; bike durability and on-bike fueling come first.
- **Sequencing**:
  - Avoid intense running the day after a heavy, leg-draining bike workout (unless a specific brick is planned).
  - Easy/technical swimming fits well the day after a heavy bike or run day.
  - Two-a-days: separate by as many hours as practical (AM/PM) and place the priority session first (unless doing an intentional bike → run brick).
- **Training camps (`camp` phase)**: lean on cycling and swimming volume for the extra hours, keeping running mileage increases conservative to avoid overuse injuries during camp.

## Brick Workouts (Bike → Run)
- **Purpose**: dial in proprioception, cadence, and pacing control during the first 10–20 min off the bike (classic error: going out far too fast).
- **Frequency**:
  - Base: unnecessary or rare (max once/month).
  - Build / Specialty: 1 brick every 1–2 weeks; **15–30 min of easy-to-race-pace running** right off the bike delivers almost all the neuromuscular adaptation without excessive injury risk. Avoid weekly long fatigued runs off the bike.
- **Fueling rehearsal**: in 70.3/Ironman specialty blocks, practice on-bike carbohydrate intake (building toward 60–90 g/h as tolerated) that leaves your stomach settled for the run.

## Environment & Logistics (Check at Intake & Brief)
- Pool length/schedule and open-water access, indoor trainer setup, safe brick run loop (or treadmill next to trainer), and weekly transition logistics.

## intervals.icu Workout Syntax
Follow each discipline's syntax module (`swimming.md` — remember `mtr`, never `m`! — `cycling.md`, `running.md`) and lint every workout with `coach_tools.py lint --type <sport>`.

## Triathlon-Specific Strength & Mobility
- Respect total training volume: 1–2 concise sessions (25–35 min) in base, 1 maintenance session in specialty.
- Blend hip/calf durability (running), lower-body force (cycling), and **rotator-cuff / scapular stability + core** (swimming & aero position).
