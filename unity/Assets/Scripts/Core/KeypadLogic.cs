using EscapeHouse.Data;

namespace EscapeHouse.Core
{
    public enum KeypadResult
    {
        Success,
        Wrong,
        LockedOut
    }

    // نفس منطق game/systems/keypad.py
    public static class KeypadLogic
    {
        private const int TensionPerWrongAttempt = 4;

        public static KeypadResult TryCode(RoomData room, string enteredCode, GameState state)
        {
            enteredCode = enteredCode?.Trim() ?? "";

            if (enteredCode == room.code)
            {
                return KeypadResult.Success;
            }

            int attempts = state.RecordAttempt(room.id);
            state.RaiseTension(TensionPerWrongAttempt * room.tier / 2 + TensionPerWrongAttempt);

            if (room.maxAttempts >= 0 && attempts >= room.maxAttempts)
            {
                return KeypadResult.LockedOut;
            }

            return KeypadResult.Wrong;
        }

        public static int AttemptsLeft(RoomData room, GameState state)
        {
            if (room.maxAttempts < 0) return -1; // غير محدود
            state.AttemptsByRoom.TryGetValue(room.id, out int used);
            int left = room.maxAttempts - used;
            return left < 0 ? 0 : left;
        }
    }
}
