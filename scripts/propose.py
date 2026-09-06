#!/usr/bin/env python3
"""propose.py: run a LifeOS ritual against ANY chat model, propose-only.

Works with anything that speaks the OpenAI chat-completions API, which today
means almost everything:

  Ollama        http://localhost:11434/v1        (default)
  LM Studio     http://localhost:1234/v1
  llama.cpp     http://localhost:8080/v1         (llama-server)
  vLLM / TGI    http://localhost:8000/v1
  OpenAI        https://api.openai.com/v1          key required
  Gemini        https://generativelanguage.googleapis.com/v1beta/openai   key required
  Anthropic     https://api.anthropic.com/v1       key required
  OpenRouter    https://openrouter.ai/api/v1       key required
  Mistral       https://api.mistral.ai/v1          key required

It READS data/*.json and PRINTS proposals as Markdown. It never writes to
data/. You (or an agent with judgment) apply what you agree with, in the app
or by editing the JSON. That is rule 11 in CLAUDE.md, and it is the reason a
7B model on your own machine is safe to point at your life.

Usage
  python scripts/propose.py checkin                 # classify inbox, propose focus 3
  python scripts/propose.py bites                   # 10-minute first moves for overdue tasks
  python scripts/propose.py week                    # weekly review draft, wins first
  python scripts/propose.py cards                   # a hand of learning cards to veto
  python scripts/propose.py checkin --out proposals/today.md

Configuration, by flag or environment variable
  --url    LIFEOS_LLM_URL    base URL ending in /v1   (default http://localhost:11434/v1)
  --model  LIFEOS_LLM_MODEL  model name               (default llama3.2)
  --key    LIFEOS_LLM_KEY    API key if the endpoint needs one
  --full-contract            send the whole of CLAUDE.md as the system prompt instead of
                             the compact built-in version (needs a bigger context window)
  --dry-run                  print the prompt and exit without calling the model

No dependencies beyond the Python standard library.
"""
import argparse
import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
FOCUS_MAX = 3  # keep in step with lifeos.html

COMPACT_CONTRACT = """You are the review engine for a personal LifeOS. You PROPOSE; a human applies.
You never claim to have written anything. Output plain Markdown, no preamble.

Design principles (these override your instincts):
- Nothing nags. Never mention how long something has been overdue, how many days were
  missed, or how many times a task was attempted. Missed days cost nothing.
- Overdue tasks are changed, not repeated: give them a real 10-minute first move ("bite"),
  rewrite the title so the payoff is immediate, or propose Someday.
- Caps: 3 focus tasks, 5 habits, 4 active goals, 4 active learning tracks.
- Blocked tasks (waiting on something) are not proposed for focus.
- Someday is a parking lot, not a graveyard. Surface at most one someday item, gently.
- Learning cards are 20-30 minutes, payoff stated first, one tangible win, pointed at a
  track's artifact (a thing that exists afterwards). Two swaps means scoped wrong: shrink.
- Wins before problems, always. Lead any review with what was completed.
- Be brief. One line of rationale per item. Propose and batch; do not ask questions one at
  a time. If you need one decision from the human, ask exactly one question at the end.
"""


def today() -> str:
    return dt.date.today().isoformat()


def load(name):
    try:
        txt = (DATA / f"{name}.json").read_text(encoding="utf-8").strip()
        return json.loads(txt) if txt else None
    except FileNotFoundError:
        return None
    except json.JSONDecodeError as e:
        sys.exit(f"data/{name}.json is not valid JSON: {e}")


def days_ago(n: int) -> str:
    return (dt.date.today() - dt.timedelta(days=n)).isoformat()


def slim_task(t):
    keep = ("id", "title", "status", "focus", "due", "goal", "blocked", "bite", "rescope", "snooze", "created")
    return {k: t[k] for k in keep if t.get(k) not in (None, False, "")}


