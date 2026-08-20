using System;
using System.Collections;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;

namespace EscapeHouse.UI
{
    // كل واجهة اللعب بتتبني هنا بالكود وقت التشغيل — مفيش Prefabs محتاجة تجهيز يدوي
    public class HUDController : MonoBehaviour
    {
        private Text _lookText;
        private Text _messageText;
        private Text _roomHeaderText;
        private Text _inventoryText;
        private Text _tensionText;
        private Text _endText;

        private GameObject _inventoryPanel;
        private GameObject _keypadPanel;
        private GameObject _endPanel;
        private Text _keypadDisplay;

        private string _enteredDigits = "";
        private Action<string> _onKeypadSubmit;
        private Action _onKeypadClose;

        public bool KeypadOpen { get; private set; }

        private static Font GetDefaultFont()
        {
            Font font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            if (font == null) font = Resources.GetBuiltinResource<Font>("Arial.ttf");
            if (font == null) font = Font.CreateDynamicFontFromOSFont("Arial", 24);
            return font;
        }

        public void Initialize()
        {
            if (FindObjectOfType<EventSystem>() == null)
            {
                var esGo = new GameObject("EventSystem");
                esGo.AddComponent<EventSystem>();
                esGo.AddComponent<StandaloneInputModule>();
            }

            GameObject canvasGo = new GameObject("HUDCanvas");
            Canvas canvas = canvasGo.AddComponent<Canvas>();
            canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            CanvasScaler scaler = canvasGo.AddComponent<CanvasScaler>();
            scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
            scaler.referenceResolution = new Vector2(1280, 720);
            canvasGo.AddComponent<GraphicRaycaster>();
            canvasGo.transform.SetParent(transform, false);

            BuildCrosshair(canvasGo.transform);
            _lookText = BuildText(canvasGo.transform, "LookText", new Vector2(0.5f, 0.5f), new Vector2(0, -60), 22, TextAnchor.UpperCenter, 700, 40);
            _messageText = BuildText(canvasGo.transform, "MessageText", new Vector2(0.5f, 0f), new Vector2(0, 140), 24, TextAnchor.LowerCenter, 900, 200);
            _roomHeaderText = BuildText(canvasGo.transform, "RoomHeaderText", new Vector2(0.5f, 1f), new Vector2(0, -60), 30, TextAnchor.UpperCenter, 900, 60);
            _tensionText = BuildText(canvasGo.transform, "TensionText", new Vector2(0f, 1f), new Vector2(140, -20), 16, TextAnchor.UpperLeft, 260, 30);

            _inventoryPanel = BuildPanel(canvasGo.transform, "InventoryPanel", new Vector2(1f, 1f), new Vector2(-190, -20), 340, 220);
            _inventoryText = BuildText(_inventoryPanel.transform, "InventoryText", new Vector2(0.5f, 0.5f), Vector2.zero, 18, TextAnchor.UpperRight, 320, 200);
            _inventoryPanel.SetActive(false);

            BuildKeypad(canvasGo.transform);

            _endPanel = BuildPanel(canvasGo.transform, "EndPanel", new Vector2(0.5f, 0.5f), Vector2.zero, 900, 300);
            Image endBg = _endPanel.GetComponent<Image>();
            endBg.color = new Color(0f, 0f, 0f, 0.92f);
            _endText = BuildText(_endPanel.transform, "EndText", new Vector2(0.5f, 0.5f), Vector2.zero, 26, TextAnchor.MiddleCenter, 820, 260);
            _endPanel.SetActive(false);

            SetTensionValue(0);
        }

        private void BuildCrosshair(Transform parent)
        {
            GameObject go = new GameObject("Crosshair");
            go.transform.SetParent(parent, false);
            Image img = go.AddComponent<Image>();
            img.color = new Color(1f, 1f, 1f, 0.85f);
            RectTransform rt = go.GetComponent<RectTransform>();
            rt.anchorMin = rt.anchorMax = new Vector2(0.5f, 0.5f);
            rt.sizeDelta = new Vector2(4, 4);
        }

        private Text BuildText(Transform parent, string name, Vector2 anchor, Vector2 pos, int fontSize, TextAnchor alignment, float width, float height)
        {
            GameObject go = new GameObject(name);
            go.transform.SetParent(parent, false);
            Text txt = go.AddComponent<Text>();
            txt.font = GetDefaultFont();
            txt.fontSize = fontSize;
            txt.alignment = alignment;
            txt.color = Color.white;
            txt.horizontalOverflow = HorizontalWrapMode.Wrap;
            txt.verticalOverflow = VerticalWrapMode.Overflow;
            txt.text = "";

            RectTransform rt = go.GetComponent<RectTransform>();
            rt.anchorMin = rt.anchorMax = anchor;
            rt.pivot = anchor;
            rt.anchoredPosition = pos;
            rt.sizeDelta = new Vector2(width, height);
            return txt;
        }

