# Virtual Shopping Complex – AR/VR

A first-person shopping mall you can walk around on a normal computer with keyboard and mouse.
It is built in Unity, uses only Unity's built-in features, and is structured so you can convert it to VR (OpenXR) later.

- **Engine:** Unity 6 LTS (`6000.0.x` or `6000.3.x` LTS). The scripts are plain C#.
- **Assets:** no paid assets, no external models and no TextMeshPro import. Everything is built from Unity primitives.
- **Render pipeline:** works in the Built-in Render Pipeline and in URP, because materials are copied from Unity's own default material.
- **Input:** works with the classic Input Manager or the new Input System package, whichever the project has enabled.

---

## 1. Quick start (about 5 minutes)

1. Install **Unity Hub** and a **Unity 6 LTS** editor (Hub → *Installs* → *Install Editor* → the newest *Unity 6 … LTS*).
   For Windows builds, tick *Windows Build Support (Mono)*.
2. Download this repository. You can use `git clone`, or *Code → Download ZIP* on GitHub and unzip it.
3. In Unity Hub choose *Projects → Add → Add project from disk*, then select the **`VirtualShoppingComplex`** folder.
   That folder contains `Assets/`, `Packages/` and `ProjectSettings/`.
   - If Hub says the editor version `6000.0.23f1` is not installed, pick the Unity 6 version you have installed and confirm.
4. Open the project. The first import takes a few minutes.
   - If you see **"…native platform backends for the new input system are not enabled… Enable?"**, click **Yes**, and Unity restarts.
     Clicking **No** also works. The scripts support both input systems.
5. The scene `Assets/Scenes/VirtualShoppingComplex.unity` is **created and opened automatically**.
   If it is not open, use the menu **Virtual Mall → Open or Create Mall Scene**.
6. Press **▶ Play**. Click **START TOUR** (or press Enter), then click inside the Game view so the mouse is captured.

> Tip: in the Game view toolbar, set the aspect to *16:9* or *Full HD (1920×1080)*, and turn on *Maximize On Play*.

---

## 2. Controls

| Key | Action |
|---|---|
| **W A S D** / arrow keys | Move |
| **Mouse** | Look around |
| **Space** | Jump |
| **Shift** | Run |
| **E** | Interact (product → product info, counter → shop info). Also closes the info panel |
| **Esc** | Unlock the cursor, or close the open panel |
| **Left click** | Lock the cursor again |

---

## 3. What is in the demo

```
START MENU (title + controls)  →  spawn on the plaza at the MAIN ENTRANCE
→ "Welcome to the Virtual Shopping Complex" (hides after 4 s)
→ enter the building → MAIN LOBBY (fountain, directory boards, information desk)
→ CENTRAL CORRIDOR (benches, planters, hanging direction signs)
   left side:  1 FASHION STORE    3 SPORTS STORE     5 GROCERY STORE
   right side: 2 ELECTRONICS STORE 4 FOOTWEAR STORE  6 ACCESSORIES STORE
→ look at a product → "Press E to Interact" → E → PRODUCT NAME / PRICE / DESCRIPTION → Close (button, E or Esc)
→ look at a shop counter → "Press E to Explore Shop" → SHOP NAME / NUMBER OF PRODUCTS / DESCRIPTION
→ EXIT HALL at the end of the corridor → walk out of the green EXIT door
→ "Thank you for visiting!" → Continue Exploring / Restart Tour / Quit
```

Each shop has:

- a coloured storefront with its name board, a projecting blade sign, display windows and a door frame;
- its own floor, walls, rug, poster wall, interior name board and light;
- a **counter**, which is the shop interaction point, plus a cash register and a shopkeeper;
- **4 featured products** on podiums, each with a floating name and price label;
- **2 shelf units** at the back, each with 3 shelves of extra stock and a price tag on every shelf.

That makes 22 interactive items per shop and 132 in the whole mall.

