import base64
from datetime import datetime, timedelta
from typing import Iterable
from zoneinfo import ZoneInfo

KST = ZoneInfo("Asia/Seoul")


def _format_ampm_hour(dt: datetime) -> tuple[str, int]:
    ampm = "오전" if dt.hour < 12 else "오후"
    hour = dt.hour % 12
    if hour == 0:
        hour = 12
    return ampm, hour


def make_hash_input(dt: datetime, username: str, score: int, salt: str) -> str:
    ampm, hour = _format_ampm_hour(dt)
    minute = f"{dt.minute:02d}"
    return f"{ampm}{hour}:{minute}:{username}:{score}:{salt}"


def base64_utf8(value: str) -> str:
    encoded = value.encode("utf-8")
    return base64.b64encode(encoded).decode("ascii")


def make_hash(dt: datetime, username: str, score: int, salt: str, length: int = 16) -> str:
    full = base64_utf8(make_hash_input(dt, username, score, salt))
    return full[:length]


def iter_valid_hashes(
    now: datetime, username: str, score: int, salt: str, window_minutes: int = 1
) -> Iterable[str]:
    for offset in range(window_minutes + 1):
        dt = now - timedelta(minutes=offset)
        yield make_hash(dt, username, score, salt)


def is_valid_hash(
    username: str,
    score: int,
    given_hash: str,
    salt: str,
    now: datetime | None = None,
    window_minutes: int = 1,
) -> bool:
    if now is None:
        now = datetime.now(KST)
    return given_hash in set(iter_valid_hashes(now, username, score, salt, window_minutes))
