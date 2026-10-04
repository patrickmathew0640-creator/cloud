using System.Globalization;
using UnityEngine;
using UnityEngine.Rendering;

namespace VirtualMall
{
    /// <summary>
    /// Generates the complete shopping complex from Unity primitives:
    /// exterior plaza, building shell, main entrance, lobby, central corridor, six shops,
    /// exit hall, lighting, the first-person player and the UI.
    ///
    /// Layout (top view, metres): X = across the mall, Z = into the mall.
    ///   z  0..12  Main lobby (entrance in the front wall at z = 0)
    ///   z 12..54  Central corridor (x -4..4) with 3 shops on each side (each 14 m wide, 16 m deep)
    ///   z 54..62  Exit hall (exit door in the back wall at z = 62)
    /// </summary>
    public static class MallBuilder
    {
        public const float HalfWidth = 20f;
        public const float Length = 62f;
        public const float WallHeight = 5f;
        public const float CorridorHalfWidth = 4f;
        public const float LobbyEnd = 12f;
        public const float ShopsEnd = 54f;
        public const float ShopWidth = 14f;   // along the corridor
        public const float ShopDepth = 16f;   // away from the corridor

        public static readonly Vector3 SpawnPosition = new Vector3(0f, 0.05f, -7f);
        public const float SpawnYaw = 0f;

        private const float WallThickness = 0.3f;
        private static readonly Color LabelDark = new Color(0.08f, 0.09f, 0.11f, 0.88f);
        private static readonly Color LabelGold = new Color(1f, 0.83f, 0.3f);

        private static Material M(Color c, float smooth = 0.15f) => MallAssets.GetMaterial(c, smooth);
        private static Material M(float r, float g, float b, float smooth = 0.15f) => MallAssets.GetMaterial(new Color(r, g, b), smooth);
        private static Transform Group(string name, Transform parent, Vector3 pos = default, float yaw = 0f)
            => MallAssets.CreateGroup(name, parent, pos, new Vector3(0f, yaw, 0f)).transform;
        private static Color Opaque(Color c) => new Color(c.r, c.g, c.b, 1f);

        // ================================================================== entry points

        /// <summary>Builds everything (environment, lighting, player, UI) under <paramref name="root"/>.</summary>
        public static UIManager BuildAll(Transform root)
        {
            DisableOtherCamerasAndSuns(root);
            ApplyRenderSettings();
            BuildLighting(root);
            BuildEnvironment(root);
            CreatePlayer(root);
            return CreateUI(root);
        }

        public static void ApplyRenderSettings()
        {
            RenderSettings.ambientMode = AmbientMode.Trilight;
            RenderSettings.ambientSkyColor = new Color(0.80f, 0.82f, 0.86f);
            RenderSettings.ambientEquatorColor = new Color(0.62f, 0.62f, 0.64f);
            RenderSettings.ambientGroundColor = new Color(0.40f, 0.38f, 0.36f);
            RenderSettings.ambientIntensity = 1f;
            RenderSettings.fog = false;
        }

        /// <summary>Human readable name of the area at a world position (used by the HUD).</summary>
        public static string DescribeLocation(Vector3 p)
        {
            foreach (ShopInteraction shop in ShopInteraction.All)
            {
                Bounds a = shop.Area;
                if (a.size.sqrMagnitude > 0f && a.Contains(new Vector3(p.x, a.center.y, p.z))) return Title(shop.ShopName);
            }

            bool insideX = Mathf.Abs(p.x) < HalfWidth;
            if (!insideX) return "Outside the Shopping Complex";
            if (p.z < 0f) return "Main Entrance (Outside)";
            if (p.z > Length) return "Outside - Exit";
            if (p.z < LobbyEnd) return "Main Lobby";
            if (p.z < ShopsEnd) return "Central Corridor";
            return "Exit Hall";
        }

        public static string Title(string s)
        {
            return string.IsNullOrEmpty(s) ? s : CultureInfo.InvariantCulture.TextInfo.ToTitleCase(s.ToLowerInvariant());
        }

        // ================================================================== lighting

        private static void DisableOtherCamerasAndSuns(Transform root)
        {
            var scene = root.gameObject.scene;
            foreach (Camera cam in Object.FindObjectsByType<Camera>(FindObjectsSortMode.None))
            {
                if (cam.gameObject.scene != scene || cam.transform.IsChildOf(root)) continue;
                cam.gameObject.SetActive(false);
                Debug.Log("[VirtualMall] Disabled existing camera '" + cam.name + "' (the mall creates its own first-person camera).");
            }
            foreach (Light light in Object.FindObjectsByType<Light>(FindObjectsSortMode.None))
            {
                if (light.gameObject.scene != scene || light.transform.IsChildOf(root) || light.type != LightType.Directional) continue;
                light.enabled = false;
                Debug.Log("[VirtualMall] Disabled existing directional light '" + light.name + "' (the mall creates its own sun).");
            }
        }

        private static void BuildLighting(Transform root)
        {
            Transform lighting = Group("Lighting", root);
            var sunGo = new GameObject("Sun");
            sunGo.transform.SetParent(lighting, false);
            sunGo.transform.rotation = Quaternion.Euler(62f, -35f, 0f);
            var sun = sunGo.AddComponent<Light>();
            sun.type = LightType.Directional;
            sun.color = new Color(1f, 0.96f, 0.9f);
            sun.intensity = 1.1f;
            sun.shadows = LightShadows.Soft;
            sun.shadowStrength = 0.6f;
            RenderSettings.sun = sun;
        }

        private static void PointLight(string name, Transform parent, Vector3 localPos, float range, float intensity, Color color)
        {
            var go = new GameObject(name);
            go.transform.SetParent(parent, false);
            go.transform.localPosition = localPos;
            var light = go.AddComponent<Light>();
            light.type = LightType.Point;
            light.range = range;
            light.intensity = intensity;
            light.color = color;
            light.shadows = LightShadows.None; // keep it cheap: only the sun casts shadows
        }

        private static void CeilingPanel(Transform parent, Vector3 localPos, Vector3 size)
        {
            MallAssets.CreateBlock("CeilingLightPanel", parent, localPos, size, M(1f, 1f, 0.97f, 0.9f), false, false);
        }

        // ================================================================== environment

