# AI integration

LifeOS is two halves. The app (`lifeos.html`) is the screen you glance at. An AI assistant is the review engine that processes your inbox, picks your day, restocks the learning deck, and does the weekly and quarterly thinking. This document is how to wire the second half up.

Nothing here is required to use the app on its own. It works as a plain task and habit tracker with no assistant at all. But the learning deck and the overdue mechanic both assume something with judgment is curating the data once a week.

## The contract

Everything an assistant needs is in two places:

- **`CLAUDE.md`**: schemas, rules, ritual summaries. Despite the name it is tool-agnostic. It is named for the file Claude Code loads automatically.
- **`.claude/skills/*/SKILL.md`**: the four rituals as step-by-step instructions, each with a hard time cap.

An assistant that reads those two and can edit JSON files in the folder is fully integrated. `AGENTS.md` at the root points there for tools that look for that filename instead.

The app reloads its data whenever the tab regains focus, and there is a reload button in the header. So the loop is: you talk to the assistant in a terminal or editor, it edits `data/*.json`, you switch back to the browser tab, the change is there.

## Route 1: Claude Code (zero setup)

Install [Claude Code](https://claude.com/claude-code), open a terminal in the LifeOS folder, run `claude`. The skills in `.claude/skills/` are picked up as slash commands automatically:

```
/checkin          daily
/curate           weekly
/weekly-review    weekly
/portfolio        quarterly
```

### Optional: a status line on every session

`scripts/checkin_status.py` prints one line of status (inbox count, focus count, overdue, days since last check-in) and, when a ritual is due, tells the assistant to offer it in one sentence. Add it as a SessionStart hook in `.claude/settings.json` in the LifeOS folder:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          { "type": "command", "command": "python scripts/checkin_status.py" }
        ]
      }
    ]
  }
}
```

Use `py` instead of `python` on Windows if that is how Python is installed. The script exits silently on any error so a broken hook never breaks a session.

### Optional: scheduled restocking

Once you have two weeks of Done/Swap signal, the curate skill offers to hand steps 4-6 (propose cards, build lessons, restock the queue) to a scheduled agent, so Monday's card is a genuine surprise. Claude Code's `/schedule` command or any cron-driven agent runner works. Keep the veto step: the agent proposes into a branch or a `proposed[]` array and you approve in a minute.

## Route 2: another coding agent (Codex, Cursor, Copilot, Aider, Cline, Gemini CLI, and so on)

Open the folder. Most of these tools read `AGENTS.md` at the root automatically; the ones that don't will read it if you point them at it once.

Then ask in plain words:

> Run the daily check-in as described in `.claude/skills/checkin/SKILL.md`.

The skill files are ordinary Markdown. If your tool supports custom commands or rules files, copy the four skill files into its format (Cursor rules, Codex `~/.codex/prompts`, and so on). Nothing in them depends on Claude-specific features except the `AskUserQuestion` phrasing, which any tool can read as "ask the user".

## Route 3: a chat model with no file access

Paste `CLAUDE.md` and the relevant `data/*.json` files into the chat and ask for the ritual. You get proposals; you apply them in the app. It is slower and misses the lesson-building half of curation, but for the daily check-in it is perfectly workable.

## Route 4: a local model (Ollama, LM Studio, llama.cpp)

Local models are good at the bulk language parts and bad at the judgment parts. Use them **propose-only**:

- Draft `bite` lines (10-minute first moves) for every overdue task, for the assistant or you to accept.
- First-pass classification of inbox items into task / someday / delete.
- Summarise the week's ledger takeaways into two lines for the weekly review.

They never write to `data/*.json`. Write a small script that reads the files, calls the model, and prints proposals to the terminal or to a scratch file. The human or the primary assistant does the writing. This is rule 11 in `CLAUDE.md` and it exists because a model that writes without judgment quietly corrupts a data set you will not notice for weeks.

## Feeding the move card from outside

`data/today.json` is the one hook designed for other systems. Any process that knows what your single most important thing is today can write:

```json
{
  "date": "2026-09-07",
  "title": "Call the dentist back",
  "note": "They left a message Friday. Ask about the earlier slot.",
  "link": "https://calendar.example/event/123",
  "linkText": "Open calendar",
  "source": "calendar",
  "done": false
}
```

The app shows it in the right-hand deck card when `date` is today, with a Done button that sets `done: true`. A stale date is ignored, so the writer never needs to clear it. Set the file to `null` to fall back to the top focus task.

Good writers for this: the check-in skill (it already does), a calendar exporter, a job-application tracker, a CRM, a project tool's "next action". Bad writers: anything that changes it more than once a day. One thing, decided once.

## Building lessons

The curate skill builds one HTML lesson per learning card. The method is written into the skill, and the three lessons in `learning/lessons/` are the reference implementation: link `../assets/lesson.css` and `../assets/quiz.js`, payoff first, a timer, a fetched-and-verified primary source, a quiz with equal-length options, a win box.

The assistant needs web access to do this properly. A card citing a URL from memory is a card citing a URL that may not exist. If your assistant can't fetch pages, either give it the sources yourself or accept that curation produces card outlines you then fill.

## Safety rails

- **One writer at a time.** Don't run a ritual while editing in the app. The app reloads on focus, so the order is: assistant writes, you switch tabs.
- **Git is the undo.** Each ritual commits. If a file gets mangled, `git checkout data/tasks.json` and try again. If you don't want git, back up `data/` some other way; the app has no undo.
- **Append-only files stay append-only.** `unstick.json`, the learning `ledger`, and `portfolio.json` are records. An assistant that "tidies" them is destroying the only evidence the weekly review runs on.
- **Caps are caps.** Three focus tasks, five habits, four active goals, four active tracks. An assistant that adds a sixth habit without removing one is not following the contract.
- **Personal data.** Everything stays in the folder. Nothing in the app phones home; the only network requests are two Google Fonts stylesheets, and it works without them. If you use a cloud assistant, your data goes to that assistant. If that matters to you, use Route 4 with a local model for the reading and do the writing yourself.

## Adapting the rituals

The skills are opinionated about time caps and about never producing guilt. Both come from the design's origin with ADHD; see `docs/DESIGN.md`. Loosen them if you like, but loosen them deliberately. In the original owner's experience every version that asked more questions or took longer was the version that stopped being used.
