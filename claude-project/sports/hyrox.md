# Sport Module: HYROX & Hybrid Racing

Upload this file to your Claude Project Library alongside `endurance-methodology.md` and `running.md` if you train for HYROX (Open, Pro, Doubles, or Relay) or hybrid running/functional-fitness racing.

## Scientific Foundation (Evidence-Based Framing)
Early peer-reviewed data from a **simulated HYROX race on 11 amateur athletes** (Brandt et al., *Frontiers in Physiology* 2025; low evidence level due to small sample size and simulated setting, to be updated as larger competition studies emerge) frames HYROX as an **interval-based endurance event under heavy localized muscular fatigue**, rather than a pure strength competition:
- **Time split (in that cohort)**: ~59% of total time (~51.2 min) was spent **running** (8 × 1 km) vs ~38% (~32.8 min) on the **8 functional stations** (+ Roxzone transitions, median total 86.5 min).
- **Physiological intensity**: ~80% of time was spent at *very hard* HR intensity and ~20% at *hard* intensity; blood lactate peaked higher on stations (median ~8.5 mmol/L, highest on Wall Balls) than on runs (~7.7 mmol/L).
- **Correlates of performance (small cohort)**: higher **VO2max** and **endurance training volume** correlated with faster finish times, whereas isolated grip strength or general resistance-training volume did not.
- **Concurrent training (Schumann et al., *Sports Med* 2022; moderate evidence)**: endurance training does not blunt maximal strength gains when sensibly programmed, but explosive power suffers if heavy strength and high-intensity endurance are stacked without spacing (aim for ≥ 3–6 h separation or separate days).

## Official Divisions & Station Standards
*(Sled Push and Sled Pull weights include the sled itself.)*

| Station | Work | Women Open | Men Open / Women Pro | Men Pro |
|---|---|---|---|---|
| 1. SkiErg | 1,000 m | Bodyweight | Bodyweight | Bodyweight |
| 2. Sled Push | 50 m (4 × 12.5 m) | 102 kg | 152 kg | 202 kg |
| 3. Sled Pull | 50 m (4 × 12.5 m) | 78 kg | 103 kg | 153 kg |
| 4. Burpee Broad Jumps | 80 m | Bodyweight | Bodyweight | Bodyweight |
| 5. Rowing (RowErg) | 1,000 m | Bodyweight | Bodyweight | Bodyweight |
| 6. Farmers Carry | 200 m | 2 × 16 kg | 2 × 24 kg | 2 × 32 kg |
| 7. Sandbag Lunges | 100 m | 10 kg | 20 kg | 30 kg |
| 8. Wall Balls | 100 reps | 4 kg (2.75 m) | 6 kg (W: 2.75 m / M: 3.05 m) | 9 kg (3.05 m) |

*(In Doubles, partners run all 8 × 1 km together and split station work—pacing prioritizes repeated high-intensity station surges and fast partner handoffs. In Relays, each athlete completes 2 × 1 km + 2 stations at near-5K/VO2max intensity.)*

## Critical intervals.icu Blind Spot: Local Muscular Fatigue
intervals.icu excels at tracking your running load, Concept2 ergs, CTL/ATL/TSB, and HRV/RHR—**but underestimates local muscular/neuromuscular load from heavy stations**.
- Heavy Sled Push/Pull, Sandbag Lunges, Farmers Carry, and Wall Balls cause substantial quad, posterior-chain, lower-back, and grip fatigue while generating relatively low HRSS/CTL points.
- **Rule**: never judge HYROX weekly stress from intervals.icu CTL/TSB alone. Always combine CTL/TSB with **session RPE × duration (sRPE)**, **local muscle soreness** (quads/lower back/calves), and the **global hard-day budget**.
- **Recovery spacing**: heavy sleds or lunges cause 48 h of quad fatigue (similar to steep trail descents)—never schedule VO2max track intervals or hard threshold runs the day after heavy lower-body station work.

## Programming & Periodization (Four Pillars)
Avoid the classic HYROX trap of doing maximal "Metcon / HYROX circuits" 4 times per week (high fatigue, poor aerobic progression, injury risk). Build across **four distinct pillars**:

1. **Aerobic & Threshold Running Engine (largest share of training time)**
   - Follow `running.md`: 70–80% easy aerobic running (Z1–Z2), threshold cruise intervals (developing lactate clearance at/near HYROX run pace), and phase-appropriate VO2max work. Guard single-session distance spikes (`longest_run_km` ≤ +10% vs prior 30-day max, Frandsen et al. *BJSM* 2025) alongside the weekly `run_km` heuristic.
2. **Erg Efficiency (SkiErg & RowErg)**
   - Sync Concept2 ErgData directly to intervals.icu (pace/500 m, watts, HR).
   - **Pacing discipline (coaching field heuristic)**: over-cooking 1,000 m SkiErg or RowErg by several seconds per 500 m saves very little time on the erg while disproportionately hurting subsequent runs. Target sustainable threshold/race-specific pacing (as a rough starting heuristic, ~2–5 s/500 m slower than 2k PR, smooth stroke rate, low tension—calibrate on simulations).