        private static void BuildEnvironment(Transform root)
        {
            Transform env = Group("Environment", root);
            BuildExterior(Group("Exterior", env));
            BuildShell(Group("Building", env));
            BuildLobby(Group("Lobby", env));
            BuildCorridor(Group("Corridor", env));
            BuildExitHall(Group("ExitHall", env));

            Transform shops = Group("Shops", env);
            ShopDefinition[] defs = MallCatalog.Shops;
            for (int i = 0; i < defs.Length && i < 6; i++)
            {
                bool left = i % 2 == 0;
                int row = i / 2;
                float z = LobbyEnd + ShopWidth * (row + 0.5f);
                float x = (CorridorHalfWidth + ShopDepth * 0.5f) * (left ? -1f : 1f);
                // Local +Z of a shop always points out of the shop towards the corridor.
                BuildShop(defs[i], shops, new Vector3(x, 0f, z), left ? 90f : -90f, i + 1);
            }
        }

        private static void BuildExterior(Transform ext)
        {
            MallAssets.CreateBlock("Ground", ext, new Vector3(0f, -0.25f, 25f), new Vector3(100f, 0.5f, 120f), M(0.36f, 0.55f, 0.30f, 0.05f));
            Material paving = MallAssets.GetMaterial(new Color(0.78f, 0.77f, 0.74f), 0.1f, MallAssets.FloorTexture, new Vector2(16f, 9f));
            MallAssets.CreateBlock("EntrancePlaza", ext, new Vector3(0f, 0.005f, -9f), new Vector3(32f, 0.01f, 18f), paving, false);
            MallAssets.CreateBlock("ExitPlaza", ext, new Vector3(0f, 0.005f, 67f), new Vector3(16f, 0.01f, 10f), paving, false);
            MallAssets.CreateBlock("Road", ext, new Vector3(0f, 0.004f, -22f), new Vector3(100f, 0.01f, 8f), M(0.2f, 0.2f, 0.22f), false);
            for (int i = -6; i <= 6; i++)
                MallAssets.CreateBlock("RoadMarking", ext, new Vector3(i * 7f, 0.012f, -22f), new Vector3(3f, 0.01f, 0.25f), M(0.95f, 0.95f, 0.95f), false, false);

            Vector2[] trees =
            {
                new Vector2(-13f, -6f), new Vector2(13f, -6f), new Vector2(-13f, -14f), new Vector2(13f, -14f),
                new Vector2(-25f, 8f), new Vector2(25f, 8f), new Vector2(-25f, 30f), new Vector2(25f, 30f),
                new Vector2(-25f, 52f), new Vector2(25f, 52f), new Vector2(-10f, 70f), new Vector2(10f, 70f)
            };
            foreach (Vector2 t in trees) Tree(ext, new Vector3(t.x, 0f, t.y));

            foreach (float x in new[] { -8f, 8f })
            {
                Transform lamp = Group("StreetLamp", ext, new Vector3(x, 0f, -12f));
                MallAssets.CreatePart("Pole", PrimitiveType.Cylinder, lamp, new Vector3(0f, 2f, 0f), new Vector3(0.15f, 2f, 0.15f), M(0.2f, 0.2f, 0.22f, 0.5f)).AddComponent<BoxCollider>();
                MallAssets.CreatePart("Lamp", PrimitiveType.Sphere, lamp, new Vector3(0f, 4.1f, 0f), Vector3.one * 0.45f, M(1f, 0.97f, 0.85f, 0.9f));
            }

            // Bench on the plaza
            Bench(ext, new Vector3(-8f, 0f, -6f), 0f);
            Bench(ext, new Vector3(8f, 0f, -6f), 0f);

            // Invisible boundary so the player cannot walk off the world.
            MallAssets.CreateBlocker("BoundaryWest", ext, new Vector3(-49f, 5f, 25f), new Vector3(1f, 10f, 120f), false);
            MallAssets.CreateBlocker("BoundaryEast", ext, new Vector3(49f, 5f, 25f), new Vector3(1f, 10f, 120f), false);
            MallAssets.CreateBlocker("BoundarySouth", ext, new Vector3(0f, 5f, -34f), new Vector3(100f, 10f, 1f), false);
            MallAssets.CreateBlocker("BoundaryNorth", ext, new Vector3(0f, 5f, 84f), new Vector3(100f, 10f, 1f), false);
        }

        private static void Tree(Transform parent, Vector3 pos)
        {
            Transform tree = Group("Tree", parent, pos);
            MallAssets.CreatePart("Trunk", PrimitiveType.Cylinder, tree, new Vector3(0f, 1.5f, 0f), new Vector3(0.35f, 1.5f, 0.35f), M(0.4f, 0.28f, 0.18f)).AddComponent<BoxCollider>();
            MallAssets.CreatePart("Leaves", PrimitiveType.Sphere, tree, new Vector3(0f, 3.8f, 0f), new Vector3(2.8f, 2.6f, 2.8f), M(0.2f, 0.5f, 0.22f));
        }

        private static void Bench(Transform parent, Vector3 pos, float yaw)
        {
            Transform bench = Group("Bench", parent, pos, yaw);
            Material wood = M(0.55f, 0.38f, 0.22f, 0.3f);
            Material metal = M(0.25f, 0.25f, 0.28f, 0.5f);
            MallAssets.CreatePart("Seat", PrimitiveType.Cube, bench, new Vector3(0f, 0.45f, 0f), new Vector3(2.2f, 0.08f, 0.55f), wood);
            MallAssets.CreatePart("Back", PrimitiveType.Cube, bench, new Vector3(0f, 0.75f, -0.25f), new Vector3(2.2f, 0.4f, 0.06f), wood);
            MallAssets.CreatePart("LegL", PrimitiveType.Cube, bench, new Vector3(-0.95f, 0.21f, 0f), new Vector3(0.08f, 0.42f, 0.5f), metal);
            MallAssets.CreatePart("LegR", PrimitiveType.Cube, bench, new Vector3(0.95f, 0.21f, 0f), new Vector3(0.08f, 0.42f, 0.5f), metal);
            MallAssets.CreateBlocker("Collider", bench, new Vector3(0f, 0.5f, -0.05f), new Vector3(2.2f, 1f, 0.65f), false);
        }

