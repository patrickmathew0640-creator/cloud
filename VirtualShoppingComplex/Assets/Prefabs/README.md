# Prefabs

Filled by the menu **Virtual Mall > Bake Mall Into Open Scene (editable objects + prefabs)**:

- `Products/` – one prefab per product (Smartphone, Laptop, Football, ...). Each has a BoxCollider and `InteractableProduct`.
- `Shops/` – one prefab per shop (Fashion Store, Electronics Store, ...), with nested product prefabs and a `ShopInteraction` counter.
- `Player.prefab` – CharacterController + `PlayerController`, camera with `MouseLook` and `InteractionSystem`.

You do not need these for the demo to run: by default the mall is generated when you press Play.
