using UnityEngine;

namespace VirtualMall
{
    /// <summary>
    /// Builds simple primitive-based 3D placeholder models for every product.
    /// Every model's pivot is at its bottom centre and its front faces local +Z.
    /// Visual parts have no colliders; the product root gets one BoxCollider in
    /// <see cref="MallBuilder"/> so it is easy to aim at.
    /// </summary>
    public static class ProductFactory
    {
        private static readonly Color Metal = new Color(0.62f, 0.64f, 0.67f);
        private static readonly Color Dark = new Color(0.08f, 0.08f, 0.09f);
        private static readonly Color White = new Color(0.96f, 0.96f, 0.96f);
        private static readonly Color Screen = new Color(0.10f, 0.35f, 0.75f);

        private static Material M(Color c, float smooth = 0.2f) => MallAssets.GetMaterial(c, smooth);

        private static GameObject Cube(Transform p, string n, Vector3 pos, Vector3 scale, Color c, Vector3 euler = default, float smooth = 0.2f)
            => MallAssets.CreatePart(n, PrimitiveType.Cube, p, pos, scale, M(c, smooth), euler);

        private static GameObject Cyl(Transform p, string n, Vector3 pos, Vector3 scale, Color c, Vector3 euler = default, float smooth = 0.2f)
            => MallAssets.CreatePart(n, PrimitiveType.Cylinder, p, pos, scale, M(c, smooth), euler);

        private static GameObject Sphere(Transform p, string n, Vector3 pos, Vector3 scale, Color c, float smooth = 0.3f)
            => MallAssets.CreatePart(n, PrimitiveType.Sphere, p, pos, scale, M(c, smooth));

        private static Transform Group(Transform p, string n, Vector3 pos, Vector3 euler = default)
            => MallAssets.CreateGroup(n, p, pos, euler).transform;

        /// <summary>Creates the model under a new root GameObject called <paramref name="name"/>.</summary>
        public static GameObject Create(ProductModel model, string name, Color color, Transform parent)
        {
            var root = new GameObject(name);
            root.transform.SetParent(parent, false);
            Transform t = root.transform;

            switch (model)
            {
                case ProductModel.Shirt: Garment(t, color, 0.38f, 22f, White, false); break;
                case ProductModel.Jacket: Garment(t, color, 0.52f, 10f, Dark, true); break;
                case ProductModel.TShirt: Garment(t, color, 0.17f, 45f, color * 0.8f, false); break;
                case ProductModel.Jeans: Jeans(t, color); break;
                case ProductModel.Smartphone: Smartphone(t, color); break;
                case ProductModel.Laptop: Laptop(t, color); break;
                case ProductModel.Headphones: Headphones(t, color); break;
                case ProductModel.Smartwatch: WristDisplay(t, color, true); break;
                case ProductModel.Watch: WristDisplay(t, color, false); break;
                case ProductModel.Football: Football(t, color); break;
                case ProductModel.Basketball: Basketball(t, color); break;
                case ProductModel.TennisRacket: TennisRacket(t, color); break;
                case ProductModel.SportsShoes:
                case ProductModel.Sneakers:
                case ProductModel.RunningShoes:
                case ProductModel.Sandals:
                case ProductModel.Boots:
                    ShoePair(t, model, color); break;
                case ProductModel.JuiceBottle: Bottle(t, color, new Color(0.15f, 0.6f, 0.2f), 0.22f); break;
                case ProductModel.MilkBottle: Bottle(t, color, new Color(0.15f, 0.35f, 0.85f), 0.24f); break;
                case ProductModel.CerealBox: CerealBox(t, color); break;
                case ProductModel.SnackPacket: SnackPacket(t, color); break;
                case ProductModel.Sunglasses: Sunglasses(t, color); break;
                case ProductModel.Backpack: Backpack(t, color); break;
                case ProductModel.Wallet: Wallet(t, color); break;
                default: Cube(t, "Box", new Vector3(0f, 0.15f, 0f), Vector3.one * 0.3f, color); break;
            }
            return root;
        }

        // ------------------------------------------------------------------ fashion