        private static void Planter(Transform parent, Vector3 pos)
        {
            Transform planter = Group("Planter", parent, pos);
            MallAssets.CreatePart("Pot", PrimitiveType.Cube, planter, new Vector3(0f, 0.3f, 0f), new Vector3(0.9f, 0.6f, 0.9f), M(0.85f, 0.85f, 0.82f, 0.4f));
            MallAssets.CreatePart("Soil", PrimitiveType.Cube, planter, new Vector3(0f, 0.6f, 0f), new Vector3(0.8f, 0.02f, 0.8f), M(0.3f, 0.2f, 0.12f));
            MallAssets.CreatePart("Bush", PrimitiveType.Sphere, planter, new Vector3(0f, 1.05f, 0f), new Vector3(0.95f, 1.0f, 0.95f), M(0.22f, 0.55f, 0.25f));
            MallAssets.CreateBlocker("Collider", planter, new Vector3(0f, 0.75f, 0f), new Vector3(0.9f, 1.5f, 0.9f), false);
        }

        // ------------------------------------------------------------------ building shell

        private static void BuildShell(Transform b)
        {
            const float H = WallHeight;
            Material wall = M(0.93f, 0.92f, 0.89f);
            Material facade = M(0.28f, 0.31f, 0.36f, 0.3f);
            Material gold = M(0.95f, 0.72f, 0.25f, 0.5f);
            Material floor = MallAssets.GetMaterial(new Color(0.96f, 0.95f, 0.93f), 0.35f, MallAssets.FloorTexture, new Vector2(20f, 31f));

            MallAssets.CreateBlock("Floor", b, new Vector3(0f, 0.01f, Length * 0.5f), new Vector3(HalfWidth * 2f, 0.02f, Length), floor);
            MallAssets.CreateBlock("Ceiling", b, new Vector3(0f, H + 0.1f, Length * 0.5f), new Vector3(HalfWidth * 2f + 0.6f, 0.2f, Length + 0.6f),
                M(0.97f, 0.97f, 0.97f), true, false); // no shadow: daylight still reaches the interior like a skylight

            // Front wall with a 6 m wide main entrance (x -3..3).
            MallAssets.CreateBlock("FrontWall_L", b, new Vector3(-11.5f, H * 0.5f, 0f), new Vector3(17f, H, WallThickness), wall);
            MallAssets.CreateBlock("FrontWall_R", b, new Vector3(11.5f, H * 0.5f, 0f), new Vector3(17f, H, WallThickness), wall);
            MallAssets.CreateBlock("FrontWall_Header", b, new Vector3(0f, (3.6f + H) * 0.5f, 0f), new Vector3(6f, H - 3.6f, WallThickness), wall);

            // Back wall with a 4 m wide exit (x -2..2).
            MallAssets.CreateBlock("BackWall_L", b, new Vector3(-11f, H * 0.5f, Length), new Vector3(18f, H, WallThickness), wall);
            MallAssets.CreateBlock("BackWall_R", b, new Vector3(11f, H * 0.5f, Length), new Vector3(18f, H, WallThickness), wall);
            MallAssets.CreateBlock("BackWall_Header", b, new Vector3(0f, (3f + H) * 0.5f, Length), new Vector3(4f, H - 3f, WallThickness), wall);

            MallAssets.CreateBlock("SideWall_L", b, new Vector3(-HalfWidth, H * 0.5f, Length * 0.5f), new Vector3(WallThickness, H, Length + WallThickness), wall);
            MallAssets.CreateBlock("SideWall_R", b, new Vector3(HalfWidth, H * 0.5f, Length * 0.5f), new Vector3(WallThickness, H, Length + WallThickness), wall);

            // Exterior roof trim
            MallAssets.CreateBlock("RoofTrim_Front", b, new Vector3(0f, H + 0.45f, -0.05f), new Vector3(HalfWidth * 2f + 0.8f, 0.5f, 0.5f), facade, false);
            MallAssets.CreateBlock("RoofTrim_Back", b, new Vector3(0f, H + 0.45f, Length + 0.05f), new Vector3(HalfWidth * 2f + 0.8f, 0.5f, 0.5f), facade, false);

            // Main entrance: frame, canopy, columns and signs.
            Transform entrance = Group("MainEntrance", b);
            MallAssets.CreateBlock("FramePillar_L", entrance, new Vector3(-3.15f, 1.8f, 0f), new Vector3(0.3f, 3.6f, 0.45f), gold);
            MallAssets.CreateBlock("FramePillar_R", entrance, new Vector3(3.15f, 1.8f, 0f), new Vector3(0.3f, 3.6f, 0.45f), gold);
            MallAssets.CreateBlock("Canopy", entrance, new Vector3(0f, 3.7f, -1.7f), new Vector3(9.4f, 0.2f, 3.4f), facade);
            MallAssets.CreateBlock("CanopyFascia", entrance, new Vector3(0f, 3.62f, -3.38f), new Vector3(9.4f, 0.4f, 0.06f), gold, false);
            MallAssets.CreateBlock("Column_L", entrance, new Vector3(-4.3f, 1.8f, -3.0f), new Vector3(0.3f, 3.6f, 0.3f), facade);
            MallAssets.CreateBlock("Column_R", entrance, new Vector3(4.3f, 1.8f, -3.0f), new Vector3(0.3f, 3.6f, 0.3f), facade);
            MallAssets.CreateBlock("DoorMat", entrance, new Vector3(0f, 0.025f, 1.2f), new Vector3(5f, 0.01f, 1.8f), M(0.25f, 0.22f, 0.22f), false);

            MallAssets.CreateBlock("MallSignBoard", entrance, new Vector3(0f, 4.4f, -0.3f), new Vector3(15f, 1.1f, 0.15f), facade, false);
            MallAssets.CreateLabel("MallSign", entrance, MallCatalog.MallName, new Vector3(0f, 4.4f, -0.39f), Vector3.back,
                new Vector2(14.6f, 1f), 120, LabelGold);
            MallAssets.CreateLabel("EntranceSign", entrance, "MAIN ENTRANCE", new Vector3(0f, 3.62f, -3.42f), Vector3.back,
                new Vector2(5f, 0.36f), 56, new Color(0.1f, 0.1f, 0.12f));
            MallAssets.CreateLabel("EntranceInside", entrance, "MAIN ENTRANCE", new Vector3(0f, 4.3f, 0.17f), Vector3.forward,
                new Vector2(5.6f, 1.0f), 90, LabelGold, LabelDark);
        }

        // ------------------------------------------------------------------ lobby

