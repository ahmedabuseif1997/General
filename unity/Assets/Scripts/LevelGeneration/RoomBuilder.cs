using System.Collections.Generic;
using EscapeHouse.Data;
using EscapeHouse.Doors;
using EscapeHouse.Interaction;
using UnityEngine;

namespace EscapeHouse.LevelGeneration
{
    public class RoomBuildResult
    {
        public GameObject Root;
        public KeypadDoor Door;
        public Vector3 SpawnPoint;
        public Light RoomLight;
    }

    // بيبني أوضة whitebox كاملة (أرضية، حيطان، سقف، باب، وأغراض قابلة للفحص) من بيانات الأوضة
    public static class RoomBuilder
    {
        private const float RoomWidth = 10f;
        private const float RoomDepth = 10f;
        private const float RoomHeight = 4f;
        private const float WallThickness = 0.3f;

        public static RoomBuildResult Build(RoomData room, Transform parent)
        {
            GameObject root = new GameObject($"Room_{room.id}_{room.name}");
            root.transform.SetParent(parent, false);

            BuildFloorAndCeiling(root.transform);
            BuildWalls(root.transform);

            GameObject doorGo = BuildDoor(root.transform, room);
            KeypadDoor door = doorGo.AddComponent<KeypadDoor>();
            door.Room = room;

            Light light = BuildLight(root.transform);
            PlaceObjects(root.transform, room);

            return new RoomBuildResult
            {
                Root = root,
                Door = door,
                SpawnPoint = new Vector3(0f, 1f, -RoomDepth / 2f + 1.2f),
                RoomLight = light,
            };
        }

        private static void BuildFloorAndCeiling(Transform parent)
        {
            GameObject floor = CreateCube(parent, "Floor", new Vector3(0, -0.15f, 0), new Vector3(RoomWidth, 0.3f, RoomDepth), new Color(0.25f, 0.22f, 0.18f));
            GameObject ceiling = CreateCube(parent, "Ceiling", new Vector3(0, RoomHeight, 0), new Vector3(RoomWidth, 0.3f, RoomDepth), new Color(0.08f, 0.08f, 0.08f));
        }

        private static void BuildWalls(Transform parent)
        {
            Color wallColor = new Color(0.35f, 0.32f, 0.30f);
            float hh = RoomHeight / 2f;

            // جنوب (المدخل غير موجود هنا، اللاعب بيبدأ هنا)
            CreateCube(parent, "Wall_South", new Vector3(0, hh, -RoomDepth / 2f), new Vector3(RoomWidth, RoomHeight, WallThickness), wallColor);
            // شرق وغرب
            CreateCube(parent, "Wall_East", new Vector3(RoomWidth / 2f, hh, 0), new Vector3(WallThickness, RoomHeight, RoomDepth), wallColor);
            CreateCube(parent, "Wall_West", new Vector3(-RoomWidth / 2f, hh, 0), new Vector3(WallThickness, RoomHeight, RoomDepth), wallColor);

            // شمال — فيها فتحة الباب في النص، فبنبنيها كجزئين يمين وشمال بس
            float doorGap = 1.6f;
            float sideWidth = (RoomWidth - doorGap) / 2f;
            CreateCube(parent, "Wall_North_Left", new Vector3(-(doorGap / 2f + sideWidth / 2f), hh, RoomDepth / 2f), new Vector3(sideWidth, RoomHeight, WallThickness), wallColor);
            CreateCube(parent, "Wall_North_Right", new Vector3((doorGap / 2f + sideWidth / 2f), hh, RoomDepth / 2f), new Vector3(sideWidth, RoomHeight, WallThickness), wallColor);
            // لينتل فوق الباب
            CreateCube(parent, "Wall_North_Lintel", new Vector3(0, RoomHeight - 0.5f, RoomDepth / 2f), new Vector3(doorGap, 1f, WallThickness), wallColor);
        }

        private static GameObject BuildDoor(Transform parent, RoomData room)
        {
            GameObject doorGo = CreateCube(parent, $"Door_{room.id}", new Vector3(-0.7f, 1.5f, RoomDepth / 2f), new Vector3(1.5f, 3f, 0.15f), new Color(0.4f, 0.15f, 0.1f));
            // نخلي محور الدوران عند الحافة (المفصلة) مش النص
            doorGo.transform.position += doorGo.transform.right * 0.75f;
            GameObject pivot = new GameObject($"DoorPivot_{room.id}");
            pivot.transform.SetParent(parent, false);
            pivot.transform.position = new Vector3(-1.45f, 1.5f, RoomDepth / 2f);
            doorGo.transform.SetParent(pivot.transform, true);
            return pivot;
        }

