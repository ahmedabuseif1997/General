using EscapeHouse.Data;
using UnityEngine;

namespace EscapeHouse.Interaction
{
    // بيتحط على أي غرض قابل للفحص في الأوضة
    public class Interactable : MonoBehaviour
    {
        public int RoomId;
        public GameObjectData Data;

        public string DisplayName => Data != null ? Data.name : gameObject.name;
    }
}