# ---------------------------------------------------------------- ritual prompts
def build_checkin():
    iso = today()
    inbox = load("inbox") or []
    tasks = load("tasks") or []
    goals = [g for g in (load("goals") or []) if g.get("status") == "active"]
    habits = load("habits") or []
    open_tasks = [t for t in tasks if t.get("status") == "todo" and not (t.get("snooze") and t["snooze"] > iso)]
    someday = [t["title"] for t in tasks if t.get("status") == "someday"]
    habit_lines = [f'{h["name"]}: done today={iso in h.get("log", [])}, yesterday={days_ago(1) in h.get("log", [])}' for h in habits]
    ctx = {
        "today": iso,
        "inbox": [i["text"] for i in inbox],
        "open_tasks": [slim_task(t) for t in open_tasks],
        "goals": [{"id": g["id"], "title": g["title"], "next": g.get("next")} for g in goals],
        "habits": habit_lines,
        "someday_titles": someday[:20],
    }
    ask = f"""Run the daily check-in for {iso}. Produce, in this order:

1. **Status**: one sentence. Inbox count, open focus tasks, anything overdue (no durations).
2. **Inbox**: for each inbox line, one of task / someday / goal-material / habit-idea / delete, with a
   one-line reason. If task, propose a title with a verb. Present as a table.
3. **Focus {FOCUS_MAX}**: propose today's {FOCUS_MAX} focus tasks from open tasks and goal next-actions. Skip blocked
   tasks. One line each on why today.
4. **Goal pulse**: any active goal with no next action gets one proposed line. Otherwise skip.
5. **Someday** (optional, at most one): "still want this?" for one item, or skip.
6. **Ready to paste**: a JSON array of the proposed new tasks in this exact shape, so the human can
   drop them into data/tasks.json after review:
   {{"id":"t_xxxxxx","title":"...","status":"todo","focus":false,"created":"{iso}","completed":null,"due":null,"goal":null}}
   Include every field, even when null. Use a fresh random 6-char lowercase id per task.

Data:
```json
{json.dumps(ctx, indent=2, ensure_ascii=False)}
```"""
    return ask


def build_bites():
    iso = today()
    tasks = load("tasks") or []
    goals = {g["id"]: g["title"] for g in (load("goals") or [])}
    targets = [t for t in tasks if t.get("status") == "todo" and (t.get("rescope") or (t.get("due") and t["due"] < iso))]
    if not targets:
        return None
    ctx = [dict(slim_task(t), goal_title=goals.get(t.get("goal"))) for t in targets]
    return f"""These tasks are overdue or flagged for rescoping. The human has already judged each one not
important enough to do as written. Do NOT comment on lateness. For each task propose:

- **bite**: a real ten-minute first move. Physical and specific: "open X and do Y", not "start on".
- **title** (optional): a rewrite that puts the payoff in the title, if the current one hides it.
- **or someday**: if it genuinely reads as not-this-season, say so in one line instead.

Then a **Ready to paste** block: for each task, the JSON fields to change, e.g.
{{"id":"t_abc123","bite":"...","rescope":false}} or {{"id":"t_abc123","status":"someday","due":null}}.

Tasks:
```json
{json.dumps(ctx, indent=2, ensure_ascii=False)}
```"""


def build_week():
    iso, week_ago = today(), days_ago(6)
    tasks = load("tasks") or []
    L = load("learning") or {}
    unstick = load("unstick") or []
    habits = load("habits") or []
    goals = [g for g in (load("goals") or []) if g.get("status") == "active"]
    shipped = [t["title"] for t in tasks if t.get("status") == "done" and (t.get("completed") or "") >= week_ago]
    learned = [{"title": e["title"], "takeaway": e.get("takeaway")} for e in L.get("ledger", []) if e.get("date", "") >= week_ago]
    carried = [slim_task(t) for t in tasks if t.get("status") == "todo" and t.get("focus")]
    stale = [t["title"] for t in tasks if t.get("status") == "todo" and t.get("created", iso) < days_ago(14)][:15]
    un = [{"task": u.get("task"), "state": u.get("state"), "intervention": u.get("intervention"), "worked": u.get("worked"),
           "hour": (u.get("created") or "")[11:13]} for u in unstick if (u.get("created") or "") >= week_ago]
    hab = [{"name": h["name"], "days_done_this_week": sum(1 for d in h.get("log", []) if d >= week_ago)} for h in habits]
    ctx = {"today": iso, "shipped": shipped, "learned": learned, "carried_focus": carried, "stale_open_tasks": stale,
           "unstick_this_week": un, "habits": hab, "goals": [{"title": g["title"], "next": g.get("next")} for g in goals]}
    return f"""Draft the weekly review. Order is mandatory:

1. **Shipped**: one warm, plain paragraph on what was completed and learned this week. Include the
   takeaway lines. This comes first no matter how thin the week was.
2. **Carried**: for each still-open focus task, one proposal: refocus / split smaller / someday / delete.
   If the unstick data shows 3+ attempts on the same task with none that worked, say "scoped wrong,
   split it" rather than suggesting more effort.
3. **Stale**: for each task older than 14 days, someday or delete, one line each. Skip if none.
4. **Goals**: per goal, did anything shipped move it? Is the next action still right?
5. **Patterns**: only what the human can act on. A recurring unstick state across different tasks is a
   condition, not a task problem. Interventions that worked get named so they can be reached for first.
   Never present counts of attempts as a score.
6. **Habits**: one sentence. A habit under ~30% for the week: ask whether to shrink it or drop it.
7. **Next week**: one theme and Monday's {FOCUS_MAX} focus tasks.

Data:
```json
{json.dumps(ctx, indent=2, ensure_ascii=False)}
```"""


