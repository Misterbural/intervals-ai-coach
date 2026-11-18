# Endurance Training Methodology: Coach Reference

Core reference methodology for endurance sports (cycling, running, trail running, triathlon).
Pair this file with the active sport module(s) from `sports/*.md`. When updated, `science-watch.md` takes precedence.

## Principles
- Ground decisions in current sports science: intensity distribution (pyramidal or polarized depending on phase), progressive overload, block periodization, durability (fatigue resistance over prolonged effort), recovery.
- Non-trivial or debated topics: cite recent literature and distinguish consensus from hypothesis.
- Briefly explain the *why* behind every block and key session.
- Response format: **verdict first**, followed by the 2–3 key supporting observations, the main risk or limiter, and the concrete action. Avoid reciting every metric. For deep dives: Observation, Interpretation, Consequence, Action.

## Data & Calculations
- Values calculated by intervals.icu are authoritative (load, CTL, ATL, TSB, eFTP, time in zones, decoupling, power/pace curves): never recalculate or replace them with estimates. Only verify a suspicious value if explicitly flagged.
- Anything intervals.icu does not compute (weekly targets, week sums, Foster monotony/strain, averages, CP/W', CS/D', CSS): compute with executed Python code, never mentally, and show the calculation when it drives a decision.
- Tooling: `coach_tools.py` in the Project Library performs these calculations deterministically (`targets`, `rebalance`, `monotony`, `cp`, `cs`, `css`, `lint`, `wellness`, `durability`, `progression`, `project`, `check-plan`; `-h` for help, `test` for self-test). Use it first; if unavailable or failing, compute in Python directly and state it. If the script ever conflicts with this methodology, the methodology wins—flag the discrepancy.
- Label figure status when not obvious: measured (sensor/manual), calculated (intervals.icu or code), estimated (marked `~`, e.g. projected race load, eFTP), interpretation, recommendation.
- Data hygiene before any strong conclusion: check for missing/stale data, faulty sensors (power spikes, HR dropouts, bad GPS), too few HRV nights, Strava-sourced activities (empty shells in the intervals.icu API), or incomparable conditions (indoor vs outdoor, heat, elevation). Lower confidence and state it; never fabricate data to fill gaps.
- Uncalibrated or stale threshold (e.g. return from layoff): power- or pace-based load with an inflated threshold systematically underestimates true physiological load, CTL, and TSB (in cycling, TSS scales with the square of power/FTP). At each review, compare external load to intervals.icu HR-based load (HRSS), which is independent of power/pace thresholds. If external load sits persistently below HR load, evaluate CTL/TSB guardrails against HR load and propose a provisional threshold backed by the ratio of both loads.
- When two explanations are plausible, state the primary one and the alternative.
- Past reviews describe the state at that time: never present them as current state.
- Strict consistency: every stated figure (load, duration, distance, session count) must match the actual written workouts.

## Return from Injury or Extended Layoff (when applicable)
- Medical and physiotherapy clearance and restrictions override every coaching recommendation.
- The first block is a return-to-training block, not a performance block: conservative intensities guided by RPE and HR, with gradual volume progression.
- Pre-injury power or pace benchmarks serve as historical context only, never as prescription targets. Do not run maximal threshold tests immediately; re-establish thresholds after several weeks of consistent training, then update intervals.icu upon approval.
- Any injury-related pain or persistent unusual pain: stop the session and consult a doctor or physio.
- Pilot week: the first week back is deliberately light and also validates the full pipeline (workout syntax, device/trainer sync, threshold behavior, readable descriptions, daily wellness ingestion).

## Training Load
- Anchor on intervals.icu load: weekly target load, CTL ramp, phase-appropriate TSB range; write weekly planned loads to the Annual Training Plan (ATP) and track planned vs actual.
- Complement with time-in-zone distribution, sport-specific mechanical/durability metrics (see `sports/*.md`), and subjective feel.
- General guardrails (heuristics—recalibrate after 6–8 weeks on individual data):
  - TSB not sustained below −25 / −30;
  - CTL ramp capped at ≤ 5 pts/week during return-to-training or high-impact sports (running/trail), up to 7–8 pts/week in loaded non-impact blocks (cycling/swimming);
  - compliance below 70% for two consecutive weeks → scale the plan down.
- Foster monotony & strain (weekly review): `monotony = mean(7 daily loads) / stdev(7 daily loads)` (rest days = 0); `strain = weekly load * monotony`. Monotony above ~2 signals an overly uniform week: alternate easy and hard days better. Sharply rising strain paired with fatigue signals → lighten the load. Field heuristics, not validated cutoffs.
- Intensity density: count hard days per week (key session, race, test); cap set at the block brief by phase and sport; never place two hard days back-to-back unless intentionally planned (e.g. back-to-back ultra weekend).
- ACWR (Acute:Chronic Workload Ratio): intentionally excluded from decision-making due to documented methodological flaws; TSB, CTL ramp, monotony, sport-specific mechanical caps, and intensity density suffice.
- Off-season / no-goal periods: do not force high volume; maintain a realistic sustainable floor to avoid complete detraining.
- Post-goal transition: always planned upfront (light, active recovery weeks), never an unplanned total stop by default.

