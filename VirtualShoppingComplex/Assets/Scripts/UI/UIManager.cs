using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;
#if !ENABLE_LEGACY_INPUT_MANAGER && ENABLE_INPUT_SYSTEM
using UnityEngine.InputSystem.UI;
#endif

namespace VirtualMall
{
    /// <summary>
    /// Builds and controls all screen UI (start menu, welcome message, interaction prompt,
    /// product/shop information panel, exit screen, HUD) and owns the game state:
    /// which screen is open and whether the cursor is locked / player input is enabled.
    /// The UI is created from code, so there are no prefab/Inspector references to break.
    /// </summary>
    [DisallowMultipleComponent]
    public class UIManager : MonoBehaviour
    {
        public enum State { StartScreen, Playing, Panel, ExitScreen }

        public static UIManager Instance { get; private set; }

        [Header("Settings")]
        [SerializeField] private bool showStartScreen = true;
        [SerializeField] private float welcomeDuration = 4f;

        [Header("References (created automatically by BuildUI)")]
        [SerializeField] private Canvas canvas;
        [SerializeField] private GameObject crosshair;
        [SerializeField] private GameObject promptPanel;
        [SerializeField] private Text promptText;
        [SerializeField] private Text promptTargetText;
        [SerializeField] private CanvasGroup welcomeGroup;
        [SerializeField] private Text locationText;
        [SerializeField] private GameObject controlsHint;
        [SerializeField] private GameObject pausedBanner;
        [SerializeField] private GameObject infoPanel;
        [SerializeField] private Image infoAccentBar;
        [SerializeField] private Text infoHeaderText;
        [SerializeField] private Text infoTitleText;
        [SerializeField] private Text infoSubtitleText;
        [SerializeField] private Text infoBodyText;
        [SerializeField] private Button infoCloseButton;
        [SerializeField] private GameObject startPanel;
        [SerializeField] private Button startButton;
        [SerializeField] private Button startQuitButton;
        [SerializeField] private GameObject exitPanel;
        [SerializeField] private Button exitContinueButton;
        [SerializeField] private Button exitRestartButton;
        [SerializeField] private Button exitQuitButton;
        [SerializeField] private PlayerController player;

        private State state = State.StartScreen;
        private int panelOpenedFrame = -1;
        private int panelClosedFrame = -1;
        private float welcomeTimer;
        private float locationTimer;
        private MallExit activeExit;

        private static readonly Color PanelColor = new Color(0.07f, 0.09f, 0.13f, 0.94f);
        private static readonly Color Gold = new Color(1f, 0.82f, 0.32f);

        public State CurrentState => state;
        public bool IsPlaying => state == State.Playing;
        public bool IsPanelOpen => state == State.Panel;
        /// <summary>True when the player may press E on something this frame.</summary>
        public bool AcceptsInteraction => state == State.Playing && Time.frameCount != panelClosedFrame;

        // ------------------------------------------------------------------ lifecycle

        private void Awake()
        {
            if (Instance != null && Instance != this)
            {
                Debug.LogWarning("Another UIManager already exists. Disabling this one.", this);
                enabled = false;
                return;
            }
            Instance = this;
        }

        private void OnDestroy()
        {
            if (Instance == this) Instance = null;
        }

        private void Start()
        {
            if (canvas == null) BuildUI();
            EnsureEventSystem();
            WireButtons();
            if (player == null) player = FindAnyObjectByType<PlayerController>();

            infoPanel.SetActive(false);
            exitPanel.SetActive(false);
            promptPanel.SetActive(false);
            welcomeGroup.gameObject.SetActive(false);

            if (showStartScreen) ShowStartScreen();
            else StartTour();
        }

