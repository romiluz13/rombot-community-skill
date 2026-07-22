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
    requires:
      env:
        - ROMBOT_CLI_TOKEN
        - ROMBOT_CLI_URL
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

1. **Install** — `npx skills add romiluz13/rombot-community-skill`
2. **Get a token** — send `/rombot-cli` to **RomBot** on WhatsApp. You'll get a token tied to your phone number (self-service — no need to ask Rom).
3. **Configure** — run `python3 scripts/rombot-ask.py setup` and paste your token when prompted. This writes `~/.config/rombot-cli/.env`.
4. **Ask** — `/rombot-cli <question>` in your coding agent.

## How to call

Run the CLI via Bash:

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
