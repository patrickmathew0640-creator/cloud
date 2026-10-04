# Models

All products and furniture are built from Unity primitives (Cube, Sphere, Cylinder, Capsule) in
`Scripts/Environment/ProductFactory.cs`, so no external 3D models are needed.

To use a real model later: import the `.fbx` here, drag it into a product prefab
(Assets/Prefabs/Products after baking) and keep the root's BoxCollider + `InteractableProduct`.