        private static void BuildLobby(Transform lobby)
        {
            // Central fountain
            Transform fountain = Group("Fountain", lobby, new Vector3(0f, 0f, 6.5f));
            MallAssets.CreatePart("Basin", PrimitiveType.Cylinder, fountain, new Vector3(0f, 0.3f, 0f), new Vector3(3.2f, 0.3f, 3.2f), M(0.8f, 0.78f, 0.75f, 0.4f));
            MallAssets.CreatePart("Water", PrimitiveType.Cylinder, fountain, new Vector3(0f, 0.55f, 0f), new Vector3(2.9f, 0.06f, 2.9f), M(0.25f, 0.55f, 0.85f, 0.95f));
            MallAssets.CreatePart("Pillar", PrimitiveType.Cylinder, fountain, new Vector3(0f, 1.0f, 0f), new Vector3(0.35f, 0.5f, 0.35f), M(0.8f, 0.78f, 0.75f, 0.4f));
            MallAssets.CreatePart("TopBowl", PrimitiveType.Cylinder, fountain, new Vector3(0f, 1.5f, 0f), new Vector3(1.2f, 0.08f, 1.2f), M(0.8f, 0.78f, 0.75f, 0.4f));
            MallAssets.CreatePart("Spray", PrimitiveType.Sphere, fountain, new Vector3(0f, 1.75f, 0f), new Vector3(0.6f, 0.45f, 0.6f), M(0.55f, 0.8f, 1f, 0.95f));
            MallAssets.CreateBlocker("Collider", fountain, new Vector3(0f, 0.9f, 0f), new Vector3(3.0f, 1.8f, 3.0f), false);

            // Directory boards
            string L = MallAssets.LeftArrow, R = MallAssets.RightArrow;
            DirectoryBoard(lobby, new Vector3(-7f, 0f, 9.5f),
                "MALL DIRECTORY\n<size=44>" + L + "  LEFT SIDE</size>\n\n<color=#FFD54A>1</color>  FASHION STORE\n<color=#FFD54A>3</color>  SPORTS STORE\n<color=#FFD54A>5</color>  GROCERY STORE");
            DirectoryBoard(lobby, new Vector3(7f, 0f, 9.5f),
                "MALL DIRECTORY\n<size=44>RIGHT SIDE  " + R + "</size>\n\n<color=#FFD54A>2</color>  ELECTRONICS STORE\n<color=#FFD54A>4</color>  FOOTWEAR STORE\n<color=#FFD54A>6</color>  ACCESSORIES STORE");

            // Information desk (decorative)
            Transform desk = Group("InformationDesk", lobby, new Vector3(-13f, 0f, 4f));
            MallAssets.CreateBlock("Desk", desk, new Vector3(0f, 0.55f, 0f), new Vector3(3.2f, 1.1f, 1f), M(0.28f, 0.31f, 0.36f, 0.3f));
            MallAssets.CreateBlock("DeskTop", desk, new Vector3(0f, 1.13f, 0f), new Vector3(3.4f, 0.06f, 1.1f), M(0.95f, 0.95f, 0.95f, 0.6f), false);
            MallAssets.CreateLabel("DeskSign", desk, "INFORMATION", desk.TransformPoint(new Vector3(0f, 0.6f, -0.52f)), Vector3.back,
                new Vector2(3f, 0.45f), 60, Color.white);

            Bench(lobby, new Vector3(13f, 0f, 4f), 180f);
            Bench(lobby, new Vector3(13f, 0f, 8f), 0f);
            Planter(lobby, new Vector3(-18.8f, 0f, 1.2f));
            Planter(lobby, new Vector3(18.8f, 0f, 1.2f));
            Planter(lobby, new Vector3(-18.8f, 0f, 10.8f));
            Planter(lobby, new Vector3(18.8f, 0f, 10.8f));

            // Hanging sign at the start of the corridor (two-sided)
            Transform hanging = Group("CorridorEntranceSign", lobby, new Vector3(0f, 4.15f, 12f));
            MallAssets.CreateBlock("Board", hanging, Vector3.zero, new Vector3(7.6f, 0.8f, 0.08f), M(0.15f, 0.17f, 0.2f), false);
            MallAssets.CreateBlock("Rod_L", hanging, new Vector3(-3f, 0.62f, 0f), new Vector3(0.04f, 0.45f, 0.04f), M(0.5f, 0.5f, 0.5f), false);
            MallAssets.CreateBlock("Rod_R", hanging, new Vector3(3f, 0.62f, 0f), new Vector3(0.04f, 0.45f, 0.04f), M(0.5f, 0.5f, 0.5f), false);
            MallAssets.CreateLabel("Front", hanging, MallAssets.UpArrow + "  ALL SHOPS   |   EXIT AT THE END  " + MallAssets.UpArrow,
                hanging.position + Vector3.back * 0.05f, Vector3.back, new Vector2(7.4f, 0.7f), 64, Color.white);
            MallAssets.CreateLabel("Back", hanging, MallAssets.UpArrow + "  MAIN LOBBY & ENTRANCE  " + MallAssets.UpArrow,
                hanging.position + Vector3.forward * 0.05f, Vector3.forward, new Vector2(7.4f, 0.7f), 64, Color.white);

            Color warm = new Color(1f, 0.95f, 0.88f);
            PointLight("LobbyLight_C", lobby, new Vector3(0f, 4.4f, 6f), 18f, 1.2f, warm);
            PointLight("LobbyLight_L", lobby, new Vector3(-12f, 4.4f, 6f), 12f, 0.8f, warm);
            PointLight("LobbyLight_R", lobby, new Vector3(12f, 4.4f, 6f), 12f, 0.8f, warm);
            for (int i = -2; i <= 2; i++) CeilingPanel(lobby, new Vector3(i * 7.5f, 4.98f, 6f), new Vector3(3f, 0.04f, 1f));
        }

