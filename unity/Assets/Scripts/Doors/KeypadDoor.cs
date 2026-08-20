using System.Collections;
using EscapeHouse.Data;
using UnityEngine;

namespace EscapeHouse.Doors
{
    // الباب المرتبط بالكيباد بتاع الأوضة الحالية
    public class KeypadDoor : MonoBehaviour
    {
        public RoomData Room;
        private bool _isOpen = false;

        public void Open()
        {
            if (_isOpen) return;
            _isOpen = true;
            StartCoroutine(SwingOpen());
        }

        private IEnumerator SwingOpen()
        {
            Quaternion start = transform.rotation;
            Quaternion end = start * Quaternion.Euler(0f, 90f, 0f);
            float t = 0f;
            const float duration = 1.2f;

            while (t < duration)
            {
                t += Time.deltaTime;
                transform.rotation = Quaternion.Slerp(start, end, t / duration);
                yield return null;
            }
            transform.rotation = end;
        }
    }
}
