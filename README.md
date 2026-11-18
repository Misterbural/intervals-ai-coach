# intervals-ai-coach

[![CI](https://github.com/Misterbural/intervals-ai-coach/actions/workflows/ci.yml/badge.svg)](https://github.com/Misterbural/intervals-ai-coach/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**An AI endurance coach connected directly to [intervals.icu](https://intervals.icu) via MCP** — built for **cycling, running, trail running, swimming, triathlon, and HYROX**, combining structured sports-science methodology, deterministic Python tooling, modular Claude Skills, and a hardened self-hosted deployment guide.

> **Project status (honest disclaimer):** **Experimental.** The VPS + Cloudflare Access OAuth + MCP + Claude Project + Skills pipeline has been verified at installation for **cycling** (prior to running a full live pilot block). The additional sport modules (`running`, `trail`, `swimming`, `triathlon`, `hyrox`), training-camp rules, and `coach_tools.py` calculators (`cs`, `css`, `hyrox`, `check-plan`) are unit-tested in CI but have **not yet been field-tested** in live training blocks. Feedback and PRs are welcome!
>
> **Use in Any Language:** The repository is written in English for broad accessibility, but **your coach works in your native language** (French, Spanish, German, Italian, etc.). Simply tell the coach your preferred language at the start of the initial intake (or set it in `athlete-profile.md`)—all chats, generated files, and intervals.icu workout titles/descriptions will follow your language while keeping intervals.icu syntax valid.
>
> **Platform compatibility:** Designed for **Claude** (Projects, Library files, Skills, remote OAuth MCP connector, Python execution, and Scheduled Tasks). Because the methodology, sport modules, `coach_tools.py`, and MCP deployment are plain Markdown + standard-library Python, ~90% of the repo is also directly reusable with any MCP-compatible agent (Claude Code, Antigravity, Codex, Gemini CLI, etc.).

---

## Why This Architecture?

Naive "chat with an LLM about my workouts" setups fail in predictable ways: hallucinated TSS math, broken intervals.icu workout syntax, sycophantic approval of overtraining, forgotten history across threads, and empty Strava activity shells.

This repository addresses each failure mode explicitly:

- **Deterministic math (`tools/coach_tools.py`)**: intervals.icu remains the sole source of truth for CTL, ATL, TSB, eFTP, and curves. Every other calculation—block load targets (including planned `camp` overload weeks), ±5% weekly rebalancing, Foster monotony/strain, CP/W', Critical Speed/D', CSS, HYROX compromised-running split diagnostics, HRV/RHR readiness flags, fatigued-curve durability, plan sanity checks, and intervals.icu workout linting—runs in a zero-dependency Python 3 script with **78 built-in unit tests**.
- **Modular multi-sport & cross-training design**: a lean endurance core (`endurance-methodology.md`, including cross-sport load & hard-day budgeting) paired with drop-in sport modules (`cycling.md`, `running.md`, `trail.md`, `swimming.md`, `triathlon.md`, `hyrox.md`)—plus support for custom modules (`sports/<your-sport>.md`). Mix and match freely (e.g. `cycling.md` + `running.md` for cross-training or dual-sport balance without triathlon) so your coach loads only the physiology, terrain/gym constraints, and workout syntax relevant to your sports.
- **Lazy-loaded workflows (`skills/`)**: 6 focused `SKILL.md` procedures (initial intake, season revision, block brief, Sunday weekly review, daily adjustment, end-of-block review) keep project instructions concise and execution reliable.
- **Human-in-the-loop & anti-sycophancy**: strict decision hierarchy (medical/pain > validated plan > thresholds > progression), "can vs should" rule (feeling fresh never overrides a recovery week), mandatory approval before every calendar write, and a built-in monthly critical self-review.
- **Hardened remote MCP hosting**: non-root `systemd` service bound to `127.0.0.1`, Cloudflare Tunnel (zero open HTTP ports), and Cloudflare Access Managed OAuth locked to your email address.

---

## Architecture

```text
Wearables / Bike Computer / Trainer (direct sync, not via Strava)
                      │
                      ▼
               intervals.icu  ◄──── Structured workouts & ATP
                      ▲
                      │ API (read/write, DELETE_MODE=safe)
                      │
     VPS (systemd, 127.0.0.1:8000)
          intervals-icu-mcp
                      ▲
                      │ Outbound Cloudflare Tunnel (no open HTTP port)
                      │
       Cloudflare Access (Managed OAuth — email allowlist)
                      ▲
                      │ Remote MCP Connector
                      ▼
         Claude Project ("Endurance Coach")
          ├── Project Instructions (short rules & workflow router)
          ├── Library: methodology + sport module(s) + profile/season/journal/science
          ├── Library: coach_tools.py (deterministic calculations & linter)
          └── 6 Skills (loaded on demand)
```

---

## Repository Structure

```text
├── README.md
├── LICENSE                                  # MIT
├── docs/
│   ├── vps-mcp-deployment.md                # Full VPS + systemd + Cloudflare Tunnel & OAuth guide
│   └── workflow-and-best-practices.md       # Weekly routine, pilot week, scheduled tasks, checklist
├── claude-project/
│   ├── project-instructions.md              # Paste into Claude Project Instructions
│   ├── endurance-methodology.md             # Shared endurance methodology (incl. training camps)
│   ├── sports/                              # Pick the module(s) matching your sport(s):
│   │   ├── cycling.md                       # CP/W', indoor/outdoor FTP, kJ durability, virtual races
│   │   ├── running.md                       # CS/D', pace/LTHR, mechanical mileage progression caps
│   │   ├── trail.md                         # Vert gain/loss, flatlander D+ strategies, eccentric load, GAP
│   │   ├── swimming.md                      # Pool & open water, CSS, shoulder load, `mtr` syntax
│   │   ├── triathlon.md                     # 3-sport load integration, bricks, race-distance priorities
│   │   └── hyrox.md                         # Open/Pro/Doubles standards, compromised running, sled/erg pacing, HRSS blind-spot rules
│   └── templates/
│       ├── athlete-profile.md               # Optional: fill manually OR let initial intake generate it
│       ├── season-goals.md                  # Generated by coach-initial-intake (leave out at start)
│       ├── coaching-journal.md              # Long-term block plans, reviews & monthly self-critiques
│       └── science-watch.md                 # Baseline evidence benchmarks (v0)
├── skills/                                  # 6 Claude Skills (SKILL.md <= 200-char description)
│   ├── coach-initial-intake/SKILL.md
│   ├── coach-season-revision/SKILL.md
│   ├── coach-block-brief/SKILL.md
│   ├── coach-weekly-review/SKILL.md
│   ├── coach-daily-adjustment/SKILL.md
│   └── coach-block-review/SKILL.md
├── tools/
│   └── coach_tools.py                       # Deterministic CLI (Python 3 stdlib only, 78 self-tests)
└── scripts/
    └── build_skills_zip.py                  # Validates SKILL.md files and builds dist/skills/*.zip
```

---

## Quick Start

1. **Prepare intervals.icu**
   - Generate an API key and note your Athlete ID (`i123456`).
   - Connect your watch / head unit / indoor trainer **directly** to intervals.icu (not via Strava—Strava-sourced activities return empty shells via the intervals.icu API).
   - Enable daily wearable wellness sync (HRV, resting HR, sleep).
2. **Deploy the MCP server**
   - Follow [docs/vps-mcp-deployment.md](docs/vps-mcp-deployment.md) to run [`intervals-icu-mcp`](https://github.com/hhopke/intervals-icu-mcp) behind Cloudflare Tunnel + Access Managed OAuth and add it as a Custom Connector in Claude (**Always allow** read tools, **Manual approval** for write/delete tools).
3. **Package & import the 6 Skills**
   ```bash
   python3 tools/coach_tools.py test
   python3 scripts/build_skills_zip.py
   ```
   Import the 6 generated archives from `dist/skills/` into **Claude → Customize → Skills**.
4. **Create the Claude Project**
   - Paste [claude-project/project-instructions.md](claude-project/project-instructions.md) into **Project Settings → Memory → Project Instructions**.
   - Upload to the Project Library:
     - `claude-project/endurance-methodology.md`
     - Your active sport module(s) from `claude-project/sports/` (`cycling.md`, `running.md`, `trail.md`, `swimming.md`, `triathlon.md`, `hyrox.md` — or drop in your own custom `sports/<my-sport>.md` for rowing, Nordic skiing, ski-mo, etc.)
     - `coaching-journal.md` and `science-watch.md`
     - `tools/coach_tools.py`
     - *(Optional)* Your filled-in `athlete-profile.md` — or leave **both** `athlete-profile.md` and `season-goals.md` out initially so `coach-initial-intake` interviews you (in your preferred language) and generates both files for you.
5. **Run a smoke test, then start your intake**
   - Ask Claude to read your last 7 days from intervals.icu, confirm all 6 skills are visible, and run `python3 coach_tools.py test`.
   - Start your first real session in your preferred language (e.g. *"Initial intake: coach me in French, review my intervals.icu history, and help me build my profile and season."*).
   - Follow [docs/workflow-and-best-practices.md](docs/workflow-and-best-practices.md) for your pilot week, Sunday reviews, and optional Scheduled Tasks.

---

## Deterministic CLI (`tools/coach_tools.py`)

Zero external dependencies (Python 3 standard library only). Run `python3 tools/coach_tools.py <command> -h` for full options:

| Command | Purpose | Primary workflow |
|---|---|---|
| `targets` | Weekly block load targets (`3:1` / `2:1`, CTL ramp cap, recovery drop, `--camp-weeks` overload camps) & projected CTL/TSB | `coach-block-brief` |
| `check-plan` | Sanity checks: load jumps, CTL ramp, `camp` recovery/intensity safety, taper, hard days, intensity split, running single-session `longest_run_km` (+10% / Frandsen 2025) & trail vert caps | `coach-block-brief`, `coach-season-revision` |
| `rebalance` | Checks weekly totals and adjusts an easy session to land within ±5% of target load/duration | `coach-block-brief`, `coach-weekly-review` |
| `lint` | Lints intervals.icu workout text (`cycling`, `running`, `trail`, `swimming`, `hyrox`, `strength`), catches `400m` vs `400mtr` in swim, `% FTP`, parentheses, duration mismatches | `coach-block-brief`, `coach-weekly-review`, `coach-daily-adjustment` |
| `wellness` | 7-day ln(rMSSD) HRV vs non-overlapping 28-day normal range, 7-day RHR trend & single-night spike, sleep | `coach-daily-adjustment`, `coach-weekly-review` |
| `monotony` | Foster monotony, strain, and consecutive hard days | `coach-weekly-review` |
| `project` | Projects CTL / ATL / TSB to race day against a taper TSB window | `coach-season-revision` |
| `cp` | Cycling Critical Power & W' (3-min + 12-min tests) + optional indoor/outdoor FTP offset | `coach-block-review` |
| `cs` | Running Critical Speed & D' from two maximal efforts → threshold pace (`min:sec/km`) | `coach-block-review` |
| `css` | Swimming Critical Swim Speed (400 m + 200 m tests) → CSS (`min:sec/100m`) | `coach-block-review` |
| `hyrox` | HYROX split & compromised-running analyzer (run vs station %, Run 1 over-pacing, fade vs CS) | `coach-block-review` |
| `durability` | Fatigued vs fresh power-curve retention, status, and primary limiter | `coach-block-review` |
| `progression` | Power-curve deltas across two equivalent periods | `coach-block-review` |
| `test` | Runs the 78-assertion self-test suite | Setup & verification |

---

## Security & Privacy Highlights

- **Never commit personal files**: keep your filled-in `athlete-profile.md`, `season-goals.md`, `coaching-journal.md`, and API keys strictly private (outside git).
- **Principle of least privilege**: read tools auto-approved; write/delete tools manually approved; `INTERVALS_ICU_DELETE_MODE=safe`.
- **Prompt-injection hygiene**: project instructions explicitly treat activity titles, notes, comments, and external web pages as untrusted data, never directives.

---

## Medical Disclaimer

This project is an experimental training organization and decision-support tool. **It is not medical advice.** Always follow the clearance and restrictions of a qualified physician or physiotherapist—especially when returning from injury, illness, or surgery—and stop training if you experience persistent pain, chest discomfort, dizziness, or unusual symptoms.

---

## Credits & License

- Built on top of the open-source [`intervals-icu-mcp`](https://github.com/hhopke/intervals-icu-mcp) server and [intervals.icu](https://intervals.icu).
- Methodology refinements (deterministic calculation scripts, Foster monotony/strain, durability retention, plan validation checks) inspired in part by the public documentation of [Montis.icu](https://montis.icu) and endurance sports-science literature cited in `science-watch.md`.
- Released under the [MIT License](LICENSE).