        private static void DirectoryBoard(Transform parent, Vector3 pos, string text)
        {
            Transform board = Group("DirectoryBoard", parent, pos);
            Material dark = M(0.15f, 0.17f, 0.2f, 0.4f);
            MallAssets.CreatePart("Panel", PrimitiveType.Cube, board, new Vector3(0f, 1.9f, 0f), new Vector3(3.6f, 2.4f, 0.12f), dark);
            MallAssets.CreatePart("Leg_L", PrimitiveType.Cube, board, new Vector3(-1.5f, 0.35f, 0f), new Vector3(0.12f, 0.7f, 0.12f), dark);
            MallAssets.CreatePart("Leg_R", PrimitiveType.Cube, board, new Vector3(1.5f, 0.35f, 0f), new Vector3(0.12f, 0.7f, 0.12f), dark);
            MallAssets.CreateBlocker("Collider", board, new Vector3(0f, 1.55f, 0f), new Vector3(3.6f, 3.1f, 0.3f), false);
            MallAssets.CreateLabel("DirectoryText", board, text, board.position + new Vector3(0f, 1.9f, -0.07f), Vector3.back,
                new Vector2(3.4f, 2.25f), 52, Color.white);
        }

        // ------------------------------------------------------------------ corridor

        private static void BuildCorridor(Transform corridor)
        {
            float midZ = (LobbyEnd + ShopsEnd) * 0.5f;
            MallAssets.CreateBlock("FloorStripe", corridor, new Vector3(0f, 0.025f, midZ), new Vector3(1.4f, 0.01f, ShopsEnd - LobbyEnd), M(0.55f, 0.57f, 0.62f, 0.5f), false);

            ShopDefinition[] defs = MallCatalog.Shops;
            string L = MallAssets.LeftArrow, R = MallAssets.RightArrow;
            for (int row = 0; row < 3; row++)
            {
                float shopZ = LobbyEnd + ShopWidth * (row + 0.5f);

                Bench(corridor, new Vector3(0f, 0f, shopZ), 90f);
                Planter(corridor, new Vector3(0f, 0f, shopZ - 2.4f));
                Planter(corridor, new Vector3(0f, 0f, shopZ + 2.4f));

                // Two-sided hanging direction sign before each pair of shops.
                string leftShop = defs[row * 2].Name, rightShop = defs[row * 2 + 1].Name;
                Transform sign = Group("DirectionSign_" + (row + 1), corridor, new Vector3(0f, 4.2f, shopZ - 4.5f));
                MallAssets.CreateBlock("Board", sign, Vector3.zero, new Vector3(7.6f, 0.7f, 0.08f), M(0.15f, 0.17f, 0.2f), false);
                MallAssets.CreateBlock("Rod_L", sign, new Vector3(-3f, 0.57f, 0f), new Vector3(0.04f, 0.45f, 0.04f), M(0.5f, 0.5f, 0.5f), false);
                MallAssets.CreateBlock("Rod_R", sign, new Vector3(3f, 0.57f, 0f), new Vector3(0.04f, 0.45f, 0.04f), M(0.5f, 0.5f, 0.5f), false);
                MallAssets.CreateLabel("Front", sign, L + " " + leftShop + "        " + rightShop + " " + R,
                    sign.position + Vector3.back * 0.05f, Vector3.back, new Vector2(7.4f, 0.62f), 56, Color.white);
                MallAssets.CreateLabel("Back", sign, L + " " + rightShop + "        " + leftShop + " " + R,
                    sign.position + Vector3.forward * 0.05f, Vector3.forward, new Vector2(7.4f, 0.62f), 56, Color.white);

                PointLight("CorridorLight_" + (row + 1), corridor, new Vector3(0f, 4.4f, shopZ), 12f, 1.0f, new Color(1f, 0.97f, 0.92f));
                CeilingPanel(corridor, new Vector3(0f, 4.98f, shopZ - 3.5f), new Vector3(1.2f, 0.04f, 3f));
                CeilingPanel(corridor, new Vector3(0f, 4.98f, shopZ + 3.5f), new Vector3(1.2f, 0.04f, 3f));
            }
        }

        // ------------------------------------------------------------------ exit hall

        private static void BuildExitHall(Transform hall)
        {
            Material green = M(0.1f, 0.6f, 0.3f, 0.4f);
            MallAssets.CreateBlock("ExitSignBoard", hall, new Vector3(0f, 3.95f, Length - 0.2f), new Vector3(3.4f, 0.9f, 0.1f), green, false);
            MallAssets.CreateLabel("ExitSign", hall, "EXIT  " + MallAssets.UpArrow, new Vector3(0f, 3.95f, Length - 0.26f), Vector3.back,
                new Vector2(3.2f, 0.8f), 90, Color.white);
            MallAssets.CreateBlock("ExitSignBoardOutside", hall, new Vector3(0f, 3.95f, Length + 0.2f), new Vector3(3.4f, 0.9f, 0.1f), green, false);
            MallAssets.CreateLabel("ExitSignOutside", hall, "EXIT", new Vector3(0f, 3.95f, Length + 0.26f), Vector3.forward,
                new Vector2(3.2f, 0.8f), 90, Color.white);

            MallAssets.CreateLabel("ThankYou_L", hall, "THANK YOU FOR\nVISITING!", new Vector3(-10f, 2.6f, Length - 0.17f), Vector3.back,
                new Vector2(7f, 1.8f), 80, LabelGold, LabelDark);
            MallAssets.CreateLabel("ThankYou_R", hall, "PLEASE VISIT\nAGAIN", new Vector3(10f, 2.6f, Length - 0.17f), Vector3.back,
                new Vector2(7f, 1.8f), 80, LabelGold, LabelDark);
            MallAssets.CreateBlock("ExitFrame_L", hall, new Vector3(-2.15f, 1.5f, Length), new Vector3(0.3f, 3f, 0.45f), green);
            MallAssets.CreateBlock("ExitFrame_R", hall, new Vector3(2.15f, 1.5f, Length), new Vector3(0.3f, 3f, 0.45f), green);

            Bench(hall, new Vector3(-12f, 0f, 57f), 0f);
            Bench(hall, new Vector3(12f, 0f, 57f), 0f);
            Planter(hall, new Vector3(-18.8f, 0f, 61f));
            Planter(hall, new Vector3(18.8f, 0f, 61f));

            PointLight("ExitHallLight", hall, new Vector3(0f, 4.4f, 58f), 16f, 1.1f, new Color(1f, 0.97f, 0.92f));
            CeilingPanel(hall, new Vector3(-8f, 4.98f, 58f), new Vector3(3f, 0.04f, 1f));
            CeilingPanel(hall, new Vector3(8f, 4.98f, 58f), new Vector3(3f, 0.04f, 1f));

            // Where "Continue Exploring" puts the player (inside, facing back into the mall).
            Transform returnPoint = Group("ExitReturnPoint", hall, new Vector3(0f, 0.05f, Length - 2.5f), 180f);

            var zone = new GameObject("ExitZone");
            zone.transform.SetParent(hall, false);
            zone.transform.localPosition = new Vector3(0f, 2f, Length + 4f);
            zone.AddComponent<MallExit>().Setup(new Vector3(14f, 4f, 6f), returnPoint);
        }

