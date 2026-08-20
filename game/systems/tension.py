"""مقياس التوتر/الرعب — بيوصف حالة اللاعب النفسية كل ما يتقدم في اللعبة."""
from __future__ import annotations

from game.engine.state import GameState

LEVELS = [
    (0, "الهدوء غريب، بس مفيش حاجة مخيفة لسه."),
    (20, "قلبك بيدق أسرع شوية من غير سبب واضح."),
    (40, "بتحس إن فيه حد بيراقبك من بعيد."),
    (60, "الصوت في البيت بقى أعلى. خطوات، همس، مش فاكر إيه بالظبط."),
    (80, "مش قادر تفكر صح. البيت بقى حي، وبيكرهك."),
]


def describe(state: GameState) -> str:
    description = LEVELS[0][1]
    for threshold, text in LEVELS:
        if state.tension >= threshold:
            description = text
    return description