def build_cards():
    L = load("learning") or {}
    tracks = [t for t in L.get("tracks", []) if t.get("status") == "active"]
    if not tracks:
        return None
    done_by = {}
    for e in L.get("ledger", []):
        done_by[e["track"]] = done_by.get(e["track"], 0) + 1
    queued = [{"track": c["track"], "title": c["title"], "swaps": c.get("swaps", 0)} for c in L.get("queue", []) if c.get("status") == "queued"]
    recent = [{"title": e["title"], "takeaway": e.get("takeaway")} for e in L.get("ledger", [])[-8:]]
    mission = read_text(ROOT / "learning" / "MISSION.md")
    notes = read_text(ROOT / "learning" / "NOTES.md")
    ctx = {"tracks": [{"id": t["id"], "name": t["name"], "artifact": t["artifact"], "sessions": t["sessions"], "done": done_by.get(t["id"], 0)} for t in tracks],
           "already_queued": queued, "recent_ledger": recent}
    return f"""Propose a hand of learning cards: 5 to 7 across the active tracks, each pointed at that track's
artifact and building on what the ledger shows was learned, plus 2 wildcards (adjacent, interesting,
labelled "wildcard"). Cards already queued with swaps >= 2 were scoped wrong: propose a shrunk
replacement rather than leaving them. Never repeat a title from the ledger.

For each card: **title**, **do** (one line, concrete, ends in something that exists or works),
**minutes** (20-30), **track**, and **source to verify** (what kind of primary source a human or an
agent with web access should fetch; do not invent URLs, you cannot check them).

Mission:
{mission}

Teaching notes:
{notes}

Tracks and signal:
```json
{json.dumps(ctx, indent=2, ensure_ascii=False)}
```"""


def read_text(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        return "(missing)"


RITUALS = {"checkin": build_checkin, "bites": build_bites, "week": build_week, "cards": build_cards}


# ---------------------------------------------------------------- model call
def chat(url: str, model: str, key: str, system: str, user: str, timeout: int = 300) -> str:
    body = json.dumps({
        "model": model,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        "temperature": 0.3,
        "stream": False,
    }).encode("utf-8")
    req = urllib.request.Request(url.rstrip("/") + "/chat/completions", data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", f"Bearer {key or 'none'}")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")[:500]
        sys.exit(f"Model endpoint returned HTTP {e.code}: {detail}")
    except urllib.error.URLError as e:
        sys.exit(f"Could not reach {url}: {e.reason}\nIs the server running? Ollama: `ollama serve`. LM Studio: start the local server.")
    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        sys.exit(f"Unexpected response shape:\n{json.dumps(data, indent=2)[:800]}")


def main():
    ap = argparse.ArgumentParser(description="Run a LifeOS ritual against any chat model. Proposes only; never writes data/.")
    ap.add_argument("ritual", choices=RITUALS.keys())
    ap.add_argument("--url", default=os.environ.get("LIFEOS_LLM_URL", "http://localhost:11434/v1"))
    ap.add_argument("--model", default=os.environ.get("LIFEOS_LLM_MODEL", "llama3.2"))
    ap.add_argument("--key", default=os.environ.get("LIFEOS_LLM_KEY", ""))
    ap.add_argument("--out", help="also write the proposals to this Markdown file")
    ap.add_argument("--full-contract", action="store_true", help="use all of CLAUDE.md as the system prompt")
    ap.add_argument("--dry-run", action="store_true", help="print the prompt and exit")
    a = ap.parse_args()

    user = RITUALS[a.ritual]()
    if user is None:
        print({"bites": "Nothing overdue or flagged for rescope. Nothing to propose.",
               "cards": "No active learning tracks. Define one in data/learning.json (see learning/MISSION.md) first."}[a.ritual])
        return
    system = read_text(ROOT / "CLAUDE.md") if a.full_contract else COMPACT_CONTRACT

    if a.dry_run:
        print("=== system ===\n" + system + "\n\n=== user ===\n" + user)
        return

    reply = chat(a.url, a.model, a.key, system, user)
    header = f"# LifeOS {a.ritual} proposals, {today()}\n\n_Model: {a.model} at {a.url}. Proposals only; nothing has been written to data/._\n\n"
    text = header + reply.strip() + "\n"
    print(text)
    if a.out:
        out = Path(a.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
        print(f"\n(written to {out})", file=sys.stderr)


if __name__ == "__main__":
    main()