        // ================================================================== shops

        /// <summary>
        /// Builds one shop in its own local space: 14 m wide (x), 16 m deep (z), entrance in the
        /// front wall at local +Z. The same code builds all six shops.
        /// </summary>
        private static void BuildShop(ShopDefinition def, Transform parent, Vector3 center, float yaw, int number)
        {
            const float H = WallHeight;
            const float hw = ShopWidth * 0.5f;   // 7
            const float hd = ShopDepth * 0.5f;   // 8
            const float doorHalf = 2f;

            Transform shop = Group(def.Name, parent, center, yaw);
            Material wall = M(def.WallColor);
            Material floor = MallAssets.GetMaterial(def.FloorColor, 0.35f, MallAssets.FloorTexture, new Vector2(7f, 8f));
            Material accent = M(def.Accent, 0.3f);
            Material accentDark = M(Opaque(def.Accent * 0.55f), 0.3f);
            Material white = M(0.97f, 0.97f, 0.97f, 0.5f);

            // --- structure
            Transform s = Group("Structure", shop);
            MallAssets.CreateBlock("Floor", s, new Vector3(0f, 0.02f, 0f), new Vector3(ShopWidth - 0.4f, 0.02f, ShopDepth - 0.4f), floor, false);
            MallAssets.CreateBlock("BackWall", s, new Vector3(0f, H * 0.5f, -hd + 0.1f), new Vector3(ShopWidth - 0.4f, H, 0.2f), wall);
            MallAssets.CreateBlock("SideWall_L", s, new Vector3(-hw + 0.1f, H * 0.5f, 0f), new Vector3(0.2f, H, ShopDepth), wall);
            MallAssets.CreateBlock("SideWall_R", s, new Vector3(hw - 0.1f, H * 0.5f, 0f), new Vector3(0.2f, H, ShopDepth), wall);
            float frontWidth = hw - 0.2f - doorHalf; // 4.8
            float frontX = doorHalf + frontWidth * 0.5f;
            MallAssets.CreateBlock("FrontWall_L", s, new Vector3(-frontX, H * 0.5f, hd - 0.1f), new Vector3(frontWidth, H, 0.2f), wall);
            MallAssets.CreateBlock("FrontWall_R", s, new Vector3(frontX, H * 0.5f, hd - 0.1f), new Vector3(frontWidth, H, 0.2f), wall);
            MallAssets.CreateBlock("DoorHeader", s, new Vector3(0f, (3.2f + H) * 0.5f, hd - 0.1f), new Vector3(doorHalf * 2f, H - 3.2f, 0.2f), wall);
            MallAssets.CreateBlock("DoorFrame_L", s, new Vector3(-doorHalf - 0.1f, 1.6f, hd - 0.1f), new Vector3(0.2f, 3.2f, 0.32f), accent);
            MallAssets.CreateBlock("DoorFrame_R", s, new Vector3(doorHalf + 0.1f, 1.6f, hd - 0.1f), new Vector3(0.2f, 3.2f, 0.32f), accent);
            MallAssets.CreateBlock("DoorFrame_Top", s, new Vector3(0f, 3.25f, hd - 0.1f), new Vector3(doorHalf * 2f + 0.4f, 0.12f, 0.32f), accent, false);

            // Storefront: fascia, name board, display windows, projecting blade sign
            Transform front = Group("Storefront", shop);
            MallAssets.CreateBlock("Fascia", front, new Vector3(0f, 4.2f, hd + 0.04f), new Vector3(ShopWidth - 0.4f, 1.4f, 0.08f), accentDark, false);
            MallAssets.CreateBlock("NameBoard", front, new Vector3(0f, 4.2f, hd + 0.1f), new Vector3(7.2f, 1.05f, 0.06f), white, false);
            LabelLocal(shop, front, "ShopName", def.Name, new Vector3(0f, 4.2f, hd + 0.14f), Vector3.forward, new Vector2(7f, 0.95f), 110, Opaque(def.Accent * 0.8f));
            LabelLocal(shop, front, "ShopNumber", "SHOP " + number, new Vector3(-5.2f, 4.2f, hd + 0.09f), Vector3.forward, new Vector2(2.2f, 0.5f), 56, Color.white);
            LabelLocal(shop, front, "OpenSign", "OPEN", new Vector3(5.2f, 4.2f, hd + 0.09f), Vector3.forward, new Vector2(2.2f, 0.5f), 56, new Color(0.6f, 1f, 0.6f));
            Material glass = M(0.55f, 0.7f, 0.82f, 0.95f);
            MallAssets.CreateBlock("Window_L", front, new Vector3(-frontX, 1.7f, hd + 0.02f), new Vector3(frontWidth - 0.6f, 2.4f, 0.04f), glass, false);
            MallAssets.CreateBlock("Window_R", front, new Vector3(frontX, 1.7f, hd + 0.02f), new Vector3(frontWidth - 0.6f, 2.4f, 0.04f), glass, false);
            LabelLocal(shop, front, "WindowText_L", "NEW ARRIVALS", new Vector3(-frontX, 1.9f, hd + 0.05f), Vector3.forward, new Vector2(3.6f, 0.5f), 56, Color.white, new Color(0f, 0f, 0f, 0.35f));
            LabelLocal(shop, front, "WindowText_R", "WELCOME!", new Vector3(frontX, 1.9f, hd + 0.05f), Vector3.forward, new Vector2(3.6f, 0.5f), 56, Color.white, new Color(0f, 0f, 0f, 0.35f));
            MallAssets.CreateBlock("BladeSign", front, new Vector3(-hw + 1f, 3.0f, hd + 0.75f), new Vector3(0.08f, 0.7f, 1.3f), accent, false);
            LabelLocal(shop, front, "BladeText_A", def.Name, new Vector3(-hw + 1.05f, 3.0f, hd + 0.75f), Vector3.right, new Vector2(1.25f, 0.65f), 40, Color.white);
            LabelLocal(shop, front, "BladeText_B", def.Name, new Vector3(-hw + 0.95f, 3.0f, hd + 0.75f), Vector3.left, new Vector2(1.25f, 0.65f), 40, Color.white);

            // --- interior decoration and lighting
            Transform interior = Group("Interior", shop);
            MallAssets.CreateBlock("Rug", interior, new Vector3(0f, 0.035f, -1f), new Vector3(12f, 0.01f, 2.8f), accentDark, false);
            MallAssets.CreateBlock("BackSignBoard", interior, new Vector3(0f, 3.55f, -hd + 0.23f), new Vector3(8.4f, 1.1f, 0.06f), white, false);
            LabelLocal(shop, interior, "BackSign", def.Name, new Vector3(0f, 3.55f, -hd + 0.27f), Vector3.forward, new Vector2(8f, 1f), 110, Opaque(def.Accent * 0.8f));
            MallAssets.CreateBlock("PosterBoard", interior, new Vector3(-hw + 0.23f, 2.3f, 1f), new Vector3(0.06f, 1.6f, 3.4f), accent, false);
            LabelLocal(shop, interior, "PosterText", def.Description, new Vector3(-hw + 0.27f, 2.3f, 1f), Vector3.right, new Vector2(3.2f, 1.4f), 48, Color.white);
            PointLight("ShopLight", interior, new Vector3(0f, 4.2f, 0f), 13f, 1.4f, Color.Lerp(Color.white, def.Accent, 0.12f));
            CeilingPanel(interior, new Vector3(-3f, 4.98f, 0f), new Vector3(2.5f, 0.04f, 0.8f));
            CeilingPanel(interior, new Vector3(3f, 4.98f, 0f), new Vector3(2.5f, 0.04f, 0.8f));
            CeilingPanel(interior, new Vector3(0f, 4.98f, -5f), new Vector3(2.5f, 0.04f, 0.8f));

            // --- counter (shop interaction point) with a shopkeeper
            Transform counter = Group("Counter", shop, new Vector3(4.4f, 0f, 4.6f));
            MallAssets.CreatePart("Body", PrimitiveType.Cube, counter, new Vector3(0f, 0.5f, 0f), new Vector3(3.4f, 1f, 0.9f), accentDark);
            MallAssets.CreatePart("Top", PrimitiveType.Cube, counter, new Vector3(0f, 1.03f, 0f), new Vector3(3.6f, 0.06f, 1f), white);
            MallAssets.CreatePart("Register", PrimitiveType.Cube, counter, new Vector3(1f, 1.18f, -0.1f), new Vector3(0.45f, 0.25f, 0.35f), M(0.15f, 0.15f, 0.17f, 0.5f));
            MallAssets.CreatePart("RegisterScreen", PrimitiveType.Cube, counter, new Vector3(1f, 1.4f, -0.15f), new Vector3(0.35f, 0.22f, 0.03f), M(0.1f, 0.35f, 0.75f, 0.9f), new Vector3(-15f, 0f, 0f));
            MallAssets.CreateLabel("CounterSign", counter, "SHOP INFO & CHECKOUT\n<size=36>look here and press E</size>", counter.TransformPoint(new Vector3(-0.3f, 0.55f, 0.47f)),
                shop.TransformDirection(Vector3.forward), new Vector2(2.6f, 0.6f), 48, Color.white);
            var counterBox = counter.gameObject.AddComponent<BoxCollider>();
            counterBox.center = new Vector3(0f, 0.53f, 0f);
            counterBox.size = new Vector3(3.6f, 1.06f, 1f);
            counter.gameObject.AddComponent<ShopInteraction>().Setup(def.Name, def.Description, def.Accent, shop,
                new Vector3(0f, H * 0.5f, 0f), new Vector3(ShopWidth, H, ShopDepth));

            Transform keeper = Group("Shopkeeper", shop, new Vector3(4.6f, 0f, 3.6f));
            MallAssets.CreatePart("BodyCapsule", PrimitiveType.Capsule, keeper, new Vector3(0f, 0.8f, 0f), new Vector3(0.5f, 0.8f, 0.5f), accent).AddComponent<CapsuleCollider>();
            MallAssets.CreatePart("Head", PrimitiveType.Sphere, keeper, new Vector3(0f, 1.75f, 0f), Vector3.one * 0.3f, M(0.87f, 0.68f, 0.52f));

            // --- products: 4 featured podiums + 2 shelf units with more stock
            Transform products = Group("Products", shop);
            float[] podiumX = { -5.1f, -1.7f, 1.7f, 5.1f };
            for (int i = 0; i < def.Products.Length && i < podiumX.Length; i++)
            {
                BuildPodium(shop, products, def, def.Products[i], new Vector3(podiumX[i], 0f, -1f), white, accent);
            }

            if (def.Products.Length >= 4)
            {
                BuildShelfUnit(shop, products, def, "ShelfUnit_A", new Vector3(-3.5f, 0f, -hd + 0.65f), def.Products[0], def.Products[1]);
                BuildShelfUnit(shop, products, def, "ShelfUnit_B", new Vector3(3.5f, 0f, -hd + 0.65f), def.Products[2], def.Products[3]);
            }
        }

