using UnityEngine;

namespace VirtualMall
{
    /// <summary>
    /// Put on a product root that has a Collider. Pressing E while looking at it opens
    /// the product information panel (name, price, description).
    /// </summary>
    public class InteractableProduct : MonoBehaviour, IInteractable
    {
        [SerializeField] private string productName = "Product";
        [SerializeField] private int price = 999;
        [SerializeField, TextArea(2, 4)] private string description = "Product description.";
        [SerializeField] private string shopName = "SHOP";
        [SerializeField] private Color accentColor = new Color(0.2f, 0.5f, 0.9f);
        [SerializeField, Range(1f, 1.3f)] private float focusScale = 1.08f;

        private Vector3 baseScale;
        private bool hasBaseScale;

        public string ProductName => productName;
        public int Price => price;
        public string Description => description;
        public string ShopName => shopName;

        public string PromptText => "Press E to Interact";
        public string TargetName => productName;

        // Editor convenience: adding this component in the Inspector also adds a collider if missing.
        private void Reset()
        {
            if (GetComponent<Collider>() == null) gameObject.AddComponent<BoxCollider>();
        }

        public void Setup(string newName, int newPrice, string newDescription, string newShopName, Color accent)
        {
            productName = newName;
            price = newPrice;
            description = newDescription;
            shopName = newShopName;
            accentColor = accent;
        }

        public void Interact()
        {
            string body = description + "\n\nAvailable at: " + ToTitle(shopName);
            if (UIManager.Instance != null)
            {
                UIManager.Instance.ShowInfoPanel("PRODUCT INFORMATION", productName,
                    "Price: " + MallCatalog.FormatPrice(price), body, accentColor);
            }
            else
            {
                Debug.Log($"{productName} - {MallCatalog.FormatPrice(price)} - {description}");
            }
        }

        public void SetFocused(bool focused)
        {
            if (!hasBaseScale)
            {
                baseScale = transform.localScale;
                hasBaseScale = true;
            }
            transform.localScale = focused ? baseScale * focusScale : baseScale;
        }

        private void OnDisable()
        {
            if (hasBaseScale) transform.localScale = baseScale;
        }

        private static string ToTitle(string s)
        {
            if (string.IsNullOrEmpty(s)) return s;
            return System.Globalization.CultureInfo.InvariantCulture.TextInfo.ToTitleCase(s.ToLowerInvariant());
        }
    }
}