        private static Light BuildLight(Transform parent)
        {
            GameObject lightGo = new GameObject("RoomLight");
            lightGo.transform.SetParent(parent, false);
            lightGo.transform.position = new Vector3(0, RoomHeight - 0.3f, 0);
            Light light = lightGo.AddComponent<Light>();
            light.type = LightType.Point;
            light.range = 12f;
            light.intensity = 1.1f;
            light.color = new Color(1f, 0.92f, 0.75f);
            return light;
        }

        private static void PlaceObjects(Transform parent, RoomData room)
        {
            int count = room.objects.Count;
            if (count == 0) return;

            float radius = 3.4f;
            for (int i = 0; i < count; i++)
            {
                GameObjectData data = room.objects[i];
                float angle = (360f / count) * i;
                // منتجنّب قطاع الباب (حوالين 0 درجة/شمال) عشان الأغراض ما تتلخبطش مع الفتحة
                float rad = (angle + 40f) * Mathf.Deg2Rad;
                Vector3 pos = new Vector3(Mathf.Sin(rad) * radius, 0.5f, Mathf.Cos(rad) * radius * 0.9f);

                GameObject pedestal = CreateCube(parent, $"Pedestal_{i}", pos - new Vector3(0, 0.4f, 0), new Vector3(0.5f, 0.2f, 0.5f), new Color(0.2f, 0.2f, 0.2f));

                Color objColor = ColorFromName(data.name);
                GameObject objGo = CreateCube(parent, $"Object_{i}_{data.name}", pos, new Vector3(0.4f, 0.4f, 0.4f), objColor);
                // CreatePrimitive(Cube) بيحط BoxCollider أوتوماتيك، مش محتاجين نضيف واحد تاني

                Interactable interactable = objGo.AddComponent<Interactable>();
                interactable.RoomId = room.id;
                interactable.Data = data;

                BuildLabel(objGo.transform, data.name);
            }
        }

        private static void BuildLabel(Transform parent, string text)
        {
            GameObject labelGo = new GameObject("Label");
            labelGo.transform.SetParent(parent, false);
            labelGo.transform.localPosition = new Vector3(0, 0.5f, 0);
            TextMesh mesh = labelGo.AddComponent<TextMesh>();
            mesh.text = text;
            mesh.characterSize = 0.15f;
            mesh.fontSize = 48;
            mesh.anchor = TextAnchor.LowerCenter;
            mesh.alignment = TextAlignment.Center;
            mesh.color = Color.white;
            LookAtCameraBillboard billboard = labelGo.AddComponent<LookAtCameraBillboard>();
        }

        private static Color ColorFromName(string name)
        {
            int hash = 0;
            foreach (char c in name) hash = hash * 31 + c;
            float hue = Mathf.Abs(hash % 360) / 360f;
            return Color.HSVToRGB(hue, 0.35f, 0.85f);
        }

        private static GameObject CreateCube(Transform parent, string name, Vector3 localPos, Vector3 size, Color color)
        {
            GameObject go = GameObject.CreatePrimitive(PrimitiveType.Cube);
            go.name = name;
            go.transform.SetParent(parent, false);
            go.transform.localPosition = localPos;
            go.transform.localScale = size;

            Renderer renderer = go.GetComponent<Renderer>();
            renderer.material = CreateMaterial(color);

            return go;
        }

        private static Material CreateMaterial(Color color)
        {
            Shader shader = FindBestShader();
            Material mat = shader != null ? new Material(shader) : new Material(Shader.Find("Diffuse"));
            if (mat.HasProperty("_BaseColor")) mat.SetColor("_BaseColor", color);
            if (mat.HasProperty("_Color")) mat.SetColor("_Color", color);
            return mat;
        }

        private static Shader FindBestShader()
        {
            string[] candidates = { "Universal Render Pipeline/Lit", "Standard", "Legacy Shaders/Diffuse", "Unlit/Color" };
            foreach (string name in candidates)
            {
                Shader s = Shader.Find(name);
                if (s != null) return s;
            }
            return null;
        }
    }

    // بيخلي لافتة الاسم بتبص للكاميرا دايمًا
    public class LookAtCameraBillboard : MonoBehaviour
    {
        private Transform _cam;

        private void Start()
        {
            if (Camera.main != null) _cam = Camera.main.transform;
        }

        private void LateUpdate()
        {
            if (_cam == null)
            {
                if (Camera.main == null) return;
                _cam = Camera.main.transform;
            }
            transform.rotation = Quaternion.LookRotation(transform.position - _cam.position);
        }
    }
}