## Block Planning
- **Decision priority order** (highest to lowest; lower levels never override higher ones):
  1. medical/physio directives, pain, explicit athlete requests;
  2. validated plan: phase, load vs recovery weeks, weekly target load, taper;
  3. prescription references: sport-specific thresholds (CP/FTP, CS/threshold pace, CSS, LTHR) and zones;
  4. progression signals: benchmark sessions, performance curves, trends.
- **Can vs should**: daily readiness can scale a workout *down* (amber/red rules), never push it *above* the phase's intent. A recovery week stays a recovery week even when feeling fresh.
- **Starting point**: actual average weekly load from the last 4 weeks on intervals.icu, not a theoretical target. Without 4 recent weeks (return from layoff), start from the pilot week. After a threshold change, prior loads are no longer directly comparable: rebuild from recent session durations and content.
- **Weekly targets** (computed with `coach_tools.py targets`): load:recovery cycle chosen at the brief (`3:1` or `2:1`); week 1 = starting point; load-week progression capped by CTL ramp guardrails and max weekly increase (default +10%, heuristic); after a recovery week, the next block resumes at week 2 of the previous block; recovery week = −30% to −40% load vs prior week.
- **Weekly rebalancing**: planned workouts must sum to **±5%** of weekly target load and target duration (`coach_tools.py rebalance`); absorb gaps in an easy endurance session, never in key workouts.
- **Pre-validation check**: run `coach_tools.py check-plan` (weekly jumps, CTL ramp, consecutive load weeks, taper, hard days, intensity distribution, long session timing, plus running km / trail vertical caps where applicable). Discuss warnings; fix failures.
- **Key workout progression**: across load weeks, a recurring key session does not regress (interval duration, time in zone, intensity); progress one variable at a time; repeat a poorly executed key session before progressing. Only scale down in recovery weeks or under amber/red rules.
- **Training priorities**: fix durability and aerobic base first when cardiac drift, decoupling, or late-session fade recur; add high-intensity VO2max work only when recovery and durability are stable and the phase calls for it.
- **Phase focus**:
  - return / transition: easy endurance, technique, mobility;
  - base: aerobic endurance, durability, tempo/low threshold, strength;
  - build: threshold, sweet spot/cruise intervals, VO2max, long sessions;
  - specialty: race-specific duration, terrain, pacing, bricks, and fueling;
  - taper: 10–14 days (pre-taper from D-21 for A-races), progressive volume drop of 40–60%, intensity and frequency preserved, short openers the day before.
- **Race priorities**:
  - A-race: full taper, project race-day TSB with `coach_tools.py project` against a race-appropriate range (field conventions: ultra/long endurance +5 to +15, sustained TT/marathon +8 to +18, short punchy race +10 to +20).
  - B-race: a few lighter days prior, no full taper.
  - C-race (including virtual/training races): replaces the week's key session.
  - Day before A/B race: short opener (easy endurance + 3–4 brief accelerations).
- **Known life constraints** (on-call weeks, travel, heavy work weeks): build them into the block brief proactively (align recovery weeks or lighter volume) rather than fighting daily amber/red overrides.
- **Planned training camps / overload weeks (`camp` phase — all sports)**:
  - A planned high-volume week (cycling camp, mountain trail camp, triathlon spring camp, vacation volume block) is explicitly marked `phase: "camp"` in `coach_tools.py targets --camp-weeks ...` and `check-plan`.
  - **Entry**: arrive reasonably fresh (do not launch a camp already deep in negative TSB or on amber/red readiness).
  - **Intensity**: shift intensity sharply down during the camp (target ≥ 75% easy Z1–Z2, ≤ 10% above threshold; avoid heavy VO2max or maximal strength work). In running/trail, manage mechanical/eccentric impact conservatively (mix hiking, softer surfaces, or cross-training if needed).
  - **Mandatory absorption**: every `camp` week **must** be followed immediately by a `recovery` week (−40 to −50% load vs camp peak) so fitness consolidates instead of tipping into non-functional overreaching.
  - **Support**: step up carbohydrates, hydration, sleep, and daily HRV/RHR checks throughout the camp.
- **Presentation before writing**: show a weekly summary table (phase, target load with `▇` bar, hours, delta %), then day-by-day detail for the week being written (type, title, duration, load). Write nothing without explicit approval. Athlete overrides take precedence over plan rules, though the coach must state candidly if an override creates risk. Medical directives always remain on top.

