using System.Globalization;
using System.Text;
using UnityEngine;

namespace VirtualMall
{
    /// <summary>The 3D placeholder model used for a product (built from Unity primitives).</summary>
    public enum ProductModel
    {
        Shirt, Jacket, Jeans, TShirt,
        Smartphone, Laptop, Headphones, Smartwatch,
        Football, Basketball, SportsShoes, TennisRacket,
        Sneakers, RunningShoes, Sandals, Boots,
        JuiceBottle, CerealBox, MilkBottle, SnackPacket,
        Watch, Sunglasses, Backpack, Wallet
    }

    public class ProductDefinition
    {
        public readonly string Name;
        public readonly int Price;
        public readonly string Description;
        public readonly ProductModel Model;
        public readonly Color Color;

        public ProductDefinition(string name, int price, ProductModel model, Color color, string description)
        {
            Name = name;
            Price = price;
            Model = model;
            Color = color;
            Description = description;
        }
    }

    public class ShopDefinition
    {
        public readonly string Name;
        public readonly string Description;
        public readonly Color Accent;
        public readonly Color WallColor;
        public readonly Color FloorColor;
        public readonly ProductDefinition[] Products;

        public ShopDefinition(string name, string description, Color accent, Color wall, Color floor, params ProductDefinition[] products)
        {
            Name = name;
            Description = description;
            Accent = accent;
            WallColor = wall;
            FloorColor = floor;
            Products = products;
        }
    }

    /// <summary>All shop and product data in one place. Edit names, prices and descriptions here.</summary>
    public static class MallCatalog
    {
        public const string MallName = "VIRTUAL SHOPPING COMPLEX";

        private static Color C(float r, float g, float b) => new Color(r, g, b);

