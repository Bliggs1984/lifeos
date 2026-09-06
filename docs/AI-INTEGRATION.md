# AI integration

LifeOS is two halves. The app (`lifeos.html`) is the screen you glance at. An AI model is the review engine that processes your inbox, picks your day, restocks the learning deck, and does the weekly and quarterly thinking. This document is how to wire the second half up, with **any** model: a frontier model through a coding agent, a web chat, or a small model running on your own machine.

Nothing here is required to use the app on its own. It works as a plain task and habit tracker with no model at all. But the learning deck and the overdue mechanic both assume something with judgment is curating the data once a week.

## The contract is tool-agnostic

Everything a model needs is in two places, both plain Markdown:

- **`CLAUDE.md`**: schemas, rules, ritual summaries. It is named for the file Claude Code loads automatically, but nothing in it is Claude-specific. `AGENTS.md`, `GEMINI.md` and `.github/copilot-instructions.md` are one-paragraph pointers to it for tools that look for those names instead.
- **`.claude/skills/*/SKILL.md`**: the four rituals as step-by-step instructions, each with a hard time cap. The folder name is Claude Code's convention; the files are ordinary Markdown any tool can read or that you can paste anywhere.

A model that reads those and can edit JSON in the folder is fully integrated. A model that can only read gets the same instructions and hands you proposals instead. Either way the loop is: the model works, it or you edit `data/*.json`, you switch to the browser tab, and the app reloads (it refreshes whenever the tab regains focus, and there is a reload button in the header).

## Pick a route

