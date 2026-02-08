# Claude Inbox

Queue tasks from anywhere (phone, tablet) for pennies. Process them with Claude Code on your flat-rate subscription.

## How It Works

```
Phone / anywhere (API - pennies)        Your computer (flat rate)
┌─────────────────────────┐              ┌─────────────────────┐
│  claude_inbox.py        │              │  Claude Code         │
│                         │   inbox.json │                      │
│  task  → queue for later│  ─────────►  │  "what's in my inbox"│
│  quick → instant answer │   (synced    │  reads + does work   │
│          (Haiku, ~$0.001)│   via git)  │  (subscription)      │
└─────────────────────────┘              └─────────────────────┘
```

## Setup

```bash
pip install anthropic
export ANTHROPIC_API_KEY='sk-ant-...'
```

## Usage

### Queue tasks (from anywhere)

```bash
python claude_inbox.py task "Refactor auth module to use JWT"
python claude_inbox.py task -high "Fix payment bug"
```

### Quick questions (instant, low cost)

```bash
python claude_inbox.py quick "Python syntax for list comprehension?"
```

### Manage inbox

```bash
python claude_inbox.py list          # show pending tasks
python claude_inbox.py clear-done    # remove completed
```

### Process tasks (at your computer)

```bash
cd claude-inbox
claude
# then say: "what's in my inbox"
```

## Syncing via Git

Add tasks remotely, then sync:

```bash
# From phone/remote: after adding tasks
git add inbox.json && git commit -m "new tasks" && git push

# At computer: before processing
git pull
```

## Cost

| Action | Model | Cost |
|--------|-------|------|
| Queue a task | none | Free |
| Quick question | Haiku | ~$0.001 |
| Process inbox | Claude Code | $0 (subscription) |
