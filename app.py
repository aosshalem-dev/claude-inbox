#!/usr/bin/env python3
"""Minimal self-hosted Claude chat. Run it and open the link."""

import os
import sys

try:
    import anthropic
    from flask import Flask, request, Response, send_from_directory
except ImportError:
    print("Install dependencies first:\n  pip install anthropic flask")
    sys.exit(1)

API_KEY = os.environ.get("ANTHROPIC_API_KEY")
if not API_KEY:
    print("Set your API key:\n  export ANTHROPIC_API_KEY='sk-ant-...'")
    sys.exit(1)

app = Flask(__name__, static_folder="static")
client = anthropic.Anthropic(api_key=API_KEY)

# In-memory conversation per session (simple; resets on restart)
conversations = {}


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    session_id = data.get("session_id", "default")
    user_msg = data.get("message", "").strip()
    if not user_msg:
        return {"error": "empty message"}, 400

    history = conversations.setdefault(session_id, [])
    history.append({"role": "user", "content": user_msg})

    def generate():
        with client.messages.stream(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            messages=history,
        ) as stream:
            full = []
            for text in stream.text_stream:
                full.append(text)
                yield f"data: {text}\n\n"

            # Finalize: save assistant reply and send token usage
            reply = "".join(full)
            history.append({"role": "assistant", "content": reply})
            resp = stream.get_final_message()
            usage = f"{resp.usage.input_tokens}+{resp.usage.output_tokens}"
            yield f"event: done\ndata: {usage}\n\n"

    return Response(generate(), mimetype="text/event-stream")


@app.route("/clear", methods=["POST"])
def clear():
    data = request.json
    session_id = data.get("session_id", "default")
    conversations.pop(session_id, None)
    return {"ok": True}


if __name__ == "__main__":
    import socket

    # Get local IP so you can open it on your phone
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
    except Exception:
        local_ip = "127.0.0.1"
    finally:
        s.close()

    port = 5001
    print(f"\n  Open on this computer:  http://localhost:{port}")
    print(f"  Open on your phone:     http://{local_ip}:{port}\n")
    app.run(host="0.0.0.0", port=port)
