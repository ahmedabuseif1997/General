using EscapeHouse.Interaction;
using EscapeHouse.Player;
using EscapeHouse.UI;
using UnityEngine;

namespace EscapeHouse.Core
{
    // حطه على GameObject فاضي في مشهد فاضي، ودوس Play — هو بيبني كل حاجة تانية بالكود
    public class GameBootstrapper : MonoBehaviour
    {
        private void Start()
        {
            SetupAtmosphere();

            GameObject playerGo = BuildPlayer(out FirstPersonController fpc, out PlayerInteractor interactor);

            GameObject hudGo = new GameObject("HUD");
            HUDController hud = hudGo.AddComponent<HUDController>();
            hud.Initialize();

            GameObject managerGo = new GameObject("GameManager");
            GameManager manager = managerGo.AddComponent<GameManager>();
            manager.Initialize(fpc, interactor, hud);
        }

        private void SetupAtmosphere()
        {
            RenderSettings.ambientLight = new Color(0.04f, 0.04f, 0.06f);
            RenderSettings.fog = true;
            RenderSettings.fogColor = new Color(0.02f, 0.02f, 0.03f);
            RenderSettings.fogDensity = 0.045f;
        }

        private GameObject BuildPlayer(out FirstPersonController fpc, out PlayerInteractor interactor)
        {
            GameObject playerGo = new GameObject("Player");
            CharacterController cc = playerGo.AddComponent<CharacterController>();
            cc.height = 1.8f;
            cc.center = new Vector3(0, 0.9f, 0);
            cc.radius = 0.35f;

            GameObject camGo = new GameObject("PlayerCamera");
            camGo.transform.SetParent(playerGo.transform, false);
            camGo.transform.localPosition = new Vector3(0, 1.6f, 0);
            Camera cam = camGo.AddComponent<Camera>();
            cam.nearClipPlane = 0.05f;
            camGo.AddComponent<AudioListener>();

            fpc = playerGo.AddComponent<FirstPersonController>();
            interactor = playerGo.AddComponent<PlayerInteractor>();
            interactor.playerCamera = cam;

            return playerGo;
        }
    }
}