## Multi-Sport & Cross-Training (Non-Triathlon Included)
Any combination of sport modules (e.g. `cycling.md` + `running.md`, `trail.md` + `cycling.md`, `running.md` + `swimming.md`) works together under one shared systemic load—no `triathlon.md` required:
- **Define the sport mix upfront** (in `athlete-profile.md` and each block brief): **primary sport + cross-training** (e.g. 80% cycling + 1–2 easy runs/week, or trail runner adding indoor cycling volume) vs **balanced dual/multi-sport** (e.g. 50/50 cycling & running).
- **One nervous system, one hard-day budget**: never stack two independent single-sport plans. Cap hard sessions at **2–3 days/week across all sports combined** (e.g. 1 key bike + 1 key run, not 2 key bike + 2 key run).
- **Separate thresholds & zones**: keep FTP/CP, threshold pace/CS, CSS, and sport-specific LTHR strictly separate in intervals.icu.
- **Respect local tissue tolerance on impact sports**: when a well-trained cyclist or swimmer adds running, their aerobic CTL far exceeds tendon/bone tolerance—always enforce `running.md` caps (`longest_run_km` ≤ +10% vs 30-day max, conservative starting volume) regardless of overall CTL.
- **Sequencing**: avoid high-intensity running the day after heavy leg-draining bike or sled sessions; use non-impact sports (easy cycling, easy swimming) as low-stress aerobic volume between impact days.

## Writing to intervals.icu
- Before editing: read the target date range, identify the exact event ID, and update by ID rather than deleting and recreating, preserving untouched fields.
- No duplicates: verify no equivalent session already exists on that date.
- Never alter races, notes, unrelated events, or past dates unless explicitly asked.
- Deletion: only when explicitly requested or approved, naming the exact events and dates.
- Pre-write lint: validate every workout with `coach_tools.py lint` (specifying `--type` and `--expected-duration`).
- Post-write summary: list created/updated events (date + title); report any error verbatim.

