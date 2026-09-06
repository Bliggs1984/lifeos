# LifeOS

A personal life operating system: tasks, habits, goals and a daily learning card, with two interfaces over the same plain-JSON data.

- **`lifeos.html`**: a single-file local web app. Open it in Chrome or Edge; it reads and writes `data/*.json` through the File System Access API. It is the glanceable surface: the **morning deck** (today's learning card and today's one move), quick capture, ticking tasks and habits, unsticking a task you're avoiding.
- **An AI assistant** (Claude Code, or anything that can read this file and edit JSON) runs the rituals the app can't: `/checkin` daily, `/curate` weekly, `/weekly-review` weekly, `/portfolio` quarterly. Skill definitions live in `.claude/skills/`. See `docs/AI-INTEGRATION.md` for wiring up other assistants.

This file is the contract between the two. Anything that edits `data/` follows it.

## Design principles

The system was built for someone with ADHD and works for anyone who ignores things that nag. The consequences:

- **Nothing pushes.** No toast, no email, no badge. The tab being open in the morning is the whole mechanism. Anything that can be blocked out will be.
- **Every learning card ≤30 minutes, payoff in the first line.** Swap beats insist: the reroll is the fun.
- **Overdue tasks are never pinned or repeated. They are changed.** If something went overdue, the user already judged it unimportant. Re-showing it harder trains them to ignore the screen. The fix is changing the task until the importance is felt, and that is the assistant's job at curation.
- **Missed days cost nothing.** No backfilling, no guilt, no listing what was missed.
- **The app is the surface, the assistant is the review engine.** Don't rebuild app features into the skills or vice versa.

## Structure

```
lifeos/
├── CLAUDE.md          # this file: system rules, schemas, ritual summaries
├── AGENTS.md          # pointer here for Codex, Cursor, OpenCode, Zed and friends
├── GEMINI.md          # pointer here for Gemini CLI
├── .github/copilot-instructions.md   # pointer here for GitHub Copilot
├── lifeos.html        # the app (single file, no build)
├── data/
│   ├── inbox.json     # raw captures, unprocessed
│   ├── tasks.json     # all tasks
│   ├── habits.json    # habits + completion log
│   ├── goals.json     # goals with next actions
│   ├── unstick.json   # triage log: what blocked, what shifted it (append-only)
│   ├── learning.json  # tracks, card queue, takeaway ledger (one object, not an array)
│   ├── today.json     # optional: today's one move, written by an outside process
│   └── portfolio.json # quarterly life-portfolio snapshots (append-only)
├── learning/          # MISSION.md, RESOURCES.md, NOTES.md, lessons/*.html, assets/, learning-records/
├── reviews/           # dated check-in logs (YYYY-MM-DD.md) + weekly (YYYY-Www-weekly.md)
├── templates/         # reusable checklists the assistant pre-fills
├── scripts/
│   ├── morning_open.py   # scheduled: opens lifeos.html at the hour you sit down
│   ├── checkin_status.py # optional SessionStart hook: one-line status + ritual nudge
│   └── propose.py        # any ritual, any OpenAI-compatible model, propose-only
├── docs/              # DESIGN.md (the why), AI-INTEGRATION.md (the how)
└── .claude/skills/    # checkin, curate, weekly-review, portfolio
```

## Data schemas

All files are JSON, 2-space indented, trailing newline (keep them git-diffable). Dates are `YYYY-MM-DD` local time unless noted. IDs are a prefix plus six random base-36 characters (e.g. `t_k3x9f2`).

**inbox.json**: array of `{ id, text, created }` (`created` = ISO datetime). Captures are one line, never categorised at capture time.

**tasks.json**: array of `{ id, title, status, focus, created, completed, due, goal, snooze?, blocked?, bite?, rescope?, original? }`
- `status`: `"todo" | "someday" | "done"`
- `focus`: boolean. Today's top picks, max 3 true at once (the `FOCUS_MAX` constant in `lifeos.html`).
- `completed` / `due`: date or `null`; `goal`: goal id or `null`
- `snooze`: date or `null`/absent. Task is hidden and un-nagged until this date; snoozing clears `focus`. Expired snoozes need no cleanup. Not a deadline; `due` is the deadline.
- `blocked`: string or `null`/absent. What the task is waiting on. Blocked tasks stay visible with a ⏳ tag; don't propose them for focus; at check-in ask ONCE if still blocked, then move on.
- `bite`: string or absent. A real 10-minute first move, written by the assistant at `/curate`. The app's overdue prompt offers it as "Take the 10-min version" (title becomes the bite, old title kept in `original`, due cleared).
- `rescope`: boolean or absent. The user pressed Rescope on an overdue task. Shown with a ↻ tag; `/curate` must rewrite it (add a `bite`, make the payoff immediate, or propose someday) and clear the flag.

