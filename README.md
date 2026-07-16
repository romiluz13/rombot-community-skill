# 🤖 RomBot Community

**Ask the AI Agents community brain a question — get grounded, cited answers from ~4,000 developers' real-world experience, right inside your coding agent.**

[![Status: Alpha](https://img.shields.io/badge/status-alpha-orange)](#status)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Python 3](https://img.shields.io/badge/python-3.x-blue)](#quickstart)

---

## The problem

Every coding agent can search the web. But web search finds blog posts, docs, and marketing pages — not the **hard-won, battle-tested knowledge** that lives in community conversations. The gotchas people hit at 2am. The repos that actually work vs. the ones that look good on paper. The config that breaks in production. That knowledge is locked in private Discord/WhatsApp groups, invisible to your agent.

RomBot Community unlocks it. The AI Agents community (~4,000 developers across 4 WhatsApp groups) has been discussing AI coding tools, agent architectures, model comparisons, and real-world deployment for months. This skill lets your coding agent ask that community brain a question and get back a **grounded, cited answer** — with who said it, which group, when, and links to repos or resources mentioned.

---

## Proof it works

Ask a real question, get a real answer with citations:

```
$ python3 rombot-ask.py "What's the best practice for Claude Code hooks?"

To set up Claude Code hooks like a pro, you need to configure them to serve
three distinct functions: Security Guardrails, Fatigue Reduction, and
Context Management.

### 1. The Pre-Execution Guard (Blocking rm -rf)
Running Claude Code with --dangerously-skip-permissions is tempting but
disastrous. After a community member (Daniel, June 2026) had Claude execute
an accidental rm -rf that wiped his workplace, consensus shifted to enforcing
local guardrails.

Best Practice: Use a local pre-run script hook to inspect commands before
Claude executes them.
Community Evidence: Shimon Moyal (June 2026) recommended claude-code-rm-guard
(github.com/elertan/claude-code-rm-guard) as a pre-execution shield.

### 2. Tuning Confirmation Fatigue
Tal F and Uval Vered (February 2026) suggest declaring trusted safe commands
under AllowedTools in .claude/settings.local.json...

### 3. Session Interception: The Pre-Compact Hook
Tal F (April 2026) shared a PreCompact hook pattern allowing you to read raw
context .jsonl session files right before compaction takes place...

Caveats: Anthropic's strict security boundaries limit Claude Code hooks from
communicating with external networks (Guy, February 2026). Git integration
often fails due to config mismatches (Noam, January 2026).
```

Every claim is sourced. Every recommendation ties to a real person, a real date, a real repo. No hallucinated metrics, no invented best practices — just what the community actually said.

---

## 🎯 Capability pillars

| Pillar | What it means |
|---|---|
| 🧠 **Community-grounded** | Answers mined from ~4,000 developers' real conversations, not web scrapes or synthetic data |
| 📎 **Cite-or-die** | Every claim cites who said it, when, in which group, with links to repos/resources |
| 🔒 **Constrained retrieval** | The agent can ONLY query the public community corpus + KB — never session chunks, private data, or unrelated sources |
| 🔌 **Agent-agnostic** | Works in Claude Code, Codex, Pi, Cursor, and any Agent Skills-compatible harness |
| 🛡️ **Production-hardened** | Per-user token auth, rate limiting, in-flight caps, 60s timeout, PII-redacted audit, Cloudflare DDoS protection |

---

## Quickstart

### 1. Get a token

DM **RomBot** on WhatsApp and ask for a developer token. Rom issues it via the owner-operated command (tokens are SHA-256 hashed, phone-tied, revocable).

### 2. Install + configure

```bash
# Clone the skill repo
git clone https://github.com/romiluz13/rombot-community-skill.git

# Configure (enter your endpoint URL + token)
python3 rombot-community-skill/skills/rombot-community/scripts/rombot-ask.py setup
```

Or install via your agent's skill marketplace:

| Harness | Install command |
|---|---|
| **Claude Code** | `/plugin marketplace add romiluz13/rombot-community-skill` |
| **Codex** | `npx skills add https://github.com/romiluz13/rombot-community-skill` |
| **Pi** | Add to `~/.agents/skills/` or use the marketplace manifest |
| **Cursor** | Settings → Features → MCP → add the skill |

### 3. Ask

```bash
# Direct CLI
python3 rombot-ask.py "What repos do people use for AI agent memory?"

# In your coding agent
/rombot-community best practices for Claude Code hooks
/rombot-community what model works best for coding agents
/rombot-community how to handle context window limits
```

The answer prints to stdout — your coding agent passes it through **verbatim** (don't reword, summarize, or translate — the citations matter).

---

## Architecture

```mermaid
graph LR
    A[Coding agent] --> B[rombot-ask.py CLI]
    B -->|POST + bearer token| C[Cloudflare edge]
    C -->|TLS + DDoS protection| D[cloudflared tunnel]
    D -->|outbound only| E[loopback gateway]
    E --> F[community-ask handler]
    F -->|token auth + rate limit| G[community-ask agent]
    G -->|community_search only| H[(MongoDB community corpus)]
    H -->|cited answer| F
    F -->|{answer, model, latency_ms}| B
```

The gateway is **never directly exposed**. Cloudflare Tunnel connects outbound only — no open ports, no sudo, automatic HTTPS.

---

## Configuration

| Env var | Where | Description |
|---|---|---|
| `ROMBOT_ASK_URL` | `~/.config/rombot-ask/.env` or env | Endpoint URL (default: `https://api.rombot.uk/api/community-ask`) |
| `ROMBOT_ASK_TOKEN` | `~/.config/rombot-ask/.env` or env | Your developer bearer token |

**Flags:** `--json` (full `{answer, model, latency_ms}` shape) · `--timeout <s>` (default 90s)

**Exit codes:** 0 success · 1 no answer · 2 auth failed (401) · 3 rate limited (429) · 4 not configured

---

## Status

**Alpha** — the endpoint is live and answering real questions, but token issuance is owner-operated (Rom issues tokens manually). Self-serve signup is planned for phase 2.

Rate limits: 10 requests/hour per token, 50/day. The community corpus is read-only — the agent cannot write, execute commands, or access private sessions.

---

## License

[MIT](LICENSE) — the skill package is open source. The RomBot community corpus and endpoint are operated by Rom Iluz.