        private static void Stand(Transform t, float height)
        {
            Cyl(t, "StandBase", new Vector3(0f, 0.01f, -0.05f), new Vector3(0.3f, 0.01f, 0.3f), Metal, default, 0.6f);
            Cyl(t, "StandPole", new Vector3(0f, height * 0.5f, -0.05f), new Vector3(0.03f, height * 0.5f, 0.03f), Metal, default, 0.6f);
        }

        private static void Garment(Transform t, Color c, float sleeveLength, float sleeveAngle, Color collar, bool zip)
        {
            Stand(t, 0.9f);
            Cube(t, "Body", new Vector3(0f, 0.6f, 0f), new Vector3(0.44f, 0.54f, 0.07f), c);
            float sx = 0.22f + Mathf.Sin(sleeveAngle * Mathf.Deg2Rad) * sleeveLength * 0.5f + 0.04f;
            float sy = 0.84f - Mathf.Cos(sleeveAngle * Mathf.Deg2Rad) * sleeveLength * 0.5f;
            Cube(t, "SleeveL", new Vector3(-sx, sy, 0f), new Vector3(0.13f, sleeveLength, 0.065f), c, new Vector3(0f, 0f, -sleeveAngle));
            Cube(t, "SleeveR", new Vector3(sx, sy, 0f), new Vector3(0.13f, sleeveLength, 0.065f), c, new Vector3(0f, 0f, sleeveAngle));
            Cube(t, "Collar", new Vector3(0f, 0.88f, 0.005f), new Vector3(0.18f, 0.05f, 0.075f), collar);
            if (zip)
            {
                Cube(t, "Zip", new Vector3(0f, 0.6f, 0.037f), new Vector3(0.015f, 0.52f, 0.005f), Metal, default, 0.7f);
                Cube(t, "PocketL", new Vector3(-0.12f, 0.45f, 0.037f), new Vector3(0.1f, 0.08f, 0.005f), c * 0.7f);
                Cube(t, "PocketR", new Vector3(0.12f, 0.45f, 0.037f), new Vector3(0.1f, 0.08f, 0.005f), c * 0.7f);
            }
            else
            {
                Cube(t, "Placket", new Vector3(0f, 0.6f, 0.037f), new Vector3(0.02f, 0.5f, 0.004f), c * 0.75f);
            }
        }

        private static void Jeans(Transform t, Color c)
        {
            Stand(t, 0.9f);
            Cube(t, "Waist", new Vector3(0f, 0.86f, 0f), new Vector3(0.36f, 0.08f, 0.1f), c * 0.85f);
            Cube(t, "LegL", new Vector3(-0.095f, 0.5f, 0f), new Vector3(0.16f, 0.64f, 0.09f), c);
            Cube(t, "LegR", new Vector3(0.095f, 0.5f, 0f), new Vector3(0.16f, 0.64f, 0.09f), c);
            Cube(t, "Button", new Vector3(0f, 0.86f, 0.052f), new Vector3(0.025f, 0.025f, 0.005f), Metal, default, 0.7f);
        }

        // ------------------------------------------------------------------ electronics

        private static void Smartphone(Transform t, Color c)
        {
            Cube(t, "Stand", new Vector3(0f, 0.015f, -0.02f), new Vector3(0.18f, 0.03f, 0.14f), Metal, default, 0.6f);
            Transform phone = Group(t, "Phone", new Vector3(0f, 0.03f, 0f), new Vector3(-12f, 0f, 0f));
            Cube(phone, "Body", new Vector3(0f, 0.18f, 0f), new Vector3(0.18f, 0.36f, 0.02f), c, default, 0.7f);
            Cube(phone, "Screen", new Vector3(0f, 0.18f, 0.0105f), new Vector3(0.16f, 0.33f, 0.002f), Screen, default, 0.9f);
            Cube(phone, "Camera", new Vector3(0.05f, 0.31f, -0.0115f), new Vector3(0.05f, 0.05f, 0.004f), Dark);
        }

