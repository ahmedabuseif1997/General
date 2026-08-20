using System;
using System.Collections.Generic;

namespace EscapeHouse.Data
{
    [Serializable]
    public class GameObjectData
    {
        public string name;
        public string examine;
        public bool isClue;
        public string givesItem;
        public string requiresItem;
        public string examineWithItem;
    }

    [Serializable]
    public class RedHerringData
    {
        public string source;
        public string text;
    }

    [Serializable]
    public class RoomData
    {
        public int id;
        public string name;
        public int tier;
        public string intro;
        public List<GameObjectData> objects;
        public string code;
        public List<RedHerringData> redHerrings;
        public List<string> hints;
        public int maxAttempts; // -1 means unlimited
        public string tensionOnFail;
        public string difficultyNote;
    }

    [Serializable]
    public class HouseData
    {
        public string intro;
        public string endingWin;
        public string endingLose;
        public List<RoomData> rooms;
    }
}
