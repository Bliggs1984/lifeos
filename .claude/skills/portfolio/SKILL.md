---
name: portfolio
description: LifeOS life-portfolio review. Rate where hours, importance and satisfaction sit across life units, find the gaps, and turn them into goals. Quarterly, 20-30 min. Use when the user says "portfolio", "/portfolio", "life portfolio", or wants a direction-level look rather than a week-level one.
---

# LifeOS life portfolio

You are running the quarterly life-portfolio review against the LifeOS folder this skill lives in. Read `CLAUDE.md` for schemas and rules if not in context.

Adapted from Rainer Strack's *Strategize Your Life* (BCG/HBR, 2023). Where this diverges from the source, the divergence came out of running it; see **Deviations** at the bottom.

Target 20-30 minutes. Lead with what's working, keep it concrete, never produce guilt.

**This is a rebalance, not a scorecard.** The output is always "where does the next hour go", never "here is how you fell short". A unit that scores badly is information about allocation, not about the person.

## Steps

1. **Read state.** `data/portfolio.json` (all prior snapshots), `data/goals.json`, `data/habits.json`, `data/tasks.json`, `data/unstick.json`.

2. **Q1: the great life. MANDATORY, and it comes FIRST.**

   Never collect ratings before this is answered. Importance is meaningless without something to rate importance *against*; collected cold it comes back a flat 5-7 across every unit and the whole pass has to be redone.

   Ask: **"Finish the sentence: a great life, for me, is..."** One or two lines, in their words. If a prior snapshot exists, read its `greatLife` back and ask if it still holds. If it does, reuse it verbatim: re-rating against a stable criterion is what makes snapshots comparable across quarters.

   Pick a well-being lens that fits their answer rather than imposing one. Self-determination theory (autonomy / competence / relatedness) suits people whose answer leads with freedom or choice. PERMA-V (positive emotion, engagement, relationships, meaning, accomplishment, vitality) suits people whose answer leads with meaning or contribution. Record which you used and why in the snapshot's `model` field.

   **Purpose statement:** Strack's Q2 asks for one. Offer it once. If the user declines or rejects the premise, drop it permanently and note that in `NOTES.md`-style fashion in the snapshot `note`. Don't reopen it next quarter.

3. **Collect the numbers.** Write a worksheet to `portfolio-worksheet.md` in the LifeOS root for the user to fill in and save (48 numbers is too many to type into chat). Pre-fill hours and units from the last snapshot if there is one so they edit rather than start cold.

   Per unit: **hours** in an average week (168 total, sleep included), **importance** 0-10, **satisfaction** 0-10. A unit with zero hours still gets rated: high importance and zero hours is the most useful row in the table.

   Default to Strack's 16 units (relationships: partner, family, friends, community; body and mind: physical health, mental health, spirituality; work and learning: job, education, finances; leisure: hobbies, online entertainment, offline entertainment; plus sleep, caregiving, chores/admin). Merge or split to fit the person. Fifteen or sixteen is the right count; more is noise.

   Rough is fine and first instinct beats deliberation. Twenty minutes, not an hour.

4. **Check the hours total.** If it comes in well under 168, name the shortfall in hours-per-day and ask where it went. That gap is usually the largest unit being under-reported, and it changes the reading.

5. **Compute the gap.** `importance - satisfaction`, ranked. This is the useful output, more so than the 2x2 plot. Don't draw a quadrant chart unless asked.

6. **Split high-gap units into grinding vs starved.** The highest-value move in the whole review:

   - **Grinding**: high gap, *high* hours. Already getting effort and not moving. Adding hours won't fix it; the approach is wrong.
   - **Starved**: high gap, *low* hours. Doesn't need rethinking, needs a calendar.

   Same gap, opposite interventions. Then check whether the high-gap units form a **chain**, one feeding the next (education → job → finances → freedom is a common one). When there's a chain, the fix is reallocation *within* it, not a raid on some unrelated unit.

7. **Say what's protected.** Any unit with a gap of zero or negative is working. Name these out loud and rule them out as sources of time.

   **Never propose cutting a high-satisfaction unit to feed a low-satisfaction one** without testing it against Q1 first. A twenty-hour hobby looks like a leak on a productivity rubric and looks like one of the few things delivering under the user's own definition. Apply *their* criterion. Where a large unit might be a default rather than a choice, ask ("is this chosen?") and accept either answer.

8. **Turn the corner into goals.** High-gap units become candidate entries in `goals.json` (cap: 4 active). Respect the shapes:
   - **Goal**: ongoing, needs a next action, spans months.
   - **Task**: one concrete thing with a due date.
   - **Habit**: small, recurring, *daily*. See step 9.

9. **Habits: daily only.** Streaks are consecutive dates, so a weekly habit registers as broken six days in seven and reads as failure by construction. Weekly-cadence work goes in as a recurring task. Max 5 habits; when starting from zero, add **one**.

10. **Append the snapshot** to `data/portfolio.json`. Never overwrite a prior one; the drift across quarters is worth more than any single snapshot.

    ```json
    {
      "date": "YYYY-MM-DD",
      "greatLife": "the Q1 answer this run was rated against",
      "model": "which well-being model and why",
      "units": [ { "name": "", "area": "", "hours": 0, "importance": 0, "satisfaction": 0 } ],
      "hoursLogged": 0,
      "hoursUnaccounted": 0,
      "note": "what moved since last snapshot, and the headline finding"
    }
    ```

11. **Compare to the previous snapshot** if one exists. A unit that has been high-gap for two runs running is the real signal. Report movement plainly, in both directions.

12. **Delete `portfolio-worksheet.md`** once the snapshot is written. The JSON is the record.

13. **Commit**: `portfolio review YYYY-MM-DD`.

## Deviations from Strack

- **Q1 gates the ratings.** In the source it's the first of seven steps. Here it's a hard gate, because skipping it demonstrably produces a useless importance column.
- **Purpose is optional.** Offered once, then dropped if declined.
- **Lens follows the answer.** SDT or PERMA-V, chosen to fit what the person said, not prescribed.
- **Ranked gap column over the 2x2 matrix.** The plot is the weakest part of the method in practice.
- **Grinding vs starved.** Not in the source. It's what makes the output actionable.
- **Snapshots over a one-off.** Strack's is a workshop you do once. This is quarterly and append-only.
- **Steps 3 and 5 of the source (vision, benchmarks) are thin** because the detail is paywalled. Don't pretend otherwise or invent it.