| You have | Route | What you get |
|---|---|---|
| Claude Code | [1](#route-1-claude-code) | Rituals as slash commands, zero setup |
| Another coding agent: Codex CLI, Gemini CLI, Cursor, Copilot, Aider, Cline, Roo, OpenCode, Continue, Zed, Windsurf | [2](#route-2-any-coding-agent) | Full rituals, model of your choice, reads and writes the files |
| A local model server: Ollama, LM Studio, llama.cpp, vLLM, Jan | [3](#route-3-a-local-model) | Full rituals through a local-capable agent, or propose-only through the shipped script |
| An API key and no agent: OpenAI, Gemini, Anthropic, Mistral, OpenRouter, Groq | [4](#route-4-an-api-key-and-the-shipped-script) | Propose-only through the shipped script |
| A web chat: ChatGPT, Claude.ai, Gemini, Le Chat, a company portal | [5](#route-5-a-web-chat-with-no-file-access) | Proposals by copy and paste |

Routes are not exclusive. A common setup is a frontier model through a coding agent for the weekly curation, where lessons get built from fetched sources, and a local model through the script for the daily check-in, where nothing leaves the machine.

## Route 1: Claude Code

Install [Claude Code](https://claude.com/claude-code), open a terminal in the LifeOS folder, run `claude`. The skills in `.claude/skills/` are picked up as slash commands automatically:

```
/checkin          daily
/curate           weekly
/weekly-review    weekly
/portfolio        quarterly
```

Optional status line on every session: `scripts/checkin_status.py` prints one line (inbox count, focus count, overdue, days since last check-in) and, when a ritual is due, tells the model to offer it in one sentence. Add it as a SessionStart hook in `.claude/settings.json` in the LifeOS folder:

```json
{
  "hooks": {
    "SessionStart": [
      { "hooks": [ { "type": "command", "command": "python scripts/checkin_status.py" } ] }
    ]
  }
}
```

Use `py` instead of `python` on Windows if that is how Python is installed. The script exits silently on any error so a broken hook never breaks a session.

## Route 2: any coding agent

This is the route for Codex CLI, Gemini CLI, Cursor, GitHub Copilot (agent mode), Aider, Cline, Roo Code, OpenCode, Continue, Zed, Windsurf, and whatever ships next month. They all do the same three things: read instruction files in the folder, read and edit files, and talk to a model you choose.

**Step 1: open the folder.** Most agents read `AGENTS.md` automatically and it points them at `CLAUDE.md`. Gemini CLI reads `GEMINI.md`; Copilot reads `.github/copilot-instructions.md`; both are in the repo and say the same thing. For tools with their own rules format, the table below says where to put a pointer. A pointer is one line: *"Read CLAUDE.md before anything else; it is the contract for this folder."*

| Tool | Reads automatically | Or put a pointer in |
|---|---|---|
| Codex CLI | `AGENTS.md` | |
| Gemini CLI | `GEMINI.md` | `.gemini/settings.json` → `contextFileName` to add `CLAUDE.md` |
| Cursor | `AGENTS.md`, `.cursor/rules/*.mdc` | `.cursor/rules/lifeos.mdc` with `alwaysApply: true` |
| GitHub Copilot | `.github/copilot-instructions.md`, `AGENTS.md` | |
| Aider | nothing by default | `aider --read CLAUDE.md`, or `read: [CLAUDE.md]` in `.aider.conf.yml` |
| Cline / Roo Code | `.clinerules/`, `.roo/rules/` | a file in that folder containing the pointer |
| OpenCode | `AGENTS.md` | |
| Continue | `.continue/rules/*.md` | a rule file with the pointer |
| Zed, Windsurf | `AGENTS.md` (Zed), `.windsurfrules` (Windsurf) | |

**Step 2: ask for a ritual in plain words.**

> Run the daily check-in exactly as described in `.claude/skills/checkin/SKILL.md`.

The skill files are ordinary Markdown. If the tool supports custom commands, copy the four skills into its format so they become one-word commands: Codex custom prompts (`~/.codex/prompts/checkin.md`), Gemini CLI custom commands (`.gemini/commands/checkin.toml`), Cursor and Copilot prompt files, Cline workflows. Nothing in them depends on a Claude feature. Where a skill says "ask one question", any tool can ask one question.

**Step 3: choose the model.** Every agent in that table lets you point it at OpenAI, Gemini, Anthropic, Mistral, OpenRouter, or a local server. The rituals are written to be model-agnostic: short, ordered, with explicit schemas. A capable mid-size model handles the check-in and weekly review well. The curate ritual builds lessons from **fetched** web sources and is the one place where a frontier model with web access earns its cost; see [Building lessons](#building-lessons).

## Route 3: a local model

Two ways, depending on whether you want the model to write files.

### 3a. Full rituals through a local-capable agent

Aider, OpenCode, Continue, Cline, Roo Code and Goose all run against Ollama, LM Studio or a llama.cpp server. Point one at the LifeOS folder, give it the pointer from Route 2, and ask for the ritual. The model reads and writes the JSON itself.

Ollama with Aider, as one concrete example:

```
ollama pull qwen2.5-coder:14b        # or any instruct model with ≥16k context
export OLLAMA_API_BASE=http://127.0.0.1:11434
aider --model ollama/qwen2.5-coder:14b --read CLAUDE.md --read .claude/skills/checkin/SKILL.md
> Run the daily check-in as described in the skill file.
```

What to expect from small models: they follow the ordered steps well and stay inside the schemas when the file is short. They are weaker at judgment calls (is this inbox item a task or a someday?) and at restraint (they want to add encouragement; the contract says not to). Read their proposals before saying yes, and keep git as the undo. Models under about 7B parameters tend to break JSON; 9B to 14B instruct models with a 16k or larger context window are the practical floor for editing `tasks.json` directly.

### 3b. Propose-only through the shipped script

`scripts/propose.py` runs any ritual against any server that speaks the OpenAI chat-completions API, which today is nearly all of them. It **reads** `data/` and **prints proposals as Markdown**. It never writes to `data/`. You apply what you agree with in the app, or paste the ready-to-paste JSON it produces into the files.

```
python scripts/propose.py checkin                     # classify inbox, propose focus 3
python scripts/propose.py bites                       # 10-minute first moves for overdue tasks
python scripts/propose.py week                        # weekly review draft, wins first
python scripts/propose.py cards                       # a hand of learning cards to veto
```

Defaults are Ollama on localhost with `llama3.2`. Change them with flags or environment variables:

| Server | `--url` | Notes |
|---|---|---|
| Ollama | `http://localhost:11434/v1` | default; `--model qwen2.5:14b` or any pulled model |
| LM Studio | `http://localhost:1234/v1` | start the local server in LM Studio first |
| llama.cpp | `http://localhost:8080/v1` | `llama-server -m model.gguf -c 16384` |
| vLLM, TGI, Jan | `http://localhost:8000/v1` | whatever port the server reports |

```
export LIFEOS_LLM_URL=http://localhost:1234/v1     # setx on Windows, or use the flags
export LIFEOS_LLM_MODEL=mistral-nemo
python scripts/propose.py checkin --out proposals/today.md
```

`--dry-run` prints the exact prompt without calling anything, so you can see what leaves your machine (with a local server: nothing). `--full-contract` sends all of `CLAUDE.md` as the system prompt instead of the compact built-in version; use it with models that have a 32k or larger context.

This is the setup where a small model is genuinely safe to point at your life. It cannot corrupt a file it never writes. Rule 11 in `CLAUDE.md` says the same thing from the other side: anything without judgment proposes, and only a human or an agent working with the human writes.

## Route 4: an API key and the shipped script

The same script talks to hosted APIs. Set the URL, the model, and a key:

| Provider | `--url` | Example `--model` |
|---|---|---|
| OpenAI | `https://api.openai.com/v1` | `gpt-4.1-mini` |
| Google Gemini | `https://generativelanguage.googleapis.com/v1beta/openai` | `gemini-2.5-flash` |
| Anthropic | `https://api.anthropic.com/v1` | `claude-sonnet-5` |
| Mistral | `https://api.mistral.ai/v1` | `mistral-small-latest` |
| OpenRouter | `https://openrouter.ai/api/v1` | any model id on the site |
| Groq | `https://api.groq.com/openai/v1` | `llama-3.3-70b-versatile` |

```
export LIFEOS_LLM_KEY=sk-...
python scripts/propose.py week --url https://api.openai.com/v1 --model gpt-4.1-mini
```

Model names change; check the provider's current list. The script only needs the endpoint to accept `POST /chat/completions` with `messages`, `model` and a bearer token, which all of these do.

Your data goes to the provider when you use this route. If that matters, use Route 3.

## Route 5: a web chat with no file access

Paste `CLAUDE.md` and the relevant `data/*.json` files into the chat and ask for the ritual by name. You get proposals; you apply them in the app. It is slower and misses the lesson-building half of curation, but for the daily check-in it works fine.

A shortcut: run `python scripts/propose.py checkin --dry-run` and paste the output. It is the exact prompt the script would send, with your data already embedded and the contract at the top.

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

Good writers for this: the check-in ritual (the skill already does it), a calendar exporter, a job-application tracker, a CRM, a project tool's "next action", a local model summarising your calendar. Bad writers: anything that changes it more than once a day. One thing, decided once.

## Building lessons

The curate ritual builds one HTML lesson per learning card. The method is written into the skill, and the three lessons in `learning/lessons/` are the reference implementation: link `../assets/lesson.css` and `../assets/quiz.js`, payoff first, a timer, a fetched-and-verified primary source, a quiz with equal-length options, a win box.

The model needs web access to do this properly. A card citing a URL from memory is a card citing a URL that may not exist. Local models and the propose script therefore produce card **outlines** with a note on what kind of source to verify; a human or an agent with web access then fetches the source and writes the lesson. Frontier models through Route 1 or 2 do the whole thing.

## Safety rails

- **One writer at a time.** Don't run a ritual while editing in the app. The app reloads on focus, so the order is: model writes, you switch tabs.
- **Git is the undo.** Each ritual commits. If a file gets mangled, `git checkout data/tasks.json` and try again. If you don't want git, back up `data/` some other way; the app has no undo.
- **Append-only files stay append-only.** `unstick.json`, the learning `ledger`, and `portfolio.json` are records. A model that "tidies" them is destroying the only evidence the weekly review runs on. Small models are especially prone to rewriting a whole file to fix one entry; if you use one with write access, check the diff.
- **Caps are caps.** Three focus tasks, five habits, four active goals, four active tracks. A model that adds a sixth habit without removing one is not following the contract.
- **Personal data.** Everything stays in the folder. Nothing in the app phones home; the only network requests are two Google Fonts stylesheets, and it works without them. A cloud model sees whatever you send it. `--dry-run` shows you exactly what that is.

## Adapting the rituals

The skills are opinionated about time caps and about never producing guilt. Both come from the design's origin with ADHD; see `docs/DESIGN.md`. Loosen them if you like, but loosen them deliberately. In the original owner's experience every version that asked more questions or took longer was the version that stopped being used. The compact contract at the top of `scripts/propose.py` is the same rules in forty lines, which is a good place to start if you want to write your own.
