# UI

The whole screen UI (start menu, welcome message, "Press E" prompt, information panel with Close
button, exit screen, HUD) is created by `Scripts/UI/UIManager.cs` using Unity UI (uGUI) and the
built-in font, so there are no UI assets or TextMeshPro resources to import.
World-space product/shop labels are created by `MallAssets.CreateLabel`.