        private static void Laptop(Transform t, Color c)
        {
            Cube(t, "Base", new Vector3(0f, 0.0125f, 0f), new Vector3(0.5f, 0.025f, 0.34f), c, default, 0.6f);
            Cube(t, "Keyboard", new Vector3(0f, 0.026f, 0.03f), new Vector3(0.44f, 0.004f, 0.17f), Dark);
            Cube(t, "Touchpad", new Vector3(0f, 0.026f, 0.13f), new Vector3(0.12f, 0.004f, 0.06f), c * 0.85f);
            Transform lid = Group(t, "Lid", new Vector3(0f, 0.025f, -0.165f), new Vector3(-15f, 0f, 0f));
            Cube(lid, "Back", new Vector3(0f, 0.17f, 0f), new Vector3(0.5f, 0.34f, 0.015f), c, default, 0.6f);
            Cube(lid, "Display", new Vector3(0f, 0.17f, 0.008f), new Vector3(0.46f, 0.3f, 0.002f), Screen, default, 0.9f);
        }

        private static void Headphones(Transform t, Color c)
        {
            Cyl(t, "StandBase", new Vector3(0f, 0.01f, 0f), new Vector3(0.18f, 0.01f, 0.18f), Metal, default, 0.6f);
            Cyl(t, "StandPole", new Vector3(0f, 0.22f, 0f), new Vector3(0.03f, 0.21f, 0.03f), Metal, default, 0.6f);
            Cube(t, "BandTop", new Vector3(0f, 0.45f, 0f), new Vector3(0.3f, 0.03f, 0.05f), c);
            Cube(t, "BandL", new Vector3(-0.15f, 0.38f, 0f), new Vector3(0.03f, 0.15f, 0.04f), c);
            Cube(t, "BandR", new Vector3(0.15f, 0.38f, 0f), new Vector3(0.03f, 0.15f, 0.04f), c);
            Cyl(t, "CupL", new Vector3(-0.15f, 0.27f, 0f), new Vector3(0.12f, 0.03f, 0.12f), c, new Vector3(0f, 0f, 90f));
            Cyl(t, "CupR", new Vector3(0.15f, 0.27f, 0f), new Vector3(0.12f, 0.03f, 0.12f), c, new Vector3(0f, 0f, 90f));
            Cyl(t, "CushionL", new Vector3(-0.115f, 0.27f, 0f), new Vector3(0.1f, 0.01f, 0.1f), Dark, new Vector3(0f, 0f, 90f));
            Cyl(t, "CushionR", new Vector3(0.115f, 0.27f, 0f), new Vector3(0.1f, 0.01f, 0.1f), Dark, new Vector3(0f, 0f, 90f));
            Cyl(t, "AccentL", new Vector3(-0.182f, 0.27f, 0f), new Vector3(0.06f, 0.004f, 0.06f), Screen, new Vector3(0f, 0f, 90f), 0.8f);
            Cyl(t, "AccentR", new Vector3(0.182f, 0.27f, 0f), new Vector3(0.06f, 0.004f, 0.06f), Screen, new Vector3(0f, 0f, 90f), 0.8f);
        }

        // ------------------------------------------------------------------ watches

        private static void WristDisplay(Transform t, Color c, bool smart)
        {
            Color pillow = new Color(0.25f, 0.25f, 0.28f);
            Cube(t, "Pillow", new Vector3(0f, 0.09f, 0f), new Vector3(0.1f, 0.18f, 0.07f), pillow);
            Color strap = smart ? c : new Color(0.4f, 0.22f, 0.1f);
            Cube(t, "StrapFront", new Vector3(0f, 0.09f, 0.038f), new Vector3(0.045f, 0.18f, 0.006f), strap);
            Cube(t, "StrapTop", new Vector3(0f, 0.183f, 0f), new Vector3(0.045f, 0.006f, 0.08f), strap);
            if (smart)
            {
                Cube(t, "Case", new Vector3(0f, 0.12f, 0.05f), new Vector3(0.075f, 0.09f, 0.02f), c, default, 0.7f);
                Cube(t, "Screen", new Vector3(0f, 0.12f, 0.061f), new Vector3(0.062f, 0.077f, 0.003f), new Color(0.1f, 0.6f, 0.4f), default, 0.9f);
            }
            else
            {
                Cyl(t, "Case", new Vector3(0f, 0.12f, 0.05f), new Vector3(0.085f, 0.01f, 0.085f), c, new Vector3(90f, 0f, 0f), 0.8f);
                Cyl(t, "Dial", new Vector3(0f, 0.12f, 0.052f), new Vector3(0.07f, 0.0115f, 0.07f), White, new Vector3(90f, 0f, 0f), 0.6f);
                Cube(t, "HourHand", new Vector3(0f, 0.13f, 0.064f), new Vector3(0.004f, 0.022f, 0.002f), Dark);
                Cube(t, "MinuteHand", new Vector3(0.012f, 0.12f, 0.064f), new Vector3(0.028f, 0.003f, 0.002f), Dark);
            }
        }

