#!/usr/bin/env python3
"""coach_tools.py: deterministic endurance coaching calculations for intervals.icu.

Version 2.3. Python 3 standard library only (zero external dependencies).
Supports cycling, running, trail running, swimming, triathlon, and HYROX.
Implements the rules in endurance-methodology.md and sports/*.md; if a
discrepancy ever exists, the methodology takes precedence and this script
should be updated.

Subcommands (detailed help: python3 coach_tools.py <command> -h):
  targets     Weekly block load targets and CTL / ATL / TSB projection
  rebalance   Checks a week of workouts and adjusts an easy session to hit ±5%
  monotony    Foster monotony, strain, and consecutive hard days
  cp          Cycling Critical Power (CP) & W' (3-min + 12-min tests)
  cs          Running Critical Speed (CS) & D' (two maximal efforts)
  css         Swimming Critical Swim Speed (400m + 200m tests)
  hyrox       HYROX race/simulation split analysis (run vs station %, compromised-run fade)
  lint        Validates intervals.icu workout text (cycling, running, trail, swimming, hyrox, strength)
  wellness    HRV normal range, resting HR trend/spike, sleep: objective daily flags
  durability  Power retention on fatigued power curves
  progression Power-curve progression across two equivalent periods
  project     Projected CTL / ATL / TSB on race day (taper)
  check-plan  Plan sanity checks (load jumps, CTL ramp, running km / trail vert, camp, taper...)
  test        Built-in self-test suite

CTL, ATL, and TSB projections are approximations (load spread evenly across
each week): values computed by intervals.icu remain the source of truth.
"""

import argparse
import json
import math
import re
import statistics
import sys
from datetime import date, timedelta

VERSION = "2.3"
K_CTL = 1 / 42  # fitness time constant (days)
K_ATL = 1 / 7   # fatigue time constant (days)
BAR_MAX = 20


# ---------------------------------------------------------------- utilities

def round5(x):
    return int(5 * round(x / 5))


def bar(value, maximum):
    if maximum <= 0:
        return ""
    return "▇" * max(1, round(BAR_MAX * value / maximum))


def read_json(args):
    if getattr(args, "json", None):
        return json.loads(args.json)
    if getattr(args, "file", None):
        with open(args.file, encoding="utf-8") as f:
            return json.load(f)
    return json.load(sys.stdin)


def read_text(args):
    if getattr(args, "file", None):
        with open(args.file, encoding="utf-8") as f:
            return f.read()
    return sys.stdin.read()


def parse_numbers(text):
    return [float(x) for x in re.split(r"[,;\s]+", text.strip()) if x]


def parse_time_s(value):
    """Parse time into seconds: '3:20', '1:05:10', '200', '12m', '3m30s'."""
    s = str(value).strip()
    if re.fullmatch(r"\d+(?:\.\d+)?", s):
        return float(s)
    if ":" in s:
        parts = s.split(":")
        if len(parts) == 2:
            return int(parts[0]) * 60 + float(parts[1])
        if len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
    d = duration_seconds(s)
    if d is not None:
        return float(d)
    raise ValueError(f"Unrecognized time format: '{value}' (expected e.g. 3:20, 12m, 200).")


def format_pace(sec_per_unit, unit="/km"):
    """Format pace as mm:ss/km or mm:ss/100m."""
    total = round(sec_per_unit)
    minutes, sec = divmod(total, 60)
    return f"{minutes}:{sec:02d}{unit}"


def _mean(values):
    return sum(values) / len(values) if values else None


# ---------------------------------------------------------------- projection

def project_weeks(ctl0, atl0, weekly_loads):
    """Project CTL, ATL, and TSB at the end of each week (even daily load)."""
    ctl, atl, out = ctl0, atl0, []
    for load in weekly_loads:
        daily = load / 7
        for _ in range(7):
            ctl += (daily - ctl) * K_CTL
            atl += (daily - atl) * K_ATL
        out.append({"ctl": ctl, "atl": atl, "tsb": ctl - atl})
    return out


def max_load_for_ctl_ramp(ctl0, max_ramp):
    """Weekly load that raises CTL by max_ramp points in one week."""
    f = (1 - K_CTL) ** 7
    return 7 * (ctl0 + max_ramp / (1 - f))


# ---------------------------------------------------------------- block targets

def compute_targets(start_load, ctl, atl, weeks, cycle, max_increase, max_ctl_ramp,
                    recovery_drop, load_per_hour=None, sessions=None, start_date=None,
                    camp_weeks=(), camp_factor=1.35):
    """Compute weekly load targets for a training block.

    Load week 1 = start_load (actual absorbed load). Subsequent load weeks grow
    by (1 + max_increase). After a recovery week, the next block resumes at the
    level of week 2 of the previous block. Every normal load week is capped by
    max_ctl_ramp. Recovery weeks drop by recovery_drop relative to the prior week.
    Planned training camp weeks (1-indexed in `camp_weeks`) apply `camp_factor`
    on top of the last normal load week and force the following week to be a
    recovery week.
    """
    n_load, n_rec = (int(x) for x in cycle.split(":"))
    pattern = ["load"] * n_load + ["recovery"] * n_rec
    phases = [pattern[i % len(pattern)] for i in range(weeks)]
    camp_set = {int(w) for w in camp_weeks}
    for w in sorted(camp_set):
        if 1 <= w <= weeks:
            phases[w - 1] = "camp"
            if w < weeks and (w + 1) not in camp_set:
                phases[w] = "recovery"
    if isinstance(sessions, (int, float)) or sessions is None:
        sessions = [sessions] * weeks
    elif len(sessions) < weeks:
        sessions = list(sessions) + [sessions[-1]] * (weeks - len(sessions))

    out, cur_ctl, cur_atl = [], ctl, atl
    last_load, prev_load, block_start, prev_phase = None, None, None, None
    for i, phase in enumerate(phases):
        note = ""
        if phase == "camp":
            base = last_load if last_load is not None else start_load
            load = base * camp_factor
            note = f"planned training camp (x{camp_factor:g}; keep mostly Z1-Z2, recover after)"
            if block_start is None:
                block_start = base
            if last_load is None:
                last_load = base
        elif phase == "load":
            new_block = last_load is None or prev_phase in ("recovery", "camp")
            if last_load is None:
                wanted = start_load
            elif new_block:
                wanted = block_start * (1 + max_increase)
                note = "new block: resumes at previous block's week-2 level"
            else:
                wanted = last_load * (1 + max_increase)
            cap = max_load_for_ctl_ramp(cur_ctl, max_ctl_ramp)
            load = min(wanted, cap)
            if cap < wanted:
                note = f"capped by CTL ramp (<= {max_ctl_ramp:g} pts/wk)"
            if new_block:
                block_start = load
            last_load = load
        else:
            ref = prev_load if prev_load is not None else start_load
            drop = max(recovery_drop, 0.45) if prev_phase == "camp" else recovery_drop
            load = ref * (1 - drop)
            if prev_phase == "camp":
                note = f"post-camp recovery (-{drop * 100:.0f}%)"
        proj = project_weeks(cur_ctl, cur_atl, [load])[0]
        change_pct = None if prev_load is None else (load - prev_load) / prev_load * 100
        alert = "TSB below -25" if proj["tsb"] < -25 else ""
        hours = None if not load_per_hour else round(load / load_per_hour * 4) / 4
        monday = None
        if start_date:
            monday = (date.fromisoformat(start_date) + timedelta(weeks=i)).isoformat()
        out.append({
            "week": i + 1, "monday": monday, "phase": phase,
            "load": round5(load), "raw_load": load, "hours": hours,
            "sessions": sessions[i], "change_pct": change_pct,
            "ctl_end": round(proj["ctl"], 1), "ctl_ramp": round(proj["ctl"] - cur_ctl, 1),
            "tsb_end": round(proj["tsb"], 1), "note": note, "alert": alert,
        })
        cur_ctl, cur_atl, prev_load, prev_phase = proj["ctl"], proj["atl"], load, phase
    return out