| Shop | Products (price) |
|---|---|
| Fashion | Shirt ₹1,299 · Jacket ₹3,499 · Jeans ₹2,199 · T-Shirt ₹599 |
| Electronics | Smartphone ₹29,999 · Laptop ₹59,999 · Headphones ₹4,999 · Smartwatch ₹8,999 |
| Sports | Football ₹1,499 · Basketball ₹1,799 · Sports Shoes ₹3,999 · Tennis Racket ₹2,499 |
| Footwear | Sneakers ₹2,999 · Running Shoes ₹4,499 · Sandals ₹899 · Boots ₹5,499 |
| Grocery | Juice Bottle ₹120 · Cereal Box ₹349 · Milk Bottle ₹65 · Snack Packet ₹40 |
| Accessories | Watch ₹6,999 · Sunglasses ₹1,999 · Backpack ₹2,499 · Wallet ₹999 |

To change names, prices, descriptions or colours, edit `Assets/Scripts/Environment/MallCatalog.cs`.

> If Unity's built-in font cannot draw the `₹` sign on your system, prices automatically show as `Rs. 29,999` instead of an empty box.

---

## 4. Folder structure

```
VirtualShoppingComplex/
├── Assets/
│   ├── Scenes/        VirtualShoppingComplex.unity   (auto-created)
│   ├── Scripts/
│   │   ├── Core/          InputReader.cs, MallBootstrap.cs
│   │   ├── Environment/   MallBuilder.cs, MallCatalog.cs, MallAssets.cs, ProductFactory.cs
│   │   ├── Player/        PlayerController.cs, MouseLook.cs
│   │   ├── Interaction/   IInteractable.cs, InteractionSystem.cs, InteractableProduct.cs,
│   │   │                  ShopInteraction.cs, MallExit.cs
│   │   ├── UI/            UIManager.cs
│   │   └── Editor/        MallSceneSetup.cs   (editor-only menu + auto scene setup)
│   ├── Prefabs/       (filled by the Bake menu: Products/, Shops/, Player.prefab)
│   ├── Materials/     (filled by the Bake menu)
│   ├── Textures/      (filled by the Bake menu)
│   ├── Models/        (empty – everything is made of primitives)
│   └── UI/            (empty – UI is created by UIManager)
├── Packages/manifest.json
└── ProjectSettings/ProjectVersion.txt     (Unity generates the other settings on first open)
```

### Scripts and what each one does

Every MonoBehaviour's file name matches its class name.
All classes are in the `VirtualMall` namespace, and the editor tool is in `VirtualMall.EditorTools`.

| Script | Type | Purpose |
|---|---|---|
| `MallBootstrap` | MonoBehaviour | The only component the scene needs. In `Awake` it calls `MallBuilder.BuildAll`, unless the mall is already baked into the scene |
| `MallBuilder` | static class | Generates the plaza, building, entrance, lobby, corridor, 6 shops, exit hall, lights, player and UI. It also defines the mall layout |
| `MallCatalog` | static class | Shop and product data (names, prices, descriptions, colours). Also formats prices in the Indian style (₹1,49,999) |
| `MallAssets` | static class | Primitive meshes, colour materials, the built-in font, the procedural floor texture, geometry helpers and world-space labels |
| `ProductFactory` | static class | Builds the 24 primitive product models |
| `InputReader` | static class | Reads all keyboard and mouse input for both input systems. Gameplay input can be switched off while menus are open |
| `PlayerController` | MonoBehaviour | Walking, running, jumping and gravity through `CharacterController`, teleport and respawn |
| `MouseLook` | MonoBehaviour | Mouse look with light smoothing. Pitch is clamped to ±85° and yaw turns the body |
| `InteractionSystem` | MonoBehaviour | Casts a ray (plus a small sphere-cast for easier aiming) from the camera, shows the prompt and calls `Interact()` |
| `IInteractable` | interface | Contract for anything you can press E on |
| `InteractableProduct` | MonoBehaviour | Product data. On E it opens the product panel. The product grows slightly while you look at it |
| `ShopInteraction` | MonoBehaviour | Shop counter. On E it opens the shop panel. It also defines the shop's area for the "Location" HUD |
| `MallExit` | MonoBehaviour | Exit zone outside the back door. It opens the exit screen |
| `UIManager` | MonoBehaviour | Builds all screen UI from code and controls the game state, cursor lock and panels |
| `MallSceneSetup` | Editor | Creates and opens the scene, adds it to Build Settings, and adds the *Virtual Mall* menu |

