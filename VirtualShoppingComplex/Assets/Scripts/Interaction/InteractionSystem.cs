using UnityEngine;

namespace VirtualMall
{
    /// <summary>
    /// Raycasts from the first-person camera (or any ray origin, e.g. a VR controller later)
    /// and lets the player press E on objects that implement <see cref="IInteractable"/>.
    /// </summary>
    public class InteractionSystem : MonoBehaviour
    {
        [Tooltip("Where the interaction ray starts. Defaults to this transform (the camera).")]
        [SerializeField] private Transform rayOrigin;
        [SerializeField] private float interactDistance = 3.5f;
        [Tooltip("Extra forgiveness radius when the centre ray misses small products.")]
        [SerializeField] private float aimAssistRadius = 0.12f;
        [Tooltip("Everything except the 'Ignore Raycast' layer (player + walk blockers).")]
        [SerializeField] private LayerMask interactionMask = ~(1 << MallAssets.IgnoreRaycastLayer);

        private IInteractable current;

        public IInteractable Current => current;

        private void Awake()
        {
            if (rayOrigin == null) rayOrigin = transform;
        }

        private void Update()
        {
            UIManager ui = UIManager.Instance;
            bool canInteract = InputReader.GameplayEnabled && (ui == null || ui.IsPlaying);

            IInteractable target = canInteract ? FindTarget() : null;
            SetCurrent(target);

            if (ui != null)
            {
                if (current != null) ui.ShowPrompt(current.PromptText, current.TargetName);
                else ui.HidePrompt();
            }

            // AcceptsInteraction is false on the frame a panel was closed with E, so the same key
            // press does not immediately reopen it.
            if (current != null && InputReader.InteractPressed && (ui == null || ui.AcceptsInteraction))
            {
                current.Interact();
            }
        }

        private IInteractable FindTarget()
        {
            if (rayOrigin == null) return null;
            var ray = new Ray(rayOrigin.position, rayOrigin.forward);

            if (Physics.Raycast(ray, out RaycastHit hit, interactDistance, interactionMask, QueryTriggerInteraction.Ignore))
            {
                IInteractable direct = hit.collider.GetComponentInParent<IInteractable>();
                if (direct != null) return direct;
                // Something solid (a wall, a shelf board) is in front: don't reach through it.
                if (hit.distance < 0.6f) return null;
            }

            if (aimAssistRadius > 0f &&
                Physics.SphereCast(ray, aimAssistRadius, out RaycastHit sphereHit, interactDistance, interactionMask, QueryTriggerInteraction.Ignore))
            {
                return sphereHit.collider.GetComponentInParent<IInteractable>();
            }
            return null;
        }

        private void SetCurrent(IInteractable target)
        {
            if (ReferenceEquals(target, current)) return;
            if (current is Object oldObj && oldObj != null) current.SetFocused(false);
            current = target;
            current?.SetFocused(true);
        }

        private void OnDisable()
        {
            SetCurrent(null);
            if (UIManager.Instance != null) UIManager.Instance.HidePrompt();
        }
    }
}
