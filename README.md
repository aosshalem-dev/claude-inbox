# Claude Chat

A simple self-hosted web chat for Claude. Open it on your phone or computer.

## Setup

```bash
pip install anthropic flask
export ANTHROPIC_API_KEY='sk-ant-...'
```

## Run

```bash
python app.py
```

Opens on:
- **This computer:** http://localhost:5001
- **Your phone:** http://YOUR_LOCAL_IP:5001 (printed when you start)

## Features

- Streaming responses (words appear as Claude types)
- Conversation memory within a session
- Mobile-friendly, works on any phone browser
- Token usage shown after each reply
- "New chat" button to reset
