using EscapeHouse.Doors;
using UnityEngine;

namespace EscapeHouse.Interaction
{
    // بيرمي Raycast من نص الشاشة، ولو لقى غرض قابل للتفاعل بيسمح بالضغط على E
    public class PlayerInteractor : MonoBehaviour
    {
        public Camera playerCamera;
        public float interactRange = 3f;
        public LayerMask interactableMask = ~0;

        public System.Action<string> OnLookTextChanged; // بيتبعت اسم الغرض أو فاضي
        public System.Action<Interactable> OnExamine;
        public System.Action<KeypadDoor> OnOpenKeypad;

        private string _lastLookText = "";

        public bool InputLocked = false;

        private void Update()
        {
            if (InputLocked)
            {
                if (_lastLookText != "")
                {
                    _lastLookText = "";
                    OnLookTextChanged?.Invoke("");
                }
                return;
            }

            Ray ray = new Ray(playerCamera.transform.position, playerCamera.transform.forward);
            bool didHit = Physics.Raycast(ray, out RaycastHit hit, interactRange, interactableMask);

            string lookText = "";
            Interactable interactable = null;
            KeypadDoor door = null;

            if (didHit)
            {
                interactable = hit.collider.GetComponentInParent<Interactable>();
                door = hit.collider.GetComponentInParent<KeypadDoor>();

                if (interactable != null) lookText = $"اضغط E: افحص {interactable.DisplayName}";
                else if (door != null) lookText = "اضغط E: القفل الرقمي";
            }

            if (lookText != _lastLookText)
            {
                _lastLookText = lookText;
                OnLookTextChanged?.Invoke(lookText);
            }

            if (didHit && Input.GetKeyDown(KeyCode.E))
            {
                if (interactable != null) OnExamine?.Invoke(interactable);
                else if (door != null) OnOpenKeypad?.Invoke(door);
            }
        }
    }
}