        private void Update()
        {
            switch (state)
            {
                case State.StartScreen:
                    if (InputReader.SubmitPressed) StartTour();
                    break;

                case State.Playing:
                    if (Cursor.lockState == CursorLockMode.Locked)
                    {
                        if (InputReader.CancelPressed) SetCursorLocked(false);
                    }
                    else if (InputReader.ClickPressed)
                    {
                        SetCursorLocked(true);
                    }
                    break;

                case State.Panel:
                    if (Time.frameCount != panelOpenedFrame && (InputReader.InteractPressed || InputReader.CancelPressed))
                        ClosePanel();
                    break;

                case State.ExitScreen:
                    if (InputReader.CancelPressed) ContinueExploring();
                    break;
            }

            bool locked = Cursor.lockState == CursorLockMode.Locked;
            InputReader.GameplayEnabled = state == State.Playing && locked;

            if (pausedBanner != null) pausedBanner.SetActive(state == State.Playing && !locked);
            if (crosshair != null) crosshair.SetActive(state == State.Playing && locked);
            if (controlsHint != null) controlsHint.SetActive(state == State.Playing);

            UpdateWelcome();
            UpdateLocation();
        }

        // ------------------------------------------------------------------ public API

        public void ShowStartScreen()
        {
            state = State.StartScreen;
            startPanel.SetActive(true);
            SetCursorLocked(false);
            InputReader.GameplayEnabled = false;
        }

        public void StartTour()
        {
            startPanel.SetActive(false);
            state = State.Playing;
            SetCursorLocked(true);
            ShowWelcome();
            Deselect();
        }

        public void ShowPrompt(string prompt, string target)
        {
            if (state != State.Playing)
            {
                HidePrompt();
                return;
            }
            if (!promptPanel.activeSelf) promptPanel.SetActive(true);
            if (promptText.text != prompt) promptText.text = prompt;
            if (promptTargetText.text != target) promptTargetText.text = target;
        }

        public void HidePrompt()
        {
            if (promptPanel != null && promptPanel.activeSelf) promptPanel.SetActive(false);
        }

        public void ShowInfoPanel(string header, string title, string subtitle, string body, Color accent)
        {
            if (state != State.Playing) return;
            state = State.Panel;
            panelOpenedFrame = Time.frameCount;

            infoHeaderText.text = header;
            infoHeaderText.color = Color.Lerp(accent, Color.white, 0.35f);
            infoAccentBar.color = accent;
            infoTitleText.text = title.ToUpperInvariant();
            infoSubtitleText.text = subtitle;
            infoBodyText.text = body;
            infoPanel.SetActive(true);

            HidePrompt();
            SetCursorLocked(false);
        }

        public void ClosePanel()
        {
            if (state != State.Panel) return;
            infoPanel.SetActive(false);
            state = State.Playing;
            panelClosedFrame = Time.frameCount;
            SetCursorLocked(true);
            Deselect();
        }

        public void ShowExitScreen(MallExit exit)
        {
            if (state != State.Playing) return;
            activeExit = exit;
            state = State.ExitScreen;
            exitPanel.SetActive(true);
            HidePrompt();
            SetCursorLocked(false);
        }

        public void ContinueExploring()
        {
            exitPanel.SetActive(false);
            state = State.Playing;
            if (activeExit != null) activeExit.ReturnPlayerInside();
            panelClosedFrame = Time.frameCount;
            SetCursorLocked(true);
            Deselect();
        }

        public void RestartTour()
        {
            exitPanel.SetActive(false);
            infoPanel.SetActive(false);
            if (player != null) player.ResetToSpawn();
            state = State.Playing;
            panelClosedFrame = Time.frameCount;
            SetCursorLocked(true);
            ShowWelcome();
            Deselect();
        }

        public void QuitApplication()
        {
#if UNITY_EDITOR
            UnityEditor.EditorApplication.isPlaying = false;
#else
            Application.Quit();
#endif
        }

        // ------------------------------------------------------------------ helpers

        private static void SetCursorLocked(bool locked)
        {
            Cursor.lockState = locked ? CursorLockMode.Locked : CursorLockMode.None;
            Cursor.visible = !locked;
        }

        private static void Deselect()
        {
            if (EventSystem.current != null) EventSystem.current.SetSelectedGameObject(null);
        }

        private void ShowWelcome()
        {
            welcomeTimer = welcomeDuration;
            welcomeGroup.alpha = 1f;
            welcomeGroup.gameObject.SetActive(true);
        }

        private void UpdateWelcome()
        {
            if (welcomeTimer <= 0f) return;
            welcomeTimer -= Time.unscaledDeltaTime;
            welcomeGroup.alpha = Mathf.Clamp01(welcomeTimer / 0.8f); // fade out during the last 0.8 s
            if (welcomeTimer <= 0f) welcomeGroup.gameObject.SetActive(false);
        }