        private static void LabelLocal(Transform shop, Transform parent, string name, string text, Vector3 shopLocalPos, Vector3 shopLocalFace,
            Vector2 size, int fontSize, Color color, Color? background = null)
        {
            MallAssets.CreateLabel(name, parent, text, shop.TransformPoint(shopLocalPos), shop.TransformDirection(shopLocalFace),
                size, fontSize, color, background);
        }

        private static void BuildPodium(Transform shop, Transform parent, ShopDefinition def, ProductDefinition product, Vector3 localPos,
            Material white, Material accent)
        {
            Transform display = Group("Display_" + product.Name, parent, localPos);
            MallAssets.CreateBlock("Podium", display, new Vector3(0f, 0.45f, 0f), new Vector3(0.9f, 0.9f, 0.9f), white);
            MallAssets.CreateBlock("PodiumTrim", display, new Vector3(0f, 0.92f, 0f), new Vector3(0.96f, 0.04f, 0.96f), accent, false);

            GameObject item = CreateProduct(product, def, display, new Vector3(0f, 0.94f, 0f), 1f);
            float top = MallAssets.GetRendererBounds(item.transform).max.y;
            Vector3 labelPos = new Vector3(display.position.x, top + 0.32f, display.position.z);
            MallAssets.CreateLabel("Label", display,
                "<b>" + product.Name.ToUpperInvariant() + "</b>\n<color=#FFD54A>" + MallCatalog.FormatPrice(product.Price) + "</color>",
                labelPos, shop.TransformDirection(Vector3.forward), new Vector2(1.4f, 0.44f), 34, Color.white, LabelDark, FontStyle.Normal);
        }

