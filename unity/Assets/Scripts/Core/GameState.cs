using System.Collections.Generic;

namespace EscapeHouse.Core
{
    // نفس فكرة game/engine/state.py — نسخة C# من حالة اللعب
    public class GameState
    {
        public int CurrentRoomId = 1;
        public readonly HashSet<string> Inventory = new HashSet<string>();
        public readonly HashSet<string> ExaminedObjects = new HashSet<string>(); // "roomId:objectName"
        public readonly Dictionary<int, int> AttemptsByRoom = new Dictionary<int, int>();
        public readonly Dictionary<int, int> HintsShownByRoom = new Dictionary<int, int>();
        public int Tension = 0;
        public bool GameOver = false;
        public bool Victory = false;

        public bool HasItem(string item) => !string.IsNullOrEmpty(item) && Inventory.Contains(item);

        public void AddItem(string item)
        {
            if (!string.IsNullOrEmpty(item)) Inventory.Add(item);
        }

        // يرجع true لو أول مرة يتفحص فيها الغرض ده
        public bool MarkExamined(int roomId, string objectName)
        {
            string key = $"{roomId}:{objectName}";
            return ExaminedObjects.Add(key);
        }

        public int RecordAttempt(int roomId)
        {
            AttemptsByRoom.TryGetValue(roomId, out int current);
            current += 1;
            AttemptsByRoom[roomId] = current;
            return current;
        }

        public int NextHintIndex(int roomId)
        {
            HintsShownByRoom.TryGetValue(roomId, out int idx);
            HintsShownByRoom[roomId] = idx + 1;
            return idx;
        }

        public void RaiseTension(int amount)
        {
            Tension = Mathf_Min100(Tension + amount);
        }

        private static int Mathf_Min100(int v) => v > 100 ? 100 : v;
    }
}
