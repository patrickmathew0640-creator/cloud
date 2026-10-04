using System.Collections.Generic;
using UnityEngine;

namespace VirtualMall
{
    /// <summary>
    /// Shop interaction point (placed on each shop's counter). Pressing E shows the shop
    /// name, number of products and description. Also knows the shop's floor area so the
    /// HUD can show which shop the player is standing in.
    /// </summary>
    public class ShopInteraction : MonoBehaviour, IInteractable
    {
        private static readonly List<ShopInteraction> ActiveShops = new List<ShopInteraction>();
        public static IReadOnlyList<ShopInteraction> All => ActiveShops;

        [SerializeField] private string shopName = "SHOP";
        [SerializeField, TextArea(2, 4)] private string description = "Shop description.";
        [SerializeField] private Color accentColor = Color.white;
        [Tooltip("Root of the shop. Products below it are counted automatically.")]
        [SerializeField] private Transform shopRoot;
        [Tooltip("Shop floor area in the shop root's local space (used for the location HUD).")]
        [SerializeField] private Vector3 areaCenter = new Vector3(0f, 2.5f, 0f);
        [SerializeField] private Vector3 areaSize = new Vector3(14f, 5f, 16f);

        public string ShopName => shopName;

        /// <summary>World-space, axis-aligned area of the shop. Follows the shop if it is moved or rotated.</summary>
        public Bounds Area
        {
            get
            {
                Transform root = shopRoot != null ? shopRoot : transform.parent;
                if (root == null) return new Bounds(transform.position, Vector3.zero);
                Vector3 half = areaSize * 0.5f;
                Vector3 r = root.right * half.x, u = root.up * half.y, f = root.forward * half.z;
                var extents = new Vector3(
                    Mathf.Abs(r.x) + Mathf.Abs(u.x) + Mathf.Abs(f.x),
                    Mathf.Abs(r.y) + Mathf.Abs(u.y) + Mathf.Abs(f.y),
                    Mathf.Abs(r.z) + Mathf.Abs(u.z) + Mathf.Abs(f.z));
                return new Bounds(root.TransformPoint(areaCenter), extents * 2f);
            }
        }

        public string PromptText => "Press E to Explore Shop";
        public string TargetName => shopName;

        // Editor convenience: adding this component in the Inspector also adds a collider if missing.
        private void Reset()
        {
            if (GetComponent<Collider>() == null) gameObject.AddComponent<BoxCollider>();
        }

        public void Setup(string newName, string newDescription, Color accent, Transform root, Vector3 localAreaCenter, Vector3 localAreaSize)
        {
            shopName = newName;
            description = newDescription;
            accentColor = accent;
            shopRoot = root;
            areaCenter = localAreaCenter;
            areaSize = localAreaSize;
        }

        private void OnEnable()
        {
            if (!ActiveShops.Contains(this)) ActiveShops.Add(this);
        }

        private void OnDisable()
        {
            ActiveShops.Remove(this);
        }

        public void Interact()
        {
            Transform root = shopRoot != null ? shopRoot : transform.parent;
            int types = 0, items = 0;
            if (root != null)
            {
                var names = new HashSet<string>();
                foreach (InteractableProduct p in root.GetComponentsInChildren<InteractableProduct>())
                {
                    items++;
                    names.Add(p.ProductName);
                }
                types = names.Count;
            }

            string subtitle = "Number of Products: " + types + "   (" + items + " items on display)";
            if (UIManager.Instance != null)
                UIManager.Instance.ShowInfoPanel("SHOP INFORMATION", shopName, subtitle, description, accentColor);
            else
                Debug.Log($"{shopName} - {subtitle} - {description}");
        }

        public void SetFocused(bool focused) { }
    }
}