        private void UpdateLocation()
        {
            if (locationText == null || player == null) return;
            locationTimer -= Time.unscaledDeltaTime;
            if (locationTimer > 0f) return;
            locationTimer = 0.25f;
            locationText.text = "Location:  " + MallBuilder.DescribeLocation(player.transform.position);
        }

        private void WireButtons()
        {
            infoCloseButton.onClick.AddListener(ClosePanel);
            startButton.onClick.AddListener(StartTour);
            startQuitButton.onClick.AddListener(QuitApplication);
            exitContinueButton.onClick.AddListener(ContinueExploring);
            exitRestartButton.onClick.AddListener(RestartTour);
            exitQuitButton.onClick.AddListener(QuitApplication);
        }

        public void EnsureEventSystem()
        {
            if (FindAnyObjectByType<EventSystem>() != null) return;
            var go = new GameObject("EventSystem", typeof(EventSystem));
            go.transform.SetParent(transform, false);
#if ENABLE_LEGACY_INPUT_MANAGER
            go.AddComponent<StandaloneInputModule>();
#elif ENABLE_INPUT_SYSTEM
            go.AddComponent<InputSystemUIInputModule>().AssignDefaultActions();
#endif
        }

        // ------------------------------------------------------------------ UI construction

        /// <summary>Creates the whole screen-space UI and fills in every reference above.</summary>
        public void BuildUI()
        {
            var canvasGo = new GameObject("MallCanvas", typeof(RectTransform));
            canvasGo.transform.SetParent(transform, false);
            canvas = canvasGo.AddComponent<Canvas>();
            canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            canvas.sortingOrder = 100;
            var scaler = canvasGo.AddComponent<CanvasScaler>();
            scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
            scaler.referenceResolution = new Vector2(1920f, 1080f);
            scaler.matchWidthOrHeight = 0.5f;
            canvasGo.AddComponent<GraphicRaycaster>();
            Transform root = canvasGo.transform;

            // Crosshair
            crosshair = Panel("Crosshair", root, new Vector2(0.5f, 0.5f), Vector2.zero, new Vector2(8f, 8f), new Color(1f, 1f, 1f, 0.9f)).gameObject;
            crosshair.GetComponent<Image>().raycastTarget = false;

            // Location (top-left)
            Image loc = Panel("LocationHUD", root, new Vector2(0f, 1f), new Vector2(20f, -20f), new Vector2(620f, 46f), new Color(0f, 0f, 0f, 0.45f), new Vector2(0f, 1f));
            loc.raycastTarget = false;
            locationText = Label("Text", loc.transform, "Location:  Main Entrance", 24, Color.white, TextAnchor.MiddleLeft, FontStyle.Bold);
            Pad(locationText.rectTransform, 14f, 0f);

            // Controls hint (bottom-left)
            Image hint = Panel("ControlsHint", root, new Vector2(0f, 0f), new Vector2(20f, 20f), new Vector2(1060f, 40f), new Color(0f, 0f, 0f, 0.35f), new Vector2(0f, 0f));
            hint.raycastTarget = false;
            controlsHint = hint.gameObject;
            Text hintText = Label("Text", hint.transform, "WASD Move  ·  Mouse Look  ·  E Interact  ·  Space Jump  ·  Shift Run  ·  Esc Unlock Cursor", 20, new Color(0.9f, 0.9f, 0.9f), TextAnchor.MiddleLeft, FontStyle.Normal);
            Pad(hintText.rectTransform, 14f, 0f);

            // Paused banner (top-centre)
            Image paused = Panel("CursorUnlockedBanner", root, new Vector2(0.5f, 1f), new Vector2(0f, -20f), new Vector2(640f, 50f), new Color(0.85f, 0.45f, 0.1f, 0.9f), new Vector2(0.5f, 1f));
            paused.raycastTarget = false;
            pausedBanner = paused.gameObject;
            Label("Text", paused.transform, "Cursor unlocked  -  click in the game window to resume", 22, Color.white, TextAnchor.MiddleCenter, FontStyle.Bold);
            pausedBanner.SetActive(false);

            // Interaction prompt (bottom-centre)
            Image prompt = Panel("InteractionPrompt", root, new Vector2(0.5f, 0f), new Vector2(0f, 170f), new Vector2(560f, 96f), new Color(0f, 0f, 0f, 0.65f), new Vector2(0.5f, 0f));
            prompt.raycastTarget = false;
            promptPanel = prompt.gameObject;
            promptText = Label("Prompt", prompt.transform, "Press E to Interact", 32, Color.white, TextAnchor.MiddleCenter, FontStyle.Bold);
            SetBand(promptText.rectTransform, 0.45f, 1f);
            promptTargetText = Label("Target", prompt.transform, "", 24, Gold, TextAnchor.MiddleCenter, FontStyle.Normal);
            SetBand(promptTargetText.rectTransform, 0f, 0.5f);
            promptPanel.SetActive(false);

            // Welcome message (top-centre)
            Image welcome = Panel("WelcomeMessage", root, new Vector2(0.5f, 1f), new Vector2(0f, -90f), new Vector2(1100f, 130f), new Color(0f, 0f, 0f, 0.6f), new Vector2(0.5f, 1f));
            welcome.raycastTarget = false;
            welcomeGroup = welcome.gameObject.AddComponent<CanvasGroup>();
            welcomeGroup.blocksRaycasts = false;
            welcomeGroup.interactable = false;
            Text w1 = Label("Title", welcome.transform, "Welcome to the Virtual Shopping Complex", 46, Gold, TextAnchor.MiddleCenter, FontStyle.Bold);
            SetBand(w1.rectTransform, 0.4f, 1f);
            Text w2 = Label("Subtitle", welcome.transform, "Walk through the main entrance and explore all six shops", 24, Color.white, TextAnchor.MiddleCenter, FontStyle.Normal);
            SetBand(w2.rectTransform, 0f, 0.45f);
            welcome.gameObject.SetActive(false);

            BuildInfoPanel(root);
            BuildStartPanel(root);
            BuildExitPanel(root);
        }