**The overdue mechanic.** A task with `due < today` leaves the normal list and appears once, above capture, with three buttons: *Take the 10-min version* (needs a `bite`), *Rescope* (flags for `/curate`, clears `due`), *Let it go* (→ someday). No pinning, no repetition, no copy about how long it's been.

**learning.json**: one object: `{ tracks[], queue[], ledger[], notToday }`
- `tracks[]`: `{ id, name, artifact, sessions, status, created }`. `artifact` is the tangible unlock (a thing that exists afterwards), `sessions` how many Done cards reach it. `status`: `"active" | "done" | "parked"`. ≤4 active. The assistant proposes artifacts, the user vetoes.
- `queue[]`: `{ id, track, title, do, minutes, lesson, link, status, added, swaps?, done? }`. `status`: `"queued" | "done"`. The app deals the first `queued` card. *Swap* moves it to the back and bumps `swaps` (≥2 = scoped wrong; shrink at curation, don't re-deal). `lesson` is a path relative to `lifeos.html`, usually `learning/lessons/NNNN-slug.html`. `link` is the primary source URL or `null`.
- `ledger[]`: `{ id, cardId, track, title, date, takeaway }`. Append-only. One entry per Done; `takeaway` is the user's one line. Track progress = count of ledger entries per track, computed, never stored. Pressing Done also ticks any habit whose name contains "learn".
- `notToday`: date or `null`. The user pressed *Not today*; the card hides until tomorrow with no consequence.
- Ids: cards `c_xxxxxx`, ledger `l_xxxxxx`, tracks `tr_xxxx`.

**today.json**: `null`, or one object `{ date, title, note?, link?, linkText?, source?, done }`. The app's move card shows it when `date` is today; otherwise it falls back to the first starred focus task. Any outside process may write it: the check-in skill, a calendar script, another app's exporter. The app only ever sets `done: true`. A stale date is simply ignored, so nothing needs clearing.

**habits.json**: array of `{ id, name, log, created }`
- `log`: array of dates the habit was done. Streak = consecutive run ending today or yesterday, computed, never stored.
- Max **5** habits (`HABIT_MAX` in `lifeos.html`). Daily only; see rule 8.

**goals.json**: array of `{ id, title, why, next, status, created, link? }`
- `status`: `"active" | "parked" | "done"`; `next` = the single next action (string or `null`)
- `link`: optional URL; the app renders the title as a link (to a dashboard, a doc, another app)
- Aim for ≤4 active goals.

**unstick.json**: array of `{ id, task, taskId, state, intervention, worked, created }`
- Append-only log written by the app's Unstick overlay. Never edit or prune it by hand.
- `state`: `"stuck" | "overwhelmed" | "unmotivated" | "disorganized" | "discouraged"`
- `task`: the task title at time of use (denormalised so entries survive deletion); `taskId`: task id or `null` when triaged from the header button
- `intervention`: title of the strategy served; `worked`: boolean
- `created`: ISO datetime. Time of day matters; it's how stall patterns surface.

**portfolio.json**: array of `{ date, greatLife, model, units[], hoursLogged, hoursUnaccounted, note }`
- Append-only quarterly snapshots from `/portfolio`. Never overwrite a prior entry; the drift between snapshots is the point.
- `greatLife`: the criterion importance was rated against that run. Reuse it verbatim across runs so snapshots stay comparable.
- `units`: `{ name, area, hours, importance, satisfaction }`, 15-16 units, hours across a 168h week including sleep.
- The useful derived number is **importance − satisfaction**, ranked. High gap + high hours = grinding (approach is wrong); high gap + low hours = starved (needs a calendar).

## Rules

1. **Capture is sacred and frictionless.** Anything → one line in inbox. No sorting, no tags, no decisions at capture time. Sorting happens at check-in.
2. **Every task lives in exactly one place** (tasks.json). No duplicates, no side lists.
3. **Restart rule: missed days cost nothing.** Never backfill habit logs. Never guilt-review a gap. A check-in after missed days is a normal check-in.
4. **Max 5 habits, ≤4 active goals, max 3 focus tasks.** Adding beyond a cap means one has to go. Say so.
5. **Someday is a parking lot, not a graveyard.** Check-in may surface a random someday item occasionally; it never nags.
6. **The assistant edits data files freely during rituals.** Preserve schemas and 2-space indent. Commit after each ritual with a short message (e.g. `checkin 2026-09-06`) if the folder is a git repo.
7. **The app is the glanceable surface; the assistant is the review engine.** Don't rebuild app features into the skills or vice versa.
8. **Habits are daily-only.** Streaks are consecutive dates, so a weekly habit shows a broken streak six days in seven and reads as failure by construction. Weekly-cadence work goes in as a recurring task. (Changing this needs a `cadence` field on the habit schema; not built.)
9. **Never propose cutting a high-satisfaction unit to feed a low-satisfaction one** without testing it against the user's own definition of a great life. Their criterion, not a generic productivity one.
10. **The unstick log is evidence, never a scoreboard.** A task triaged four times is a task that's wrongly scoped, not a character flaw. Never count attempts back at the user, never treat a high tally as failure.
11. **Propose-only for anything without judgment.** Scripts and local models may read `data/` and propose; only the user (in the app) or an assistant running a ritual with the user writes. Never have two processes writing the same file at once.

## Unstick (in-app triage)

The `↯` button on any open task, or `↯ unstick` in the header, opens emotion-first triage: pick which of five states is blocking (Stuck, Overwhelmed, Unmotivated, Disorganized, Discouraged), get one concrete intervention plus an optional timer, mark whether it shifted. Every attempt appends to `unstick.json`. The interventions are drawn from executive-function and behaviour-change research (implementation intentions, temptation bundling, body doubling, closed lists, estimation calibration, self-compassion, task initiation) and live in `UN_LIB` in `lifeos.html`; edit them there.

**What the assistant does with the log**, at check-in and weekly review, only when the data says something actionable:
- A task with 3+ attempts and no `worked: true` → the task is scoped wrong. Offer to split it or turn it into a smaller next action.
- The same `state` recurring across unrelated tasks → a condition, not a task problem. Discouraged across a week means the goal needs rescoping; Disorganized everywhere means the system needs a reset, not more willpower.
- Interventions with consistent `worked: true` → name them and reach for them first.
- Clusters by time of day → useful for where focus tasks get placed.

## The morning deck

At the hour the user sits down, a scheduled job (`scripts/morning_open.py`) opens `lifeos.html`. Two cards, equal weight:

1. **Today's learning**: the first queued card in `learning.json`: title (links to the lesson), a one-line *do*, minutes, and the track's progress dots with its unlock. Buttons: **Done** (asks one takeaway line → ledger, ticks the learning habit), **Swap** (next card), **Not today** (gone till tomorrow).
2. **Today's move**: `today.json` if written for today, else the first starred focus task. One thing. Done button.

Under the deck: any overdue task as a change-it prompt, then capture, inbox, focus, tasks, habits, goals, and a collapsed "shipped this week" list so wins stay visible. A "Day cleared" banner appears when all focus tasks are done and habits ticked.

**Lessons** are one HTML file per card in `learning/lessons/`, built by the curate skill: payoff line first, a timer, a fetched-and-verified primary source, a quiz or check, a tangible win. The three starter lessons show the shape and teach the system itself; retire the Getting started track once a real one exists.

## The rituals

- **`/checkin`**: daily, 5-10 min, hard cap. Capture → clarify inbox to zero → focus 3 → habits → log → commit. The learning card and the move card are the app's job, not check-in's, except that check-in may write `today.json`.
- **`/curate`**: weekly, 10 min. Read Done/Swap signal, write learning records where there's evidence, rescope every overdue or `rescope`-flagged task (give it a `bite`), propose 5-7 cards + 2 wildcards, user vetoes, build the lessons, restock the queue, commit. After ~2 weeks of signal, restocking can hand over to a scheduled agent.
- **`/weekly-review`**: weekly, 15-30 min. Shipped list first (wins before problems, always), carried tasks, stale sweep, goal pulse, unstick patterns, next week's focus 3.
- **`/portfolio`**: quarterly, 20-30 min. Adapted from Rainer Strack's *Strategize Your Life*. Rate 15-16 life units on hours / importance / satisfaction against the user's own one-line definition of a great life (collected first, every time), rank by gap, split high-gap units into grinding vs starved, turn the corner into goals, append a snapshot.

## Other models and local models

Nothing in this folder is tied to one provider. `AGENTS.md`, `GEMINI.md` and `.github/copilot-instructions.md` point other coding agents here; the skill files are plain Markdown any tool can follow. `docs/AI-INTEGRATION.md` has setup for each route.

`scripts/propose.py` runs any ritual against any OpenAI-compatible endpoint (Ollama, LM Studio, llama.cpp, OpenAI, Gemini, Anthropic, Mistral, OpenRouter) in **propose-only** mode: it reads `data/` and prints Markdown proposals with ready-to-paste JSON. It never writes to `data/*.json`. That is the safe way to put a small local model on the daily check-in: it cannot corrupt a file it never writes. The writer is always the user, or an agent running a ritual with them.

## Deliberately not built

- Voice capture, phone anything, notifications of any kind, gamification beyond the track dots, a finance module. Each was considered against the design principles and declined. The friend who forks this may well disagree; see `docs/DESIGN.md` for the reasoning so the disagreement is informed.
- A standalone app. If it's wanted, pywebview is the pick: own WebView2 window, no folder permissions, a ~20-line storage swap, data stays plain JSON.