3. **Strength & Station Capacity (phased)**
   - *Base*: heavy foundational strength (squat/hinge/push/pull/loaded carry, 2×/week) + technical station mechanics at low fatigue (sled body angle, rope pull hip drive, burpee step-up rhythm, full-depth wall balls to avoid no-reps).
   - *Build*: transition to strength-endurance and race-weight (+10–20% overload on sleds for reserve) station sets under moderate fatigue.
   - *Specialty (6–8 weeks out)*: **Compromised Running** sessions (e.g. 4–6 × [station work + 1 km run at threshold/race pace]), Roxzone transition rehearsal, and **1–2 half-to-three-quarter simulations** (never run an all-out 100% full simulation within 3 weeks of race day).
4. **Taper (10–14 days for A-race)**
   - Drop heavy sleds, loaded lunges, and eccentric lower-body lifting **10–14 days out** so zero residual quad DOMS remains on race day. Keep short, sharp running + light erg/station touchpoints only in race week.

### Global Weekly Hard-Day Budget
Cap total high-stress sessions at **2–3/week across running + compromised running/stations + heavy lower-body strength combined** (e.g. Tue: threshold run; Thu: compromised running / stations; Sat: long easy run or specialty simulation; easy Z2 runs, erg aerobic work, and upper/core or mobility in between).

## Benchmarking, Analysis & Race Diagnostics
- **Running threshold**: Critical Speed (`coach_tools.py cs`) every 6–8 weeks (see `running.md`).
- **Erg benchmarks**: 1,000 m or 2,000 m SkiErg & RowErg time trials (or standardized 5 × 500 m @ fixed pace/HR).
- **HYROX simulation / race analysis**: run `coach_tools.py hyrox` on the 8 × 1 km run splits (+ station times, Roxzone, and fresh CS threshold pace) to quantify (using transparent coaching field heuristics, not peer-reviewed cutoffs):
  - exact **Run % vs Station % vs Roxzone %** breakdown;
  - **Run 1 over-pacing** (field heuristic: flag if Run 1 is > 10 s/km faster than Runs 2–8 mean);
  - **1st-half vs 2nd-half run decay** and **compromised-running penalty** vs fresh threshold pace;
  - **post-station fade hotspots** (typically Run 3 post-Sled Push, Run 5 post-Burpees, Run 8 post-Sandbag Lunges) and Roxzone share (field heuristic: > 8% flags easy transition savings).

## Gym Equipment & Substitutions (Check at Intake & Brief)
Always clarify equipment access during intake and block briefs:
- **Full HYROX / functional gym**: real sled + turf, Concept2 SkiErg & RowErg, competition sandbags, kettlebells, wall balls + target.
- **Standard commercial gym (substitutions)**:
  - *Sled Push* → heavy deadmill (unpowered treadmill) pushes, heavy leg press / Bulgarian split squats + short uphill sprints;
  - *Sled Pull* → heavy seated/standing cable rope pulls, chest-supported rows, heavy RDLs;
  - *SkiErg / RowErg* → Concept2 if available, otherwise assault/air bike or battle ropes + incline treadmill for upper/aerobic transfer;
  - *Sandbag Lunges / Wall Balls* → dumbbell/barbell walking lunges, goblet/DB thrusters.
  - Recommend **2–4 drop-in sessions at a HYROX-equipped gym** 4–8 weeks before race day to dial in real sled friction, wall-ball target height, and transitions.

## HYROX-Specific Fueling & Hydration
Because HYROX runs 55–95 min at ~80% very hard HR with heavy glycolytic demand:
- **Pre-race**: 24–36 h moderate-high carbohydrate intake + low-fiber, low-fat carb meal 2–3 h before wave start.
- **During race**: **30–60 g carbs** total (e.g. 1 isotonic gel before Sled Pull and/or 1 after RowErg, plus small water sips at aid stations; even a carb mouth rinse helps on sub-65 min races). Practice gels during compromised-running sessions so your stomach handles carbs at high HR.
- **Daily fueling**: hybrid athletes burn high glycogen across running + strength—fuel generously around double days and compromised-running workouts to avoid REDs.

## intervals.icu Workout Syntax & Logging
- **Pure running workouts**: event type `Run`, follow `running.md`, lint with `coach_tools.py lint --type running`.
- **Concept2 SkiErg / RowErg**: event type `Rowing` or `Workout`, specify target pace (`/500m`) or `% LTHR` and stroke rate in `📋 CUES`.
- **Stations, Strength & Compromised-Running Hybrid sessions**: event type `WeightTraining` or `Workout` with 🎯 / 🍌 / 📋 header, one block/exercise per line **without leading dashes** (explicit weights, division standard, reps/distance, RIR/RPE, and target compromised run pace), linted with `coach_tools.py lint --type hyrox`.
- Example hybrid workout:
  ```text
  🎯 GOAL: compromised running & lactate clearance at Men Open race weights

  🍌 FUELING: Before: low-fiber carb meal 2h prior
  During: 1 isotonic gel at mid-session + electrolytes
  After: carbs + protein within 1h

  📋 CUES: hold controlled threshold pace on runs, smooth transitions (< 30s), RPE 8/10

  Warmup
  12m easy jog Z1-Z2 + dynamic hip/ankle mobility + 2x 100m strides

  Main set (4 rounds, continuous)
  500m SkiErg @ race pace (RPE 7)
  1km Run @ 95-100% threshold pace
  25m Sled Push @ 152 kg (steady drive, short breaks)
  1km Run @ 95-100% threshold pace (settle breathing in first 200m)

  Cooldown
  10m easy walk/jog + quad & hip flexor mobility
  ```