        private void BuildInfoPanel(Transform root)
        {
            Image panel = Panel("InfoPanel", root, new Vector2(0.5f, 0.5f), new Vector2(0f, 20f), new Vector2(720f, 460f), PanelColor);
            infoPanel = panel.gameObject;

            infoAccentBar = Panel("AccentBar", panel.transform, new Vector2(0.5f, 1f), Vector2.zero, new Vector2(720f, 10f), Color.white, new Vector2(0.5f, 1f));
            infoHeaderText = Label("Header", panel.transform, "PRODUCT INFORMATION", 22, Color.white, TextAnchor.MiddleLeft, FontStyle.Bold);
            Place(infoHeaderText.rectTransform, new Vector2(36f, -24f), new Vector2(648f, 30f));
            infoTitleText = Label("Title", panel.transform, "NAME", 46, Color.white, TextAnchor.MiddleLeft, FontStyle.Bold);
            Place(infoTitleText.rectTransform, new Vector2(36f, -58f), new Vector2(648f, 62f));
            infoSubtitleText = Label("Subtitle", panel.transform, "Price", 30, Gold, TextAnchor.MiddleLeft, FontStyle.Bold);
            Place(infoSubtitleText.rectTransform, new Vector2(36f, -124f), new Vector2(648f, 44f));
            infoBodyText = Label("Description", panel.transform, "Description", 26, new Color(0.88f, 0.9f, 0.94f), TextAnchor.UpperLeft, FontStyle.Normal);
            Place(infoBodyText.rectTransform, new Vector2(36f, -182f), new Vector2(648f, 180f));
            infoBodyText.resizeTextForBestFit = true;
            infoBodyText.resizeTextMinSize = 16;
            infoBodyText.resizeTextMaxSize = 26;

            Text closeHint = Label("CloseHint", panel.transform, "Press E or Esc to close", 20, new Color(0.6f, 0.63f, 0.7f), TextAnchor.MiddleLeft, FontStyle.Italic);
            Place(closeHint.rectTransform, new Vector2(36f, -390f), new Vector2(360f, 40f));
            infoCloseButton = CreateButton("CloseButton", panel.transform, "CLOSE", new Vector2(1f, 0f), new Vector2(-30f, 26f), new Vector2(190f, 58f), new Color(0.8f, 0.22f, 0.22f), new Vector2(1f, 0f));
            infoPanel.SetActive(false);
        }

