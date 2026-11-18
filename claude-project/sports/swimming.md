# Sport Module: Swimming (Pool & Open Water)

Upload this file to your Claude Project Library alongside `endurance-methodology.md` if you train swimming (pool or open water) or triathlon.

## Thresholds & Testing (CSS — Critical Swim Speed)
- **Reference**: **CSS** in `min:sec/100m`, stored as Swimming Threshold Pace in intervals.icu.
- **Recommended protocol**: a 400 m maximal time trial followed by 5–10 min of easy recovery, then a 200 m maximal time trial in the same session (after a thorough warmup). Compute with `coach_tools.py css --t400 ... --t200 ...`.
- **Pool length**: always note whether tests and workouts are in a **25 m (SCM)**, **25 yd (SCY)**, or **50 m (LCM)** pool, as turns significantly change 100 m pace.
- **Benchmark session**: standardized repeatable set (e.g. 5 × 200 m on fixed send-off at steady RPE 6–7, or 1,000 m steady aerobic swim) in the same pool length; track pace/100 m, stroke count/SWOLF, and RPE.

## Technique, Volume & Shoulder Load Management
Unlike cycling or running, **hydrodynamic drag dominates energy cost** in swimming—technique gains often beat pure fitness gains.
- **Technique first**: include focused drills (catch-up, fingertip drag, sculling, single-arm, kick balance) during warmup when fresh, never tacked onto the end when fatigued.
- **Shoulder protection**:
  - Increase weekly swim distance gradually (generally ≤ +15–20% over the previous 3-week max when rebuilding).
  - Introduce **hand paddles** progressively (small volume at first; stop immediately at any anterior shoulder pinch or impingement).
  - Balance high-volume freestyle with backstroke/easy pull cooldowns and regular scapular/rotator-cuff prehab.
- **Training toys** (pull buoy, fins, paddles, center snorkel): use intentionally for specific cues (body position, ankle mobility, catch feel, force), not as permanent crutches.

## Open-Water Preparation (if applicable)
- Practice **sighting** (crocodile eyes without lifting the chest), **bilateral breathing**, and **pace changes** (buoy turns, race starts) in the pool 6–8 weeks out.
- Rehearse wetsuit fit/shoulder mobility, cold-water acclimation, and drafting in real open water whenever safely available (never swim open water alone; use a tow buoy).

## Environment & Logistics (Check at Intake & Brief)
- Pool length (25 m / 50 m), lane availability, and fixed club/masters sessions.
- Available swim gear (pull buoy, paddles, fins, kickboard, snorkel, wetsuit).
- Open-water access and water temperature (if targeting open-water races or triathlon).

## intervals.icu Workout Syntax (Swimming)
- Event type: `Swim`.
- **Critical intervals.icu rule**: always write swim distances with **`mtr`** (e.g. `400mtr`, `100mtr`), **never `400m`** (which intervals.icu parses as 400 minutes!). `coach_tools.py lint --type swimming` catches this automatically.
- Intensities: `% Pace` (% of CSS), **explicit** pace/HR zones (`Z1 Pace`–`Z5 Pace` or `Z1 HR`), or `rest` for interval recoveries.
- Example steps:
  ```text
  Warmup
  - 300mtr Z1 Pace

  Drills 4x
  - 50mtr Z2 Pace
  - 15s rest

  Main set 6x
  - 200mtr 100% Pace
  - 30s rest

  Cooldown
  - 200mtr Z1 Pace
  ```

## Swimming-Specific Fueling & Hydration
In addition to the core carbohydrate tiers in `endurance-methodology.md`:
- **Hidden sweat losses**: swimmers still sweat significantly in warm pools without feeling it. Keep a bottle on the pool deck for every session; use electrolytes + 30–60 g/h of liquid carbs for sessions > 60–75 min or high-intensity sets.
- **Horizontal posture & reflux**: avoid heavy, fatty, or very large meals within 1.5–2 h before swimming; for early-morning swims, a small fast-digesting snack (e.g. banana, toast, or sports drink) works better than swimming fasted on hard sets.
- **Open-water events**: practice feeding from a kayak/pontoon or carrying gels in a wetsuit sleeve if racing ≥ 5 km / 1.5 h+.

## Swimming-Specific Strength & Mobility
- Priority: rotator cuff & scapular stabilizers (face pulls, external rotations, Y-T-W raises), lats/pulling strength, core anti-rotation.
- Mobility: thoracic extension, shoulder flexion/internal-external rotation, ankle plantarflexion.
