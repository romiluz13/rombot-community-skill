#!/usr/bin/env python3
"""rombot-ask — thin CLI that asks RomBot's community brain a question.

Usage:
  rombot-ask.py "<question>"          # prints the answer to stdout
  rombot-ask.py "<question>" --json   # full {answer, model, latency_ms}
  rombot-ask.py setup                 # writes ~/.config/rombot-ask/.env

Reads ROMBOT_ASK_URL + ROMBOT_ASK_TOKEN from env or ~/.config/rombot-ask/.env.
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

CONFIG_DIR = Path.home() / ".config" / "rombot-ask"
CONFIG_FILE = CONFIG_DIR / ".env"
DEFAULT_TIMEOUT = 90


def load_env() -> dict[str, str]:
    """Load ROMBOT_ASK_URL + ROMBOT_ASK_TOKEN from env or ~/.config/rombot-ask/.env."""
    env = {}
    # env vars take precedence
    for key in ("ROMBOT_ASK_URL", "ROMBOT_ASK_TOKEN"):
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
    """Interactive setup — writes ~/.config/rombot-ask/.env."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    print("RomBot Community Ask setup")
    url = input("RomBot endpoint URL (e.g. https://api.rombot.uk/api/community-ask): ").strip()
    token = input("Your developer token: ").strip()
    if not url or not token:
        print("Error: both URL and token are required.", file=sys.stderr)
        return 4
    CONFIG_FILE.write_text(f'ROMBOT_ASK_URL="{url}"\nROMBOT_ASK_TOKEN="{token}"\n')
    CONFIG_FILE.chmod(0o600)
    print(f"Config written to {CONFIG_FILE}")
    return 0


def ask(question: str, as_json: bool, timeout: int) -> int:
    env = load_env()
    url = env.get("ROMBOT_ASK_URL")
    token = env.get("ROMBOT_ASK_TOKEN")
    if not url or not token:
        print("Not configured. Run: rombot-ask.py setup", file=sys.stderr)
        return 4

    body = json.dumps({"message": question}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "X-Community-Ask-Token": token,
            "User-Agent": "rombot-ask/0.2 (+https://github.com/romiluz13/rombot-community-skill)",
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
            timeout = int(args[i]) if i < len(args) else DEFAULT_TIMEOUT
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
