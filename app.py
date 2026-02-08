#!/usr/bin/env python3
"""Minimal self-hosted Claude chat — web UI + WhatsApp via Twilio."""

import os
import sys

try:
    import anthropic
    from flask import Flask, request, Response, send_from_directory
except ImportError:
    print("Install dependencies first:\n  pip3 install anthropic flask twilio")
    sys.exit(1)

try:
    from twilio.twiml.messaging_response import MessagingResponse
    HAS_TWILIO = True
except ImportError:
    HAS_TWILIO = False

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


# --- WhatsApp via Twilio ---

@app.route("/whatsapp", methods=["POST"])
def whatsapp():
    """Twilio webhook: receives WhatsApp messages, replies via Claude."""
    if not HAS_TWILIO:
        return "twilio package not installed", 500

    incoming_msg = request.form.get("Body", "").strip()
    sender = request.form.get("From", "unknown")

    if not incoming_msg:
        resp = MessagingResponse()
        resp.message("Send me a message and I'll reply as Claude.")
        return str(resp)

    # Use phone number as session key for conversation memory
    history = conversations.setdefault(sender, [])

    # "reset" command clears conversation
    if incoming_msg.lower() in ("reset", "new chat", "clear"):
        conversations.pop(sender, None)
        resp = MessagingResponse()
        resp.message("Conversation cleared. Send a new message to start fresh.")
        return str(resp)

    history.append({"role": "user", "content": incoming_msg})

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,  # WhatsApp has a ~1600 char limit per message
            messages=history,
        )
        reply = response.content[0].text
        history.append({"role": "assistant", "content": reply})

        # WhatsApp max message length is ~1600 chars; truncate if needed
        if len(reply) > 1500:
            reply = reply[:1497] + "..."

    except Exception as e:
        reply = f"Error: {e}"

    resp = MessagingResponse()
    resp.message(reply)
    return str(resp)


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
    print(f"\n  Web chat:")
    print(f"    Computer:  http://localhost:{port}")
    print(f"    Phone:     http://{local_ip}:{port}")
    print(f"\n  WhatsApp webhook (use with ngrok + Twilio):")
    print(f"    http://{local_ip}:{port}/whatsapp")
    if not HAS_TWILIO:
        print(f"    (twilio not installed — run: pip3 install twilio)")
    print()
    app.run(host="0.0.0.0", port=port)
