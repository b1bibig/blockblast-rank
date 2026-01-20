from __future__ import annotations

import argparse
from datetime import datetime, timedelta

from server.hash_utils import KST, make_hash


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="서버와 동일한 해시를 오프라인에서 생성합니다.",
    )
    parser.add_argument("username", help="사용자 이름")
    parser.add_argument("score", type=int, help="점수")
    parser.add_argument(
        "--salt",
        default="CHANGE_ME",
        help="서버에서 사용하는 HASH_SALT 값 (기본값: CHANGE_ME)",
    )
    parser.add_argument(
        "--time",
        help="해시를 만들 기준 시각 (KST) 예: 2024-05-01T13:45",
    )
    parser.add_argument(
        "--window-minutes",
        type=int,
        default=0,
        help="유효 해시 창을 출력할 분 단위 범위 (기본값: 0)",
    )
    parser.add_argument(
        "--length",
        type=int,
        default=16,
        help="해시 길이 (서버 기본값: 16)",
    )
    return parser.parse_args()


def _parse_time(value: str | None) -> datetime:
    if not value:
        return datetime.now(KST)
    return datetime.fromisoformat(value).replace(tzinfo=KST)


def main() -> None:
    args = _parse_args()
    now = _parse_time(args.time)

    if args.window_minutes > 0:
        for offset in range(args.window_minutes + 1):
            dt = now - timedelta(minutes=offset)
            value = make_hash(
                dt,
                args.username,
                args.score,
                args.salt,
                length=args.length,
            )
            print(f"{offset}분 전: {value}")
        return

    value = make_hash(
        now,
        args.username,
        args.score,
        args.salt,
        length=args.length,
    )
    print(value)


if __name__ == "__main__":
    main()
