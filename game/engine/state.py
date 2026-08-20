"""حالة اللعب: مكان اللاعب، حقيبته، محاولاته، مستوى التوتر."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class GameState:
    current_room_id: int = 1
    inventory: set[str] = field(default_factory=set)
    examined_objects: set[tuple[int, str]] = field(default_factory=set)
    attempts_by_room: dict[int, int] = field(default_factory=dict)
    hints_shown_by_room: dict[int, int] = field(default_factory=dict)
    solved_rooms: set[int] = field(default_factory=set)
    tension: int = 0
    game_over: bool = False
    victory: bool = False
    quit_requested: bool = False

    def has_item(self, item: str) -> bool:
        return item in self.inventory

    def add_item(self, item: str) -> None:
        self.inventory.add(item)

    def mark_examined(self, room_id: int, object_name: str) -> bool:
        """يرجع True لو أول مرة يتفحص فيها الغرض ده."""
        key = (room_id, object_name)
        if key in self.examined_objects:
            return False
        self.examined_objects.add(key)
        return True

    def record_attempt(self, room_id: int) -> int:
        self.attempts_by_room[room_id] = self.attempts_by_room.get(room_id, 0) + 1
        return self.attempts_by_room[room_id]

    def next_hint_index(self, room_id: int) -> int:
        idx = self.hints_shown_by_room.get(room_id, 0)
        self.hints_shown_by_room[room_id] = idx + 1
        return idx

    def raise_tension(self, amount: int) -> None:
        self.tension = min(100, self.tension + amount)
