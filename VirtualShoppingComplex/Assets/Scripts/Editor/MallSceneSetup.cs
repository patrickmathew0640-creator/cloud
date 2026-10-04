using System.Collections.Generic;
using System.IO;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace VirtualMall.EditorTools
{
    /// <summary>
    /// Editor helpers (menu: Virtual Mall):
    ///  * On first load, creates Assets/Scenes/VirtualShoppingComplex.unity (one GameObject with
    ///    MallBootstrap), adds it to Build Settings and opens it if nothing else is open.
    ///  * "Bake Mall Into Open Scene" generates the mall in Edit Mode so every object is visible
    ///    in the Hierarchy, and saves Materials, Textures and Prefabs (products, shops, player).
    /// </summary>
    [InitializeOnLoad]
    public static class MallSceneSetup
    {
        public const string ScenePath = "Assets/Scenes/VirtualShoppingComplex.unity";
        private const string SessionKey = "VirtualMall.AutoSetupDone";
        private const string RootName = "VirtualShoppingComplex";

        static MallSceneSetup()
        {
            EditorApplication.delayCall += AutoSetup;
        }

        // ------------------------------------------------------------------ automatic first-time setup

        private static void AutoSetup()
        {
            if (Application.isBatchMode || EditorApplication.isPlayingOrWillChangePlaymode) return;
            if (SessionState.GetBool(SessionKey, false)) return;
            SessionState.SetBool(SessionKey, true);

            Scene active = SceneManager.GetActiveScene();
            bool untitled = string.IsNullOrEmpty(active.path);

            if (!File.Exists(ScenePath))
            {
                if (untitled && active.isDirty)
                {
                    Debug.Log("[VirtualMall] Use the menu 'Virtual Mall > Open or Create Mall Scene' to create the mall scene.");
                    return;
                }
                CreateSceneAsset(untitled);
                Debug.Log("[VirtualMall] Created " + ScenePath + ". Open it and press Play.");
            }
            AddSceneToBuildSettings();

            if (untitled && !active.isDirty && SceneManager.GetActiveScene().path != ScenePath)
            {
                EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
            }
        }

        // ------------------------------------------------------------------ menu items

        [MenuItem("Virtual Mall/Open or Create Mall Scene", false, 0)]
        public static void OpenOrCreateScene()
        {
            if (EditorApplication.isPlaying) return;
            if (!EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo()) return;
            if (!File.Exists(ScenePath)) CreateSceneAsset(true);
            else EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
            AddSceneToBuildSettings();
        }

        [MenuItem("Virtual Mall/Bake Mall Into Open Scene (editable objects + prefabs)", false, 20)]
        public static void BakeMall()
        {
            if (EditorApplication.isPlaying)
            {
                Debug.LogWarning("[VirtualMall] Exit Play Mode before baking.");
                return;
            }

            var bootstrap = Object.FindAnyObjectByType<MallBootstrap>();
            if (bootstrap == null)
            {
                var go = new GameObject(RootName);
                bootstrap = go.AddComponent<MallBootstrap>();
            }

            ClearChildren(bootstrap.transform);
            UIManager ui = MallBuilder.BuildAll(bootstrap.transform);
            ui.BuildUI();
            ui.EnsureEventSystem();

            SaveGeneratedAssets(bootstrap.transform);

            Scene scene = bootstrap.gameObject.scene;
            EditorSceneManager.MarkSceneDirty(scene);
            if (!string.IsNullOrEmpty(scene.path)) EditorSceneManager.SaveScene(scene);
            Selection.activeGameObject = bootstrap.gameObject;
            Debug.Log("[VirtualMall] Mall baked into the scene. Materials, textures and prefabs were saved to Assets/Materials, Assets/Textures and Assets/Prefabs.");
        }

        [MenuItem("Virtual Mall/Clear Baked Mall From Open Scene", false, 21)]
        public static void ClearBakedMall()
        {
            if (EditorApplication.isPlaying) return;
            var bootstrap = Object.FindAnyObjectByType<MallBootstrap>();
            if (bootstrap == null) return;
            ClearChildren(bootstrap.transform);
            EditorSceneManager.MarkSceneDirty(bootstrap.gameObject.scene);
            Debug.Log("[VirtualMall] Baked objects removed. The mall will be generated automatically when you press Play.");
        }

        // ------------------------------------------------------------------ helpers

        private static void CreateSceneAsset(bool replaceCurrent)
        {
            EnsureFolder("Assets/Scenes");
            Scene scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,
                replaceCurrent ? NewSceneMode.Single : NewSceneMode.Additive);

            var root = new GameObject(RootName);
            SceneManager.MoveGameObjectToScene(root, scene);
            root.AddComponent<MallBootstrap>();

            EditorSceneManager.SaveScene(scene, ScenePath);
            if (!replaceCurrent) EditorSceneManager.CloseScene(scene, true);
            AssetDatabase.Refresh();
        }

        private static void AddSceneToBuildSettings()
        {
            if (!File.Exists(ScenePath)) return;
            var scenes = new List<EditorBuildSettingsScene>(EditorBuildSettings.scenes);
            if (scenes.Exists(s => s.path == ScenePath)) return;
            scenes.Insert(0, new EditorBuildSettingsScene(ScenePath, true));
            EditorBuildSettings.scenes = scenes.ToArray();
        }

        private static void ClearChildren(Transform t)
        {
            for (int i = t.childCount - 1; i >= 0; i--) Object.DestroyImmediate(t.GetChild(i).gameObject);
        }

        private static void EnsureFolder(string path)
        {
            if (AssetDatabase.IsValidFolder(path)) return;
            string parent = Path.GetDirectoryName(path)?.Replace('\\', '/');
            if (!string.IsNullOrEmpty(parent)) EnsureFolder(parent);
            AssetDatabase.CreateFolder(parent, Path.GetFileName(path));
        }

        private static string Sanitize(string name)
        {
            foreach (char c in Path.GetInvalidFileNameChars()) name = name.Replace(c, '_');
            return name.Replace(' ', '_');
        }

        private static void SaveGeneratedAssets(Transform root)
        {
            EnsureFolder("Assets/Materials");
            EnsureFolder("Assets/Textures");
            EnsureFolder("Assets/Prefabs/Products");
            EnsureFolder("Assets/Prefabs/Shops");

            // 1) Materials (+ their procedural textures) become .mat / .asset files.
            var materialMap = new Dictionary<Material, Material>();
            foreach (Renderer r in root.GetComponentsInChildren<Renderer>(true))
            {
                Material[] mats = r.sharedMaterials;
                bool changed = false;
                for (int i = 0; i < mats.Length; i++)
                {
                    Material m = mats[i];
                    if (m == null || AssetDatabase.Contains(m)) continue;
                    if (!materialMap.TryGetValue(m, out Material asset))
                    {
                        asset = PersistMaterial(m);
                        materialMap[m] = asset;
                    }
                    mats[i] = asset;
                    changed = true;
                }
                if (changed) r.sharedMaterials = mats;
            }
            AssetDatabase.SaveAssets();

            // 2) One prefab per product; every other copy becomes an instance of it.
            var productPrefabs = new Dictionary<string, GameObject>();
            foreach (InteractableProduct product in root.GetComponentsInChildren<InteractableProduct>(true))
            {
                GameObject go = product.gameObject;
                if (!productPrefabs.TryGetValue(product.ProductName, out GameObject prefab))
                {
                    string path = "Assets/Prefabs/Products/" + Sanitize(product.ProductName) + ".prefab";
                    prefab = PrefabUtility.SaveAsPrefabAssetAndConnect(go, path, InteractionMode.AutomatedAction);
                    productPrefabs[product.ProductName] = prefab;
                    continue;
                }

                Transform t = go.transform;
                var instance = (GameObject)PrefabUtility.InstantiatePrefab(prefab, t.parent);
                instance.transform.SetLocalPositionAndRotation(t.localPosition, t.localRotation);
                instance.transform.localScale = t.localScale;
                instance.transform.SetSiblingIndex(t.GetSiblingIndex());
                Object.DestroyImmediate(go);
            }

            // 3) One prefab per shop (contains nested product prefabs).
            foreach (ShopInteraction shop in root.GetComponentsInChildren<ShopInteraction>(true))
            {
                Transform shopRoot = shop.transform.parent;
                if (shopRoot == null) continue;
                string path = "Assets/Prefabs/Shops/" + Sanitize(MallBuilder.Title(shop.ShopName)) + ".prefab";
                PrefabUtility.SaveAsPrefabAssetAndConnect(shopRoot.gameObject, path, InteractionMode.AutomatedAction);
            }

            // 4) Player prefab.
            var player = root.GetComponentInChildren<PlayerController>(true);
            if (player != null)
            {
                PrefabUtility.SaveAsPrefabAssetAndConnect(player.gameObject, "Assets/Prefabs/Player.prefab", InteractionMode.AutomatedAction);
            }

            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();
        }

        private static Material PersistMaterial(Material m)
        {
            foreach (string prop in new[] { "_MainTex", "_BaseMap" })
            {
                if (!m.HasProperty(prop)) continue;
                if (m.GetTexture(prop) is Texture2D tex && !AssetDatabase.Contains(tex))
                {
                    m.SetTexture(prop, PersistTexture(tex));
                }
            }

            string path = "Assets/Materials/" + Sanitize(m.name) + ".mat";
            var existing = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (existing != null)
            {
                EditorUtility.CopySerialized(m, existing);
                return existing;
            }
            AssetDatabase.CreateAsset(m, path);
            return m;
        }

        private static Texture2D PersistTexture(Texture2D tex)
        {
            string path = "Assets/Textures/" + Sanitize(tex.name) + ".asset";
            var existing = AssetDatabase.LoadAssetAtPath<Texture2D>(path);
            if (existing != null) return existing;
            AssetDatabase.CreateAsset(tex, path);
            return tex;
        }
    }
}
