using UnityEngine;

namespace EscapeHouse.Data
{
    // بيحمّل Assets/Resources/Data/rooms.json وقت التشغيل
    public static class RoomLoader
    {
        private const string ResourcePath = "Data/rooms";

        public static HouseData Load()
        {
            TextAsset asset = Resources.Load<TextAsset>(ResourcePath);
            if (asset == null)
            {
                Debug.LogError($"[RoomLoader] مش لاقي الملف Resources/{ResourcePath}.json");
                return null;
            }

            HouseData house = JsonUtility.FromJson<HouseData>(asset.text);
            house.rooms.Sort((a, b) => a.id.CompareTo(b.id));
            return house;
        }
    }
}
