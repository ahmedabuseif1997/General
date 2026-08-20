#!/usr/bin/env python3
"""نقطة البداية للعبة الهروب. تشغيل: python3 -m game.main"""
from __future__ import annotations

from game.content.rooms import load_house
from game.engine.game_loop import run
from game.engine.state import GameState


def main() -> None:
    house = load_house()
    state = GameState(current_room_id=house.rooms[0].id)
    run(house, state)


if __name__ == "__main__":
    main()
