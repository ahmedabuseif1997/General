"""يحوّل جملة نصية من اللاعب لأمر مفهوم (فعل + هدف)."""
from __future__ import annotations

import re
from dataclasses import dataclass

# كل فعل له مرادفات — أول كلمة في الجملة بتتقارن بالمرادفات دي
VERB_SYNONYMS: dict[str, list[str]] = {
    "examine": ["افحص", "عاين", "شوف", "افتح", "اقرا", "اقرأ"],
    "take": ["خذ", "احمل", "ياخد"],
    "enter_code": ["ادخل", "كود", "الكود"],
    "inventory": ["الجرد", "حقيبتي", "اغراضي", "أغراضي"],
    "hint": ["تلميح", "لمحني", "ساعدني"],
    "look": ["انظر", "حواليا", "الغرفة", "وصف"],
    "help": ["مساعدة", "اوامر", "أوامر"],
    "quit": ["خروج", "استسلام", "quit", "exit"],
}

VERB_BY_WORD: dict[str, str] = {
    w: verb for verb, words in VERB_SYNONYMS.items() for w in words
}


@dataclass
class Command:
    verb: str
    target: str


def _normalize(text: str) -> str:
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    return text


def parse(raw: str) -> Command:
    text = _normalize(raw)
    if not text:
        return Command(verb="unknown", target="")

    parts = text.split(" ", 1)
    first_word = parts[0]
    rest = parts[1] if len(parts) > 1 else ""

    verb = VERB_BY_WORD.get(first_word)
    if verb is None:
        # حالة "ادخل 4471" ممكن تتكتب "4471" لوحدها لو اللاعب في وضع كتابة كود مباشر
        if text.isdigit():
            return Command(verb="enter_code", target=text)
        return Command(verb="unknown", target=text)

    return Command(verb=verb, target=rest)
