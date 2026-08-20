"""عرض ومعالجة حقيبة اللاعب."""
from __future__ import annotations

from game.engine.state import GameState


def describe(state: GameState) -> str:
    if not state.inventory:
        return "حقيبتك فاضية."
    items = "، ".join(sorted(state.inventory))
    return f"معاك: {items}."
