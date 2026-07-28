---
name: rombot-cli
version: "0.2.0"
description: "Ask the AI Agents community brain a question — get grounded, cited answers from ~4,000 members' tips, repos, discussions, and gotchas while you code."
argument-hint: "ask the AI Agents community brain | /rombot-cli best practices for claude code hooks | /rombot-cli what repos people use for X"
allowed-tools: Bash, Read
user-invocable: true
metadata:
  openclaw:
    emoji: "🤖"
    bins:
      - python3
    tags:
      - community
      - knowledge-base
      - developer
      - ai-agents
      - tips
      - repos
      - gotchas
      - discussions
      - citations
      - clawhub
---

# RomBot CLI

Ask the AI Agents community brain a question from inside your coding agent. Get grounded, cited answers from ~4,000 members' tips, repos, discussions, and gotchas.

## When to use

Use when you want community-grounded knowledge on a coding/agent topic: best practices, repos people use, gotchas, discussions, tips. Don't use for general web search or questions unrelated to the AI Agents community.

## Setup

You — the coding agent — drive setup. The human never opens a terminal for the skill.

1. **Install the skill** (if not already installed): `npx skills add romiluz13/rombot-community-skill`.
2. **Check whether the skill is configured.** Run `python3 scripts/rombot-ask.py "test"`. If it exits `4` ("Not configured"), the skill is not set up — proceed to step 3. If it runs, skip to **Asking a question**.
3. **Get a token from the human.** Ask the human: "Send `/rombot-cli` to **RomBot** on WhatsApp to get a token, then paste it here." The token is tied to the human's phone number — the agent cannot get it; the human is the only one who can. Wait for the human to paste the token into the chat.
4. **Configure the skill yourself.** With the token the human pasted, run setup so the token is in the environment (the CLI reads it from there and writes the config non-interactively, no prompts):
   ```bash
   ROMBOT_CLI_TOKEN=<the token> python3 scripts/rombot-ask.py setup
   ```
   This writes `~/.config/rombot-cli/.env` with the token and the default endpoint URL.
5. **Verify the skill is configured.** Re-run step 2 (`python3 scripts/rombot-ask.py "test"`). If it now runs (exit `0`), setup succeeded — proceed to **Asking a question**. If it still exits `4` ("Not configured"), setup failed — re-run step 4.
6. **Ask.** You're now configured — proceed to **Asking a question**.

## Asking a question

With the skill configured (above), run the CLI via Bash:

```bash
python3 scripts/rombot-ask.py "<question>"
```

- **Pass the answer through verbatim** to the human. Do NOT reword, summarize, or translate RomBot's answer.
- You may rephrase the human's question into a crisp query before calling the CLI.
- RomBot's answer includes inline citations (who said it, which group, when, repo links). Do not strip them.
- If the CLI exits non-zero, report the error to the human.

## Flags

- `--json` — full `{answer, model, latency_ms}` shape.
- `--timeout <s>` — override the default 90s timeout.

## Language

RomBot answers in English by default. If the human writes Hebrew, RomBot answers in Hebrew.

## Exit codes

- 0 — success (answer on stdout)
- 1 — no answer
- 2 — auth failed (401)
- 3 — rate limited (429)
- 4 — not configured (run `setup`)
