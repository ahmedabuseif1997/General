using System.Collections;
using EscapeHouse.Data;
using EscapeHouse.Doors;
using EscapeHouse.Interaction;
using EscapeHouse.LevelGeneration;
using EscapeHouse.Player;
using EscapeHouse.UI;
using UnityEngine;

namespace EscapeHouse.Core
{
    // المايسترو: بيحمّل المحتوى، يبني الأوض، ويوصّل الأنظمة كلها ببعض
    public class GameManager : MonoBehaviour
    {
        private HouseData _house;
        private GameState _state;
        private FirstPersonController _player;
        private PlayerInteractor _interactor;
        private HUDController _hud;
        private Transform _roomRoot;
        private RoomBuildResult _currentRoom;
        private Light _roomLight;
        private const float BaseLightIntensity = 1.1f;

        public void Initialize(FirstPersonController player, PlayerInteractor interactor, HUDController hud)
        {
            _house = RoomLoader.Load();
            if (_house == null)
            {
                Debug.LogError("[GameManager] فشل تحميل rooms.json");
                return;
            }

            _state = new GameState();
            _player = player;
            _interactor = interactor;
            _hud = hud;

            _interactor.OnLookTextChanged += _hud.SetLookText;
            _interactor.OnExamine += OnExamine;
            _interactor.OnOpenKeypad += OnOpenKeypad;

            _roomRoot = new GameObject("RoomRoot").transform;

            _hud.ShowMessage(_house.intro);
            LoadRoom(_house.rooms[0].id);
        }

        private void Update()
        {
            if (_state == null || _state.GameOver) return;

            if (Input.GetKeyDown(KeyCode.Tab)) _hud.ToggleInventory();
            if (Input.GetKeyDown(KeyCode.H)) HandleHintKey();

            UpdateLightFlicker();
        }

        private void LoadRoom(int roomId)
        {
            if (_currentRoom != null) Destroy(_currentRoom.Root);

            RoomData room = _house.rooms.Find(r => r.id == roomId);
            _state.CurrentRoomId = roomId;
            _currentRoom = RoomBuilder.Build(room, _roomRoot);
            _roomLight = _currentRoom.RoomLight;

            _player.transform.position = _currentRoom.SpawnPoint;
            _player.transform.rotation = Quaternion.identity;

            _hud.ShowRoomHeader(room.name, room.id, _house.rooms.Count);
            _hud.ShowMessage(room.intro);
            _hud.SetTensionValue(_state.Tension);
            RefreshInventoryUI();
        }

        private void OnExamine(Interactable interactable)
        {
            GameObjectData data = interactable.Data;
            bool firstTime = _state.MarkExamined(interactable.RoomId, data.name);

            string text;
            bool hasRequirement = !string.IsNullOrEmpty(data.requiresItem);
            if (hasRequirement && !_state.HasItem(data.requiresItem))
            {
                text = data.examine;
            }
            else if (hasRequirement && _state.HasItem(data.requiresItem))
            {
                text = !string.IsNullOrEmpty(data.examineWithItem) ? data.examineWithItem : data.examine;
            }
            else
            {
                text = data.examine;
            }

            _hud.ShowMessage(text);

            if (!string.IsNullOrEmpty(data.givesItem) && firstTime)
            {
                _state.AddItem(data.givesItem);
                RefreshInventoryUI();
            }
        }

        private void OnOpenKeypad(KeypadDoor door)
        {
            _interactor.InputLocked = true;
            _player.InputLocked = true;

            _hud.OpenKeypad(
                digits => OnKeypadSubmit(door, digits),
                () =>
                {
                    _interactor.InputLocked = false;
                    _player.InputLocked = false;
                });
        }

        private void OnKeypadSubmit(KeypadDoor door, string digits)
        {
            RoomData room = door.Room;
            KeypadResult result = KeypadLogic.TryCode(room, digits, _state);

            if (result == KeypadResult.Success)
            {
                _hud.ShowMessage("*** بيب! القفل بيفتح، والباب بيتحرك ببطء. ***");
                door.Open();
                _hud.CloseKeypad();
                StartCoroutine(AdvanceAfterDelay(room));
                return;
            }

            if (result == KeypadResult.LockedOut)
            {
                _hud.ShowMessage(room.tensionOnFail + "\nالقفل اتجمد. مفيش محاولات تانية.");
                _hud.SetTensionValue(_state.Tension);
                _state.GameOver = true;
                _state.Victory = false;
                _hud.CloseKeypad();
                EndGame();
                return;
            }

            // Wrong
            int remaining = KeypadLogic.AttemptsLeft(room, _state);
            string msg = "الكود غلط.\n" + room.tensionOnFail;
            if (remaining >= 0) msg += $"\nباقيلك {remaining} محاولة/محاولات بس.";
            msg += "\n" + TensionSystem.Describe(_state.Tension);
            _hud.ShowMessage(msg);
            _hud.SetTensionValue(_state.Tension);
        }

        private IEnumerator AdvanceAfterDelay(RoomData room)
        {
            yield return new WaitForSeconds(2f);

            int index = _house.rooms.FindIndex(r => r.id == room.id);
            if (index == _house.rooms.Count - 1)
            {
                _state.Victory = true;
                _state.GameOver = true;
                EndGame();
            }
            else
            {
                LoadRoom(_house.rooms[index + 1].id);
            }
        }

        private void EndGame()
        {
            _player.InputLocked = true;
            _interactor.InputLocked = true;
            string text = _state.Victory ? _house.endingWin : _house.endingLose;
            _hud.ShowEndScreen(text);
        }

        private void HandleHintKey()
        {
            RoomData room = _house.rooms.Find(r => r.id == _state.CurrentRoomId);
            int idx = _state.NextHintIndex(room.id);
            string text = idx < room.hints.Count ? $"تلميح: {room.hints[idx]}" : "مفيش تلميحات تانية للغرفة دي.";
            _hud.ShowMessage(text);
        }

        private void RefreshInventoryUI()
        {
            string text = _state.Inventory.Count == 0
                ? "حقيبتك فاضية."
                : "معاك:\n" + string.Join("\n", _state.Inventory);
            _hud.SetInventoryText(text);
        }

        private void UpdateLightFlicker()
        {
            if (_roomLight == null) return;

            if (_state.Tension >= 40)
            {
                float noise = Mathf.PerlinNoise(Time.time * 6f, 0f);
                float amount = Mathf.Clamp01((_state.Tension - 40) / 60f);
                _roomLight.intensity = BaseLightIntensity - amount * noise * 0.8f;
            }
            else
            {
                _roomLight.intensity = BaseLightIntensity;
            }
        }
    }
}