        private static void BuildShelfUnit(Transform shop, Transform parent, ShopDefinition def, string name, Vector3 localPos,
            ProductDefinition a, ProductDefinition b)
        {
            const float width = 5.6f, depth = 0.7f, height = 2.3f;
            Transform unit = Group(name, parent, localPos);
            Material wood = M(0.92f, 0.9f, 0.86f, 0.3f);
            Material trim = M(Opaque(def.Accent * 0.7f), 0.3f);

            MallAssets.CreatePart("Side_L", PrimitiveType.Cube, unit, new Vector3(-width * 0.5f + 0.025f, height * 0.5f, 0f), new Vector3(0.05f, height, depth), trim);
            MallAssets.CreatePart("Side_R", PrimitiveType.Cube, unit, new Vector3(width * 0.5f - 0.025f, height * 0.5f, 0f), new Vector3(0.05f, height, depth), trim);
            MallAssets.CreatePart("BackPanel", PrimitiveType.Cube, unit, new Vector3(0f, height * 0.5f, -depth * 0.5f + 0.02f), new Vector3(width, height, 0.04f), wood);
            MallAssets.CreatePart("Plinth", PrimitiveType.Cube, unit, new Vector3(0f, 0.075f, 0f), new Vector3(width - 0.1f, 0.15f, depth - 0.04f), trim);
            MallAssets.CreatePart("Board_1", PrimitiveType.Cube, unit, new Vector3(0f, 0.88f, 0f), new Vector3(width - 0.1f, 0.04f, depth - 0.04f), wood);
            MallAssets.CreatePart("Board_2", PrimitiveType.Cube, unit, new Vector3(0f, 1.63f, 0f), new Vector3(width - 0.1f, 0.04f, depth - 0.04f), wood);
            MallAssets.CreatePart("TopBoard", PrimitiveType.Cube, unit, new Vector3(0f, height - 0.02f, 0f), new Vector3(width, 0.04f, depth), trim);
            // Solid for the player but ignored by the interaction ray, so products on the shelves stay clickable.
            MallAssets.CreateBlocker("WalkBlocker", unit, new Vector3(0f, height * 0.5f, 0.02f), new Vector3(width, height, depth + 0.04f), true);

            float[] levelTops = { 0.15f, 0.9f, 1.65f };
            ProductDefinition[] levels = { a, b, a };
            const float shelfScale = 0.55f;
            for (int level = 0; level < levelTops.Length; level++)
            {
                ProductDefinition p = levels[level];
                for (int k = -1; k <= 1; k++)
                {
                    CreateProduct(p, def, unit, new Vector3(k * 1.8f, levelTops[level], 0.02f), shelfScale);
                }
                MallAssets.CreateLabel("PriceTag_" + (level + 1), unit,
                    "<b>" + p.Name.ToUpperInvariant() + "</b>   " + MallCatalog.FormatPrice(p.Price),
                    unit.TransformPoint(new Vector3(0f, levelTops[level] - 0.065f, depth * 0.5f + 0.01f)),
                    shop.TransformDirection(Vector3.forward), new Vector2(1.6f, 0.12f), 22, new Color(0.1f, 0.1f, 0.12f),
                    new Color(1f, 0.92f, 0.45f), FontStyle.Normal);
            }
        }

        /// <summary>Creates one interactable product (model + BoxCollider + InteractableProduct).</summary>
        public static GameObject CreateProduct(ProductDefinition p, ShopDefinition shop, Transform parent, Vector3 localPos, float scale)
        {
            GameObject go = ProductFactory.Create(p.Model, p.Name, p.Color, parent);
            go.transform.localPosition = localPos;
            go.transform.localRotation = Quaternion.identity;
            go.transform.localScale = Vector3.one * scale;

            Bounds local = MallAssets.GetLocalMeshBounds(go.transform);
            var box = go.AddComponent<BoxCollider>();
            box.center = local.center;
            box.size = local.size + Vector3.one * 0.04f; // a little larger = easier to aim at

            go.AddComponent<InteractableProduct>().Setup(p.Name, p.Price, p.Description, shop.Name, shop.Accent);
            return go;
        }

        // ================================================================== player & UI

        public static PlayerController CreatePlayer(Transform root)
        {
            var player = new GameObject("Player");
            player.transform.SetParent(root, false);
            player.transform.SetPositionAndRotation(SpawnPosition, Quaternion.Euler(0f, SpawnYaw, 0f));
            player.layer = MallAssets.IgnoreRaycastLayer;
            player.tag = "Player";

            var cc = player.AddComponent<CharacterController>();
            cc.height = 1.8f;
            cc.radius = 0.35f;
            cc.center = new Vector3(0f, 0.9f, 0f);
            cc.stepOffset = 0.35f;
            cc.slopeLimit = 45f;
            cc.skinWidth = 0.05f;
            cc.minMoveDistance = 0f;
            var controller = player.AddComponent<PlayerController>();

            var camGo = new GameObject("PlayerCamera");
            camGo.transform.SetParent(player.transform, false);
            camGo.transform.localPosition = new Vector3(0f, 1.62f, 0f);
            camGo.tag = "MainCamera";
            var cam = camGo.AddComponent<Camera>();
            cam.nearClipPlane = 0.05f;
            cam.farClipPlane = 400f;
            cam.fieldOfView = 70f;
            if (RenderSettings.skybox == null)
            {
                cam.clearFlags = CameraClearFlags.SolidColor;
                cam.backgroundColor = new Color(0.55f, 0.75f, 0.95f);
            }
            camGo.AddComponent<AudioListener>();
            camGo.AddComponent<MouseLook>();
            camGo.AddComponent<InteractionSystem>();
            return controller;
        }

        public static UIManager CreateUI(Transform root)
        {
            var ui = new GameObject("UI");
            ui.transform.SetParent(root, false);
            return ui.AddComponent<UIManager>();
        }
    }
}
