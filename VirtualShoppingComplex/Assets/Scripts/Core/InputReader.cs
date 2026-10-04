using UnityEngine;
#if !ENABLE_LEGACY_INPUT_MANAGER && ENABLE_INPUT_SYSTEM
using UnityEngine.InputSystem;
#endif

namespace VirtualMall
{
    /// <summary>
    /// Single place where keyboard/mouse input is read.
    /// Works with the classic Input Manager (default for this project) and, if a project is
    /// switched to "Input System Package (New)" only, with the new Input System package.
    /// For VR later, replace these properties with XR controller input without touching the
    /// player / interaction scripts.
    /// </summary>
    public static class InputReader
    {
        /// <summary>False while menus/panels are open: movement, look and jump then read as zero.</summary>
        public static bool GameplayEnabled { get; set; } = true;

        // Reset static state when entering Play Mode (supports "Enter Play Mode Options" without domain reload).
        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.SubsystemRegistration)]
        private static void ResetState()
        {
            GameplayEnabled = true;
        }

        public static Vector2 Move => GameplayEnabled ? RawMove : Vector2.zero;
        public static Vector2 Look => GameplayEnabled ? RawLook : Vector2.zero;
        public static bool JumpPressed => GameplayEnabled && RawJump;
        public static bool SprintHeld => GameplayEnabled && RawSprint;

        // UI / state keys are never gated.
        public static bool InteractPressed => RawInteract;
        public static bool CancelPressed => RawCancel;
        public static bool SubmitPressed => RawSubmit;
        public static bool ClickPressed => RawClick;

#if ENABLE_LEGACY_INPUT_MANAGER
        private static Vector2 RawMove
        {
            get
            {
                float x = 0f, y = 0f;
                if (Input.GetKey(KeyCode.A) || Input.GetKey(KeyCode.LeftArrow)) x -= 1f;
                if (Input.GetKey(KeyCode.D) || Input.GetKey(KeyCode.RightArrow)) x += 1f;
                if (Input.GetKey(KeyCode.S) || Input.GetKey(KeyCode.DownArrow)) y -= 1f;
                if (Input.GetKey(KeyCode.W) || Input.GetKey(KeyCode.UpArrow)) y += 1f;
                return Vector2.ClampMagnitude(new Vector2(x, y), 1f);
            }
        }

        // "Mouse X" / "Mouse Y" exist in every default Input Manager configuration.
        private static Vector2 RawLook => new Vector2(Input.GetAxisRaw("Mouse X"), Input.GetAxisRaw("Mouse Y"));
        private static bool RawJump => Input.GetKeyDown(KeyCode.Space);
        private static bool RawSprint => Input.GetKey(KeyCode.LeftShift) || Input.GetKey(KeyCode.RightShift);
        private static bool RawInteract => Input.GetKeyDown(KeyCode.E);
        private static bool RawCancel => Input.GetKeyDown(KeyCode.Escape);
        private static bool RawSubmit => Input.GetKeyDown(KeyCode.Return) || Input.GetKeyDown(KeyCode.KeypadEnter);
        private static bool RawClick => Input.GetMouseButtonDown(0);
#elif ENABLE_INPUT_SYSTEM
        // Scale so the new Input System's pixel delta feels like the legacy "Mouse X/Y" axes.
        private const float MouseDeltaScale = 0.1f;

        private static Vector2 RawMove
        {
            get
            {
                Keyboard k = Keyboard.current;
                if (k == null) return Vector2.zero;
                float x = 0f, y = 0f;
                if (k.aKey.isPressed || k.leftArrowKey.isPressed) x -= 1f;
                if (k.dKey.isPressed || k.rightArrowKey.isPressed) x += 1f;
                if (k.sKey.isPressed || k.downArrowKey.isPressed) y -= 1f;
                if (k.wKey.isPressed || k.upArrowKey.isPressed) y += 1f;
                return Vector2.ClampMagnitude(new Vector2(x, y), 1f);
            }
        }

        private static Vector2 RawLook
        {
            get
            {
                Mouse m = Mouse.current;
                return m != null ? m.delta.ReadValue() * MouseDeltaScale : Vector2.zero;
            }
        }

        private static bool RawJump => Keyboard.current != null && Keyboard.current.spaceKey.wasPressedThisFrame;
        private static bool RawSprint => Keyboard.current != null && (Keyboard.current.leftShiftKey.isPressed || Keyboard.current.rightShiftKey.isPressed);
        private static bool RawInteract => Keyboard.current != null && Keyboard.current.eKey.wasPressedThisFrame;
        private static bool RawCancel => Keyboard.current != null && Keyboard.current.escapeKey.wasPressedThisFrame;
        private static bool RawSubmit => Keyboard.current != null && (Keyboard.current.enterKey.wasPressedThisFrame || Keyboard.current.numpadEnterKey.wasPressedThisFrame);
        private static bool RawClick => Mouse.current != null && Mouse.current.leftButton.wasPressedThisFrame;
#else
        private static Vector2 RawMove => Vector2.zero;
        private static Vector2 RawLook => Vector2.zero;
        private static bool RawJump => false;
        private static bool RawSprint => false;
        private static bool RawInteract => false;
        private static bool RawCancel => false;
        private static bool RawSubmit => false;
        private static bool RawClick => false;
#endif
    }
}