        private void BuildStartPanel(Transform root)
        {
            Image panel = Panel("StartPanel", root, new Vector2(0.5f, 0.5f), Vector2.zero, new Vector2(940f, 680f), PanelColor);
            startPanel = panel.gameObject;
            Panel("AccentBar", panel.transform, new Vector2(0.5f, 1f), Vector2.zero, new Vector2(940f, 10f), Gold, new Vector2(0.5f, 1f));

            Text title = Label("Title", panel.transform, "VIRTUAL SHOPPING COMPLEX", 58, Gold, TextAnchor.MiddleCenter, FontStyle.Bold);
            Place(title.rectTransform, new Vector2(20f, -36f), new Vector2(900f, 76f));
            Text sub = Label("Subtitle", panel.transform, "AR/VR Project  -  First-Person Desktop Demo", 26, new Color(0.8f, 0.83f, 0.9f), TextAnchor.MiddleCenter, FontStyle.Normal);
            Place(sub.rectTransform, new Vector2(20f, -112f), new Vector2(900f, 40f));

            Text controlsTitle = Label("ControlsTitle", panel.transform, "CONTROLS:", 32, Color.white, TextAnchor.MiddleCenter, FontStyle.Bold);
            Place(controlsTitle.rectTransform, new Vector2(20f, -176f), new Vector2(900f, 46f));

            const string keys = "WASD\nMouse\nE\nSpace\nShift\nESC";
            const string actions = "Move\nLook Around\nInteract\nJump\nRun\nUnlock Cursor  (click to lock again)";
            Text keyText = Label("Keys", panel.transform, keys, 28, Gold, TextAnchor.UpperRight, FontStyle.Bold);
            Place(keyText.rectTransform, new Vector2(120f, -232f), new Vector2(250f, 250f));
            keyText.lineSpacing = 1.15f;
            Text actionText = Label("Actions", panel.transform, actions, 28, Color.white, TextAnchor.UpperLeft, FontStyle.Normal);
            Place(actionText.rectTransform, new Vector2(400f, -232f), new Vector2(500f, 250f));
            actionText.lineSpacing = 1.15f;
            Text dash = Label("Dashes", panel.transform, "-\n-\n-\n-\n-\n-", 28, new Color(0.6f, 0.6f, 0.65f), TextAnchor.UpperCenter, FontStyle.Normal);
            Place(dash.rectTransform, new Vector2(370f, -232f), new Vector2(30f, 250f));
            dash.lineSpacing = 1.15f;

            startButton = CreateButton("StartButton", panel.transform, "START TOUR", new Vector2(0.5f, 0f), new Vector2(-110f, 60f), new Vector2(320f, 74f), new Color(0.18f, 0.62f, 0.32f), new Vector2(0.5f, 0f));
            startQuitButton = CreateButton("QuitButton", panel.transform, "QUIT", new Vector2(0.5f, 0f), new Vector2(170f, 60f), new Vector2(200f, 74f), new Color(0.35f, 0.37f, 0.42f), new Vector2(0.5f, 0f));
            Text enterHint = Label("EnterHint", panel.transform, "or press Enter to start", 20, new Color(0.6f, 0.63f, 0.7f), TextAnchor.MiddleCenter, FontStyle.Italic);
            Place(enterHint.rectTransform, new Vector2(20f, -636f), new Vector2(900f, 30f));
            startPanel.SetActive(false);
        }

