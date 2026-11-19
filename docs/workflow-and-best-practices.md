# Coaching Routine, Best Practices & Checklist

## The Four Coaching Rhythms

Once your Claude Project, skills, and MCP connector are live, the system runs on four lightweight rhythms:

1. **Initial Intake (`coach-initial-intake`)** — *once at startup (leave `season-goals.md` — and optionally `athlete-profile.md` — out of the Library)*
   - Prompt (in your preferred language): *"Initial intake: coach me in [Language], review my intervals.icu history, and help me build my profile and season."*
   - Confirms language, environment/terrain access (e.g. trail vertical access, pool setup), goals, and constraints; produces `athlete-profile.md` and `season-goals.md`.
2. **Block Brief (`coach-block-brief`)** — *every 3–6 weeks before a new training block*
   - Refreshes `science-watch.md` if due, locks schedule/constraints/targets, runs `coach_tools.py targets` + `check-plan`, writes full-block loads to the ATP, writes **Week 1 only** to the calendar, and opens the block's entry in `coaching-journal.md`.
3. **Sunday Weekly Review (`coach-weekly-review`)** — *once a week (new chat thread per week)*
   - Prompt: *"Weekly review and proposal for the week of [date]. Availability: … Feel: …"*
   - Analyzes actual vs planned load, compliance, HRV/RHR, monotony, and durability; proposes next week within ±5% of target; writes after your approval.
   - On the **first Sunday of each month**, automatically adds a candid critical self-review of its own coaching.
4. **Daily Adjustment (`coach-daily-adjustment`)** — *only when needed (poor sleep, soreness, pain, schedule change)*
   - Short message inside the current week's thread: *"Slept 5 h, heavy legs"* or *"Only 45 min free tonight instead of 90"*.
   - Applies Green / Amber / Amber+ / Red rules and updates today's event by ID after approval.

**Plus two milestone workflows:**
- **End of Block (`coach-block-review`)**: runs CP / CS / CSS calculators, checks benchmark sessions and durability, proposes threshold updates, closes the block's journal entry, and delivers a quarterly dashboard every 3 months.
- **Season Revision (`coach-season-revision`)**: whenever a race is added, moved, or dropped, or an injury disrupts the season.

---

## Six Habits That Compensate for AI Coaching Limits

1. **Keep `coaching-journal.md` updated** — it is the long-term memory across weekly chat threads.
2. **Keep the weekly loop low-friction** — wearables sync HRV/RHR/sleep automatically; morning check-in fields in intervals.icu are optional (at minimum, flag `Injury = 2` whenever a sensitive area speaks up, and log post-session RPE).
3. **Demand candor** — if the coach feels too agreeable, ask: *"What would a demanding human coach tell me right now?"*
4. **Always inspect calendar writes** — take 15 seconds after every write to verify dates, durations, and intensities in intervals.icu.
5. **Keep `athlete-profile.md` current** — update after threshold changes, gear changes, or schedule shifts.
6. **Plan life constraints upfront** — place recovery weeks on known travel or on-call weeks during the block brief instead of fighting daily Amber+ alerts.

---

## Pilot Week (Recommended First Week)

Treat your first week (especially when returning from injury or layoff) as a **deliberately light pilot week** to validate the entire pipeline:
- Workouts appear accurately in intervals.icu and sync cleanly to your watch / bike computer / indoor trainer (check whether your indoor app uses intervals.icu's Indoor FTP or its own setting).
- Descriptions render cleanly (🎯 GOAL / 🍌 FUELING / 📋 CUES) without stray dashes creating bogus steps.
- `python3 coach_tools.py test` runs cleanly inside a project chat thread.
- Direct activity uploads (not Strava shells) come back with full power/pace/HR streams readable via MCP.
- Daily HRV, RHR, and sleep appear automatically in intervals.icu wellness.

---

## Optional: Automating with Scheduled Tasks

> **Requirement:** Claude Project Scheduled Tasks run in the cloud and require a **remote MCP connector (Option B self-hosted VPS or Option C Official Intervals.icu MCP)**—they do not work with local Claude Desktop `stdio` (Option A).

After **3–4 weeks of real use** (once routines are dialed in and your 14–28 night HRV baseline is established), you can add Claude Project Scheduled Tasks:

| Schedule | Coach action | Your action |
|---|---|---|
| Every morning | Checks HRV, RHR, sleep, and today's workout; alerts you **only** if Amber/Red | Nothing, or approve adjustment |
| Sunday evening | Drafts the weekly review and next week's proposal | Review, tweak, approve |
| 1st Sunday of month | Appends the monthly critical self-review | Read & apply corrections |
| End of block | Prepares block analysis and brief questions | Reply & validate next block |

> **Heads-up on OAuth expiry:** if your Cloudflare Access Managed OAuth grant expires every 2 weeks, scheduled tasks will pause until you re-authenticate. Adjust grant duration or set a recurring reminder when enabling scheduled tasks.

---

## Known Limitations & Mitigations

| Limitation | Mitigation in this setup |
|---|---|
| LLM reasoning is not a model trained on millions of athletes | Deterministic Python math (`coach_tools.py`), written decision rules, benchmark sessions, cited literature, block-level evaluation |
| Generic CTL/ATL/TSB misses intensity, durability & impact stress | Time in zones, Pa:Hr decoupling, fatigued power curves, Foster monotony/strain, running km & trail vert caps, HRV/RHR |
| No continuous memory across threads | `athlete-profile.md`, `season-goals.md`, `coaching-journal.md`, Project Memory, one thread per week |
| Cannot observe you physically | Post-session RPE/feel + optional injury flag in intervals.icu |
| LLM arithmetic or syntax errors | Never recalculate intervals.icu metrics; all other math in `coach_tools.py`; pre-write syntax linter (`lint`) |
| LLM sycophancy | Explicit candor rule + monthly critical self-review |
| Not medical advice | Medical/physio clearance and pain rules sit at priority #1 |

---

## Setup Checklist

- [ ] intervals.icu API key & Athlete ID created
- [ ] Watch / bike computer / trainer connected **directly** to intervals.icu (not via Strava)
- [ ] Daily wellness (HRV, RHR, sleep) syncing to intervals.icu
- [ ] VPS hardened, `intervals-icu-mcp` running via `systemd`, Cloudflare Access + Tunnel live and verified (`401` on unauthenticated `curl`)
- [ ] Custom connector added in Claude: read tools = Always allow, write/delete tools = Manual approval
- [ ] Claude Project created with `project-instructions.md` pasted in Project Instructions
- [ ] Uploaded to Library: `endurance-methodology.md`, active sport module(s) from `sports/`, `athlete-profile.md`, `coaching-journal.md`, `science-watch.md`, and `coach_tools.py` *(leave `season-goals.md` out until intake)*
- [ ] All 6 skills generated (`python3 scripts/build_skills_zip.py`) and imported into Claude
- [ ] Smoke test passed in a fresh project thread: MCP read works, all 6 skills visible, `python3 coach_tools.py test` passes
- [ ] Initial intake completed (`season-goals.md` uploaded)
- [ ] Pilot week completed and pipeline verified
- [ ] Thresholds and daily readiness cutoffs recalibrated after 6–8 weeks
- [ ] *(Optional, after 3–4 weeks)* Project Scheduled Tasks configured
