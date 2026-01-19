from dataclasses import dataclass
from datetime import datetime
from typing import Dict

from flask import Flask, jsonify

from hash_utils import KST, is_valid_hash

app = Flask(__name__)


@dataclass
class ScoreEntry:
    username: str
    score: int
    updated_at: datetime


SCORES: Dict[str, ScoreEntry] = {}


@app.get("/<username>/<int:score>/<hash_value>")
def log_score(username: str, score: int, hash_value: str):
    salt = app.config.get("HASH_SALT", "CHANGE_ME")
    now = datetime.now(KST)

    if not is_valid_hash(username, score, hash_value, salt, now=now):
        return jsonify({"ok": False, "reason": "invalid_hash"}), 403

    current = SCORES.get(username)
    if current is None or score > current.score:
        SCORES[username] = ScoreEntry(username=username, score=score, updated_at=now)

    return jsonify({"ok": True, "username": username, "score": score})


@app.get("/health")
def health():
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.config["HASH_SALT"] = "CHANGE_ME"
    app.run(host="0.0.0.0", port=5000, debug=True)