        private void BuildExitPanel(Transform root)
        {
            Image panel = Panel("ExitPanel", root, new Vector2(0.5f, 0.5f), Vector2.zero, new Vector2(820f, 400f), PanelColor);
            exitPanel = panel.gameObject;
            Panel("AccentBar", panel.transform, new Vector2(0.5f, 1f), Vector2.zero, new Vector2(820f, 10f), new Color(0.2f, 0.75f, 0.35f), new Vector2(0.5f, 1f));

            Text title = Label("Title", panel.transform, "Thank you for visiting!", 48, Gold, TextAnchor.MiddleCenter, FontStyle.Bold);
            Place(title.rectTransform, new Vector2(20f, -40f), new Vector2(780f, 70f));
            Text body = Label("Body", panel.transform,
                "You have exited the Virtual Shopping Complex.\nWe hope you enjoyed exploring all six shops.",
                26, Color.white, TextAnchor.MiddleCenter, FontStyle.Normal);
            Place(body.rectTransform, new Vector2(20f, -120f), new Vector2(780f, 110f));

            exitContinueButton = CreateButton("ContinueButton", panel.transform, "CONTINUE EXPLORING", new Vector2(0.5f, 0f), new Vector2(-235f, 50f), new Vector2(320f, 66f), new Color(0.18f, 0.5f, 0.85f), new Vector2(0.5f, 0f));
            exitRestartButton = CreateButton("RestartButton", panel.transform, "RESTART TOUR", new Vector2(0.5f, 0f), new Vector2(85f, 50f), new Vector2(250f, 66f), new Color(0.18f, 0.62f, 0.32f), new Vector2(0.5f, 0f));
            exitQuitButton = CreateButton("QuitButton", panel.transform, "QUIT", new Vector2(0.5f, 0f), new Vector2(305f, 50f), new Vector2(160f, 66f), new Color(0.35f, 0.37f, 0.42f), new Vector2(0.5f, 0f));
            exitPanel.SetActive(false);
        }

        // Small UI factory helpers -------------------------------------------------------------

        private static Image Panel(string name, Transform parent, Vector2 anchor, Vector2 position, Vector2 size, Color color, Vector2? pivot = null)
        {
            var go = new GameObject(name, typeof(RectTransform));
            go.transform.SetParent(parent, false);
            var rt = (RectTransform)go.transform;
            rt.anchorMin = anchor;
            rt.anchorMax = anchor;
            rt.pivot = pivot ?? new Vector2(0.5f, 0.5f);
            rt.anchoredPosition = position;
            rt.sizeDelta = size;
            var image = go.AddComponent<Image>();
            image.color = color;
            return image;
        }

        /// <summary>Text that fills its parent.</summary>
        private static Text Label(string name, Transform parent, string text, int size, Color color, TextAnchor align, FontStyle style)
        {
            var go = new GameObject(name, typeof(RectTransform));
            go.transform.SetParent(parent, false);
            MallAssets.Stretch((RectTransform)go.transform);
            var t = go.AddComponent<Text>();
            t.font = MallAssets.Font;
            t.text = text;
            t.fontSize = size;
            t.color = color;
            t.alignment = align;
            t.fontStyle = style;
            t.supportRichText = true;
            t.horizontalOverflow = HorizontalWrapMode.Wrap;
            t.verticalOverflow = VerticalWrapMode.Overflow;
            t.raycastTarget = false;
            return t;
        }

        /// <summary>Positions a rect from its parent's top-left corner.</summary>
        private static void Place(RectTransform rt, Vector2 topLeftOffset, Vector2 size)
        {
            rt.anchorMin = new Vector2(0f, 1f);
            rt.anchorMax = new Vector2(0f, 1f);
            rt.pivot = new Vector2(0f, 1f);
            rt.anchoredPosition = topLeftOffset;
            rt.sizeDelta = size;
        }

        /// <summary>Stretches horizontally and occupies a vertical band (0 = bottom, 1 = top) of the parent.</summary>
        private static void SetBand(RectTransform rt, float yMin, float yMax)
        {
            rt.anchorMin = new Vector2(0f, yMin);
            rt.anchorMax = new Vector2(1f, yMax);
            rt.offsetMin = Vector2.zero;
            rt.offsetMax = Vector2.zero;
        }

        private static void Pad(RectTransform rt, float x, float y)
        {
            rt.offsetMin = new Vector2(x, y);
            rt.offsetMax = new Vector2(-x, -y);
        }

        private static Button CreateButton(string name, Transform parent, string label, Vector2 anchor, Vector2 position, Vector2 size, Color color, Vector2 pivot)
        {
            Image image = Panel(name, parent, anchor, position, size, color, pivot);
            var button = image.gameObject.AddComponent<Button>();
            button.targetGraphic = image;
            Label("Label", image.transform, label, 26, Color.white, TextAnchor.MiddleCenter, FontStyle.Bold);
            return button;
        }
    }
}
