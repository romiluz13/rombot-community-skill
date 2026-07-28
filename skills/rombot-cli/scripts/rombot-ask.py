#!/usr/bin/env python3
"""rombot-ask — thin CLI that asks RomBot's community brain a question.

Usage:
  rombot-ask.py "<question>"          # prints the answer to stdout
  rombot-ask.py "<question>" --json   # full {answer, model, latency_ms}
  rombot-ask.py setup                 # writes ~/.config/rombot-cli/.env

Reads ROMBOT_CLI_URL + ROMBOT_CLI_TOKEN from env or ~/.config/rombot-cli/.env.
Sends the dev-token in the X-Community-Ask-Token header (NOT Authorization).
Exit codes: 0 success, 1 no answer, 2 auth failed (401), 3 rate limited (429),
4 not configured.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "rombot-cli"
CONFIG_FILE = CONFIG_DIR / ".env"
# The URL is optional in `setup`: a blank answer uses this default, so a user
# who only has a token can press Enter. Only the token is required.
DEFAULT_URL = "https://api.rombot.uk/api/community-ask"
DEFAULT_TIMEOUT = 90


def load_env() -> dict[str, str]:
    """Load ROMBOT_CLI_URL + ROMBOT_CLI_TOKEN from env or ~/.config/rombot-cli/.env."""
    env = {}
    # env vars take precedence
    for key in ("ROMBOT_CLI_URL", "ROMBOT_CLI_TOKEN"):
        val = os.environ.get(key)
        if val:
            env[key] = val
    # fall back to config file
    if CONFIG_FILE.exists():
        for line in CONFIG_FILE.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                env.setdefault(k.strip(), v.strip().strip('"').strip("'"))
    return env


def do_setup() -> int:
    """Write ~/.config/rombot-cli/.env from the environment or interactive prompts.

    When the token is already in the environment, writes the config
    non-interactively (no prompts) — this is how a coding agent drives setup:
    it exports the token in its shell and runs `setup`. When the token is
    absent, falls back to the interactive prompts for a human at a terminal.

    The URL is optional (blank/empty uses DEFAULT_URL); only a missing token
    is an error. Tokens are issued by RomBot on WhatsApp — never guessed.
    """
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    # Env-aware path: the agent exports the token; skip the prompts entirely.
    env_token = os.environ.get("ROMBOT_CLI_TOKEN", "").strip()
    if env_token:
        url = os.environ.get("ROMBOT_CLI_URL", "").strip() or DEFAULT_URL
        token = env_token
        CONFIG_FILE.write_text(f'ROMBOT_CLI_URL="{url}"\nROMBOT_CLI_TOKEN="{token}"\n')
        CONFIG_FILE.chmod(0o600)
        print(f"Config written to {CONFIG_FILE}")
        return 0

    # Interactive path: a human at a terminal.
    print("RomBot CLI setup")
    url = input(f"RomBot endpoint URL (blank = {DEFAULT_URL}): ").strip() or DEFAULT_URL
    token = input("Your token (send /rombot-cli to RomBot on WhatsApp to get one): ").strip()
    if not token:
        print(
            "Error: a token is required. Send /rombot-cli to RomBot on WhatsApp to get one.",
            file=sys.stderr,
        )
        return 4
    CONFIG_FILE.write_text(f'ROMBOT_CLI_URL="{url}"\nROMBOT_CLI_TOKEN="{token}"\n')
    CONFIG_FILE.chmod(0o600)
    print(f"Config written to {CONFIG_FILE}")
    return 0


def ask(question: str, as_json: bool, timeout: int) -> int:
    env = load_env()
    url = env.get("ROMBOT_CLI_URL")
    token = env.get("ROMBOT_CLI_TOKEN")
    if not url or not token:
        print(
            "Not configured. Run: rombot-ask.py setup "
            "(send /rombot-cli to RomBot on WhatsApp to get a token)",
            file=sys.stderr,
        )
        return 4

    body = json.dumps({"message": question}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "X-Community-Ask-Token": token,
            "User-Agent": "rombot-cli/0.2 (+https://github.com/romiluz13/rombot-community-skill)",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 401:
            print("Auth failed (401): invalid or revoked token.", file=sys.stderr)
            return 2
        if e.code == 429:
            print("Rate limited (429): too many requests. Try again later.", file=sys.stderr)
            return 3
        print(f"HTTP error {e.code}: {e.read().decode('utf-8', errors='replace')}", file=sys.stderr)
        return 1
    except urllib.error.URLError as e:
        print(f"Connection error: {e.reason}", file=sys.stderr)
        return 1

    answer = payload.get("answer", "")
    if not answer:
        print("No answer from RomBot.", file=sys.stderr)
        return 1

    if as_json:
        print(json.dumps(payload, indent=2))
    else:
        print(answer)
    return 0


def main() -> int:
    args = sys.argv[1:]
    if not args:
        print(__doc__, file=sys.stderr)
        return 1

    if args[0] == "setup":
        return do_setup()

    # parse flags
    as_json = False
    timeout = DEFAULT_TIMEOUT
    question_parts: list[str] = []
    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--json":
            as_json = True
        elif arg == "--timeout":
            i += 1
            if i >= len(args):
                print("Error: --timeout requires a value.", file=sys.stderr)
                return 1
            try:
                timeout = int(args[i])
            except ValueError:
                print(f"Error: --timeout needs a number, got {args[i]!r}.", file=sys.stderr)
                return 1
        else:
            question_parts.append(arg)
        i += 1

    question = " ".join(question_parts).strip()
    if not question:
        print("Error: no question provided.", file=sys.stderr)
        return 1

    return ask(question, as_json, timeout)


if __name__ == "__main__":
    sys.exit(main())
