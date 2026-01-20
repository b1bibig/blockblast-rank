from dataclasses import dataclass
from datetime import datetime
from html import escape
from io import BytesIO
from typing import Dict, Tuple

from flask import Flask, Response, jsonify
from PIL import Image, ImageDraw, ImageFont

from server.hash_utils import KST, is_valid_hash

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


def _render_text_svg(
    text: str,
    *,
    size: Tuple[int, int],
    background_color: Tuple[int, int, int],
    text_color: Tuple[int, int, int],
    font_size: int,
    multiline: bool,
) -> bytes:
    width, height = size
    font_color = f"rgb{text_color}"
    background = f"rgb{background_color}"
    safe_lines = [escape(line) for line in text.splitlines()] if multiline else [escape(text)]
    line_height = font_size + 6
    total_height = line_height * len(safe_lines)
    start_y = (height - total_height) / 2 + font_size
    tspans = "\n".join(
        f'<tspan x="{width / 2}" y="{start_y + idx * line_height}">{line}</tspan>'
        for idx, line in enumerate(safe_lines)
    )
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">
  <rect width="100%" height="100%" fill="{background}" />
  <text x="{width / 2}" y="{height / 2}" fill="{font_color}" font-size="{font_size}"
        font-family="Noto Sans KR, Apple SD Gothic Neo, Malgun Gothic, Arial, sans-serif"
        text-anchor="middle" dominant-baseline="middle">
    {tspans}
  </text>
</svg>"""
    return svg.encode("utf-8")


def _render_text_image(
    text: str,
    *,
    size: Tuple[int, int] = (520, 140),
    background_color: Tuple[int, int, int] = (245, 245, 245),
    text_color: Tuple[int, int, int] = (33, 33, 33),
    font_size: int = 24,
    multiline: bool = False,
) -> bytes:
    image = Image.new("RGB", size, background_color)
    draw = ImageDraw.Draw(image)
    font = _load_font(font_size)
    if multiline:
        text_bbox = draw.multiline_textbbox((0, 0), text, font=font, spacing=6, align="center")
    else:
        text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    x = (size[0] - text_width) // 2
    y = (size[1] - text_height) // 2
    if multiline:
        draw.multiline_text(
            (x, y),
            text,
            fill=text_color,
            font=font,
            spacing=6,
            align="center",
        )
    else:
        draw.text((x, y), text, fill=text_color, font=font)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue(), "image/png"


def _render_text_response(
    text: str,
    *,
    size: Tuple[int, int] = (520, 140),
    background_color: Tuple[int, int, int] = (245, 245, 245),
    text_color: Tuple[int, int, int] = (33, 33, 33),
    font_size: int = 24,
    multiline: bool = False,
) -> Response:
    image_bytes, mimetype = _render_text_image(
        text,
        size=size,
        background_color=background_color,
        text_color=text_color,
        font_size=font_size,
        multiline=multiline,
    )
    return Response(image_bytes, mimetype=mimetype)


def _render_text_svg_response(
    text: str,
    *,
    size: Tuple[int, int] = (520, 140),
    background_color: Tuple[int, int, int] = (245, 245, 245),
    text_color: Tuple[int, int, int] = (33, 33, 33),
    font_size: int = 24,
    multiline: bool = False,
) -> Response:
    svg_bytes = _render_text_svg(
        text,
        size=size,
        background_color=background_color,
        text_color=text_color,
        font_size=font_size,
        multiline=multiline,
    )
    return Response(svg_bytes, mimetype="image/svg+xml")


@app.get("/<username>/<int:score>/<hash_value>")
def log_score(username: str, score: int, hash_value: str):
    salt = app.config.get("HASH_SALT", "CHANGE_ME")
    now = datetime.now(KST)

    if not is_valid_hash(username, score, hash_value, salt, now=now):
        return _render_text_svg_response("해시 검증이 틀렸습니다")

    current = SCORES.get(username)
    if current is None or score > current.score:
        SCORES[username] = ScoreEntry(username=username, score=score, updated_at=now)

    message = f"{username}:점수 {score}점!"
    return _render_text_response(message)


@app.get("/ranking")
def ranking():
    entries = sorted(SCORES.values(), key=lambda entry: entry.score, reverse=True)
    if not entries:
        return _render_text_response(
            "아직 등록된 점수가 없습니다.",
            size=(520, 180),
        )

    lines = ["랭킹 TOP 10"]
    for idx, entry in enumerate(entries[:10], start=1):
        lines.append(f"{idx}. {entry.username} - {entry.score}점")
    ranking_text = "\n".join(lines)
    return _render_text_response(
        ranking_text,
        size=(520, 320),
        font_size=20,
        multiline=True,
    )


@app.get("/health")
def health():
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.config["HASH_SALT"] = "CHANGE_ME"
    app.run(host="0.0.0.0", port=5000, debug=True)