---

## 5. Scene hierarchy (created when you press Play)

The saved scene only contains:

```
VirtualShoppingComplex            ← GameObject with the MallBootstrap component
```

When you press Play, this is generated under it:

```
VirtualShoppingComplex (MallBootstrap)
├── Lighting
│   └── Sun                         Light: Directional, Soft Shadows, intensity 1.1, rotation (62,-35,0)
├── Environment
│   ├── Exterior                    Ground (BoxCollider), plazas, road, trees, street lamps, benches,
│   │                               invisible boundary colliders
│   ├── Building                    Floor, Ceiling, Front/Back/Side walls (BoxColliders), roof trim
│   │   └── MainEntrance            frame pillars, canopy, columns, "VIRTUAL SHOPPING COMPLEX" sign
│   ├── Lobby                       Fountain, 2 DirectoryBoards, InformationDesk, benches, planters,
│   │                               CorridorEntranceSign, 3 point lights
│   ├── Corridor                    floor stripe, 3 benches, 6 planters, 3 two-sided DirectionSigns, 3 lights
│   ├── ExitHall                    EXIT signs, thank-you boards, ExitReturnPoint,
│   │   └── ExitZone                MallExit (zone 14×4×6 m outside the back door)
│   └── Shops
│       ├── FASHION STORE           (same structure for all 6 shops)
│       │   ├── Structure           Floor, BackWall, SideWall_L/R, FrontWall_L/R, DoorHeader, DoorFrame_*
│       │   ├── Storefront          Fascia, NameBoard + ShopName label, windows, BladeSign
│       │   ├── Interior            Rug, BackSign, Poster, ShopLight (Point), ceiling panels
│       │   ├── Counter             BoxCollider + ShopInteraction   ← "Press E to Explore Shop"
│       │   ├── Shopkeeper          CapsuleCollider
│       │   └── Products
│       │       ├── Display_Shirt   Podium (BoxCollider), Shirt (BoxCollider + InteractableProduct), Label
│       │       ├── Display_Jacket / Display_Jeans / Display_T-Shirt
│       │       ├── ShelfUnit_A     WalkBlocker (layer Ignore Raycast), 9 products, 3 price tags
│       │       └── ShelfUnit_B
│       ├── ELECTRONICS STORE … ACCESSORIES STORE
├── Player                          tag Player, layer Ignore Raycast, position (0, 0.05, -7)
│   │                               CharacterController (height 1.8, radius 0.35, center (0,0.9,0),
│   │                               step offset 0.35, slope 45) + PlayerController
│   └── PlayerCamera                tag MainCamera, local position (0, 1.62, 0), Camera (FOV 70, near 0.05),
│                                   AudioListener, MouseLook, InteractionSystem
└── UI                              UIManager
    ├── MallCanvas                  Canvas (Screen Space Overlay), CanvasScaler (1920×1080), GraphicRaycaster
    │   ├── Crosshair, LocationHUD, ControlsHint, CursorUnlockedBanner
    │   ├── InteractionPrompt       "Press E to Interact" / "Press E to Explore Shop" + target name
    │   ├── WelcomeMessage          "Welcome to the Virtual Shopping Complex" (fades after 4 s)
    │   ├── InfoPanel               header, title, price/products line, description, CLOSE button
    │   ├── StartPanel              title, CONTROLS list, START TOUR, QUIT
    │   └── ExitPanel               CONTINUE EXPLORING, RESTART TOUR, QUIT
    └── EventSystem                 EventSystem + StandaloneInputModule (or InputSystemUIInputModule)
```