        // ------------------------------------------------------------------ sports

        private static void BallStand(Transform t)
        {
            Cyl(t, "Ring", new Vector3(0f, 0.02f, 0f), new Vector3(0.14f, 0.02f, 0.14f), Metal, default, 0.6f);
        }

        private static void Football(Transform t, Color c)
        {
            BallStand(t);
            Vector3 center = new Vector3(0f, 0.16f, 0f);
            Sphere(t, "Ball", center, Vector3.one * 0.24f, c);
            Vector3[] dirs =
            {
                new Vector3(0f, 0.3f, 1f), new Vector3(0.9f, 0.4f, 0.3f), new Vector3(-0.9f, 0.4f, 0.3f),
                new Vector3(0.5f, 1f, -0.4f), new Vector3(-0.5f, 1f, -0.4f), new Vector3(0f, -0.2f, -1f),
                new Vector3(0f, 1f, 0.3f)
            };
            for (int i = 0; i < dirs.Length; i++)
                Sphere(t, "Patch" + i, center + dirs[i].normalized * 0.104f, Vector3.one * 0.05f, Dark);
        }

        private static void Basketball(Transform t, Color c)
        {
            BallStand(t);
            Vector3 center = new Vector3(0f, 0.165f, 0f);
            Sphere(t, "Ball", center, Vector3.one * 0.25f, c);
            Cyl(t, "SeamH", center, new Vector3(0.252f, 0.003f, 0.252f), Dark);
            Cyl(t, "SeamV1", center, new Vector3(0.252f, 0.003f, 0.252f), Dark, new Vector3(90f, 0f, 0f));
            Cyl(t, "SeamV2", center, new Vector3(0.252f, 0.003f, 0.252f), Dark, new Vector3(0f, 0f, 90f));
        }

        private static void TennisRacket(Transform t, Color c)
        {
            Cube(t, "Stand", new Vector3(0f, 0.015f, 0f), new Vector3(0.2f, 0.03f, 0.12f), Metal, default, 0.6f);
            Cyl(t, "Handle", new Vector3(0f, 0.16f, 0f), new Vector3(0.035f, 0.13f, 0.035f), Dark);
            Cube(t, "ThroatL", new Vector3(-0.03f, 0.32f, 0f), new Vector3(0.015f, 0.08f, 0.015f), c, new Vector3(0f, 0f, 20f));
            Cube(t, "ThroatR", new Vector3(0.03f, 0.32f, 0f), new Vector3(0.015f, 0.08f, 0.015f), c, new Vector3(0f, 0f, -20f));
            Cyl(t, "Frame", new Vector3(0f, 0.52f, 0f), new Vector3(0.27f, 0.008f, 0.35f), c, new Vector3(90f, 0f, 0f), 0.5f);
            Cyl(t, "Strings", new Vector3(0f, 0.52f, 0f), new Vector3(0.235f, 0.011f, 0.315f), new Color(0.95f, 0.95f, 0.8f), new Vector3(90f, 0f, 0f));
        }

        // ------------------------------------------------------------------ footwear

        private static void ShoePair(Transform t, ProductModel model, Color c)
        {
            Shoe(Group(t, "LeftShoe", new Vector3(-0.075f, 0f, 0f), new Vector3(0f, -6f, 0f)), model, c);
            Shoe(Group(t, "RightShoe", new Vector3(0.075f, 0f, 0f), new Vector3(0f, 6f, 0f)), model, c);
        }

