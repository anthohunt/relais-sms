"""SMS relay endpoint: receives POSTs from a phone automation app (MacroDroid, Tasker...)
and appends them to a JSON-lines log."""
import hmac
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from flask import Flask, request, jsonify

app = Flask(__name__)
TOKEN = os.environ.get("SMS_RELAY_TOKEN", "")
if len(TOKEN) < 16:
    raise SystemExit("SMS_RELAY_TOKEN must be set (16 characters or more). Generate one with: openssl rand -hex 24")
DATA_DIR = Path(os.environ.get("SMS_RELAY_DATA", "/data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = DATA_DIR / "sms-log.jsonl"


@app.route("/sms-relay", methods=["POST"])
def relay():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer ") or not hmac.compare_digest(auth[7:].encode(), TOKEN.encode()):
        return jsonify({"error": "unauthorized"}), 401

    payload = request.get_json(force=True, silent=True) or {}

    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "from_name": payload.get("from_name", ""),
        "from_number": payload.get("from_number", ""),
        "message": payload.get("message", ""),
        "raw": payload,
    }

    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    return jsonify({"status": "ok"}), 200


@app.route("/sms-relay/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"}), 200


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000)