        private GameObject BuildPanel(Transform parent, string name, Vector2 anchor, Vector2 pos, float width, float height)
        {
            GameObject go = new GameObject(name);
            go.transform.SetParent(parent, false);
            Image img = go.AddComponent<Image>();
            img.color = new Color(0f, 0f, 0f, 0.75f);
            RectTransform rt = go.GetComponent<RectTransform>();
            rt.anchorMin = rt.anchorMax = anchor;
            rt.pivot = anchor;
            rt.anchoredPosition = pos;
            rt.sizeDelta = new Vector2(width, height);
            return go;
        }

        // ---------------- كيباد ----------------

        private void BuildKeypad(Transform parent)
        {
            _keypadPanel = BuildPanel(parent, "KeypadPanel", new Vector2(0.5f, 0.5f), Vector2.zero, 340, 460);
            _keypadDisplay = BuildText(_keypadPanel.transform, "KeypadDisplay", new Vector2(0.5f, 1f), new Vector2(0, -20), 34, TextAnchor.MiddleCenter, 280, 60);

            string[] labels = { "1", "2", "3", "4", "5", "6", "7", "8", "9", "مسح", "0", "دخول" };
            for (int i = 0; i < labels.Length; i++)
            {
                int col = i % 3;
                int row = i / 3;
                string label = labels[i];
                GameObject btnGo = BuildButton(_keypadPanel.transform, "Key_" + label,
                    new Vector2(-100 + col * 100, -110 - row * 80), 90, 70, label,
                    () => OnKeypadKey(label));
            }

            GameObject closeBtn = BuildButton(_keypadPanel.transform, "CloseBtn", new Vector2(0, -420), 200, 50, "إغلاق (Esc)", CloseKeypad);

            _keypadPanel.SetActive(false);
        }

        private GameObject BuildButton(Transform parent, string name, Vector2 pos, float width, float height, string label, Action onClick)
        {
            GameObject go = new GameObject(name);
            go.transform.SetParent(parent, false);
            Image img = go.AddComponent<Image>();
            img.color = new Color(0.15f, 0.15f, 0.15f, 0.95f);
            RectTransform rt = go.GetComponent<RectTransform>();
            rt.anchorMin = rt.anchorMax = new Vector2(0.5f, 1f);
            rt.pivot = new Vector2(0.5f, 1f);
            rt.anchoredPosition = pos;
            rt.sizeDelta = new Vector2(width, height);

            Button btn = go.AddComponent<Button>();
            btn.onClick.AddListener(() => onClick());

            Text txt = BuildText(go.transform, "Label", new Vector2(0.5f, 0.5f), Vector2.zero, 22, TextAnchor.MiddleCenter, width, height);
            txt.text = label;
            txt.raycastTarget = false;

            return go;
        }

        private void OnKeypadKey(string label)
        {
            if (label == "مسح") { _enteredDigits = ""; }
            else if (label == "دخول") { SubmitKeypad(); return; }
            else if (_enteredDigits.Length < 6) { _enteredDigits += label; }
            _keypadDisplay.text = _enteredDigits;
        }

        private void SubmitKeypad()
        {
            string digits = _enteredDigits;
            _enteredDigits = "";
            _keypadDisplay.text = "";
            _onKeypadSubmit?.Invoke(digits);
        }

        public void OpenKeypad(Action<string> onSubmit, Action onClose)
        {
            _enteredDigits = "";
            _keypadDisplay.text = "";
            _onKeypadSubmit = onSubmit;
            _onKeypadClose = onClose;
            _keypadPanel.SetActive(true);
            KeypadOpen = true;
            Cursor.lockState = CursorLockMode.None;
            Cursor.visible = true;
        }

        public void CloseKeypad()
        {
            _keypadPanel.SetActive(false);
            KeypadOpen = false;
            _onKeypadClose?.Invoke();
            Cursor.lockState = CursorLockMode.Locked;
            Cursor.visible = false;
        }

        private void Update()
        {
            if (KeypadOpen && Input.GetKeyDown(KeyCode.Escape))
            {
                CloseKeypad();
            }
        }

        // ---------------- تحديثات عامة ----------------

        public void SetLookText(string text) => _lookText.text = text;

        private Coroutine _messageFade;

        public void ShowMessage(string text)
        {
            if (_messageFade != null) StopCoroutine(_messageFade);
            _messageText.text = text;
            _messageFade = StartCoroutine(ClearMessageAfter(6f));
        }

        private IEnumerator ClearMessageAfter(float seconds)
        {
            yield return new WaitForSeconds(seconds);
            _messageText.text = "";
        }

        public void ShowRoomHeader(string roomName, int index, int total)
        {
            _roomHeaderText.text = $"الغرفة {index}/{total}: {roomName}";
        }

        public void SetInventoryText(string text) => _inventoryText.text = text;

        public void ToggleInventory() => _inventoryPanel.SetActive(!_inventoryPanel.activeSelf);

        public void SetTensionValue(int tension)
        {
            _tensionText.text = $"التوتر: {tension}%";
            _tensionText.color = Color.Lerp(Color.white, new Color(0.9f, 0.1f, 0.1f), tension / 100f);
        }

        public void ShowEndScreen(string text)
        {
            _endText.text = text;
            _endPanel.SetActive(true);
            Cursor.lockState = CursorLockMode.None;
            Cursor.visible = true;
        }
    }
}