        private static void Shoe(Transform s, ProductModel model, Color c)
        {
            switch (model)
            {
                case ProductModel.Sandals:
                    Cube(s, "Sole", new Vector3(0f, 0.015f, 0f), new Vector3(0.1f, 0.03f, 0.26f), new Color(0.3f, 0.2f, 0.12f));
                    Cube(s, "StrapFront", new Vector3(0f, 0.045f, 0.06f), new Vector3(0.102f, 0.03f, 0.04f), c);
                    Cube(s, "StrapBack", new Vector3(0f, 0.05f, -0.04f), new Vector3(0.102f, 0.04f, 0.035f), c);
                    break;

                case ProductModel.Boots:
                    Cube(s, "Sole", new Vector3(0f, 0.02f, 0f), new Vector3(0.11f, 0.04f, 0.28f), Dark);
                    Cube(s, "Foot", new Vector3(0f, 0.08f, 0.02f), new Vector3(0.1f, 0.08f, 0.22f), c);
                    Cube(s, "Shaft", new Vector3(0f, 0.18f, -0.06f), new Vector3(0.1f, 0.24f, 0.13f), c);
                    Cube(s, "Lace", new Vector3(0f, 0.14f, 0.0f), new Vector3(0.05f, 0.12f, 0.01f), c * 0.6f, new Vector3(-20f, 0f, 0f));
                    break;

                default: // sneakers / running / sports shoes
                    bool running = model == ProductModel.RunningShoes;
                    float sole = running ? 0.045f : 0.03f;
                    Cube(s, "Sole", new Vector3(0f, sole * 0.5f, 0f), new Vector3(0.105f, sole, 0.28f), White);
                    Cube(s, "Upper", new Vector3(0f, sole + 0.045f, -0.03f), new Vector3(0.1f, 0.09f, 0.2f), c);
                    Cube(s, "Toe", new Vector3(0f, sole + 0.025f, 0.08f), new Vector3(0.1f, 0.05f, 0.1f), c);
                    Cube(s, "Laces", new Vector3(0f, sole + 0.091f, 0.0f), new Vector3(0.05f, 0.004f, 0.1f), White);
                    Color stripe = model == ProductModel.SportsShoes ? White : (running ? new Color(1f, 0.5f, 0.1f) : new Color(0.2f, 0.3f, 0.7f));
                    Cube(s, "Stripe", new Vector3(0f, sole + 0.045f, -0.03f), new Vector3(0.104f, 0.02f, 0.12f), stripe, new Vector3(-15f, 0f, 0f));
                    break;
            }
        }

        // ------------------------------------------------------------------ grocery

        private static void Bottle(Transform t, Color c, Color cap, float height)
        {
            float half = height * 0.5f;
            Cyl(t, "Body", new Vector3(0f, half, 0f), new Vector3(0.1f, half, 0.1f), c, default, 0.6f);
            Cyl(t, "Label", new Vector3(0f, half, 0f), new Vector3(0.103f, height * 0.18f, 0.103f), cap);
            Cyl(t, "Shoulder", new Vector3(0f, height + 0.015f, 0f), new Vector3(0.065f, 0.015f, 0.065f), c, default, 0.6f);
            Cyl(t, "Cap", new Vector3(0f, height + 0.04f, 0f), new Vector3(0.045f, 0.012f, 0.045f), cap);
        }

        private static void CerealBox(Transform t, Color c)
        {
            Cube(t, "Box", new Vector3(0f, 0.16f, 0f), new Vector3(0.22f, 0.32f, 0.07f), c);
            Cube(t, "Banner", new Vector3(0f, 0.24f, 0.0355f), new Vector3(0.2f, 0.07f, 0.002f), new Color(0.85f, 0.15f, 0.15f));
            Cyl(t, "Bowl", new Vector3(0f, 0.11f, 0.036f), new Vector3(0.12f, 0.002f, 0.08f), White, new Vector3(90f, 0f, 0f));
        }

