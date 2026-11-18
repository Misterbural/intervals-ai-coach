---
name: coach-daily-adjustment
description: "Adjusts today's endurance workout based on feel, sleep, HRV, RHR, or schedule changes using green/amber/red readiness rules, then updates intervals.icu after approval."
---
# Daily Adjustment

1. Read today's planned workout(s) and recent wellness data (last 35+ days if available) from intervals.icu; run `coach_tools.py wellness` to evaluate objective flags (7d HRV vs normal range, 7d RHR trend & last-night spike, sleep).
2. Cross-check with what the athlete reports: subjective feel, legs, soreness, pain, time constraints, or schedule disruption. Remember: missing subjective fields in intervals.icu do not confirm everything is green.
3. Classify the day as **Green**, **Amber**, **Amber+**, or **Red** per `endurance-methodology.md` (and mechanical red flags in `running.md`/`trail.md` if applicable), naming the exact triggering flag(s).
4. Propose the adjusted workout and its ripple effect on the rest of the week (e.g. shifting a key session by 1–2 days without creating back-to-back hard days, never "making up" a missed key session the next day).
5. Only after explicit approval: lint the modified workout with `coach_tools.py lint`, update the exact calendar event by ID in intervals.icu, and summarize the change (date + title).
6. Injury-related pain or persistent localized tendon/bone pain: advise stopping and consulting a doctor or physio.
