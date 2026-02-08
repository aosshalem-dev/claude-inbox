#!/usr/bin/env python3
"""
Claude Inbox - Lightweight task queuing & quick questions.

Two modes:
  task  - Queue a task for Claude Code to handle later (near-zero cost)
  quick - Ask a short question and get an immediate answer (low tokens, ~1¢)

Usage:
  python claude_inbox.py task "Refactor the auth module to use JWT"
  python claude_inbox.py task "Download latest React docs cheat sheet"
  python claude_inbox.py quick "What's the Python syntax for list comprehension?"
  python claude_inbox.py list
  python claude_inbox.py clear-done

Requires: pip install anthropic
Set:      export ANTHROPIC_API_KEY='sk-ant-...'
"""

import json
import os
import sys
from datetime import datetime, timezone

INBOX_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "inbox.json")

# --- Inbox helpers ---

def load_inbox():
    if os.path.exists(INBOX_FILE):
        with open(INBOX_FILE) as f:
            return json.load(f)
    return []


def save_inbox(tasks):
    with open(INBOX_FILE, "w") as f:
        json.dump(tasks, f, indent=2)


def add_task(description, priority="normal"):
    tasks = load_inbox()
    task = {
        "id": len(tasks) + 1,
        "description": description,
        "priority": priority,
        "status": "pending",
        "created": datetime.now(timezone.utc).isoformat(),
        "result": None,
    }
    tasks.append(task)
    save_inbox(tasks)
    print(f"Queued task #{task['id']}: {description}")
    return task


def list_tasks():
    tasks = load_inbox()
    pending = [t for t in tasks if t["status"] == "pending"]
    if not pending:
        print("Inbox empty.")
        return
    print(f"\n{len(pending)} pending task(s):\n")
    for t in pending:
        flag = "!" if t["priority"] == "high" else " "
        print(f"  [{flag}] #{t['id']}  {t['description']}")
        print(f"        added {t['created'][:16]}")
    print()


def clear_done():
    tasks = load_inbox()
    kept = [t for t in tasks if t["status"] == "pending"]
    removed = len(tasks) - len(kept)
    save_inbox(kept)
    print(f"Cleared {removed} completed task(s). {len(kept)} remaining.")


# --- Quick question (low-token API call) ---

def quick_question(question):
    try:
        import anthropic
    except ImportError:
        print("Run: pip install anthropic")
        sys.exit(1)

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Set your API key: export ANTHROPIC_API_KEY='sk-ant-...'")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    # Use Haiku for cheapest/fastest quick answers
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        messages=[{"role": "user", "content": question}],
        system="Answer concisely in 1-3 sentences. Be direct.",
    )

    answer = response.content[0].text
    cost_in = response.usage.input_tokens
    cost_out = response.usage.output_tokens

    print(f"\n{answer}")
    print(f"\n  [{cost_in} in / {cost_out} out tokens — Haiku]")
    return answer


# --- CLI ---

USAGE = """Usage:
  python claude_inbox.py task "description"          Queue a task
  python claude_inbox.py task -high "description"    Queue high-priority task
  python claude_inbox.py quick "short question"      Get an immediate answer (low cost)
  python claude_inbox.py list                        Show pending tasks
  python claude_inbox.py clear-done                  Remove completed tasks
"""


def main():
    if len(sys.argv) < 2:
        print(USAGE)
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "task":
        if len(sys.argv) < 3:
            print("Provide a task description.")
            sys.exit(1)
        priority = "normal"
        desc_start = 2
        if sys.argv[2] == "-high":
            priority = "high"
            desc_start = 3
        description = " ".join(sys.argv[desc_start:])
        add_task(description, priority)

    elif cmd == "quick":
        if len(sys.argv) < 3:
            print("Provide a question.")
            sys.exit(1)
        question = " ".join(sys.argv[2:])
        quick_question(question)

    elif cmd == "list":
        list_tasks()

    elif cmd == "clear-done":
        clear_done()

    else:
        print(USAGE)


if __name__ == "__main__":
    main()