        private static void SnackPacket(Transform t, Color c)
        {
            Cube(t, "Pack", new Vector3(0f, 0.14f, 0f), new Vector3(0.2f, 0.24f, 0.05f), c, default, 0.7f);
            Cube(t, "TopSeal", new Vector3(0f, 0.27f, 0f), new Vector3(0.2f, 0.025f, 0.015f), Metal, default, 0.7f);
            Cube(t, "BottomSeal", new Vector3(0f, 0.015f, 0f), new Vector3(0.2f, 0.025f, 0.015f), Metal, default, 0.7f);
            Cube(t, "Window", new Vector3(0f, 0.12f, 0.026f), new Vector3(0.13f, 0.07f, 0.002f), new Color(1f, 0.85f, 0.3f));
        }

        // ------------------------------------------------------------------ accessories

        private static void Sunglasses(Transform t, Color c)
        {
            Cyl(t, "StandBase", new Vector3(0f, 0.01f, -0.06f), new Vector3(0.14f, 0.01f, 0.14f), Metal, default, 0.6f);
            Cyl(t, "StandPole", new Vector3(0f, 0.1f, -0.06f), new Vector3(0.025f, 0.09f, 0.025f), Metal, default, 0.6f);
            Cyl(t, "LensL", new Vector3(-0.058f, 0.2f, 0f), new Vector3(0.09f, 0.006f, 0.07f), c, new Vector3(90f, 0f, 0f), 0.95f);
            Cyl(t, "LensR", new Vector3(0.058f, 0.2f, 0f), new Vector3(0.09f, 0.006f, 0.07f), c, new Vector3(90f, 0f, 0f), 0.95f);
            Cube(t, "Bridge", new Vector3(0f, 0.21f, 0f), new Vector3(0.03f, 0.01f, 0.01f), Dark);
            Cube(t, "ArmL", new Vector3(-0.105f, 0.21f, -0.08f), new Vector3(0.008f, 0.012f, 0.16f), Dark);
            Cube(t, "ArmR", new Vector3(0.105f, 0.21f, -0.08f), new Vector3(0.008f, 0.012f, 0.16f), Dark);
        }

        private static void Backpack(Transform t, Color c)
        {
            Cube(t, "Body", new Vector3(0f, 0.2f, 0f), new Vector3(0.3f, 0.4f, 0.16f), c);
            Cube(t, "Flap", new Vector3(0f, 0.39f, 0.01f), new Vector3(0.31f, 0.06f, 0.17f), c * 0.8f);
            Cube(t, "Pocket", new Vector3(0f, 0.14f, 0.09f), new Vector3(0.22f, 0.16f, 0.04f), c * 0.8f);
            Cube(t, "Zip", new Vector3(0f, 0.22f, 0.111f), new Vector3(0.2f, 0.008f, 0.002f), Metal, default, 0.7f);
            Cube(t, "Handle", new Vector3(0f, 0.44f, 0f), new Vector3(0.08f, 0.03f, 0.02f), Dark);
            Cube(t, "StrapL", new Vector3(-0.08f, 0.22f, -0.09f), new Vector3(0.04f, 0.34f, 0.02f), Dark);
            Cube(t, "StrapR", new Vector3(0.08f, 0.22f, -0.09f), new Vector3(0.04f, 0.34f, 0.02f), Dark);
        }

        private static void Wallet(Transform t, Color c)
        {
            Cube(t, "Stand", new Vector3(0f, 0.02f, -0.02f), new Vector3(0.16f, 0.04f, 0.1f), Metal, default, 0.6f);
            Transform w = Group(t, "Wallet", new Vector3(0f, 0.04f, 0f), new Vector3(-20f, 0f, 0f));
            Cube(w, "Body", new Vector3(0f, 0.06f, 0f), new Vector3(0.18f, 0.12f, 0.03f), c);
            Cube(w, "Stitch", new Vector3(0f, 0.06f, 0.0155f), new Vector3(0.16f, 0.1f, 0.001f), c * 1.25f);
            Cube(w, "Card", new Vector3(0.03f, 0.125f, 0f), new Vector3(0.12f, 0.02f, 0.02f), new Color(0.2f, 0.45f, 0.85f));
        }
    }
}
