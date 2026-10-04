using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.UI;

namespace VirtualMall
{
    /// <summary>
    /// Shared, dependency-free building blocks: Unity primitive meshes, colour materials,
    /// the built-in font, a procedural floor texture and helpers that create geometry and
    /// world-space text labels. Materials are copied from Unity's own default material,
    /// so the project works in both the Built-in Render Pipeline and URP.
    /// </summary>
    public static class MallAssets
    {
        private static readonly Dictionary<PrimitiveType, Mesh> Meshes = new Dictionary<PrimitiveType, Mesh>();
        private static readonly Dictionary<string, Material> Materials = new Dictionary<string, Material>();
        private static Material baseMaterial;
        private static Font font;
        private static Texture2D floorTexture;
        private static string currencySymbol;

        public const int IgnoreRaycastLayer = 2; // built-in layer "Ignore Raycast"

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.SubsystemRegistration)]
        private static void ResetState()
        {
            Meshes.Clear();
            Materials.Clear();
            baseMaterial = null;
            font = null;
            floorTexture = null;
            currencySymbol = null;
        }

        // ------------------------------------------------------------------ meshes & materials

        public static Mesh GetMesh(PrimitiveType type)
        {
            if (Meshes.TryGetValue(type, out Mesh cached) && cached != null) return cached;

            // Create a temporary primitive only to grab Unity's built-in mesh and default material.
            GameObject temp = GameObject.CreatePrimitive(type);
            Mesh mesh = temp.GetComponent<MeshFilter>().sharedMesh;
            if (baseMaterial == null) baseMaterial = temp.GetComponent<MeshRenderer>().sharedMaterial;
            Object.DestroyImmediate(temp);

            Meshes[type] = mesh;
            return mesh;
        }

        private static Material BaseMaterial
        {
            get
            {
                if (baseMaterial == null) GetMesh(PrimitiveType.Cube);
                return baseMaterial;
            }
        }

        public static Material GetMaterial(Color color, float smoothness = 0.15f)
        {
            return GetMaterial(color, smoothness, null, Vector2.one);
        }

        public static Material GetMaterial(Color color, float smoothness, Texture texture, Vector2 tiling)
        {
            string key = ColorUtility.ToHtmlStringRGBA(color) + "_" + Mathf.RoundToInt(smoothness * 100f)
                         + (texture != null ? "_" + texture.name + "_" + tiling.x + "x" + tiling.y : "");
            if (Materials.TryGetValue(key, out Material cached) && cached != null) return cached;

            var mat = BaseMaterial != null ? new Material(BaseMaterial) : new Material(Shader.Find("Standard"));
            mat.name = "Mall_" + key;
            mat.enableInstancing = true;
            mat.color = color;
            if (mat.HasProperty("_BaseColor")) mat.SetColor("_BaseColor", color); // URP Lit
            if (mat.HasProperty("_Color")) mat.SetColor("_Color", color);         // Built-in Standard
            if (mat.HasProperty("_Glossiness")) mat.SetFloat("_Glossiness", smoothness);
            if (mat.HasProperty("_Smoothness")) mat.SetFloat("_Smoothness", smoothness);
            if (mat.HasProperty("_Metallic")) mat.SetFloat("_Metallic", 0f);

            if (texture != null)
            {
                foreach (string prop in new[] { "_MainTex", "_BaseMap" })
                {
                    if (!mat.HasProperty(prop)) continue;
                    mat.SetTexture(prop, texture);
                    mat.SetTextureScale(prop, tiling);
                }
            }

            Materials[key] = mat;
            return mat;
        }

        /// <summary>Procedural light floor tile with grout lines (no texture files needed).</summary>
        public static Texture2D FloorTexture
        {
            get
            {
                if (floorTexture != null) return floorTexture;
                const int size = 128;
                floorTexture = new Texture2D(size, size, TextureFormat.RGBA32, true)
                {
                    name = "FloorTile",
                    wrapMode = TextureWrapMode.Repeat,
                    filterMode = FilterMode.Bilinear,
                    anisoLevel = 4
                };
                var pixels = new Color32[size * size];
                for (int y = 0; y < size; y++)
                {
                    for (int x = 0; x < size; x++)
                    {
                        bool grout = x < 2 || y < 2;
                        float noise = Mathf.PerlinNoise(x * 0.08f, y * 0.08f) * 0.06f;
                        float v = grout ? 0.62f : 0.93f - noise;
                        pixels[y * size + x] = new Color(v, v, v * 0.98f, 1f);
                    }
                }
                floorTexture.SetPixels32(pixels);
                floorTexture.Apply(true);
                return floorTexture;
            }
        }

        // ------------------------------------------------------------------ text

        public static Font Font
        {
            get
            {
                if (font == null) font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
                return font;
            }
        }

        /// <summary>"₹" when the built-in font can draw it, otherwise "Rs. " (never shows a missing-glyph box).</summary>
        public static string CurrencySymbol
        {
            get
            {
                if (currencySymbol == null)
                {
                    Font f = Font;
                    currencySymbol = f != null && f.HasCharacter('₹') ? "₹" : "Rs. ";
                }
                return currencySymbol;
            }
        }

        public static string LeftArrow => Glyph('←', "<");
        public static string RightArrow => Glyph('→', ">");
        public static string UpArrow => Glyph('↑', "^");

        private static string Glyph(char c, string fallback)
        {
            Font f = Font;
            return f != null && f.HasCharacter(c) ? c.ToString() : fallback;
        }

        // ------------------------------------------------------------------ geometry helpers

        public static GameObject CreateGroup(string name, Transform parent, Vector3 localPosition, Vector3 localEuler = default)
        {
            var go = new GameObject(name);
            go.transform.SetParent(parent, false);
            go.transform.localPosition = localPosition;
            go.transform.localRotation = Quaternion.Euler(localEuler);
            return go;
        }

        /// <summary>Visual-only primitive (no collider).</summary>
        public static GameObject CreatePart(string name, PrimitiveType type, Transform parent, Vector3 localPosition,
            Vector3 localScale, Material material, Vector3 localEuler = default, bool castShadows = true)
        {
            var go = new GameObject(name);
            go.transform.SetParent(parent, false);
            go.transform.localPosition = localPosition;
            go.transform.localRotation = Quaternion.Euler(localEuler);
            go.transform.localScale = localScale;
            go.AddComponent<MeshFilter>().sharedMesh = GetMesh(type);
            var renderer = go.AddComponent<MeshRenderer>();
            renderer.sharedMaterial = material;
            renderer.shadowCastingMode = castShadows ? ShadowCastingMode.On : ShadowCastingMode.Off;
            return go;
        }

        /// <summary>Cube with a matching BoxCollider (walls, floors, counters...).</summary>
        public static GameObject CreateBlock(string name, Transform parent, Vector3 localCenter, Vector3 size,
            Material material, bool collider = true, bool castShadows = true)
        {
            GameObject go = CreatePart(name, PrimitiveType.Cube, parent, localCenter, size, material, default, castShadows);
            if (collider) go.AddComponent<BoxCollider>();
            return go;
        }

        /// <summary>Invisible collision volume.</summary>
        public static BoxCollider CreateBlocker(string name, Transform parent, Vector3 localCenter, Vector3 size, bool ignoreRaycast)
        {
            var go = new GameObject(name);
            go.transform.SetParent(parent, false);
            go.transform.localPosition = localCenter;
            if (ignoreRaycast) go.layer = IgnoreRaycastLayer;
            var box = go.AddComponent<BoxCollider>();
            box.size = size;
            return box;
        }

        /// <summary>
        /// Creates a world-space Canvas label. <paramref name="faceDirection"/> is the world direction
        /// pointing from the label towards the people who should read it.
        /// </summary>
        public static Text CreateLabel(string name, Transform parent, string text, Vector3 worldPosition,
            Vector3 faceDirection, Vector2 sizeMeters, int fontSize, Color textColor, Color? background = null,
            FontStyle style = FontStyle.Bold)
        {
            const float pixelsPerMeter = 200f;

            var go = new GameObject(name, typeof(RectTransform));
            go.transform.SetParent(parent, false);
            var rt = (RectTransform)go.transform;
            rt.position = worldPosition;
            rt.rotation = Quaternion.LookRotation(-faceDirection.normalized, Vector3.up);
            rt.sizeDelta = sizeMeters * pixelsPerMeter;
            Vector3 parentScale = parent != null ? parent.lossyScale : Vector3.one;
            float s = 1f / pixelsPerMeter;
            rt.localScale = new Vector3(s / Mathf.Max(parentScale.x, 0.0001f), s / Mathf.Max(parentScale.y, 0.0001f),
                s / Mathf.Max(parentScale.z, 0.0001f));

            var canvas = go.AddComponent<Canvas>();
            canvas.renderMode = RenderMode.WorldSpace;
            var scaler = go.AddComponent<CanvasScaler>();
            scaler.dynamicPixelsPerUnit = 3f; // sharper text

            if (background.HasValue)
            {
                var bg = new GameObject("Background", typeof(RectTransform));
                bg.transform.SetParent(go.transform, false);
                Stretch((RectTransform)bg.transform);
                var image = bg.AddComponent<Image>();
                image.color = background.Value;
                image.raycastTarget = false;
            }

            var textGo = new GameObject("Text", typeof(RectTransform));
            textGo.transform.SetParent(go.transform, false);
            var textRt = (RectTransform)textGo.transform;
            Stretch(textRt);
            textRt.offsetMin = new Vector2(6f, 4f);
            textRt.offsetMax = new Vector2(-6f, -4f);
            var label = textGo.AddComponent<Text>();
            label.font = Font;
            label.text = text;
            label.fontSize = fontSize;
            label.fontStyle = style;
            label.color = textColor;
            label.alignment = TextAnchor.MiddleCenter;
            label.horizontalOverflow = HorizontalWrapMode.Wrap;
            label.verticalOverflow = VerticalWrapMode.Truncate;
            label.resizeTextForBestFit = true;
            label.resizeTextMinSize = 8;
            label.resizeTextMaxSize = fontSize;
            label.supportRichText = true;
            label.raycastTarget = false;
            return label;
        }

        public static void Stretch(RectTransform rt)
        {
            rt.anchorMin = Vector2.zero;
            rt.anchorMax = Vector2.one;
            rt.offsetMin = Vector2.zero;
            rt.offsetMax = Vector2.zero;
        }

        /// <summary>World-space bounds of all renderers below <paramref name="root"/>.</summary>
        public static Bounds GetRendererBounds(Transform root)
        {
            Renderer[] renderers = root.GetComponentsInChildren<Renderer>();
            if (renderers.Length == 0) return new Bounds(root.position, Vector3.one * 0.2f);
            Bounds b = renderers[0].bounds;
            for (int i = 1; i < renderers.Length; i++) b.Encapsulate(renderers[i].bounds);
            return b;
        }

        /// <summary>Bounds of all meshes below <paramref name="root"/>, expressed in root's local space.</summary>
        public static Bounds GetLocalMeshBounds(Transform root)
        {
            bool any = false;
            var result = new Bounds(Vector3.zero, Vector3.zero);
            Matrix4x4 toRoot = root.worldToLocalMatrix;
            foreach (MeshFilter mf in root.GetComponentsInChildren<MeshFilter>())
            {
                if (mf.sharedMesh == null) continue;
                Bounds mb = mf.sharedMesh.bounds;
                Matrix4x4 m = toRoot * mf.transform.localToWorldMatrix;
                for (int i = 0; i < 8; i++)
                {
                    var corner = new Vector3(
                        (i & 1) == 0 ? mb.min.x : mb.max.x,
                        (i & 2) == 0 ? mb.min.y : mb.max.y,
                        (i & 4) == 0 ? mb.min.z : mb.max.z);
                    Vector3 p = m.MultiplyPoint3x4(corner);
                    if (!any)
                    {
                        result = new Bounds(p, Vector3.zero);
                        any = true;
                    }
                    else
                    {
                        result.Encapsulate(p);
                    }
                }
            }
            return any ? result : new Bounds(Vector3.up * 0.1f, Vector3.one * 0.2f);
        }
    }
}
