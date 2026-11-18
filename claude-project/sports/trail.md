# Sport Module: Trail & Ultra-Trail Running

Upload this file to your Claude Project Library alongside `endurance-methodology.md` (and `running.md` if you also train on roads).

## Core Trail Constraints
In trail running, distance alone misses most of the stress: **vertical gain/loss, technical terrain, and eccentric quad breakdown on descents** often outweigh pure cardiovascular strain.
- **Track two volume dimensions**: **weekly duration** (more meaningful than km on mountain terrain) and **weekly vertical gain (`vert_m`)** (and descent).
- **Vertical gain progression**: avoid increasing weekly vertical gain by more than **20–25%** above the highest of the previous 3 weeks (`vert_m` in `coach_tools.py check-plan`).
- **Pacing vs terrain**: raw pace breaks down on trails. Prescribe by **HR (`% LTHR`)** and **RPE**; analyze with intervals.icu's **Grade Adjusted Pace (GAP)**.
- **Eccentric load (descents)**: long or fast descents cause delayed onset muscle soreness (DOMS) for 48–72 h even at low HR. Never schedule an intense interval session or heavy lower-body strength workout within 48 h after a big descent session.

## Trail-Specific Training
- **Power hiking**: on steep climbs (> 12–15% grade), fast hiking with or without poles is often more economical than running. Train it deliberately in Z2–Z3.
- **Poles**: if allowed and useful for your target race, introduce them early in the build phase on long outings to condition upper-body endurance and stow/deploy transitions.
- **Back-to-back long weekends** (long trail / ultra goals only, durable athletes): pair two moderate-to-long outings on Saturday + Sunday to train durability under muscular fatigue without exceeding 4–5 h in a single outing (lower injury risk than a single 7–8 h run). Always follow with 2–3 very easy days or a recovery week.
- **Terrain specificity**: 6–8 weeks out from an A-race, align training terrain with the race's vertical-to-distance ratio (e.g. 50–70 m vert/km for alpine races).
- **Cross-training (cycling/indoor trainer)**: high-ROI tool in trail running to build aerobic volume and durability without hammering legs with impact.

## Vertical Gain Access & Flatlander Strategies (Check at Intake & Brief)
Many trail runners do not live next to mountains. Always clarify local vertical access during intake and block briefs:
- **Daily trail/mountain access**: spread vertical gain across 2–4 sessions/week and build terrain-specific descending resilience progressively.
- **Weekend-only vertical access**: keep weekday runs focused on flat aerobic volume, threshold/VO2max, and eccentric strength; concentrate vertical gain and technical descending on weekend long runs.
- **Flatlander (no nearby hills)**: do *not* prescribe unreachable weekly D+ targets. Combine:
  - incline treadmill power-hiking (10–15% grade), stadium/building stairs, or repeated short local hills/parking ramps for climbing economy;
  - targeted **eccentric quad strength** (slow-tempo split squats, step-downs, lunges) to compensate for missing downhill volume (note: incline treadmill alone builds climbing but provides *zero* eccentric downhill conditioning);
  - occasional **mountain weekends or planned training camps (`camp` phase)** 4–10 weeks before an A-race to expose legs to real descents and technical terrain.

## Thresholds, Benchmarks & Progression
- **Threshold test**: run on flat ground (CS/D' protocol in `running.md` with `coach_tools.py cs`) or track a standardized steady climb (e.g. 15–20 min on the same gradient → track vertical speed VAM in `m/h` and average HR).
- **Benchmark sessions**:
  - 1 flat benchmark run (HR at fixed pace, decoupling);
  - 1 repeatable steady climb (same hill, same HR/RPE cap → track time or VAM in `m/h`).

## Fueling & Hydration on Trails
- As duration stretches (> 3 h) and intensity moderates, **gastrointestinal tolerance under mechanical jostling** (descents, heat, altitude) becomes a primary limiter.
- **Mandatory gut training** during specific long runs: build progressively toward 60–90 g/h using your actual race pack, flasks, drink mix, gels, and savory/solid options for ultras.
- **Sodium & self-sufficiency**: plan fluid and electrolyte capacity around aid-station spacing and expected weather/altitude.

## intervals.icu Workout Syntax (Trail)
- Event type: `TrailRun` (or `Run` if your watch syncs everything as `Run`).
- Prefer **duration + HR (`% LTHR` or `Z1–Z5`)** over raw pace, and specify vertical gain target and descent/pole cues in `📋 CUES`.
- Lint before writing: `coach_tools.py lint --type trail --expected-duration <min>`.
- Example steps:
  ```text
  Warmup
  - 20m Z1-Z2

  Sustained climbs 4x
  - 6m 85-92% LTHR
  - 4m Z1

  Cooldown
  - 15m Z1
  ```

## Trail-Specific Strength & Mobility
- Top priority: **eccentric quad resilience** (walking lunges, slow-eccentric 3–4 s Bulgarian split squats, controlled step-downs), **calves/ankles** (force + proprioception), **glutes**, and **core** (especially with pack/poles).
- Drop heavy eccentric strength work 10–14 days before an A-race so zero residual muscle soreness remains on race day.
