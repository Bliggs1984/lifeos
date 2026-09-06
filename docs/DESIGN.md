# Design notes

Why LifeOS looks the way it does, so that anyone adapting it can disagree with the reasoning rather than with the result.

## The failure that shaped it

The first two versions of this system were conventional: a morning brief emailed and toasted at 7 a.m., an evening check-up, a task list with due dates and colours. They ran for a month and were used almost never. The brief was delivered faithfully for nineteen mornings and read zero times. The owner's diagnosis, in his words: "another distraction I can block out."

The rebuild started from one question: what would you actually want from this thing? The answer was specific. *Be surprised each morning with something useful to learn that accumulates toward something I can use, plus the tasks that get me there.* Not a planner. A deck.

So the learning card leads, tasks follow, and nothing nags.

## ADHD as a design constraint

The owner has ADHD. Two of his sentences became rules:

> "If it hasn't got any actual importance or immediate implications and takes too long or is boring, I might not do it."

Consequence: every card is 20-30 minutes, the payoff is in the first line, and Swap is a first-class button. Interest is not a nice-to-have; it is the mechanism.

> "If it's overdue, the probability is I have regarded it as unimportant. If it is important, the task needs to change somehow."

Consequence: the overdue mechanic. A late task is shown once with three ways to change it and no way to be nagged about it. Red pinned tasks train you to ignore the screen; the screen is the only asset the system has.

These constraints turn out to be good design for people without ADHD too. Nobody has ever been made more productive by a red badge.

## Nothing pushes

No toast, no email, no phone, no badge, no streak-loss warning. A scheduled job opens the tab at the hour you sit down and that is the entire delivery mechanism. The reasoning: anything that can be blocked out will be, and each ignored notification lowers the value of the next one. A tab that is simply there, with something worth reading on it, has no such decay.

## Missed days cost nothing

The restart rule. No backfilling of habit logs, no listing what was missed, no reduced check-in as penalty. Streaks just start a new run. Guilt about a gap is the most common reason personal systems get abandoned, so this one is built so a gap costs exactly nothing. Every ritual is written to obey it.

## Caps everywhere

Three focus tasks. Five habits. Four active goals. Four active tracks. Caps exist because an open list can never be finished, and so never delivers the completion signal you are working for. A closed list can end. The "Day cleared" banner is the reward for ending it.

## Habits are daily only

Streaks are consecutive dates. A weekly habit therefore shows as broken six days out of seven and reads as failure by construction, which collides with the restart rule. Weekly-cadence work goes in as a recurring task. Adding a `cadence` field would fix this and was deliberately not done; it is the first thing an adapter might reasonably add.

## Artifacts, not subjects

A learning track is a route to a thing that exists afterwards: a working script, a one-page document, a machine set up a particular way, five dinners you can cook without a recipe. The progress dots under the card count toward it. "3 of 5 sessions in Python" is a number; "3 of 5 toward a working script" is a promise. Curation proposes artifacts, the user vetoes.

## Unstick: emotion first

The ↯ button routes by what is blocking, not by what is due. Five states (Stuck, Overwhelmed, Unmotivated, Disorganized, Discouraged), seven interventions each, a timer, and a "did it shift?" question. The states are the ones that show up in the ADHD self-help literature; the interventions are drawn from executive-function and behaviour-change research: implementation intentions, temptation bundling, body doubling, closed lists, estimation calibration, self-compassion, task initiation.

Every attempt is logged. The log is evidence for the weekly review, never a scoreboard for the user: a task triaged four times is a task that is wrongly scoped, and the fix is scoping, not willpower.

## The life portfolio

A quarterly direction check adapted from Rainer Strack's *Strategize Your Life*. The adaptations came from running it: importance ratings are worthless until the person has said in one line what a great life is to them, so that question gates everything; the famous 2x2 plot told us less than a ranked gap column; and the split between *grinding* (high gap, high hours: the approach is wrong) and *starved* (high gap, low hours: it needs a calendar) is what makes the output actionable. Snapshots are append-only because the drift between them is the point.

One rule from this exercise generalises: never propose cutting a high-satisfaction unit to feed a low-satisfaction one without testing it against the person's own criterion. A twenty-hour hobby looked like a leak until the owner said it was one of the few things actually delivering on his definition. Apply their test, not a productivity rubric.

## The app is the surface, the assistant is the engine

Deliberate split. The app does what is glanceable and tactile: capture, tick, star, swap, unstick. The assistant does what needs judgment and time: classifying the inbox, writing ten-minute bites for stuck tasks, building lessons from verified sources, noticing patterns in the unstick log. Neither should grow features that belong to the other. The app has no settings screen because settings are a conversation.

## Plain files, no build, no server

One HTML file, JSON in a folder, the File System Access API. No accounts, no sync service, no dependencies to rot. Git is the backup and the undo. The trade-off is that it only runs in Chrome and Edge, and needs one folder-permission click per browser profile. That was judged a fine price for owning the data outright.

## What was declined, and why

- **Voice capture.** The owner thinks in speech, not typing, so it was tempting. Declined until the deck had proven itself for two weeks: one new behaviour at a time.
- **Phone.** He hardly uses it. A system on a device you don't look at is a system you don't use.
- **Fun and experience suggestions.** "Fun I can handle myself." The system's job is the useful and the boring, made less boring.
- **A finance module.** Declined outright as a learning track. Money was handled as a goal with a next action instead.
- **Gamification** beyond the progress dots. Points and badges are a push mechanism in disguise.
- **Email and toast delivery.** Both were built, both were ignored, both were removed.

An adapter will disagree with some of these. That is fine. The point of writing them down is that the disagreement is with the reason, not with a mystery.

## If it becomes an app

pywebview is the recommended route: it gives the HTML its own WebView2 window, removes the folder-permission step, and the storage layer is about twenty lines to swap. Data stays plain JSON. Tauri if an installer is needed. Electron never; the whole thing is 75 KB and it should stay in that spirit.
