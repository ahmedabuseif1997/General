using UnityEngine;

namespace EscapeHouse.Player
{
    // كنترولر بسيط: WASD للحركة، الماوس للنظر — Input Manager القديم (متاح افتراضيًا في أي مشروع Unity)
    [RequireComponent(typeof(CharacterController))]
    public class FirstPersonController : MonoBehaviour
    {
        public float moveSpeed = 4f;
        public float mouseSensitivity = 2f;
        public float gravity = -9.81f;

        private CharacterController _controller;
        private Camera _camera;
        private float _pitch = 0f;
        private Vector3 _verticalVelocity;

        public bool InputLocked = false; // بيتقفل لما الكيباد أو شاشة فاحصة مفتوحة

        private void Awake()
        {
            _controller = GetComponent<CharacterController>();
            _camera = GetComponentInChildren<Camera>();
        }

        private void Start()
        {
            Cursor.lockState = CursorLockMode.Locked;
            Cursor.visible = false;
        }

        private void Update()
        {
            HandleCursorToggle();

            if (InputLocked) return;

            HandleLook();
            HandleMove();
        }

        private void HandleCursorToggle()
        {
            // Esc يفك قفل الماوس مؤقتًا (مفيد وقت الاختبار)
            if (Input.GetKeyDown(KeyCode.Escape))
            {
                bool locked = Cursor.lockState == CursorLockMode.Locked;
                Cursor.lockState = locked ? CursorLockMode.None : CursorLockMode.Locked;
                Cursor.visible = locked;
            }
        }

        private void HandleLook()
        {
            if (Cursor.lockState != CursorLockMode.Locked) return;

            float mouseX = Input.GetAxis("Mouse X") * mouseSensitivity;
            float mouseY = Input.GetAxis("Mouse Y") * mouseSensitivity;

            transform.Rotate(Vector3.up * mouseX);

            _pitch -= mouseY;
            _pitch = Mathf.Clamp(_pitch, -80f, 80f);
            if (_camera != null)
            {
                _camera.transform.localEulerAngles = new Vector3(_pitch, 0f, 0f);
            }
        }

        private void HandleMove()
        {
            float h = Input.GetAxisRaw("Horizontal");
            float v = Input.GetAxisRaw("Vertical");
            Vector3 move = (transform.right * h + transform.forward * v).normalized * moveSpeed;

            if (_controller.isGrounded && _verticalVelocity.y < 0)
            {
                _verticalVelocity.y = -2f;
            }
            _verticalVelocity.y += gravity * Time.deltaTime;

            _controller.Move((move + _verticalVelocity) * Time.deltaTime);
        }
    }
}
