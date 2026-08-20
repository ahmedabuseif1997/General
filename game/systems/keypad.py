"""التحقق من كود القفل الرقمي لكل باب."""
from __future__ import annotations

from enum import Enum, auto

from game.content.rooms import Room
from game.engine.state import GameState

# مقدار زيادة التوتر لكل محاولة غلط، بيتصاعد مع صعوبة الغرفة
TENSION_PER_WRONG_ATTEMPT = 4


class KeypadResult(Enum):
    SUCCESS = auto()
    WRONG = auto()
    LOCKED_OUT = auto()


def try_code(room: Room, entered_code: str, state: GameState) -> KeypadResult:
    entered_code = entered_code.strip()

    if entered_code == room.code:
        state.solved_rooms.add(room.id)
        return KeypadResult.SUCCESS

    attempts = state.record_attempt(room.id)
    state.raise_tension(TENSION_PER_WRONG_ATTEMPT * room.tier // 2 + TENSION_PER_WRONG_ATTEMPT)

    if room.max_attempts is not None and attempts >= room.max_attempts:
        return KeypadResult.LOCKED_OUT

    return KeypadResult.WRONG


def attempts_left(room: Room, state: GameState) -> int | None:
    if room.max_attempts is None:
        return None
    used = state.attempts_by_room.get(room.id, 0)
    return max(0, room.max_attempts - used)