Building the mall from code at runtime means there are no broken prefab links, missing references or missing scripts to fix by hand.

### Optional: see and edit everything in Edit Mode, with real prefabs

Use **Virtual Mall → Bake Mall Into Open Scene (editable objects + prefabs)** while the mall scene is open. This:

- generates the whole hierarchy above into the scene, so you can move, recolour or delete objects in the Inspector;
- saves materials to `Assets/Materials`, the floor texture to `Assets/Textures`, and prefabs to `Assets/Prefabs`:
  24 product prefabs, 6 shop prefabs with nested product prefabs, and `Player.prefab`;
- saves the scene.

When the scene already contains a baked mall, `MallBootstrap` does not generate it again.
To go back to the generated version, use **Virtual Mall → Clear Baked Mall From Open Scene**.

---

## 6. Manual setup (if you want to do it yourself instead of using the menu)

1. *File → New Scene → Empty (Built-in or URP)*. Save it as `Assets/Scenes/VirtualShoppingComplex.unity`.
2. *GameObject → Create Empty*. Rename it `VirtualShoppingComplex` and set its Transform to position (0,0,0), rotation (0,0,0), scale (1,1,1).
3. In the Inspector, choose **Add Component → Mall Bootstrap**.
4. *File → Build Profiles* (in older versions, *Build Settings*) → **Add Open Scenes**.
5. Press Play.

You do **not** need to add a camera, light, EventSystem or Canvas. If the scene already has a Main Camera or a Directional Light, the bootstrap disables them during Play and creates its own.

### Using the scripts in another project (for example a URP template project)

Copy the folder `Assets/Scripts` into that project's `Assets` folder, then do step 2–5 above, or use the
**Virtual Mall → Open or Create Mall Scene** menu.
The only requirement is **Unity UI (uGUI)** (`com.unity.ugui`), which is included in every Unity 6 project.
`com.unity.inputsystem` is optional.

---

## 7. Packages

`Packages/manifest.json` contains only:

| Package | Why |
|---|---|
| `com.unity.ugui` 2.0.0 | Canvas, Text, Image and Button for the UI and the 3D labels (built into Unity 6) |
| `com.unity.inputsystem` | Optional. Included so the project compiles whichever *Active Input Handling* setting is selected |
| `com.unity.modules.*` | Built-in engine modules (physics, UI, text rendering, audio, …) |

No XR packages are installed, so the desktop version cannot be broken by XR setup.
If you want IDE integration, add *Visual Studio Editor* or *JetBrains Rider Editor* from the Package Manager.

---

## 8. Converting to VR later (OpenXR)

The project is already split so this is a contained job:

- **Environment** (`MallBuilder`, `MallCatalog`, `ProductFactory`, shop and product prefabs) has no input code.
- **Interaction** goes through `IInteractable.Interact()`. Any VR interactor can call it.
- **Input** is all in `InputReader`.
- **Player** is separate (`PlayerController`, `MouseLook`).

Steps:

1. *Window → Package Manager → Unity Registry*, then install:
   - **XR Plugin Management** (`com.unity.xr.management`)
   - **OpenXR Plugin** (`com.unity.xr.openxr`)
   - **XR Interaction Toolkit** (`com.unity.xr.interaction.toolkit`). From its *Samples* tab, import **Starter Assets**.
2. *Edit → Project Settings → XR Plug-in Management* → tick **OpenXR** for PC. Under *OpenXR*, add the interaction profile for your headset
   (for example *Oculus Touch Controller Profile* for Meta Quest via Link).
