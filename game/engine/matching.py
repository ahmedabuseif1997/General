"""مطابقة تقريبية بين اسم غرض كتبه اللاعب وأغراض الغرفة (يتجاهل "ال" التعريف)."""
from __future__ import annotations

from game.content.rooms import GameObject


def normalize_ar(text: str) -> str:
    tokens = text.strip().split()
    normalized = []
    for token in tokens:
        token = token.strip(".,!؟،")
        if token.startswith("ال") and len(token) > 2:
            token = token[2:]
        normalized.append(token)
    return " ".join(normalized)


def match_object(objects: list[GameObject], target: str) -> GameObject | None:
    if not target:
        return None
    target_norm = normalize_ar(target)
    if not target_norm:
        return None
    for obj in objects:
        obj_norm = normalize_ar(obj.name)
        if target_norm == obj_norm or target_norm in obj_norm or obj_norm in target_norm:
            return obj
    return None
