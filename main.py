#!/usr/bin/env python3
"""
agentForge — Comprehensive AI Coding Agent Framework.
Modularized version — see src/ directory for individual modules.

Run:  python main.py
Need: pip install -r requirements.txt + .env with ANTHROPIC_API_KEY
"""

import threading
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.config import PROMPT, CLI_ACTIVE, terminal_print
from src.hooks import trigger_hooks
from src.agent_loop import (
    agent_loop, update_context, cron_autorun_loop,
    print_turn_assistants, agent_lock
)


def main():
    global CLI_ACTIVE
    CLI_ACTIVE = True

    print("Enter a question, press Enter to send. Type q to quit.\n")
    history = []
    context = update_context({}, [])
    threading.Thread(target=cron_autorun_loop,
                     args=(history, context), daemon=True).start()
    while True:
        try:
            query = input(PROMPT)
        except (EOFError, KeyboardInterrupt):
            break
        if query.strip().lower() in ("q", "exit", ""):
            break
        trigger_hooks("UserPromptSubmit", query)
        turn_start = len(history)
        history.append({"role": "user", "content": query})
        with agent_lock:
            agent_loop(history, context)
            context = update_context(context, history)
            print_turn_assistants(history, turn_start)


if __name__ == "__main__":
    main()