# Agents

This folder is a LifeOS: a personal task, habit, goal and learning system stored as plain JSON in `data/`, with a single-file web app (`lifeos.html`) as its screen and an AI assistant as its review engine.

**Read `CLAUDE.md` first.** It is the contract: data schemas, the rules, and what each ritual does. It is not Claude-specific despite the name; it is the file Claude Code reads automatically, and everything in it applies to any assistant.

The four rituals are defined step by step in `.claude/skills/*/SKILL.md`:

| Ritual | File | When |
|---|---|---|
| Daily check-in | `.claude/skills/checkin/SKILL.md` | Every day, 5-10 min |
| Curate the learning queue | `.claude/skills/curate/SKILL.md` | Weekly, 10 min |
| Weekly review | `.claude/skills/weekly-review/SKILL.md` | Weekly, 15-30 min |
| Life portfolio | `.claude/skills/portfolio/SKILL.md` | Quarterly, 20-30 min |

When the user asks for one of these, open the file and follow it. `docs/AI-INTEGRATION.md` covers setup for specific tools.

Hard rules, in case you read nothing else: preserve the JSON schemas and 2-space indent; never backfill habit logs; never nag about overdue or missed days; never edit `unstick.json`, the learning `ledger`, or `portfolio.json` entries by hand; propose and batch-confirm rather than asking one question at a time.