3. Bake the mall (section 5) so it exists in the scene. Delete or disable the baked `Player` object.
4. Drag the **XR Origin (XR Rig)** prefab from the Starter Assets into the scene at position (0, 0, -7).
5. On the right-hand controller's ray interactor, listen to *Select Entered*. Use `GetComponentInParent<IInteractable>()` on the
   selected object and call `Interact()`. That is the same method the desktop E key uses.
   Alternatively, add an `InteractionSystem` to the controller and set its *Ray Origin* to the controller transform.
6. For VR, change the `UIManager` canvas to *World Space* and place it about 2 m in front of the player
   (screen-space overlays do not appear in headsets). Then add a *Tracked Device Graphic Raycaster* to the canvas.

---

## 9. Building a standalone .exe

*File → Build Profiles* → *Windows* (or macOS/Linux) → check that `Scenes/VirtualShoppingComplex` is in the scene list → **Build**.
The QUIT buttons close the built application. In the Editor they stop Play Mode.

---

## 10. Final test checklist

Go through this list in Play Mode:

- [ ] Project opens with **no red errors in the Console** (*Window → General → Console*).
- [ ] `Assets/Scenes/VirtualShoppingComplex.unity` opens. The Hierarchy shows `VirtualShoppingComplex` with *Mall Bootstrap* and no "Missing script".
- [ ] Press Play → the start menu shows **VIRTUAL SHOPPING COMPLEX** and the **CONTROLS** list.
- [ ] START TOUR / Enter → cursor hides → **"Welcome to the Virtual Shopping Complex"** shows and fades out after about 4 s.
- [ ] Player stands on the plaza facing the **main entrance** and the big mall sign.
- [ ] **W/A/S/D** move smoothly. **Shift** runs. **Space** jumps.
- [ ] **Mouse** looks around. Looking straight up or down stops at the limit, and the view never flips.
- [ ] You cannot walk through walls, shop walls, counters, shelves, podiums, benches, the fountain or boards.
- [ ] Walk through the entrance → Lobby → Corridor. The *Location* HUD (top-left) updates.
- [ ] All **six shop names** are visible on the storefronts, blade signs and direction signs.
- [ ] Enter each shop. Every product has a **name and price label**, and the shelves have price tags.
- [ ] Look at a product → **"Press E to Interact"** + product name. The product grows slightly.
- [ ] Press **E** → panel with **name, price, description**. Movement stops and the cursor appears.
- [ ] Close with the **CLOSE** button, **E** or **Esc** → back to playing. The panel does not reopen by itself.
- [ ] Look at a counter → **"Press E to Explore Shop"** → E → **shop name, number of products, description**.
- [ ] **Esc** while playing → cursor unlocks and the orange banner appears. **Left click** → cursor locks again.
- [ ] Walk to the end of the corridor → Exit Hall → out through the green **EXIT** door → **Thank you** screen.
- [ ] **Continue Exploring** puts you back inside. **Restart Tour** returns you to the entrance. **Quit** stops Play Mode.
- [ ] If you jump off the world edge or fall, you respawn at the entrance. The world also has invisible boundary walls.

---

## 11. Troubleshooting

| Problem | Fix |
|---|---|
| Mouse does not turn the camera | Click inside the Game view to lock the cursor. Make sure the start menu is closed |
| Mouse moves too fast or too slow | Select `Player/PlayerCamera` during Play and change *Mouse Look → Sensitivity* (default 2) |
| Pink/magenta objects | The project's render pipeline asset was removed or changed while the mall was baked. Use *Clear Baked Mall*, then *Bake* again, or just use the runtime-generated version |
| "Input System … backends not enabled" dialog | Either answer works. **Yes** is recommended |
| Errors after copying scripts into another project | Make sure `com.unity.ugui` is installed (Package Manager → *Unity UI*) |
| Scene did not open automatically | Use **Virtual Mall → Open or Create Mall Scene** |
