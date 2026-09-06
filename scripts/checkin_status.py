"""SessionStart hook: one-line LifeOS status injected into the assistant's context.

Prints a compact status; when the last check-in is stale (or the weekly review
is due), appends an instruction for the assistant to offer the ritual in one
line. Must be fast and silent on any error: a broken hook must never break a
session.

Wire it up in .claude/settings.json (see docs/AI-INTEGRATION.md). Output is
plain ASCII so it survives any console encoding.
"""
import datetime
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FOCUS_MAX = 3  # keep in step with FOCUS_MAX in lifeos.html


def load(name):
    try:
        txt = (ROOT / "data" / f"{name}.json").read_text(encoding="utf-8").strip()
        return json.loads(txt) if txt else []
    except Exception:
        return []


def main():
    today = datetime.date.today()
    iso = today.isoformat()

    tasks = load("tasks")
    inbox = load("inbox")
    open_tasks = [t for t in tasks if t.get("status") == "todo"
                  and not (t.get("snooze") and t["snooze"] > iso)]
    focus = [t for t in open_tasks if t.get("focus")]
    overdue = [t for t in open_tasks if t.get("due") and t["due"] < iso]
    flagged = [t for t in open_tasks if t.get("rescope")]

    reviews = ROOT / "reviews"
    daily_dates = [p.stem for p in reviews.glob("*.md")
                   if re.fullmatch(r"\d{4}-\d{2}-\d{2}", p.stem)]
    days_since = None
    if daily_dates:
        try:
            days_since = (today - datetime.date.fromisoformat(max(daily_dates))).days
        except ValueError:
            pass

    weekly_files = sorted(reviews.glob("*-weekly.md"))
    weekly_stale = True
    if weekly_files:
        m = re.match(r"(\d{4})-W(\d{2})", weekly_files[-1].stem)
        if m:
            y, w = int(m.group(1)), int(m.group(2))
            cy, cw, _ = today.isocalendar()
            weekly_stale = (cy, cw) > (y, w + 1)  # stale if older than last week

    bits = [f"inbox {len(inbox)}", f"focus {len(focus)}/{FOCUS_MAX}"]
    if overdue:
        bits.append(f"{len(overdue)} overdue")
    if flagged:
        bits.append(f"{len(flagged)} flagged for rescope")
    when = ("today" if days_since == 0 else f"{days_since}d ago") if days_since is not None else "never"
    print(f"LifeOS: last check-in {when} | {' | '.join(bits)}.")

    if days_since is None or days_since >= 1:
        print("Assistant: before the main task, offer a quick /checkin in ONE short line "
              "(restart rule: no guilt, no listing what was missed). If the user declines or ignores it, drop it.")
    if weekly_stale and today.weekday() in (5, 6, 0):  # Sat/Sun/Mon
        print("Assistant: a weekly review hasn't run recently; mention /weekly-review in the same line.")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(0)
