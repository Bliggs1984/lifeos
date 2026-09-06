---
name: weekly-review
description: LifeOS weekly review. 15-30 min synthesis of the week: shipped list first, then stale tasks, goal pulse, unstick patterns, and next week's shape. Use when the user says "weekly review", "/weekly-review", or wants a week-level look at their LifeOS.
---

# LifeOS weekly review

You are running the weekly review against the LifeOS folder this skill lives in. Read `CLAUDE.md` for schemas and rules if not in context. Target 15-30 minutes; two question batches maximum. Lead with wins, keep everything concrete, never produce guilt.

## Steps

1. **Read state.** All of `data/*.json` (including `unstick.json` and `learning.json`), the last ~7 files in `reviews/`, and `git log --oneline` for the week if available.

2. **Open with the shipped list.** Everything completed in the last 7 days, plus learning cards done (with the takeaway lines), plainly celebrated in one paragraph. Memory deletes wins; this is the antidote and it goes FIRST, before any problem.

3. **The carried list.** Tasks that were in focus at some point this week but are still open, with a proposal each: refocus next week, split smaller (check `unstick.json`: 3+ attempts with no `worked: true` means scoped wrong), demote to someday, or delete. Batch-confirm.

4. **Stale sweep.** Open tasks untouched >14 days: propose someday or delete for each. Surface ONE someday item: "still want this?" Skip if nothing qualifies.

5. **Goal pulse.** Per active goal: did anything move this week (link to shipped items)? Is `next` still the right next action? If a goal had zero movement two weeks running, ask whether to rescope or park it. Parking is a valid outcome, not a failure.

6. **Unstick patterns.** Apply the analysis rules in `CLAUDE.md`: repeated states across tasks, interventions that consistently work, time-of-day clusters. Only report what the user can act on; evidence, never a scoreboard.

7. **Habit trends** (if any tracked): completion rate this week vs last, one sentence. A habit below ~30% for two weeks: ask if it should be redesigned smaller or dropped. Dropping is allowed.

8. **Shape next week.** One or two themes at most. Set Monday's focus 3 now so the week starts pre-decided. Confirm.

9. **Write the log** to `reviews/YYYY-Www-weekly.md` (e.g. `2026-W37-weekly.md`):

   ```markdown
   # Weekly review YYYY-Www
   ## Shipped
   - ...
   ## Carried → decision
   - task → refocused / split / someday / deleted
   ## Goals
   - goal: moved? next action
   ## Patterns
   - unstick/habit observations (only actionable ones)
   ## Next week
   - theme · Monday focus 3
   ```

10. **Commit** (`weekly review YYYY-Www`) and close with next week's theme in one line.

## Rules

- Restart rule governs: a thin week gets a thin review, not an inquest.
- Every proposal is batch-confirmed, never silently applied.
- If the user is short on time, do steps 2, 8, 9, 10 only.
