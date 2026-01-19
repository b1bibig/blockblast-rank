from dataclasses import dataclass
from datetime import datetime
from io import BytesIO
from typing import Dict, Tuple

from flask import Flask, Response, jsonify
from PIL import Image, ImageDraw, ImageFont

from hash_utils import KST, is_valid_hash

app = Flask(__name__)


@dataclass
class ScoreEntry:
    username: str
    score: int
    updated_at: datetime


SCORES: Dict[str, ScoreEntry] = {}


def _load_font(size: int) -> ImageFont.ImageFont:
    try:
        return ImageFont.truetype("DejaVuSans.ttf", size=size)
    except OSError:
        return ImageFont.load_default()


def _render_text_image(
    text: str,
    *,
    size: Tuple[int, int] = (520, 140),
    background_color: Tuple[int, int, int] = (245, 245, 245),
    text_color: Tuple[int, int, int] = (33, 33, 33),
    font_size: int = 24,
) -> bytes:
    image = Image.new("RGB", size, background_color)
    draw = ImageDraw.Draw(image)
    font = _load_font(font_size)
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    x = (size[0] - text_width) // 2
    y = (size[1] - text_height) // 2
    draw.text((x, y), text, fill=text_color, font=font)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


@app.get("/<username>/<int:score>/<hash_value>")
def log_score(username: str, score: int, hash_value: str):
    salt = app.config.get("HASH_SALT", "CHANGE_ME")
    now = datetime.now(KST)

    if not is_valid_hash(username, score, hash_value, salt, now=now):
        image_bytes = _render_text_image("해시 검증이 틀렸습니다")
        return Response(image_bytes, status=403, mimetype="image/png")

    current = SCORES.get(username)
    if current is None or score > current.score:
        SCORES[username] = ScoreEntry(username=username, score=score, updated_at=now)

    message = f"{username}:점수 {score}점!"
    image_bytes = _render_text_image(message)
    return Response(image_bytes, mimetype="image/png")


@app.get("/health")
def health():
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.config["HASH_SALT"] = "CHANGE_ME"
    app.run(host="0.0.0.0", port=5000, debug=True)
