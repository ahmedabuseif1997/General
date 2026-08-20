"""كل نصوص العرض للاعب — مكان واحد للتحكم في شكل المخرجات."""
from __future__ import annotations

DIVIDER = "─" * 44


def divider() -> None:
    print(DIVIDER)


def show(text: str) -> None:
    print(text)


def show_room_header(room_name: str, room_number: int, total_rooms: int) -> None:
    divider()
    print(f"الغرفة {room_number}/{total_rooms}: {room_name}")
    divider()


def show_help() -> None:
    print(
        "\n".join(
            [
                "الأوامر المتاحة:",
                "  افحص <غرض>      — تفحص غرض في الأوضة",
                "  خذ <غرض>        — تاخد غرض لو ممكن",
                "  ادخل <رقم>      — تدخل كود في القفل",
                "  الجرد           — تشوف اللي معاك",
                "  تلميح           — تاخد تلميح للغرفة دي",
                "  انظر            — وصف الأوضة تاني",
                "  مساعدة          — الأوامر دي تاني",
                "  خروج            — تسيب اللعبة",
            ]
        )
    )


def show_objects_list(object_names: list[str]) -> None:
    names = "، ".join(object_names)
    print(f"الأغراض اللي حواليك: {names}")