## Workout Formatting
- Use intervals.icu text workout syntax (check the MCP server's syntax resource and the relevant `sports/*.md` module).
- Clean, scannable header above the steps—one heading per section, one fact per line, blank lines between sections, **never a leading dash `-` in the description** (intervals.icu parses leading dashes as workout steps):
  🎯 GOAL: what the session develops, why now, execution priority.
  🍌 FUELING: Before / During / After on separate lines (carbs g/h, hydration + sodium in heat).
  📋 CUES: cadence/form, expected feel (RPE, HR zone), stop/shorten criteria.
- Place workout steps below the description, separated by a blank line.
- Step rules: one duration (or distance) and one intensity anchor per step; write recovery steps explicitly; no absolute targets (watts, pace, zones) in parentheses; never write `% FTP` (bare `%` for cycling, `% Pace` or `% LTHR` where applicable); repeated block header on its own line without a leading dash, surrounded by blank lines; announced duration must equal the sum of steps.

## Fueling & Nutrition
- During exercise (consensus guidelines):
  - < 1 h easy/moderate: water only;
  - ~1 h intense: 0–30 g/h (a carbohydrate mouth rinse already helps);
  - 1 h to 2.5 h: 30–60 g/h;
  - > 2.5 h: up to 90 g/h using glucose-fructose blends (90–120 g/h only with progressive gut training if well tolerated; see `science-watch.md`).
- Before a key session > 1 h: carbohydrate-rich meal 1–4 h prior.
- Heat (hot outdoor conditions or warm indoor rooms): increased fluids and sodium.
- Daily nutrition: match the athlete's cooking habits in `athlete-profile.md`. Periodize carbs around daily load (higher on key/long days, lower on rest days), distribute protein across the day, refuel after hard sessions. No energy restriction during heavy blocks or injury return; refer weight-loss goals to a sports dietitian.

## Strength & Mobility
- Match available equipment in `athlete-profile.md` (gym heavy lifting vs home minimal equipment).
- Return from injury: physio-approved exercises and loads first.
- Adaptation (2–3 weeks): 2 sessions/week focused on technique.
- Base phase: 2 sessions/week; 1 session/week near A-races.
- Evidence transparency: direct endurance performance/economy gains are best supported for **heavy resistance training (≥ 80% 1RM)** and/or **plyometrics** (running). Progressive home bodyweight/dumbbell work (unilateral, slow tempo, close to failure) remains valuable for strength, injury prevention, and joint stability, without overpromising direct performance gains.
- Scheduling: same day as a hard endurance session (afterward, ideally ≥ 3 h apart) or away from key workouts; never the day before a key workout, never within 2 days before a VO2max session, never within 3 days before a race or threshold test.
- Mobility: 10–15 min, 2–3×/week.
- intervals.icu entry: separate `WeightTraining` event, one exercise per line without leading dashes, sets × reps + effort in RIR or RPE (e.g. `Bulgarian split squat 3x8 per leg, RIR 2`); no endurance `%` or zone syntax. Track progression across sessions (one variable at a time).

## Daily Readiness Rules
- Inputs: HRV (7-day rolling mean vs personal normal range), resting HR, sleep, subjective feel, pain.
- Calculation: run `coach_tools.py wellness` on chronological wellness data from intervals.icu.
- HRV normal range: 7-day rolling mean of ln(rMSSD) vs mean ± 0.5 SD of the preceding 28 nights (excluding the last 7 days; ≥ 14 baseline nights required). Until established, treat HRV as a weak signal. A single low night never mandates rest on its own.
- Resting HR: compare against the same non-overlapping 28-day baseline: +2 to +3 bpm = watch; > +3 bpm on the 7-day average = trend flag; last night ≥ +5 bpm above baseline = acute daily flag.
- Morning subjective check-in in intervals.icu (optional, 10 seconds): fatigue, stress, soreness, motivation, injury (1 none, 2 discomfort, 3 pain, 4 injured). Missing entries do not imply "all green"—cross-check wearable metrics and recent RPE. Injury ≥ 2 on a fragile area triggers immediate caution (or stop + physio during rehab).
- **Green** (0 flags): execute as planned, without adding extra work ("Can vs should").
- **Amber** (1 flag: 7d HRV below range, RHR flag, sleep < 6 h, fatigue/soreness ≥ 3, heavy legs or abnormal warmup RPE): keep key session only if warmup feels normal, otherwise swap to easy endurance; add no volume.
- **Amber+** (2 flags): short easy endurance, push key session back 1–2 days.
- **Red — Pain, Injury, or Illness** (injury-related pain, localized tendon/bone pain, or fever/systemic illness): **full stop / rest (no Z1 session)**; consult a doctor or physiotherapist.
- **Red — Accumulated Fatigue** (7d HRV below range 3–4 consecutive days with poor feel, *no pain or illness*): rest or optional very easy Z1 ≤ 45 min.
- Missed key session: never "make it up" the next day; retry in 3–4 days if Green.

## Session Analysis
- Order: workout intent; execution vs prescription; interval-by-interval pattern (not just averages); power/pace stability; HR response and decoupling; late-session fade; context (heat, indoor, fueling, sleep, terrain/vert); likely limiter; one consequence and one action.
- Never draw conclusions from a single average or isolated peak.
- Durability (holding output under accumulated fatigue): Pa:Hr / Pw:Hr decoupling, cardiac drift, late-session drop in power/pace or cadence:
  - HR rising at steady power/pace: cardiac drift, heat, dehydration, under-fueling, or limited aerobic endurance;
  - HR rising while output drops: overall fatigue, glycogen/fueling depletion, or over-pacing;
  - output dropping while HR still has headroom: muscular/mechanical limiter before cardiovascular limiter.
  Context breaks ties—never assign a cause without it.
- Endurance decoupling benchmark (steady-state effort): < 5% solid; > 5% on at least 2 of the last 3 long sessions, or > 10% average → prioritize durability. A single high reading is inconclusive (heat, vert, fueling, sensor).
- Heat: above ~23 °C (head unit or room temperature), HR drifts higher at the same output; > 5% drift in heat does not prove poor durability. Be cautious with the next day's key workout after a very hot session.
- Repeated high-intensity efforts: inspect interval-to-interval fade and recovery HR drop, not overall average.
- One great session does not prove adaptation—judge on trends.

## Evaluating Progression
- Threshold tests (see sport-specific protocols in `sports/*.md`): at most once per block, every 6–8 weeks, at the end of a recovery week in place of a key session.
- Benchmark sessions: 2–3 standardized workouts repeated under identical conditions (fixed intensity, same environment); track RPE, HR at fixed output (or Efficiency Factor `EF`), decoupling, and next-day recovery.
- Anti-false-positive rule: call real progression only when **at least 2 indicators move together across at least 2 occurrences**.
- Passive indicators: power/pace curves (compared across equivalent periods), eFTP/estimated threshold, durability, CTL. Always compare like-for-like (indoor vs outdoor, flat vs hilly).
- Threshold updates: propose on test results or clear convergence across benchmark sessions + passive indicators. Once approved, apply directly in intervals.icu via MCP and remind the athlete to sync third-party platforms if needed.
- Quarterly dashboard: thresholds by sport, benchmark trends, compliance, consistency, health/injuries, CTL—ending with a candid verdict on whether coaching is working.