def format_targets(rows):
    maxi = max(s["load"] for s in rows)
    lines = [
        "| Wk | Monday | Phase | Target load | | Hours | Sessions | Delta | CTL end (~) | TSB end (~) | Note |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for s in rows:
        delta = "—" if s["change_pct"] is None else f"{s['change_pct']:+.0f}%"
        h = "—" if s["hours"] is None else f"{s['hours']:g} h"
        sess = "—" if s["sessions"] is None else str(s["sessions"])
        note = "; ".join(x for x in (s["note"], s["alert"]) if x)
        lines.append(
            f"| {s['week']} | {s['monday'] or '—'} | {s['phase']} | {s['load']} | "
            f"{bar(s['load'], maxi)} | {h} | {sess} | {delta} | {s['ctl_end']} "
            f"({s['ctl_ramp']:+}) | {s['tsb_end']} | {note} |"
        )
    lines.append("")
    lines.append("Projected CTL, ATL, and TSB (~) assume even daily load; intervals.icu values are authoritative.")
    return "\n".join(lines)


def cmd_targets(args):
    if args.last_4_weeks:
        loads = parse_numbers(args.last_4_weeks)
        start = statistics.mean(loads)
        print(f"Starting load: mean of {len(loads)} weeks = {start:.0f}")
    elif args.start is not None:
        start = args.start
    else:
        sys.exit("Error: provide --start or --last-4-weeks.")
    ratio = args.load_per_hour
    if args.start_hours:
        ratio = start / args.start_hours
    sessions = None
    if args.sessions:
        vals = [int(x) for x in parse_numbers(args.sessions)]
        sessions = vals[0] if len(vals) == 1 else vals
    camp_weeks = [int(x) for x in parse_numbers(args.camp_weeks)] if args.camp_weeks else ()
    rows = compute_targets(
        start, args.ctl, args.atl if args.atl is not None else args.ctl,
        args.weeks, args.cycle, args.max_increase, args.max_ctl_ramp,
        args.recovery_drop, ratio, sessions, args.start_date,
        camp_weeks=camp_weeks, camp_factor=args.camp_factor,
    )
    if args.json_out:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
    else:
        print(format_targets(rows))


# ---------------------------------------------------------------- rebalance

def rebalance_week(sessions, target_load, target_duration=None, tolerance=0.05,
                   min_duration=30, max_duration_factor=2.0):
    sessions = [dict(s) for s in sessions]
    total = sum(s["load"] for s in sessions)
    report = {
        "before_load": total,
        "before_duration_min": sum(s["duration_min"] for s in sessions),
        "modified": None,
        "messages": [],
    }
    if abs(total - target_load) / target_load > tolerance:
        candidates = [s for s in sessions if s.get("adjustable")]
        if not candidates:
            candidates = sorted([s for s in sessions if not s.get("key")], key=lambda s: -s["duration_min"])
        if not candidates:
            report["messages"].append("No adjustable session (all are key sessions): adjust session count.")
        else:
            s = candidates[0]
            lpm = s["load"] / s["duration_min"]
            wanted = (s["load"] + target_load - total) / lpm
            max_bound = s["duration_min"] * max_duration_factor
            new_dur = round5(min(max(wanted, min_duration), max_bound))
            if wanted < min_duration or wanted > max_bound:
                report["messages"].append(
                    f"'{s['title']}' cannot absorb the full gap (bounds {min_duration} to "
                    f"{max_bound:.0f} min): add or remove a session."
                )
            old_vals = (s["duration_min"], s["load"])
            s["duration_min"] = new_dur
            s["load"] = round(new_dur * lpm)
            s["rebalanced"] = True
            report["modified"] = {"title": s["title"], "before": old_vals, "after": (s["duration_min"], s["load"])}
    after = sum(s["load"] for s in sessions)
    duration = sum(s["duration_min"] for s in sessions)
    report.update({
        "after_load": after,
        "after_duration_min": duration,
        "load_gap_pct": (after - target_load) / target_load * 100,
        "load_ok": abs(after - target_load) / target_load <= tolerance,
    })
    if target_duration:
        report["duration_gap_pct"] = (duration - target_duration) / target_duration * 100
        report["duration_ok"] = abs(duration - target_duration) / target_duration <= tolerance
    return sessions, report


def cmd_rebalance(args):
    d = read_json(args)
    sessions, r = rebalance_week(
        d["sessions"], d["target_load"], d.get("target_duration_min"), d.get("tolerance", 0.05)
    )
    if args.json_out:
        print(json.dumps({"sessions": sessions, "report": r}, ensure_ascii=False, indent=2))
        return
    print("| Day | Workout | Duration | Load | Key | Status |")
    print("|---|---|---|---|---|---|")
    for s in sessions:
        print(
            f"| {s.get('day', '')} | {s['title']} | {s['duration_min']} min | {s['load']} | "
            f"{'yes' if s.get('key') else ''} | {'rebalanced' if s.get('rebalanced') else ''} |"
        )
    print()
    print(
        f"Load: {r['before_load']:.0f} -> {r['after_load']:.0f} vs target {d['target_load']} "
        f"({r['load_gap_pct']:+.1f}%): {'OK' if r['load_ok'] else 'OUT OF TOLERANCE'}"
    )
    if "duration_ok" in r:
        print(
            f"Duration: {r['after_duration_min']} min vs target {d['target_duration_min']} min "
            f"({r['duration_gap_pct']:+.1f}%): {'OK' if r['duration_ok'] else 'OUT OF TOLERANCE'}"
        )
    for m in r["messages"]:
        print("Warning: " + m)
    if r["load_ok"] and r.get("duration_ok") is False:
        print("Warning: target load and target duration conflict for these sessions; review easy intensity, "
              "session count, or duration target.")


# ---------------------------------------------------------------- monotony

def compute_monotony(daily_loads, hard_days=()):
    if len(daily_loads) != 7:
        raise ValueError("Provide exactly 7 daily loads (Monday -> Sunday).")
    total = sum(daily_loads)
    mean = total / 7
    sd = statistics.pstdev(daily_loads)
    mono = None if sd == 0 else mean / sd
    strain = None if mono is None else total * mono
    hard = sorted(set(int(j) for j in hard_days))
    back_to_back = [(a, b) for a, b in zip(hard, hard[1:]) if b == a + 1]
    return {
        "total": total, "mean": mean, "stdev": sd, "monotony": mono, "strain": strain,
        "hard_days": len(hard), "consecutive_hard_days": back_to_back,
        "too_uniform": mono is not None and mono > 2,
    }


def cmd_monotony(args):
    loads = parse_numbers(args.loads)
    hard = parse_numbers(args.hard_days) if args.hard_days else []
    r = compute_monotony(loads, hard)
    if args.json_out:
        print(json.dumps(r, ensure_ascii=False, indent=2))
        return
    print(f"Weekly load: {r['total']:.0f} (mean {r['mean']:.1f}/day, SD {r['stdev']:.1f})")
    if r["monotony"] is None:
        print("Monotony: undefined (identical load every day).")
    else:
        print(f"Monotony: {r['monotony']:.2f}" + (" (> 2: week too uniform)" if r["too_uniform"] else ""))
        print(f"Strain: {r['strain']:.0f}")
    print(
        f"Hard days: {r['hard_days']}"
        + (f"; back-to-back: {', '.join(f'{a}-{b}' for a, b in r['consecutive_hard_days'])}"
           if r["consecutive_hard_days"] else "")
    )


# ---------------------------------------------------------------- thresholds: CP (cycling), CS (running), CSS (swimming)

def compute_cp(p3, p12, location, indoor_offset=0.0):
    """Two-point work-time model for cycling: Work = CP * t + W'."""
    if p3 <= p12:
        raise ValueError("3-min power must exceed 12-min power.")
    if not 0 <= indoor_offset < 0.5:
        raise ValueError("Indoor/outdoor offset must be between 0 and 0.5.")
    t3, t12 = 180, 720
    cp = (p12 * t12 - p3 * t3) / (t12 - t3)
    w_prime = (p3 - cp) * t3
    if location == "indoor":
        ftp_in, ftp_out = cp, cp / (1 - indoor_offset)
    else:
        ftp_out, ftp_in = cp, cp * (1 - indoor_offset)
    return {
        "cp": cp, "w_prime_kj": w_prime / 1000,
        "ftp_outdoor": round(ftp_out), "ftp_indoor": round(ftp_in),
        "test_location": location, "indoor_offset": indoor_offset,
    }


def cmd_cp(args):
    r = compute_cp(args.p3, args.p12, args.location, args.indoor_offset)
    if args.json_out:
        print(json.dumps(r, ensure_ascii=False, indent=2))
        return
    print(f"CP = ({args.p12:g} * 720 - {args.p3:g} * 180) / 540 = {r['cp']:.1f} W")
    print(f"W' = ({args.p3:g} - {r['cp']:.1f}) * 180 = {r['w_prime_kj']:.1f} kJ")
    if args.indoor_offset > 0:
        print(f"Test location: {args.location}; indoor/outdoor offset applied: {args.indoor_offset * 100:.0f}% "
              f"(verify with benchmark sessions and cooling/season).")
    else:
        print(f"Test location: {args.location}; no indoor/outdoor offset applied (--indoor-offset 0).")
    print(f"Recommended settings: Outdoor FTP = {r['ftp_outdoor']} W; Indoor FTP = {r['ftp_indoor']} W")
    if args.current_ftp:
        print(f"Outdoor FTP change: {(r['ftp_outdoor'] - args.current_ftp) / args.current_ftp * 100:+.1f}%")


def compute_cs(d_short_m, t_short_s, d_long_m, t_long_s):
    """Running Critical Speed (CS) & D': Distance = CS * t + D'."""
    if t_long_s <= t_short_s or d_long_m <= d_short_m:
        raise ValueError("Long effort must have greater duration and distance than short effort.")
    if d_short_m / t_short_s <= d_long_m / t_long_s:
        raise ValueError("Short effort speed must exceed long effort speed.")
    cs_ms = (d_long_m - d_short_m) / (t_long_s - t_short_s)
    d_prime_m = d_short_m - cs_ms * t_short_s
    pace_s_km = 1000 / cs_ms
    return {
        "cs_ms": round(cs_ms, 3),
        "cs_kmh": round(cs_ms * 3.6, 2),
        "threshold_pace_s_km": round(pace_s_km, 1),
        "threshold_pace": format_pace(pace_s_km, "/km"),
        "d_prime_m": round(d_prime_m, 1),
    }


def cmd_cs(args):
    t1, t2 = parse_time_s(args.t1), parse_time_s(args.t2)
    r = compute_cs(args.d1, t1, args.d2, t2)
    if args.json_out:
        print(json.dumps(r, ensure_ascii=False, indent=2))
        return
    print(f"CS = ({args.d2:g} - {args.d1:g}) / ({t2:g} - {t1:g}) = {r['cs_ms']:.3f} m/s ({r['cs_kmh']:.2f} km/h)")
    print(f"Threshold pace (CS): {r['threshold_pace']}")
    print(f"D' = {args.d1:g} - {r['cs_ms']:.3f} * {t1:g} = {r['d_prime_m']:.1f} m")
    if args.current_pace:
        cur_s = parse_time_s(args.current_pace)
        var = (cur_s / r["threshold_pace_s_km"] - 1) * 100
        print(f"Threshold speed change: {var:+.1f}% (vs {format_pace(cur_s, '/km')})")


def compute_css(t400_s, t200_s):
    """Swimming Critical Swim Speed (CSS): CSS = (400 - 200) / (t400 - t200)."""
    if t400_s <= t200_s:
        raise ValueError("400m time must exceed 200m time.")
    if t400_s / 2 <= t200_s:
        raise ValueError("200m pace must be faster than 400m pace.")
    css_ms = 200 / (t400_s - t200_s)
    sec_100m = 100 / css_ms
    return {
        "css_ms": round(css_ms, 3),
        "pace_100m_s": round(sec_100m, 1),
        "pace_100m": format_pace(sec_100m, "/100m"),
    }


def cmd_css(args):
    t400, t200 = parse_time_s(args.t400), parse_time_s(args.t200)
    r = compute_css(t400, t200)
    if args.json_out:
        print(json.dumps(r, ensure_ascii=False, indent=2))
        return
    print(f"CSS = 200 / ({t400:g} - {t200:g}) = {r['css_ms']:.3f} m/s")
    print(f"Swimming threshold pace (CSS): {r['pace_100m']}")


# ---------------------------------------------------------------- HYROX race & simulation analysis

HYROX_STATIONS = [
    "SkiErg", "Sled Push", "Sled Pull", "Burpee Broad Jumps",
    "Rowing", "Farmers Carry", "Sandbag Lunges", "Wall Balls",
]


def format_duration_hms(seconds):
    total = round(seconds)
    h, rem = divmod(total, 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def analyze_hyrox(runs_s, stations_s=None, roxzone_s=0.0, threshold_pace_s=None):
    """Analyze HYROX race or simulation splits (8 x 1 km runs + optional 8 stations & Roxzone).

    Computes run/station/Roxzone share, Run 1 over-pacing, 1st-half vs 2nd-half
    run decay, worst compromised-running splits, and penalty vs fresh threshold pace.
    """
    if len(runs_s) != 8:
        raise ValueError("Provide exactly 8 run splits (1 km each).")
    if stations_s is not None and len(stations_s) != 8:
        raise ValueError("If provided, stations must have exactly 8 splits.")

    total_run = sum(runs_s)
    total_stations = sum(stations_s) if stations_s else 0.0
    total_time = total_run + total_stations + roxzone_s

    mean_all = _mean(runs_s)
    mean_r2_8 = _mean(runs_s[1:])
    first_half = _mean(runs_s[:4])
    second_half = _mean(runs_s[4:])

    r1_overpace_s = mean_r2_8 - runs_s[0]  # positive means Run 1 was faster than Runs 2-8
    half_fade_s = second_half - first_half
    worst_idx = max(range(8), key=lambda i: runs_s[i])
    worst_prev_station = None if worst_idx == 0 else HYROX_STATIONS[worst_idx - 1]

    flags = []
    if r1_overpace_s > 10:
        flags.append(f"Run 1 over-paced by {r1_overpace_s:.0f} s/km vs Runs 2-8 mean")
    if half_fade_s > 10:
        flags.append(f"second-half run decay of +{half_fade_s:.0f} s/km (Runs 5-8 vs 1-4)")
    if roxzone_s and total_time and roxzone_s / total_time > 0.08:
        flags.append(f"Roxzone accounts for {roxzone_s / total_time * 100:.1f}% of race (> 8%: easy time to save)")

    compromised_penalty_s = None
    compromised_penalty_pct = None
    if threshold_pace_s:
        compromised_penalty_s = mean_r2_8 - threshold_pace_s
        compromised_penalty_pct = compromised_penalty_s / threshold_pace_s * 100
        if compromised_penalty_pct > 15:
            flags.append(
                f"high compromised-running penalty (+{compromised_penalty_s:.0f} s/km, "
                f"+{compromised_penalty_pct:.1f}% vs fresh threshold pace)"
            )

    res = {
        "total_time_s": round(total_time, 1),
        "total_time": format_duration_hms(total_time),
        "run_total_s": round(total_run, 1),
        "run_total": format_duration_hms(total_run),
        "run_share_pct": round(total_run / total_time * 100, 1) if total_time else None,
        "station_total_s": round(total_stations, 1) if stations_s else None,
        "station_total": format_duration_hms(total_stations) if stations_s else None,
        "station_share_pct": round(total_stations / total_time * 100, 1) if stations_s and total_time else None,
        "roxzone_s": round(roxzone_s, 1) if roxzone_s else 0.0,
        "roxzone_share_pct": round(roxzone_s / total_time * 100, 1) if roxzone_s and total_time else 0.0,
        "mean_run_pace": format_pace(mean_all, "/km"),
        "mean_runs_2_8_pace": format_pace(mean_r2_8, "/km"),
        "run1_vs_runs2_8_s": round(r1_overpace_s, 1),
        "second_vs_first_half_s": round(half_fade_s, 1),
        "slowest_run": {
            "run_number": worst_idx + 1,
            "pace": format_pace(runs_s[worst_idx], "/km"),
            "after_station": worst_prev_station,
        },
        "compromised_penalty_s": round(compromised_penalty_s, 1) if compromised_penalty_s is not None else None,
        "compromised_penalty_pct": round(compromised_penalty_pct, 1) if compromised_penalty_pct is not None else None,
        "flags": flags,
    }
    if stations_s:
        slowest_st_idx = max(range(8), key=lambda i: stations_s[i])
        res["slowest_station"] = {
            "station": HYROX_STATIONS[slowest_st_idx],
            "time": format_duration_hms(stations_s[slowest_st_idx]),
        }
    return res


def cmd_hyrox(args):
    runs = [parse_time_s(t) for t in re.split(r"[,;\s]+", args.runs.strip()) if t]
    stations = ([parse_time_s(t) for t in re.split(r"[,;\s]+", args.stations.strip()) if t]
                if args.stations else None)
    roxzone = parse_time_s(args.roxzone) if args.roxzone else 0.0
    threshold = parse_time_s(args.threshold_pace) if args.threshold_pace else None
    r = analyze_hyrox(runs, stations, roxzone, threshold)
    if args.json_out:
        print(json.dumps(r, ensure_ascii=False, indent=2))
        return
    print(f"Total time: {r['total_time']} | Runs: {r['run_total']} ({r['run_share_pct']}%)")
    if r["station_total"] is not None:
        print(f"Stations: {r['station_total']} ({r['station_share_pct']}%) | "
              f"Slowest station: {r['slowest_station']['station']} ({r['slowest_station']['time']})")
    if r["roxzone_s"]:
        print(f"Roxzone: {format_duration_hms(r['roxzone_s'])} ({r['roxzone_share_pct']}%)")
    print(f"Run pace: mean {r['mean_run_pace']} | Runs 2-8 mean {r['mean_runs_2_8_pace']} | "
          f"Run 1 vs R2-8: {r['run1_vs_runs2_8_s']:+.0f} s/km | 2nd vs 1st half: {r['second_vs_first_half_s']:+.0f} s/km")
    after = f" (after {r['slowest_run']['after_station']})" if r["slowest_run"]["after_station"] else ""
    print(f"Slowest run: Run {r['slowest_run']['run_number']} at {r['slowest_run']['pace']}{after}")
    if r["compromised_penalty_s"] is not None:
        print(f"Compromised-running penalty vs threshold pace: "
              f"{r['compromised_penalty_s']:+.0f} s/km ({r['compromised_penalty_pct']:+.1f}%)")
    if r["flags"]:
        print("Diagnostics:")
        for fl in r["flags"]:
            print("  - " + fl)
    else:
        print("Diagnostics: well-paced run splits and transitions.")


# ---------------------------------------------------------------- workout linter

RE_DUR = re.compile(r"^(?:(\d+)h)?(?:(\d+)(?:m|min))?(?:(\d+)s)?$")
RE_DUR_HM = re.compile(r"^(\d+)h(\d+)$")
RE_DUR_QUOTE = re.compile(r"^(?:(\d+)')?(?:(\d+)\")?$")
RE_DISTANCE = re.compile(r"^\d+(?:\.\d+)?(?:mtr|meters|km|mi|yd|yards)$", re.IGNORECASE)
RE_SWIM_M_AMBIGUOUS = re.compile(r"^(\d+)m$")

RE_ANCHORS = [
    re.compile(r"^\d+(?:\.\d+)?%?-\d+(?:\.\d+)?%$"),                 # 88-92%
    re.compile(r"^\d+(?:\.\d+)?%$"),                                  # 75%
    re.compile(r"^[Zz]\d(?:-[Zz]?\d)?$"),                             # Z2 or Z2-Z3
    re.compile(r"^\d+(?:-\d+)?[wW]$"),                                # 250w
    re.compile(r"^\d+(?:-\d+)?bpm$"),                                 # 145bpm
    re.compile(r"^\d+:\d{2}(?:-\d+:\d{2})?(?:/km|/100m|/mi)?$"),      # pace
]
RE_REPEAT = re.compile(r"^(?!-)(?:.*\s)?(\d+)\s*[xX]$")
RE_PAREN = re.compile(r"\([^)]*(?:\d\s*[wW]\b|bpm|[Zz]one|\b[Zz]\d|/km|/100m)[^)]*\)")
RE_PCT_FTP = re.compile(r"%\s*FTP", re.IGNORECASE)


def duration_seconds(tok):
    m = RE_DUR_QUOTE.match(tok)
    if m and any(m.groups()):
        return int(m.group(1) or 0) * 60 + int(m.group(2) or 0)
    m = RE_DUR_HM.match(tok)
    if m:
        return int(m.group(1)) * 3600 + int(m.group(2)) * 60
    m = RE_DUR.match(tok)
    if not m or not any(m.groups()):
        return None
    h, mi, s = (int(g) if g else 0 for g in m.groups())
    return h * 3600 + mi * 60 + s


def is_step(line):
    return line.lstrip().startswith("-")


def lint_workout(text, workout_type="cycling", expected_duration=None):
    errors, warnings = [], []
    lines = text.splitlines()

    if workout_type in ("strength", "hyrox"):
        for i, line in enumerate(lines, 1):
            if is_step(line):
                errors.append(f"line {i}: leading dash forbidden in {workout_type} sessions ('{line.strip()}')")
            if workout_type == "strength" and re.search(r"\d%|\b[Zz]\d\b", line):
                warnings.append(f"line {i}: endurance intensity (% or zone) found in a strength session")
        if workout_type == "hyrox":
            for symbol, name in (("🎯", "GOAL"), ("🍌", "FUELING"), ("📋", "CUES")):
                if symbol not in text:
                    warnings.append(f"section {symbol} {name} missing from description")
        elif not any(re.search(r"\d+\s*[x×]\s*\d+", line) for line in lines):
            warnings.append("no exercise in sets x reps format (e.g. 3x8)")
        if not re.search(r"RIR|RPE", text):
            warnings.append("effort cue missing (RIR or RPE)")
        return {"errors": errors, "warnings": warnings, "duration_min": None}

    for symbol, name in (("🎯", "GOAL"), ("🍌", "FUELING"), ("📋", "CUES")):
        if symbol not in text:
            warnings.append(f"section {symbol} {name} missing from description")
    if RE_PCT_FTP.search(text):
        errors.append("'% FTP' found: write bare '%' only (e.g. 88-92%)")

    total, repeat, in_block = 0, 1, False
    first_step = None
    has_distance_steps = False

    for i, raw in enumerate(lines):
        num, line = i + 1, raw.strip()
        if not line:
            in_block, repeat = False, 1
            continue
        m_rep = RE_REPEAT.match(line)
        if m_rep and not is_step(line):
            if i > 0 and lines[i - 1].strip():
                errors.append(f"line {num}: blank line required before repeated block '{line}'")
            repeat, in_block = int(m_rep.group(1)), True
            if first_step is None:
                first_step = i
            continue
        if not is_step(line):
            if in_block:
                errors.append(f"line {num}: blank line required after repeated block")
                in_block, repeat = False, 1
            continue
        if first_step is None:
            first_step = i
            if i > 0 and lines[i - 1].strip() and not is_step(lines[i - 1]):
                first_step = i - 1  # section header (e.g. "Warmup")

        tokens = line.lstrip("-").split()

        # In swimming, intervals.icu parses "400m" as 400 minutes -> must write "400mtr"
        if workout_type == "swimming":
            for t in tokens:
                m_sw = RE_SWIM_M_AMBIGUOUS.match(t)
                if m_sw and int(m_sw.group(1)) >= 25 and int(m_sw.group(1)) % 25 == 0:
                    errors.append(
                        f"line {num}: '{t}' in swimming is parsed as minutes by intervals.icu; "
                        f"write '{m_sw.group(1)}mtr' for distance"
                    )

        durs = [d for d in (duration_seconds(t) for t in tokens) if d]
        is_dist = any(RE_DISTANCE.match(t) for t in tokens)
        if not durs and is_dist:
            has_distance_steps = True
            if workout_type == "cycling":
                warnings.append(f"line {num}: distance-based step, total duration cannot be summed")
            durs = [0]
        if not durs:
            errors.append(f"line {num}: dashed line without duration or distance ('{line}')")
            continue
        if len(durs) > 1:
            warnings.append(f"line {num}: multiple durations on the same step")

        anchors = [t for t in tokens if any(r.match(t) for r in RE_ANCHORS)]
        if not anchors and any(t.lower() in ("freeride", "rest") for t in tokens):
            anchors = ["freeride/rest"]
        if not anchors:
            errors.append(f"line {num}: step missing intensity anchor ('{line}')")
        elif len(anchors) > 1:
            errors.append(f"line {num}: multiple intensities on one step ({', '.join(anchors)})")
        if RE_PAREN.search(line):
            errors.append(f"line {num}: absolute target in parentheses, remove it ('{line}')")
        total += durs[0] * repeat

    if first_step is None:
        errors.append("no workout steps found")
    elif first_step > 0 and lines[first_step - 1].strip():
        errors.append("blank line required between description and workout steps")

    duration_min = None if (has_distance_steps and total == 0) else round(total / 60, 1)
    if expected_duration is not None and not has_distance_steps:
        if duration_min is not None and abs(duration_min - expected_duration) > 1:
            errors.append(f"expected duration {expected_duration:g} min, summed steps {duration_min:g} min")
    return {
        "errors": errors, "warnings": warnings,
        "duration_min": duration_min, "has_distance_steps": has_distance_steps,
    }


def cmd_lint(args):
    r = lint_workout(read_text(args), args.type, args.expected_duration)
    if args.json_out:
        print(json.dumps(r, ensure_ascii=False, indent=2))
    else:
        if r["duration_min"] is not None:
            note = " (excluding distance steps)" if r.get("has_distance_steps") else ""
            print(f"Total step duration: {r['duration_min']:g} min{note}")
        for e in r["errors"]:
            print("ERROR: " + e)
        for w in r["warnings"]:
            print("Warning: " + w)
        print("OK" if not r["errors"] else f"{len(r['errors'])} error(s) to fix")
    sys.exit(1 if r["errors"] else 0)


# ---------------------------------------------------------------- wellness (HRV, RHR, sleep)

def evaluate_wellness(days, ref_window=28, min_ref=14, rhr_7d_threshold=3.0, rhr_day_threshold=5.0):
    """Objective daily wellness flags from chronological daily entries.

    HRV: 7-day rolling mean of ln(rMSSD) vs normal range = mean ± 0.5 SD of the
    preceding `ref_window` nights (excluding the last 7 days; Plews / Vesterinen).
    Resting HR: 7-day mean and last night vs the same non-overlapping baseline.
    """
    n = len(days)
    res = {"days": n, "flags": [], "notes": []}

    def series(key):
        return [d.get(key) for d in days]

    def coverage(key, last=None):
        s = series(key)[-last:] if last else series(key)
        return sum(1 for x in s if x not in (None, 0)) / len(s) if s else 0

    res["coverage"] = {k: round(coverage(k), 2) for k in ("hrv", "rhr", "sleep_h")}

    # HRV
    hrv = series("hrv")
    ln = [math.log(x) if x else None for x in hrv]
    ref = [x for x in ln[-(7 + ref_window):-7] if x is not None] if n > 7 else []
    if len(ref) < min_ref:
        res["hrv"] = {"status": "baseline_unestablished",
                      "detail": f"{len(ref)} baseline nights out of {min_ref} required"}
        res["notes"].append("HRV: normal range not yet established, treat as weak signal.")
    else:
        m, sd = statistics.mean(ref), statistics.pstdev(ref)
        low, high = m - 0.5 * sd, m + 0.5 * sd

        def mean7(end):
            s = [x for x in ln[max(0, end - 7):end] if x is not None]
            return _mean(s) if len(s) >= 5 else None

        current = mean7(n)
        days_below = 0
        for k in range(n, max(n - 10, 7), -1):
            v = mean7(k)
            if v is not None and v < low:
                days_below += 1
            else:
                break
        latest = next((x for x in reversed(hrv) if x), None)
        ref42 = [x for x in hrv[-42:] if x]
        status = (
            "insufficient_7d_data" if current is None else
            "below_range" if current < low else
            "above_range" if current > high else "within_range"
        )
        res["hrv"] = {
            "status": status,
            "mean7_ms": None if current is None else round(math.exp(current), 1),
            "normal_range_ms": (round(math.exp(low), 1), round(math.exp(high), 1)),
            "consecutive_days_below": days_below,
            "latest_to_42d_ratio": round(latest / _mean(ref42), 2) if latest and ref42 else None,
        }
        if status == "below_range":
            res["flags"].append(f"7d HRV below normal range ({days_below} consecutive day(s))")
        s14 = [x for x in hrv[-14:] if x]
        if len(s14) >= 7:
            res["hrv"]["stability_14d"] = round(1 - statistics.pstdev(s14) / _mean(s14), 2)

    # Resting HR (non-overlapping baseline aligned with HRV)
    rhr = series("rhr")
    rhr7 = [x for x in rhr[-7:] if x]
    rhr_ref = [x for x in rhr[-(7 + ref_window):-7] if x] if n > 7 else []
    if len(rhr7) >= 5 and len(rhr_ref) >= min_ref:
        m7 = _mean(rhr7)
        m28 = _mean(rhr_ref)
        delta7 = m7 - m28
        latest_rhr = rhr[-1] if rhr and rhr[-1] else None
        delta_day = (latest_rhr - m28) if latest_rhr is not None else None
        acute_spike = delta_day is not None and delta_day >= rhr_day_threshold
        trend_high = delta7 > rhr_7d_threshold
        level = ("elevated" if (trend_high or acute_spike) else
                 "watch" if delta7 > 2 else "normal")
        res["rhr"] = {
            "mean7": round(m7, 1), "baseline28": round(m28, 1),
            "delta_7d": round(delta7, 1), "last_night": latest_rhr,
            "delta_day": round(delta_day, 1) if delta_day is not None else None,
            "level": level,
        }
        if trend_high:
            res["flags"].append(f"7d RHR +{delta7:.1f} bpm above 28d baseline")
        elif acute_spike:
            res["flags"].append(f"last-night RHR +{delta_day:.1f} bpm above 28d baseline")
    else:
        res["rhr"] = {"level": "insufficient_baseline"}

    # Sleep
    sleep = series("sleep_h")
    if sleep and sleep[-1]:
        s14 = [x for x in sleep[-14:] if x]
        res["sleep"] = {"last_night_h": sleep[-1], "mean14_h": round(_mean(s14), 2)}
        if sleep[-1] < 6:
            res["flags"].append(f"short sleep ({sleep[-1]:g} h)")
    else:
        res["sleep"] = {"last_night_h": None}

    for k, v in res["coverage"].items():
        if v < 0.8:
            res["notes"].append(f"low {k} coverage ({v:.0%}): reduced confidence")
    return res


def cmd_wellness(args):
    d = read_json(args)
    r = evaluate_wellness(
        d["days"] if isinstance(d, dict) else d,
        rhr_7d_threshold=args.rhr_7d_threshold,
        rhr_day_threshold=args.rhr_day_threshold,
    )
    if args.json_out:
        print(json.dumps(r, ensure_ascii=False, indent=2))
        return
    v = r["hrv"]
    if "mean7_ms" in v:
        print(
            f"HRV: 7d mean {v['mean7_ms']} ms, normal range {v['normal_range_ms'][0]}–{v['normal_range_ms'][1]} ms: "
            f"{v['status']}" + (f" ({v['consecutive_days_below']} consecutive day(s))"
                                if v["consecutive_days_below"] else "")
        )
        if v.get("stability_14d") is not None:
            print(f"     14d stability: {v['stability_14d']}; latest / 42d mean: {v['latest_to_42d_ratio']}")
    else:
        print(f"HRV: {v['status']} ({v['detail']})")
    f = r["rhr"]
    if "delta_7d" in f:
        extra = f", last night {f['last_night']} ({f['delta_day']:+})" if f["delta_day"] is not None else ""
        print(f"RHR: 7d mean {f['mean7']} bpm, 28d baseline {f['baseline28']} bpm, "
              f"7d delta {f['delta_7d']:+}{extra}: {f['level']}")
    else:
        print(f"RHR: {f['level']}")
    s = r["sleep"]
    if s.get("last_night_h"):
        print(f"Sleep: last night {s['last_night_h']:g} h, 14d mean {s['mean14_h']} h")
    print("Objective flags: " + ("; ".join(r["flags"]) if r["flags"] else "none"))
    for note in r["notes"]:
        print("Note: " + note)
    print("Cross-check with subjective feel (legs, warmup RPE, pain) under the green / amber / red rules.")


# ---------------------------------------------------------------- power curves & durability

ANCHORS = ["5s", "1m", "5m", "20m", "60m"]
DOMAINS = {"sprint/anaerobic": ["5s", "1m"], "VO2max": ["5m"], "threshold": ["20m"], "endurance": ["60m"]}


def parse_curve(text):
    curve = {}
    for chunk in re.split(r"[,;\s]+", text.strip()):
        if chunk:
            k, v = chunk.split(":")
            curve[k.strip()] = float(v)
    return curve


def compute_retention(fresh, fatigued):
    by_anchor = {a: fatigued[a] / fresh[a] * 100 for a in ANCHORS if a in fresh and a in fatigued and fresh[a]}
    domains = {}
    for name, keys in DOMAINS.items():
        vals = [by_anchor[a] for a in keys if a in by_anchor]
        if vals:
            domains[name] = _mean(vals)
    overall = statistics.median(domains.values()) if len(domains) >= 3 else None
    status = ("unknown" if overall is None else "robust" if overall >= 90 else
              "moderate" if overall >= 80 else "limited")
    limiter = min(domains, key=domains.get) if domains else None
    return {"by_anchor": by_anchor, "domains": domains, "overall": overall, "status": status, "limiter": limiter}


def cmd_durability(args):
    r = compute_retention(parse_curve(args.fresh), parse_curve(args.fatigued))
    prev = None
    if args.prev_fresh and args.prev_fatigued:
        prev = compute_retention(parse_curve(args.prev_fresh), parse_curve(args.prev_fatigued))
    if args.json_out:
        print(json.dumps({"current": r, "previous": prev}, ensure_ascii=False, indent=2))
        return
    print(f"Fatigued curve after {args.kj:g} kJ" if args.kj else "Fatigued curve")
    for a, v in r["by_anchor"].items():
        print(f"  {a}: {v:.1f}% of fresh power")
    for name, v in r["domains"].items():
        print(f"  {name}: {v:.1f}%")
    if r["overall"] is None:
        print("Overall retention: unavailable (fewer than 3 domains present)")
        return
    print(f"Overall retention (domain median): {r['overall']:.1f}% ({r['status']}; >= 90 robust, >= 80 moderate)")
    print(f"Primary limiter: {r['limiter']}")
    if prev and prev["overall"] is not None:
        d = r["overall"] - prev["overall"]
        trend = "improving" if d >= 2 else "declining" if d <= -2 else "stable"
        print(f"Change: {d:+.1f} pts ({trend}, ±2 pt significance threshold)")


def compute_progression(current, previous, stable_threshold=2.0, clear_threshold=5.0):
    res = {}
    for a in ANCHORS:
        if a in current and a in previous and previous[a]:
            d = (current[a] - previous[a]) / previous[a] * 100
            status = (
                "stable" if abs(d) < stable_threshold else
                ("clear gain" if d >= clear_threshold else "slight gain") if d > 0 else
                ("clear drop" if d <= -clear_threshold else "slight drop")
            )
            res[a] = {"change_pct": d, "status": status}
    return res


def cmd_progression(args):
    r = compute_progression(parse_curve(args.current), parse_curve(args.previous))
    if args.json_out:
        print(json.dumps(r, ensure_ascii=False, indent=2))
        return
    labels = {"5s": "5s (neuromuscular)", "1m": "1m (anaerobic)", "5m": "5m (VO2max)",
              "20m": "20m (threshold)", "60m": "60m (endurance)"}
    for a, v in r.items():
        print(f"{labels[a]}: {v['change_pct']:+.1f}% ({v['status']})")
    print("Benchmarks: < 2% = measurement noise; confirm via 2-indicator / 2-occurrence rule; "
          "keep indoor and outdoor comparisons separate.")


# ---------------------------------------------------------------- race-day projection

def project_days(ctl, atl, daily_loads):
    out = []
    for c in daily_loads:
        ctl += (c - ctl) * K_CTL
        atl += (c - atl) * K_ATL
        out.append((ctl, atl, ctl - atl))
    return out


def cmd_project(args):
    if args.daily_loads:
        loads = parse_numbers(args.daily_loads)
    elif args.weekly_loads:
        loads = [c / 7 for c in parse_numbers(args.weekly_loads) for _ in range(7)]
    else:
        sys.exit("Error: provide --daily-loads or --weekly-loads.")
    res = project_days(args.ctl, args.atl if args.atl is not None else args.ctl, loads)
    ctl, atl, tsb = res[-1]
    print(f"After {len(loads)} days: CTL ~ {ctl:.1f}, ATL ~ {atl:.1f}, TSB ~ {tsb:+.1f}")
    if args.target_tsb:
        low, high = parse_numbers(args.target_tsb)
        state = "too fatigued" if tsb < low else "too fresh" if tsb > high else "on target"
        print(f"Race-day TSB target: {low:+g} to {high:+g} -> {state}")
    print("Projection (~): actual training load and intervals.icu are authoritative.")


# ---------------------------------------------------------------- plan sanity checks

def check_plan(plan):
    weeks = plan["weeks"]
    out = []

    def add(name, status, detail, source):
        out.append({"check": name, "status": status, "detail": detail, "source": source})

    loads = [w["load"] for w in weeks]
    phases = [w.get("phase", "load") for w in weeks]

    # 1. Week-to-week load jump (planned training camps exempt up to 2.0x)
    jumps = [i + 1 for i in range(1, len(loads))
             if phases[i] != "camp" and loads[i] > 1.3 * max(loads[max(0, i - 3):i])]
    camp_extreme = [i + 1 for i in range(1, len(loads))
                    if phases[i] == "camp" and loads[i] > 2.0 * max(loads[max(0, i - 3):i])]
    add("Weekly load jump <= 1.3x highest of previous 3 weeks (camps exempt up to 2.0x)",
        "FAIL" if jumps else ("WARN" if camp_extreme else "OK"),
        (f"weeks {jumps}" if jumps else "") + (f" extreme camp weeks {camp_extreme}" if camp_extreme else ""),
        "coaching convention")

    # 2. CTL ramp (non-camp weeks; 3-week cap scales with weekly cap unless overridden)
    ctl0 = plan.get("start_ctl", 0)
    atl0 = plan.get("start_atl", ctl0)
    proj = project_weeks(ctl0, atl0, loads)
    ramps = [proj[0]["ctl"] - ctl0] + [proj[i]["ctl"] - proj[i - 1]["ctl"] for i in range(1, len(proj))]
    max_wk = plan.get("max_ctl_ramp", 5)
    max_3wk = plan.get("max_3wk_ctl_ramp", 3 * max_wk)
    over_wk = [i + 1 for i, m in enumerate(ramps) if phases[i] != "camp" and m > max_wk + 0.05]
    over_3wk = [i + 1 for i in range(2, len(ramps))
                if "camp" not in phases[i - 2:i + 1] and sum(ramps[i - 2:i + 1]) > max_3wk + 0.05]
    add(f"CTL ramp <= {max_wk:g}/week and <= {max_3wk:g} over 3 weeks (non-camp)",
        "FAIL" if over_wk or over_3wk else "OK",
        (f"weeks over: {over_wk} " if over_wk else "") + (f"3-week windows over: {over_3wk}" if over_3wk else ""),
        "methodology guardrails; Friel, Couzens")

    # 3. Peak vs start (non-camp weeks)
    non_camp_loads = [loads[i] for i, p in enumerate(phases) if p != "camp"] or loads
    ratio = max(non_camp_loads) / loads[0] if loads[0] else None
    add("Peak non-camp week <= 1.8x starting week",
        "OK" if ratio is not None and ratio <= 1.8 else "WARN",
        "" if ratio is None else f"ratio {ratio:.2f}", "published plans")

    # 4. Consecutive load/camp weeks
    streak, worst = 0, 0
    for p in phases:
        streak = streak + 1 if p in ("load", "camp") else 0
        worst = max(worst, streak)
    add("At most 3 consecutive load/camp weeks", "OK" if worst <= 3 else "WARN",
        f"{worst} consecutive", "coaching convention")

    # 4b. Planned training camp safety rules
    camp_idx = [i for i, p in enumerate(phases) if p == "camp"]
    if camp_idx:
        no_recovery = [i + 1 for i in camp_idx
                       if i + 1 < len(phases) and phases[i + 1] not in ("recovery", "taper")]
        unclosed = [i + 1 for i in camp_idx if i + 1 == len(phases)]
        back_to_back = [i + 1 for i in camp_idx if i + 1 in camp_idx]
        too_intense = [i + 1 for i in camp_idx
                       if ("easy_pct" in weeks[i] and weeks[i]["easy_pct"] < 75)
                       or weeks[i].get("above_threshold_pct", 0) > 10]
        details = []
        if no_recovery:
            details.append(f"week(s) {no_recovery} not followed by recovery")
        if unclosed:
            details.append(f"week(s) {unclosed} at end of block (schedule recovery next)")
        if back_to_back:
            details.append(f"consecutive camp weeks at {back_to_back}")
        if too_intense:
            details.append(f"high intensity during camp week(s) {too_intense}")
        status = "FAIL" if no_recovery else ("WARN" if (unclosed or back_to_back or too_intense) else "OK")
        add("Training camp: followed immediately by recovery and mostly easy (>= 75% easy, <= 10% above threshold)",
            status, "; ".join(details), "overload camp best practices")

    # 5. Taper
    idx = [i for i, p in enumerate(phases) if p == "taper"]
    if idx:
        peak = max(loads[i] for i, p in enumerate(phases) if p == "load") if "load" in phases else max(loads)
        drop = 1 - _mean([loads[i] for i in idx]) / peak
        hard_kept = all((weeks[i].get("hard_days") or 0) >= 1 for i in idx)
        ok = 1 <= len(idx) <= 3 and 0.41 <= drop <= 0.60 and hard_kept
        add("Taper: 1-3 weeks, load -41% to -60% from peak, >= 1 quality session/week kept",
            "OK" if ok else "WARN",
            f"{len(idx)} week(s), mean drop {drop:.0%}, quality kept: {'yes' if hard_kept else 'no'}",
            "Bosquet 2007; Mujika & Padilla 2003")

    # 6-7. Hard days and sessions per load week
    load_idx = [i for i, p in enumerate(phases) if p == "load"]
    if any("hard_days" in weeks[i] for i in load_idx):
        bad = [i + 1 for i in load_idx if not 1 <= weeks[i].get("hard_days", 0) <= 3]
        add("1-3 hard sessions per load week", "WARN" if bad else "OK",
            f"weeks {bad}" if bad else "", "Seiler 2013; Ronnestad 2015")
    if any("sessions" in weeks[i] for i in load_idx):
        bad = [i + 1 for i in load_idx if weeks[i].get("sessions", 0) < 3]
        add("At least 3 sessions per load week", "WARN" if bad else "OK",
            f"weeks {bad}" if bad else "", "published plans")

    # 8. Intensity distribution
    if any("easy_pct" in w for w in weeks):
        bad = [i + 1 for i, w in enumerate(weeks) if "easy_pct" in w and
               (w["easy_pct"] < 60 or w.get("above_threshold_pct", 0) > 15)]
        add(">= 60% easy time and <= 15% above threshold", "WARN" if bad else "OK",
            f"weeks {bad}" if bad else "", "Neal 2013; Oliveira 2024")

    # 9. Long event peak session (use last occurrence of longest session)
    if plan.get("event_duration_min"):
        longs = [w.get("longest_session_min", 0) for w in weeks]
        mx = max(longs)
        target = min(0.6 * plan["event_duration_min"], 360)
        last_idx = len(longs) - 1 - longs[::-1].index(mx)
        weeks_out = len(weeks) - 1 - last_idx
        ok = mx >= target and 2 <= weeks_out <= 5
        add("Long event: longest session >= 60% of event (6h cap), 2-5 weeks before race",
            "OK" if ok else "WARN", f"{mx:.0f} min, {weeks_out} week(s) out", "coaching convention")

    # 10a. Running single-session long-run spike (Frandsen et al., BJSM 2025)
    if any("longest_run_km" in w for w in weeks):
        lrs = [w.get("longest_run_km", 0) for w in weeks]
        bad_lr = [i + 1 for i in range(1, len(lrs))
                  if lrs[i] > 0 and max(lrs[max(0, i - 4):i]) > 0
                  and lrs[i] > 1.10 * max(lrs[max(0, i - 4):i])]
        add("Running: single longest run <= +10% vs max of previous 4 weeks (~30 days)",
            "WARN" if bad_lr else "OK", f"weeks {bad_lr}" if bad_lr else "",
            "Frandsen et al., BJSM 2025")

    # 10b. Running weekly mileage heuristic (low-evidence guardrail)
    if any("run_km" in w for w in weeks):
        kms = [w.get("run_km", 0) for w in weeks]
        bad_km = [i + 1 for i in range(1, len(kms))
                  if kms[i] > 0 and max(kms[max(0, i - 3):i]) > 0
                  and kms[i] > 1.15 * max(kms[max(0, i - 3):i])]
        add("Running: weekly km <= +15% vs highest of previous 3 weeks (low-evidence heuristic)",
            "WARN" if bad_km else "OK", f"weeks {bad_km}" if bad_km else "", "coaching heuristic")

    # 11. Trail vertical gain cap
    if any("vert_m" in w for w in weeks):
        verts = [w.get("vert_m", 0) for w in weeks]
        bad_v = [i + 1 for i in range(1, len(verts))
                 if verts[i] > 0 and max(verts[max(0, i - 3):i]) > 0
                 and verts[i] > 1.25 * max(verts[max(0, i - 3):i])]
        add("Trail: weekly vertical gain <= +25% vs highest of previous 3 weeks (eccentric load)",
            "WARN" if bad_v else "OK", f"weeks {bad_v}" if bad_v else "", "trail eccentric progression")

    return out


def cmd_check_plan(args):
    r = check_plan(read_json(args))
    if args.json_out:
        print(json.dumps(r, ensure_ascii=False, indent=2))
        return
    for c in r:
        print(f"[{c['status']}] {c['check']}" + (f": {c['detail']}" if c["detail"] else "")
              + f"  ({c['source']})")
    n_fail = sum(1 for c in r if c["status"] == "FAIL")
    print(f"{len(r)} checks, {n_fail} failure(s). Warnings are discussion points, not automatic errors.")


# ---------------------------------------------------------------- self-test

SAMPLE_CYCLING = """🎯 GOAL: threshold, 4x8m repeats

🍌 FUELING: Before: carb-rich meal 2h prior
During: 30-45 g/h

📋 CUES: cadence 85-95 rpm

Warmup
- 15m ramp 50-75%

Main set 4x
- 8m 88-92%
- 4m 55%

Cooldown
- 10m 50%
"""

SAMPLE_RUNNING = """🎯 GOAL: threshold cruise intervals

🍌 FUELING: Before: light snack 2h prior
During: water

📋 CUES: relaxed form, quick cadence

Warmup
- 15m 70-75% LTHR

Threshold 3x
- 8m 95-100% Pace
- 3m 75% Pace

Cooldown
- 10m Z1
"""

SAMPLE_SWIMMING = """🎯 GOAL: CSS threshold repeats

🍌 FUELING: Before: hydrate
During: bottle on pool deck

📋 CUES: long stroke, steady pacing

Warmup
- 300mtr Z1

Main set 4x
- 200mtr 100% Pace
- 30s rest

Cooldown
- 200mtr Z1
"""


def run_self_test():
    n = 0

    def ok(cond, msg):
        nonlocal n
        n += 1
        if not cond:
            raise AssertionError(msg)

    # Cycling CP
    r = compute_cp(360, 270, "outdoor", indoor_offset=0.10)
    ok(abs(r["cp"] - 240.0) < 0.01, "cycling CP")
    ok(abs(r["w_prime_kj"] - 21.6) < 0.01, "cycling W'")
    ok(r["ftp_outdoor"] == 240 and r["ftp_indoor"] == 216, "outdoor CP thresholds")
    r = compute_cp(360, 270, "indoor", indoor_offset=0.10)
    ok(r["ftp_indoor"] == 240 and r["ftp_outdoor"] == 267, "indoor CP thresholds")
    r = compute_cp(360, 270, "indoor", indoor_offset=0.0)
    ok(r["ftp_indoor"] == 240 and r["ftp_outdoor"] == 240, "zero offset")
    try:
        compute_cp(250, 300, "indoor")
        ok(False, "invalid CP not caught")
    except ValueError:
        ok(True, "")

    # Running CS
    r = compute_cs(1000, 200, 3000, 680)
    ok(abs(r["cs_ms"] - 4.167) < 0.01, f"CS: {r}")
    ok(r["threshold_pace"] == "4:00/km", f"CS pace: {r}")
    ok(abs(r["d_prime_m"] - 166.7) < 0.2, f"D': {r}")
    ok(parse_time_s("3:20") == 200 and parse_time_s("1:00:00") == 3600, "parse_time_s")
    try:
        compute_cs(1000, 250, 3000, 700)
        ok(False, "invalid CS not caught")
    except ValueError:
        ok(True, "")

    # Swimming CSS
    r = compute_css(380, 180)
    ok(abs(r["css_ms"] - 1.0) < 0.001 and r["pace_100m"] == "1:40/100m", f"CSS: {r}")
    try:
        compute_css(360, 180)
        ok(False, "invalid CSS not caught")
    except ValueError:
        ok(True, "")

    # Monotony
    r = compute_monotony([0, 45, 60, 0, 80, 30, 120], [3, 5, 7])
    ok(abs(r["monotony"] - 47.857 / statistics.pstdev([0, 45, 60, 0, 80, 30, 120])) < 1e-3, "monotony")
    ok(r["hard_days"] == 3 and r["consecutive_hard_days"] == [], "hard days")
    ok(compute_monotony([50] * 7)["monotony"] is None, "flat monotony")
    ok(compute_monotony([0, 0, 90, 90, 0, 0, 0], [3, 4])["consecutive_hard_days"] == [(3, 4)], "back-to-back")

    # Targets: 3:1 from 100, +10%, recovery -35%
    res = compute_targets(100, 15, 15, 8, "3:1", 0.10, 5, 0.35)
    ok([s["load"] for s in res] == [100, 110, 120, 80, 110, 120, 135, 85], f"3:1 targets: {[s['load'] for s in res]}")
    ok([s["phase"] for s in res] == (["load"] * 3 + ["recovery"]) * 2, "phases")
    res = compute_targets(400, 20, 20, 1, "3:1", 0.10, 5, 0.35)
    ok(res[0]["raw_load"] < 400 and abs(res[0]["ctl_ramp"] - 5) < 0.05, "CTL ramp cap")
    p = project_weeks(50, 50, [350])[0]
    ok(abs(p["ctl"] - 50) < 1e-9 and abs(p["tsb"]) < 1e-9, "steady projection")

    # Rebalance
    sessions = [
        {"title": "VO2max", "duration_min": 60, "load": 70, "key": True},
        {"title": "Endurance", "duration_min": 90, "load": 60},
        {"title": "Long ride", "duration_min": 120, "load": 80},
        {"title": "Recovery", "duration_min": 45, "load": 25},
    ]
    updated, r = rebalance_week(sessions, 300)
    ok(r["load_ok"] and r["modified"]["title"] == "Long ride", "rebalance")
    ok(updated[0]["duration_min"] == 60 and updated[0]["load"] == 70, "key workout untouched")
    _, r = rebalance_week(sessions, 240)
    ok(r["modified"] is None and r["load_ok"], "already within tolerance")

    # Workout linter
    r = lint_workout(SAMPLE_CYCLING, "cycling", 73)
    ok(not r["errors"] and r["duration_min"] == 73, f"valid cycling: {r}")
    r = lint_workout(SAMPLE_RUNNING, "running", 58)
    ok(not r["errors"] and r["duration_min"] == 58, f"valid running: {r}")
    r = lint_workout(SAMPLE_SWIMMING, "swimming")
    ok(not r["errors"] and r["has_distance_steps"], f"valid swimming: {r}")
    r = lint_workout(SAMPLE_SWIMMING.replace("300mtr", "300m"), "swimming")
    ok(any("300mtr" in e for e in r["errors"]), "ambiguous 300m in swim caught")
    r = lint_workout(SAMPLE_CYCLING.replace("- 8m 88-92%", "- 8m 88% (228w)"))
    ok(any("parentheses" in e for e in r["errors"]), "parentheses")
    r = lint_workout(SAMPLE_CYCLING.replace("- 4m 55%", "- 4m 55% % FTP"))
    ok(any("% FTP" in e for e in r["errors"]), "% FTP")
    r = lint_workout(SAMPLE_CYCLING.replace("- 15m ramp 50-75%\n\n", "- 15m ramp 50-75%\n"))
    ok(any("blank line required before" in e for e in r["errors"]), "blank line before repeat")
    r = lint_workout(SAMPLE_CYCLING.replace("📋 CUES: cadence 85-95 rpm", "- cadence 85-95 rpm"))
    ok(any("without duration" in e for e in r["errors"]), "dash in description")
    r = lint_workout(SAMPLE_CYCLING.replace("- 10m 50%", "- 10m 50% Z1"))
    ok(any("multiple intensities" in e for e in r["errors"]), "two intensities")
    r = lint_workout(SAMPLE_CYCLING, "cycling", 60)
    ok(any("expected duration" in e for e in r["errors"]), "duration mismatch")
    r = lint_workout("Core\nBulgarian split squat 3x8 per leg, RIR 2\n", "strength")
    ok(not r["errors"] and not r["warnings"], "valid strength")
    r = lint_workout("- Squat 3x8\n", "strength")
    ok(r["errors"], "strength with dash")
    ok(duration_seconds("5'") == 300 and duration_seconds('1\'30"') == 90 and duration_seconds('30"') == 30, "quote durations")
    r = lint_workout(SAMPLE_CYCLING.replace("- 10m 50%", "- 10m freeride"), "cycling", 73)
    ok(not r["errors"], f"freeride: {r}")
    r = lint_workout(SAMPLE_CYCLING.replace("- 10m 50%", "- 5km 50%"))
    ok(not r["errors"] and any("distance-based" in w for w in r["warnings"]), "distance step in cycling")
    r = lint_workout(SAMPLE_CYCLING.replace("- 10m 50%", "- 10m 70% HR 200w"))
    ok(any("multiple intensities" in e for e in r["errors"]), "mixed metrics")
    ok(duration_seconds("1h30m") == 5400 and duration_seconds("1h30") == 5400
       and duration_seconds("90s") == 90 and duration_seconds("m") is None, "durations")

    # Wellness: non-overlapping HRV & RHR baseline + acute spike
    import random
    random.seed(1)
    days = [{"hrv": 55 + random.uniform(-4, 4), "rhr": 52, "sleep_h": 7.5} for _ in range(28)]
    days += [{"hrv": 42 + random.uniform(-2, 2), "rhr": 56, "sleep_h": 7.0} for _ in range(6)]
    days += [{"hrv": 41, "rhr": 57, "sleep_h": 5.5}]
    r = evaluate_wellness(days)
    ok(r["hrv"]["status"] == "below_range" and r["hrv"]["consecutive_days_below"] >= 1, "HRV below range")
    ok(r["rhr"]["baseline28"] == 52.0 and r["rhr"]["delta_7d"] > 3.0, f"non-overlapping RHR: {r['rhr']}")
    ok(r["rhr"]["level"] == "elevated", "elevated RHR")
    ok(len(r["flags"]) == 3, f"three flags: {r['flags']}")

    days_spike = [{"hrv": 55, "rhr": 52, "sleep_h": 7.5} for _ in range(34)]
    days_spike.append({"hrv": 55, "rhr": 58, "sleep_h": 7.5})
    r = evaluate_wellness(days_spike)
    ok(r["rhr"]["level"] == "elevated" and any("last-night" in f for f in r["flags"]), f"acute RHR spike: {r}")

    r = evaluate_wellness([{"hrv": 55, "rhr": 52, "sleep_h": 7} for _ in range(10)])
    ok(r["hrv"]["status"] == "baseline_unestablished" and not r["flags"], "unestablished baseline")

    # Durability
    fresh = {"5s": 900, "1m": 500, "5m": 330, "20m": 270, "60m": 240}
    fatigued = {"5s": 850, "1m": 460, "5m": 300, "20m": 235, "60m": 200}
    r = compute_retention(fresh, fatigued)
    ok(abs(r["overall"] - (87.037 + 90.909) / 2) < 0.01 and r["status"] == "moderate", "retention")
    ok(r["limiter"] == "endurance", "limiter")
    ok(compute_retention({"5m": 300}, {"5m": 280})["status"] == "unknown", "incomplete retention")

    # Power curve progression
    r = compute_progression({"5m": 340, "20m": 271, "60m": 226}, {"5m": 330, "20m": 270, "60m": 240})
    ok(r["5m"]["status"] == "slight gain" and r["20m"]["status"] == "stable"
       and r["60m"]["status"] == "clear drop", "progression")

    # Daily projection
    ok(abs(project_days(40, 40, [40] * 10)[-1][2]) < 1e-9, "daily projection")

    # Plan checks
    r = check_plan({"start_ctl": 15, "weeks": [
        {"load": c, "phase": p} for c, p in zip([100, 110, 120, 80], ["load"] * 3 + ["recovery"])
    ]})
    ok(all(c["status"] == "OK" for c in r), f"valid plan: {r}")
    r = check_plan({"start_ctl": 15, "weeks": [{"load": 100}, {"load": 140}]})
    ok(r[0]["status"] == "FAIL", "weekly jump fail")
    r = check_plan({"start_ctl": 40, "weeks": [
        {"load": 300, "phase": "load"}, {"load": 300, "phase": "load"},
        {"load": 150, "phase": "taper", "hard_days": 1}, {"load": 130, "phase": "taper", "hard_days": 1},
    ]})
    ok(any(c["check"].startswith("Taper") and c["status"] == "OK" for c in r), "taper check")
    r = check_plan({"start_ctl": 15, "weeks": [{"load": 600}]})
    ok(r[1]["status"] == "FAIL", "excessive CTL ramp")

    # 3-week CTL cap scales with max_ctl_ramp = 7 (3 weeks * +6 = +18 <= 21)
    r = check_plan({"start_ctl": 40, "max_ctl_ramp": 7, "weeks": [{"load": 530}, {"load": 570}, {"load": 610}]})
    ok(r[1]["status"] == "OK", f"scaled 3-week CTL cap: {r[1]}")

    # Last occurrence of longest session (2 equal peaks -> second one is 3 weeks out)
    r = check_plan({"start_ctl": 40, "event_duration_min": 300, "weeks": [
        {"load": 300, "longest_session_min": 180},
        {"load": 300, "longest_session_min": 120},
        {"load": 300, "longest_session_min": 180},
        {"load": 250, "longest_session_min": 120},
        {"load": 180, "longest_session_min": 90},
        {"load": 150, "longest_session_min": 60},
    ]})
    ok(any(c["check"].startswith("Long event") and c["status"] == "OK" for c in r), f"last long session: {r}")

    # Running single-session long-run cap (Frandsen 2025), weekly km, and trail vertical gain caps
    r = check_plan({"start_ctl": 30, "weeks": [
        {"load": 250, "run_km": 40, "longest_run_km": 16, "vert_m": 800},
        {"load": 270, "run_km": 52, "longest_run_km": 20, "vert_m": 1200},
    ]})
    ok(any("single longest run" in c["check"] and c["status"] == "WARN" for c in r), "longest run > +10% warns")
    ok(any("weekly km" in c["check"] and c["status"] == "WARN" for c in r), "running km jump")
    ok(any("Trail:" in c["check"] and c["status"] == "WARN" for c in r), "trail vert jump")
    r_ok = check_plan({"start_ctl": 30, "weeks": [
        {"load": 250, "longest_run_km": 16},
        {"load": 265, "longest_run_km": 17.5},
    ]})
    ok(any("single longest run" in c["check"] and c["status"] == "OK" for c in r_ok), "longest run <= +10% OK")

    # Training camp weeks in targets and check-plan
    res = compute_targets(300, 45, 45, 4, "3:1", 0.10, 5, 0.35, camp_weeks=[3], camp_factor=1.5)
    ok([s["phase"] for s in res] == ["load", "load", "camp", "recovery"], f"camp phases: {[s['phase'] for s in res]}")
    ok(res[2]["load"] > res[1]["load"] * 1.3 and res[3]["load"] < res[2]["load"] * 0.6, f"camp load/recovery: {res}")

    r = check_plan({"start_ctl": 45, "weeks": [
        {"load": 300, "phase": "load"},
        {"load": 330, "phase": "load"},
        {"load": 520, "phase": "camp", "easy_pct": 85, "above_threshold_pct": 5},
        {"load": 240, "phase": "recovery"},
    ]})
    ok(all(c["status"] == "OK" for c in r), f"valid camp plan: {r}")

    r = check_plan({"start_ctl": 45, "weeks": [
        {"load": 300, "phase": "load"},
        {"load": 500, "phase": "camp", "easy_pct": 85},
        {"load": 320, "phase": "load"},
    ]})
    ok(any(c["check"].startswith("Training camp") and c["status"] == "FAIL" for c in r), "camp without recovery fails")

    r = check_plan({"start_ctl": 45, "weeks": [
        {"load": 300, "phase": "load"},
        {"load": 500, "phase": "camp", "easy_pct": 60, "above_threshold_pct": 18},
        {"load": 220, "phase": "recovery"},
    ]})
    ok(any(c["check"].startswith("Training camp") and c["status"] == "WARN" for c in r), "too-intense camp warns")

    # HYROX analysis and linter
    runs = [parse_time_s(t) for t in ["4:05", "4:25", "4:45", "4:30", "4:50", "4:35", "4:40", "5:05"]]
    stations = [parse_time_s(t) for t in ["4:10", "3:15", "4:00", "4:20", "4:15", "2:00", "4:30", "5:30"]]
    r = analyze_hyrox(runs, stations, roxzone_s=360, threshold_pace_s=240)
    ok(abs(r["run_share_pct"] - 49.3) < 0.1 and abs(r["run_share_pct"] + r["station_share_pct"] + r["roxzone_share_pct"] - 100.0) < 0.2,
       f"hyrox share: {r}")
    ok(r["slowest_run"]["run_number"] == 8 and r["slowest_run"]["after_station"] == "Sandbag Lunges", f"slowest run: {r}")
    ok(any("Run 1 over-paced" in f for f in r["flags"]), f"run 1 over-pacing flag: {r['flags']}")
    ok(any("second-half run decay" in f for f in r["flags"]), f"2nd-half decay flag: {r['flags']}")
    ok(any("compromised-running penalty" in f for f in r["flags"]), f"compromised penalty flag: {r['flags']}")
    r_hl = lint_workout("🎯 GOAL: hybrid\n🍌 FUELING: gel\n📋 CUES: RPE 8\n\n4x 1km + 25m Sled Push 152 kg\n", "hyrox")
    ok(not r_hl["errors"] and not r_hl["warnings"], f"valid hyrox lint: {r_hl}")
    r_hl_bad = lint_workout("- 25m Sled Push\n", "hyrox")
    ok(bool(r_hl_bad["errors"]), "hyrox leading dash caught")

    print(f"All tests passed ({n}). coach_tools.py version {VERSION}.")


# ---------------------------------------------------------------- CLI

def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = p.add_subparsers(dest="command", required=True)

    c = sp.add_parser("targets", help="weekly block targets and CTL / TSB projection")
    c.add_argument("--start", type=float, help="starting weekly load")
    c.add_argument("--last-4-weeks", help="actual weekly loads from recent weeks, e.g. 120,140,130,150")
    c.add_argument("--ctl", type=float, required=True, help="current CTL (from intervals.icu)")
    c.add_argument("--atl", type=float, help="current ATL (defaults to CTL)")
    c.add_argument("--weeks", type=int, required=True)
    c.add_argument("--cycle", default="3:1", help="load:recovery ratio (e.g. 3:1 or 2:1)")
    c.add_argument("--max-increase", type=float, default=0.10, help="max week-to-week load increase (0.10 = 10%%)")
    c.add_argument("--max-ctl-ramp", type=float, default=5, help="max CTL ramp per week (5 return/run, 7-8 loaded bike)")
    c.add_argument("--recovery-drop", type=float, default=0.35, help="recovery week drop (0.30 to 0.40)")
    c.add_argument("--start-hours", type=float, help="starting weekly hours (to estimate hours)")
    c.add_argument("--load-per-hour", type=float, help="average load per hour (if --start-hours omitted)")
    c.add_argument("--sessions", help="sessions per week, e.g. 4 or 3,4,4,3")
    c.add_argument("--start-date", help="Monday of week 1 (YYYY-MM-DD)")
    c.add_argument("--camp-weeks", help="1-indexed planned training camp week(s), e.g. 3 (auto-followed by recovery)")
    c.add_argument("--camp-factor", type=float, default=1.35, help="load multiplier on camp week(s) (default: 1.35)")
    c.add_argument("--json-out", action="store_true")
    c.set_defaults(f=cmd_targets)

    c = sp.add_parser("rebalance", help="check and rebalance a week of workouts to ±5%% of target")
    c.add_argument("--json", help='{"target_load": 300, "target_duration_min": 360, "sessions": [{"day": "Tue", '
                                  '"title": "...", "duration_min": 60, "load": 50, "key": true}]}')
    c.add_argument("--file")
    c.add_argument("--json-out", action="store_true")
    c.set_defaults(f=cmd_rebalance)

    c = sp.add_parser("monotony", help="Foster monotony, strain, and consecutive hard days")
    c.add_argument("--loads", required=True, help="7 daily loads, Monday -> Sunday, rest = 0")
    c.add_argument("--hard-days", help="hard day indices (1 = Monday), e.g. 2,4,6")
    c.add_argument("--json-out", action="store_true")
    c.set_defaults(f=cmd_monotony)

    c = sp.add_parser("cp", help="cycling CP & W' (3-min and 12-min tests)")
    c.add_argument("--p3", type=float, required=True, help="mean power over 3-min test (W)")
    c.add_argument("--p12", type=float, required=True, help="mean power over 12-min test (W)")
    c.add_argument("--location", choices=["indoor", "outdoor"], required=True)
    c.add_argument("--indoor-offset", type=float, default=0.0,
                   help="optional indoor/outdoor power offset (e.g. 0.08 for 8%%, default 0)")
    c.add_argument("--current-ftp", type=float)
    c.add_argument("--json-out", action="store_true")
    c.set_defaults(f=cmd_cp)

    c = sp.add_parser("cs", help="running Critical Speed (CS) & D' from two maximal efforts")
    c.add_argument("--d1", type=float, required=True, help="short effort distance in meters (e.g. 1000)")
    c.add_argument("--t1", required=True, help="short effort time (e.g. 3:20 or 180)")
    c.add_argument("--d2", type=float, required=True, help="long effort distance in meters (e.g. 3000)")
    c.add_argument("--t2", required=True, help="long effort time (e.g. 11:20 or 720)")
    c.add_argument("--current-pace", help="current threshold pace for comparison (e.g. 4:10)")
    c.add_argument("--json-out", action="store_true")
    c.set_defaults(f=cmd_cs)

    c = sp.add_parser("css", help="swimming Critical Swim Speed (400m & 200m tests)")
    c.add_argument("--t400", required=True, help="400m time (e.g. 6:20 or 380)")
    c.add_argument("--t200", required=True, help="200m time (e.g. 3:00 or 180)")
    c.add_argument("--json-out", action="store_true")
    c.set_defaults(f=cmd_css)

    c = sp.add_parser("hyrox", help="HYROX race/simulation split & compromised-running analysis")
    c.add_argument("--runs", required=True, help="8 comma-separated 1 km splits, e.g. 4:10,4:25,4:40,...")
    c.add_argument("--stations", help="optional 8 station times in order (SkiErg -> Wall Balls)")
    c.add_argument("--roxzone", help="optional total Roxzone time (e.g. 5:30 or 330)")
    c.add_argument("--threshold-pace", help="fresh running threshold pace for compromised-running penalty (e.g. 4:00)")
    c.add_argument("--json-out", action="store_true")
    c.set_defaults(f=cmd_hyrox)

    c = sp.add_parser("lint", help="validate intervals.icu workout syntax")
    c.add_argument("--file", help="workout text file (defaults to stdin)")
    c.add_argument("--type", choices=["cycling", "running", "trail", "swimming", "hyrox", "strength", "endurance"],
                   default="cycling")
    c.add_argument("--expected-duration", type=float, help="planned duration in minutes")
    c.add_argument("--json-out", action="store_true")
    c.set_defaults(f=cmd_lint)

    c = sp.add_parser("wellness", help="HRV normal range, RHR trend/spike, sleep: daily objective flags")
    c.add_argument("--json", help='{"days": [{"date": "2026-12-01", "hrv": 55, "rhr": 52, "sleep_h": 7.4}, ...]} '
                                  '(chronological order, >= 35 days for a full baseline)')
    c.add_argument("--file")
    c.add_argument("--rhr-7d-threshold", type=float, default=3.0,
                   help="7-day RHR elevation flag threshold (default: +3 bpm)")
    c.add_argument("--rhr-day-threshold", type=float, default=5.0,
                   help="single-night acute RHR spike threshold (default: +5 bpm)")
    c.add_argument("--json-out", action="store_true")
    c.set_defaults(f=cmd_wellness)

    c = sp.add_parser("durability", help="power retention on fatigued power curves")
    c.add_argument("--fresh", required=True, help="fresh curve, e.g. 5s:900,1m:500,5m:330,20m:270,60m:240")
    c.add_argument("--fatigued", required=True, help="fatigued curve from intervals.icu, same durations")
    c.add_argument("--kj", type=float, help="work threshold of fatigued curve (kJ)")
    c.add_argument("--prev-fresh", help="previous period fresh curve")
    c.add_argument("--prev-fatigued", help="previous period fatigued curve")
    c.add_argument("--json-out", action="store_true")
    c.set_defaults(f=cmd_durability)

    c = sp.add_parser("progression", help="power-curve change between two equivalent periods")
    c.add_argument("--current", required=True, help="e.g. 5s:900,1m:500,5m:330,20m:270,60m:240")
    c.add_argument("--previous", required=True)
    c.add_argument("--json-out", action="store_true")
    c.set_defaults(f=cmd_progression)

    c = sp.add_parser("project", help="project CTL / ATL / TSB to race day (taper)")
    c.add_argument("--ctl", type=float, required=True)
    c.add_argument("--atl", type=float)
    c.add_argument("--daily-loads", help="day-by-day planned loads up to race day")
    c.add_argument("--weekly-loads", help="or weekly planned loads (spread across 7 days)")
    c.add_argument("--target-tsb", help="race-day TSB target range, e.g. 5,15")
    c.set_defaults(f=cmd_project)

    c = sp.add_parser("check-plan", help="sanity checks on a block or season plan")
    c.add_argument("--json", help='{"start_ctl": 25, "max_ctl_ramp": 5, "event_duration_min": 480, "weeks": '
                                  '[{"load": 220, "phase": "load|recovery|taper", "hard_days": 2, "sessions": 4, '
                                  '"longest_session_min": 90, "easy_pct": 80, "above_threshold_pct": 5, '
                                  '"run_km": 45, "longest_run_km": 18, "vert_m": 1000}]}')
    c.add_argument("--file")
    c.add_argument("--json-out", action="store_true")
    c.set_defaults(f=cmd_check_plan)

    c = sp.add_parser("test", help="run built-in self-test suite")
    c.set_defaults(f=lambda a: run_self_test())

    args = p.parse_args()
    args.f(args)


if __name__ == "__main__":
    main()
