---
name: curate
description: Weekly LifeOS curation. Restock the learning queue with 5-7 micro-lesson cards plus 2 wildcards, rescope anything overdue or flagged, read the Done/Swap signal. 10 minutes. Use when the user says "curate", "restock", "/curate", or the learning shelf is empty.
---

# LifeOS weekly curation

You are restocking the morning learning engine in the LifeOS folder this skill lives in. Read `CLAUDE.md` (schemas, the design rules) and `learning/MISSION.md`, `learning/NOTES.md`, `learning/RESOURCES.md` if not in context. **Ten minutes, one question batch.** The user vetoes; you propose.

If `learning/MISSION.md` is still the template, stop and fill it in with the user first (see "The mission" below). Cards without a mission are trivia.

## Steps

1. **Read the signal.** `data/learning.json`: the `ledger` (what they did, their takeaway lines), cards with `swaps ≥ 2` (scoped wrong; shrink, don't re-deal), cards still `queued` (stale?), `notToday` frequency. Summarise in two lines. Never count skips back at the user.

2. **Write learning records** if the ledger shows evidence of understanding, prior knowledge, or a corrected misconception: `learning/learning-records/NNNN-slug.md`, one to three sentences each (what was learned and why it changes what to teach next). Coverage isn't learning; wait for evidence in the takeaway lines.

3. **Rescope tasks.** In `data/tasks.json`, every task with `rescope: true` or `due < today` gets one of: a `bite` (a real 10-minute first move, written into the task; clear `rescope`), a rewrite of the title so the payoff is immediate, or a proposal to demote to someday. Immediacy, brevity, interest, or it won't happen.

4. **Propose the hand.** 5-7 cards across the active tracks in `learning.json`, each pointed at that track's `artifact`, plus 2 wildcards (adjacent, interesting, clearly labelled "wildcard"). For each: title, one-line `do`, minutes, track, primary source URL. Check `learning/RESOURCES.md` first; search and fetch for anything new and add it there. Balance so Swap always has a different track to land on.

5. **One question to the user.** The hand as a list; they strike what they don't want and can name a subject they do. Also ask here if any track's artifact needs changing or a new track is wanted (they can veto artifacts; ≤4 active tracks).

6. **Build.** For each accepted card, write `learning/lessons/NNNN-slug.html` (see "Lesson method"). Append the card to `queue` in `learning.json` with `status: "queued"`, `lesson` path relative to `lifeos.html`, and `added: today`. Update `RESOURCES.md` and `NOTES.md`.

7. **Commit.** `git add -A && git commit -m "curate YYYY-MM-DD"` (skip silently if not a git repo).

8. **Close** with the week's hand in one line each. No motivational padding.

## Lesson method

One self-contained HTML file per card, in `learning/lessons/`, numbered `NNNN-slug.html` (scan for the highest number and increment). Link `../assets/lesson.css` and `../assets/quiz.js`; look at the three starter lessons for the shape. Every lesson has:

- An eyebrow line: track name, card N of M, minutes.
- **Payoff first.** The first paragraph says what the user can do afterwards that they couldn't before. If the reason is at the bottom, nobody reaches the bottom.
- A visible timer (`timer(el, minutes)`). Stopping when it ends is allowed.
- Knowledge, then doing. Only the knowledge the win needs. Then a concrete step in the real world: run this, write that, set this up.
- **A primary source you fetched and read**, linked, with a one-line reason to read it. Never a URL from memory. If you can't fetch it, don't cite it.
- A feedback loop: two or three `quiz(el, {...})` questions with options of equal length so the format never gives the answer away, or a check the user can run.
- A **win** box: what now exists or works.
- A footer reminding them to ask you, their teacher, anything unclear.

Constraints: 20-30 minutes. One tangible win. Concrete over abstract. Examples from the user's own domain (see `NOTES.md`). Novelty over repetition: never re-deal a card unchanged.

Reusable pieces go in `learning/assets/`, not inline. If a second lesson needs the same widget, it's a component.

## The mission

`learning/MISSION.md` is why the user is learning. Every card must trace back to it. If it's empty or vague, interview: what changes in their life or work when they have this? Push past "to understand X" to what X lets them do. Write it short. Update it when the goal moves, and add a learning record saying so.

**Tracks** are routes to an **artifact**: a thing that exists afterwards (a script, a document, a set-up machine, five dinners). Four to six sessions each. You propose artifacts, the user vetoes.

## Rules

- Preserve schemas and 2-space indent. Card ids `c_xxxxxx`, ledger ids `l_xxxxxx`, track ids `tr_xxxx`. Never edit or prune the `ledger`.
- Respect everything in `NOTES.md` (formats they avoid, subjects declined, courses they're already on that cards must not duplicate).
- After ~2 weeks of Done/Swap signal, offer to hand steps 4-6 to a scheduled agent so Monday's card is a genuine surprise. Only when there is two weeks of data.
