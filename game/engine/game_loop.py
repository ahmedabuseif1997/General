"""اللوب الرئيسي: يطبع الأوضة، ياخد أوامر اللاعب، وينفذها لحد ما يخرج أو يخلص اللعبة."""
from __future__ import annotations

from game.content.rooms import House, Room
from game.engine.matching import match_object
from game.engine.parser import Command, parse
from game.engine.state import GameState
from game.systems import inventory, tension
from game.systems.keypad import KeypadResult, attempts_left, try_code
from game.ui import renderer


def _handle_examine(room: Room, target: str, state: GameState) -> None:
    obj = match_object(room.objects, target)
    if obj is None:
        renderer.show("مفيش غرض بالاسم ده هنا.")
        return

    first_time = state.mark_examined(room.id, obj.name)

    if obj.requires_item and not state.has_item(obj.requires_item):
        renderer.show(obj.examine)
        return

    if obj.requires_item and state.has_item(obj.requires_item):
        renderer.show(obj.examine_with_item or obj.examine)
    else:
        renderer.show(obj.examine)

    if obj.gives_item and first_time:
        state.add_item(obj.gives_item)


def _handle_hint(room: Room, state: GameState) -> None:
    idx = state.next_hint_index(room.id)
    if idx < len(room.hints):
        renderer.show(f"تلميح: {room.hints[idx]}")
    else:
        renderer.show("مفيش تلميحات تانية للغرفة دي.")


def _handle_code(room: Room, target: str, state: GameState) -> bool:
    """يرجع True لو الغرفة اتحلت."""
    digits = target.strip()
    if not digits:
        renderer.show("اكتب الرقم اللي عايز تجربه، مثلاً: ادخل 1974")
        return False

    result = try_code(room, digits, state)

    if result == KeypadResult.SUCCESS:
        renderer.show("*** بيب! القفل بيفتح، والباب بيتحرك ببطء. ***")
        return True

    if result == KeypadResult.LOCKED_OUT:
        renderer.show(room.tension_on_fail)
        renderer.show("القفل اتجمد. مفيش محاولات تانية.")
        state.game_over = True
        state.victory = False
        return False

    # WRONG
    renderer.show("الكود غلط.")
    renderer.show(room.tension_on_fail)
    remaining = attempts_left(room, state)
    if remaining is not None:
        renderer.show(f"باقيلك {remaining} محاولة/محاولات بس.")
    renderer.show(tension.describe(state))
    return False


def _dispatch(cmd: Command, room: Room, state: GameState) -> bool:
    """ينفذ أمر واحد، ويرجع True لو الغرفة اتحلت (الباب فتح)."""
    if cmd.verb == "examine":
        _handle_examine(room, cmd.target, state)
    elif cmd.verb == "take":
        _handle_examine(room, cmd.target, state)
    elif cmd.verb == "enter_code":
        return _handle_code(room, cmd.target, state)
    elif cmd.verb == "inventory":
        renderer.show(inventory.describe(state))
    elif cmd.verb == "hint":
        _handle_hint(room, state)
    elif cmd.verb == "look":
        renderer.show(room.intro)
        renderer.show_objects_list([o.name for o in room.objects])
    elif cmd.verb == "help":
        renderer.show_help()
    elif cmd.verb == "quit":
        state.game_over = True
        state.quit_requested = True
    else:
        renderer.show("مفهمتش الأمر. اكتب 'مساعدة' عشان تشوف الأوامر المتاحة.")
    return False


def run(house: House, state: GameState) -> None:
    total_rooms = len(house.rooms)
    renderer.show(house.intro)
    renderer.divider()
    renderer.show_help()

    while not state.game_over:
        room = house.room_by_id(state.current_room_id)
        renderer.show_room_header(room.name, room.id, total_rooms)
        renderer.show(room.intro)
        renderer.show_objects_list([o.name for o in room.objects])

        solved = False
        while not solved and not state.game_over:
            try:
                raw = input("\n> ").strip()
            except (EOFError, KeyboardInterrupt):
                renderer.show("")
                state.game_over = True
                state.quit_requested = True
                break
            cmd = parse(raw)
            solved = _dispatch(cmd, room, state)

        if state.game_over:
            break

        if room.id == house.rooms[-1].id:
            state.victory = True
            state.game_over = True
        else:
            next_id = house.rooms[house.rooms.index(room) + 1].id
            state.current_room_id = next_id

    renderer.divider()
    if state.victory:
        renderer.show(house.ending_win)
    elif state.quit_requested:
        renderer.show("سبت البيت... من غير ما تعرف حصل إيه فيه.")
    else:
        renderer.show(house.ending_lose)
