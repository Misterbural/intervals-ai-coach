# Sport Module: Running (Road & Track)

Upload this file to your Claude Project Library alongside `endurance-methodology.md` if you train road or track running (5K, 10K, half marathon, marathon).

## Core Constraint: Mechanical Impact Load
Unlike cycling or swimming, running subjects tendons, bones, and muscles to repetitive ground impact. **Aerobic fitness often outpaces musculoskeletal tissue tolerance**—especially during a return to running or for cyclists crossing over.
- **Prioritize mileage progression caps**: avoid increasing weekly running distance (`run_km`) by more than **10–15%** above the highest of the previous 3 weeks (`coach_tools.py check-plan`).
- **CTL ramp**: cap at **+3 to +5 pts/week** in pure running (lower than cycling).
- **Frequency before length**: when building volume safely, add a short easy run before abruptly extending the long run.
- **Hard days**: cap at **2 quality sessions/week** for most runners (3 only for high-volume, experienced athletes with stable recovery), never back-to-back.
- **Mechanical red flags**: localized tendon pain (Achilles, patellar, IT band, plantar fascia) or bone pain (shin, metatarsal) that worsens during warmup or lingers the next morning → treat immediately as **Red** (rest or non-impact cross-training; medical/physio review if persistent).

## Thresholds & Testing (Critical Speed CS / D', Threshold Pace & LTHR)
- **Primary references**: threshold pace (`min:sec/km`) and lactate threshold HR (`LTHR`) in intervals.icu; running power (e.g. Stryd) optionally if used consistently.
- **Recommended protocol — Critical Speed (CS & D')**: two maximal efforts on flat ground/track on separate days (e.g. 3 min + 12 min, 1,000 m + 3,000 m, or recent 5K + 10K races). Compute with `coach_tools.py cs --d1 ... --t1 ... --d2 ... --t2 ...`.
- **Return from layoff or beginner**: wait 6–8 pain-free weeks before maximal testing; guide early training by conversational feel and HR (`% LTHR`).
- **Long run guidelines**:
  - Half marathon: peak long run ~1 h 45 – 2 h (18–22 km depending on speed), 2–3 weeks out.
  - Marathon: cap long runs around **2.5–3 h max** (30–34 km depending on pace), 3–4 weeks out; beyond 3 h on asphalt, mechanical breakdown typically outweighs marginal aerobic gains.

## Intensity Distribution & Key Sessions
- **Easy aerobic running (Z1–Z2)**: 75–85% of total volume, genuinely easy (conversational effort, low HR). Classic mistake: running easy days too fast in the "gray zone".
- **Phase emphasis**:
  - Base: easy mileage, strides (6–8 × 15–20 s relaxed with full recovery), steady tempo, short hill sprints (low-impact specific strength).
  - Build: threshold cruise intervals (e.g. 3 × 8–10 min at 95–100% threshold pace), sustained tempo, VO2max (e.g. 5 × 3 min or 10 × 400 m).
  - Specialty: race-pace blocks embedded inside long runs (e.g. 3 × 15 min at half/marathon pace), race fueling and race-shoe rehearsals.
- **Benchmark runs**: standardized 45–60 min run at fixed pace on a flat course (or treadmill) under comparable conditions; track HR at fixed pace (or Efficiency Factor `EF`), Pa:Hr decoupling, RPE, and next-day leg soreness.

## intervals.icu Workout Syntax (Running)
- Event type: `Run`.
- Intensities: `% Pace` (threshold pace, e.g. `95-100% Pace`), `% LTHR` / `% HR` (e.g. `72-78% LTHR`), or zones `Z1`–`Z5`. Do not mix two intensity metrics on the same step.
- Lint before writing: `coach_tools.py lint --type running --expected-duration <min>`.
- Example steps:
  ```text
  Warmup
  - 15m 70-75% LTHR

  Threshold 3x
  - 8m 95-100% Pace
  - 3m 75% Pace

  Cooldown
  - 10m Z1
  ```

## Running-Specific Fueling & Hydration
In addition to the core carbohydrate tiers in `endurance-methodology.md`:
- **Lower GI tolerance than cycling**: vertical impact and reduced gut blood flow make runners more prone to GI distress—keep pre-run meals low in fiber and fat within 2–3 h of hard or long sessions.
- **Carry strategy**: plan handhelds, belt, or soft flasks for runs > 75 min (earlier in heat). Practice your exact race gels/drink mix during long runs and race-pace blocks, building progressively toward 60–90 g/h for marathons.
- **Post-run recovery**: prioritize carbs + protein within 1–2 h after long or threshold runs to speed glycogen replenishment and muscle repair.

## Running-Specific Strength & Prevention
- Priority muscles: calves/soleus (primary impact absorbers), glutes/glute medius (pelvic stability), hamstrings, quads, core, and foot/ankle intrinsic stability.
- Light plyometrics (pogo hops, jump rope, bounding): only outside injury return, pain-free, and introduced very gradually (strong evidence alongside heavy resistance training for running economy).
- Track shoe rotation and mileage in intervals.icu once running > 30–40 km/week.

## Environment & Logistics (Check at Intake & Brief)
- Available surfaces (track, flat pavement, soft paths/parks, treadmill), local hills, weather/heat constraints, and shoe rotation.