        // Order = visiting order along the corridor (left, right, left, right, left, right).
        public static readonly ShopDefinition[] Shops =
        {
            new ShopDefinition("FASHION STORE",
                "Explore shirts, jackets, jeans and t-shirts for every season.",
                C(0.82f, 0.22f, 0.50f), C(0.96f, 0.90f, 0.93f), C(0.72f, 0.62f, 0.66f),
                new ProductDefinition("Shirt", 1299, ProductModel.Shirt, C(0.30f, 0.55f, 0.85f),
                    "Slim-fit cotton formal shirt, perfect for office wear and special occasions."),
                new ProductDefinition("Jacket", 3499, ProductModel.Jacket, C(0.25f, 0.28f, 0.32f),
                    "Water-resistant casual jacket with a warm inner lining."),
                new ProductDefinition("Jeans", 2199, ProductModel.Jeans, C(0.18f, 0.30f, 0.55f),
                    "Classic blue stretch-denim jeans with a comfortable regular fit."),
                new ProductDefinition("T-Shirt", 599, ProductModel.TShirt, C(0.95f, 0.75f, 0.20f),
                    "Soft 100% cotton round-neck t-shirt for everyday wear.")),

            new ShopDefinition("ELECTRONICS STORE",
                "Explore smartphones, laptops, headphones and smartwatches.",
                C(0.15f, 0.45f, 0.90f), C(0.88f, 0.92f, 0.97f), C(0.55f, 0.60f, 0.68f),
                new ProductDefinition("Smartphone", 29999, ProductModel.Smartphone, C(0.12f, 0.12f, 0.14f),
                    "Modern smartphone with a 6.5-inch display and triple camera, available in the Electronics Store."),
                new ProductDefinition("Laptop", 59999, ProductModel.Laptop, C(0.70f, 0.72f, 0.75f),
                    "Lightweight 14-inch laptop with a fast processor and all-day battery life."),
                new ProductDefinition("Headphones", 4999, ProductModel.Headphones, C(0.10f, 0.10f, 0.12f),
                    "Wireless over-ear headphones with active noise cancellation."),
                new ProductDefinition("Smartwatch", 8999, ProductModel.Smartwatch, C(0.15f, 0.15f, 0.18f),
                    "Fitness smartwatch with heart-rate monitor, GPS and notifications.")),

            new ShopDefinition("SPORTS STORE",
                "Explore footballs, basketballs, sports shoes and tennis rackets.",
                C(0.15f, 0.65f, 0.30f), C(0.90f, 0.96f, 0.90f), C(0.45f, 0.55f, 0.45f),
                new ProductDefinition("Football", 1499, ProductModel.Football, C(0.97f, 0.97f, 0.97f),
                    "FIFA-size 5 match football with durable stitched panels."),
                new ProductDefinition("Basketball", 1799, ProductModel.Basketball, C(0.92f, 0.45f, 0.12f),
                    "Official size 7 indoor/outdoor basketball with superior grip."),
                new ProductDefinition("Sports Shoes", 3999, ProductModel.SportsShoes, C(0.90f, 0.20f, 0.20f),
                    "Cushioned training shoes for gym workouts and court sports."),
                new ProductDefinition("Tennis Racket", 2499, ProductModel.TennisRacket, C(0.10f, 0.45f, 0.80f),
                    "Lightweight graphite tennis racket for beginners and intermediate players.")),

            new ShopDefinition("FOOTWEAR STORE",
                "Explore sneakers, running shoes, sandals and boots.",
                C(0.80f, 0.45f, 0.15f), C(0.97f, 0.93f, 0.87f), C(0.62f, 0.50f, 0.40f),
                new ProductDefinition("Sneakers", 2999, ProductModel.Sneakers, C(0.95f, 0.95f, 0.95f),
                    "Classic low-top canvas sneakers that go with everything."),
                new ProductDefinition("Running Shoes", 4499, ProductModel.RunningShoes, C(0.20f, 0.75f, 0.85f),
                    "Breathable mesh running shoes with responsive foam cushioning."),
                new ProductDefinition("Sandals", 899, ProductModel.Sandals, C(0.55f, 0.35f, 0.20f),
                    "Comfortable everyday sandals with adjustable straps."),
                new ProductDefinition("Boots", 5499, ProductModel.Boots, C(0.40f, 0.25f, 0.12f),
                    "Genuine leather ankle boots with a rugged anti-slip sole.")),

            new ShopDefinition("GROCERY STORE",
                "Explore fresh juices, cereals, milk and snacks.",
                C(0.55f, 0.75f, 0.15f), C(0.96f, 0.98f, 0.88f), C(0.60f, 0.62f, 0.50f),
                new ProductDefinition("Juice Bottle", 120, ProductModel.JuiceBottle, C(0.98f, 0.60f, 0.10f),
                    "1 litre bottle of 100% natural orange juice with no added sugar."),
                new ProductDefinition("Cereal Box", 349, ProductModel.CerealBox, C(0.98f, 0.80f, 0.20f),
                    "Crunchy whole-grain breakfast cereal, 500 g family pack."),
                new ProductDefinition("Milk Bottle", 65, ProductModel.MilkBottle, C(0.98f, 0.98f, 0.98f),
                    "1 litre bottle of fresh toned milk from local farms."),
                new ProductDefinition("Snack Packet", 40, ProductModel.SnackPacket, C(0.85f, 0.15f, 0.15f),
                    "Crispy salted potato chips, 90 g party pack.")),

            new ShopDefinition("ACCESSORIES STORE",
                "Explore watches, sunglasses, backpacks and wallets.",
                C(0.55f, 0.30f, 0.80f), C(0.94f, 0.91f, 0.98f), C(0.55f, 0.50f, 0.62f),
                new ProductDefinition("Watch", 6999, ProductModel.Watch, C(0.85f, 0.70f, 0.30f),
                    "Elegant analog wrist watch with a genuine leather strap."),
                new ProductDefinition("Sunglasses", 1999, ProductModel.Sunglasses, C(0.10f, 0.10f, 0.10f),
                    "Polarised UV400 sunglasses with a lightweight frame."),
                new ProductDefinition("Backpack", 2499, ProductModel.Backpack, C(0.20f, 0.35f, 0.55f),
                    "Water-resistant 30 L backpack with a padded laptop compartment."),
                new ProductDefinition("Wallet", 999, ProductModel.Wallet, C(0.45f, 0.25f, 0.12f),
                    "Slim genuine leather wallet with RFID protection."))
        };

        /// <summary>Formats a price in Indian style, e.g. 29999 -> "₹29,999", 149999 -> "₹1,49,999".</summary>
        public static string FormatPrice(int price)
        {
            return MallAssets.CurrencySymbol + GroupIndian(price);
        }

        private static string GroupIndian(int value)
        {
            string digits = Mathf.Abs(value).ToString(CultureInfo.InvariantCulture);
            if (digits.Length <= 3) return (value < 0 ? "-" : "") + digits;

            string last3 = digits.Substring(digits.Length - 3);
            string rest = digits.Substring(0, digits.Length - 3);
            var sb = new StringBuilder();
            int firstGroup = rest.Length % 2;
            for (int i = 0; i < rest.Length; i++)
            {
                if (i > 0 && (i - firstGroup) % 2 == 0) sb.Append(',');
                sb.Append(rest[i]);
            }
            return (value < 0 ? "-" : "") + sb + "," + last3;
        }
    }
}
