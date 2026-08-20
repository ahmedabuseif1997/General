"""تحميل محتوى الغرف من game/data/rooms.yaml إلى كائنات بايثون بسيطة."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "rooms.yaml"


@dataclass
class GameObject:
    name: str
    examine: str = ""
    is_clue: bool = False
    gives_item: str | None = None
    requires_item: str | None = None
    examine_with_item: str | None = None


@dataclass
class RedHerring:
    source: str
    text: str


@dataclass
class Room:
    id: int
    name: str
    tier: int
    intro: str
    objects: list[GameObject]
    code: str
    red_herrings: list[RedHerring]
    hints: list[str]
    max_attempts: int | None
    tension_on_fail: str
    difficulty_note: str = ""


@dataclass
class House:
    intro: str
    ending_win: str
    ending_lose: str
    rooms: list[Room] = field(default_factory=list)

    def room_by_id(self, room_id: int) -> Room:
        for room in self.rooms:
            if room.id == room_id:
                return room
        raise KeyError(f"مفيش غرفة برقم {room_id}")


def load_house(path: Path = DATA_FILE) -> House:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))

    rooms = []
    for r in raw["rooms"]:
        objects = [
            GameObject(
                name=o["name"],
                examine=o.get("examine", ""),
                is_clue=o.get("is_clue", False),
                gives_item=o.get("gives_item"),
                requires_item=o.get("requires_item"),
                examine_with_item=o.get("examine_with_item"),
            )
            for o in r.get("objects", [])
        ]
        red_herrings = [
            RedHerring(source=h["source"], text=h["text"])
            for h in r.get("red_herrings", [])
        ]
        rooms.append(
            Room(
                id=r["id"],
                name=r["name"],
                tier=r["tier"],
                intro=r["intro"].strip(),
                objects=objects,
                code=str(r["code"]),
                red_herrings=red_herrings,
                hints=r.get("hints", []),
                max_attempts=r.get("max_attempts"),
                tension_on_fail=r.get("tension_on_fail", ""),
                difficulty_note=r.get("difficulty_note", ""),
            )
        )
    rooms.sort(key=lambda r: r.id)

    return House(
        intro=raw["intro"].strip(),
        ending_win=raw["ending_win"].strip(),
        ending_lose=raw["ending_lose"].strip(),
        rooms=rooms,
    )
