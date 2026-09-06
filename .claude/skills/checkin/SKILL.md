---
name: checkin
description: Daily LifeOS check-in. Process the inbox to zero, pick today's top 3, tick habits, log a short review. 5-10 minutes, hard cap. Use when the user says "check in", "daily review", "/checkin", or wants to process their LifeOS.
---

# LifeOS daily check-in

You are running the daily check-in against the LifeOS folder this skill lives in (the repo root, where `lifeos.html` and `data/` are). Read `CLAUDE.md` there for schemas and rules if not already in context. The whole ritual is **5-10 minutes, hard cap**. Bias toward acting and proposing, not interrogating. One or two question batches maximum.

## Steps

1. **Read state.** Load `data/inbox.json`, `data/tasks.json`, `data/habits.json`, `data/goals.json`, `data/today.json`, glance at `data/unstick.json`, and the most recent file in `reviews/` (if any). Note the date of the last check-in.

2. **Open with a compact status.** One short paragraph: items in inbox, yesterday's habit results, focus tasks left unfinished, anything overdue or flagged `rescope`. If days were missed, apply the **restart rule**: no guilt, no day-by-day catch-up, just "last check-in was X days ago, here's where things stand."

3. **Capture sweep.** Ask once: "Anything in your head that isn't captured yet?" Add whatever comes back to the inbox.

4. **Process inbox to zero.** For each item, *propose* a classification (task / someday / goal material / habit idea / delete) with a one-line rationale, and confirm the whole batch in one question rather than one at a time. Apply the results: move to `tasks.json` (status `todo` or `someday`), fold into a goal's next action, or delete. Inbox must be empty when done.

5. **Set today's focus.** Clear stale `focus` flags (unfinished focus tasks return to the pool; mention them, don't scold). Propose today's top 3 from: overdue items, goal next-actions, and what the user says matters today. Don't propose `blocked` tasks. Confirm, set `focus: true` (max 3).

6. **Today's move (optional).** If one of today's focus tasks is clearly the one that matters most, or if the day's most important thing isn't a task at all (an appointment, a call, a decision), write it to `data/today.json`:
   ```json
   { "date": "YYYY-MM-DD", "title": "...", "note": "one line, optional", "link": null, "linkText": null, "source": "check-in", "done": false }
   ```
   The app's move card shows this instead of the top focus task. Leave the file as `null` if the top focus task is the right answer already.

7. **Habits.** Ask which habits were done yesterday/today that aren't already ticked (the user may have ticked them in the app; check the log first). Update `log` arrays. Never backfill beyond yesterday.

8. **Goal pulse (10 seconds, not a review).** If any active goal has `next: null`, ask for its next action or park it. Otherwise skip.

9. **Unstick glance.** If `unstick.json` shows a focus task with 3+ attempts and no `worked: true`, say so once and offer to split it. Otherwise say nothing about the log.

10. **Write the log.** Create `reviews/YYYY-MM-DD.md`:

    ```markdown
    # Check-in YYYY-MM-DD
    - Inbox processed: N items
    - Focus today: task1 · task2 · task3
    - Habits: name ✓ / name ✗ (run 4)
    - Notes: <anything the user said worth remembering, one or two lines>
    ```

11. **Commit.** `git add -A && git commit -m "checkin YYYY-MM-DD"` in the LifeOS folder (skip silently if the folder isn't a git repo).

12. **Close with the day in one line.** Focus list + first next action. Stop there. No motivational padding.

## Rules that override everything

- **Preserve schemas exactly** (see CLAUDE.md): 2-space indent, trailing newline, dates `YYYY-MM-DD`, ids like `t_a1b2c3`.
- **Max 3 focus, max 5 habits, ≤4 active goals.** Adding beyond a cap means removing something; say so.
- **Restart rule:** missed days are free. Never backfill habit logs for days before yesterday, never enumerate what was missed.
- **Blocked tasks:** ask ONCE if still blocked, then move on.
- **Someday items:** occasionally (roughly weekly) surface ONE someday item and ask "still want this?" Otherwise leave them alone.
- If the user only has 2 minutes, do steps 4, 5, 10, 11 only.
