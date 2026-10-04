using UnityEngine;

namespace VirtualMall
{
    /// <summary>
    /// First-person mouse look. Put on the camera (child of the player).
    /// Horizontal mouse turns the player body, vertical mouse tilts the camera (clamped).
    /// </summary>
    [DisallowMultipleComponent]
    public class MouseLook : MonoBehaviour
    {
        [Tooltip("The player root that turns left/right. Defaults to this object's parent.")]
        [SerializeField] private Transform playerBody;
        [SerializeField, Range(0.1f, 10f)] private float sensitivity = 2f;
        [Tooltip("Small smoothing time in seconds. 0 = raw input.")]
        [SerializeField, Range(0f, 0.15f)] private float smoothing = 0.03f;
        [SerializeField] private float minPitch = -85f;
        [SerializeField] private float maxPitch = 85f;
        [SerializeField] private bool invertY = false;

        [Tooltip("Largest mouse movement accepted in one frame (filters the jump that happens when the cursor gets locked).")]
        [SerializeField] private float maxDeltaPerFrame = 25f;

        private float pitch;
        private Vector2 smoothedDelta;
        private bool wasLocked;
        private int ignoreFrames;

        private void Start()
        {
            if (playerBody == null) playerBody = transform.parent;
            ResetPitch();
        }

        private void Update()
        {
            // When the cursor is (re)locked, the OS reports one big jump of mouse movement.
            // Ignore the first frames after locking so the camera does not snap to the floor.
            bool locked = Cursor.lockState == CursorLockMode.Locked;
            if (locked && !wasLocked) ignoreFrames = 3;
            wasLocked = locked;

            Vector2 input = InputReader.Look;
            if (ignoreFrames > 0)
            {
                ignoreFrames--;
                input = Vector2.zero;
            }
            input = Vector2.ClampMagnitude(input, maxDeltaPerFrame);
            Vector2 raw = input * sensitivity;

            if (smoothing > 0f)
            {
                float t = 1f - Mathf.Exp(-Time.unscaledDeltaTime / smoothing);
                smoothedDelta = Vector2.Lerp(smoothedDelta, raw, t);
            }
            else
            {
                smoothedDelta = raw;
            }

            pitch += invertY ? smoothedDelta.y : -smoothedDelta.y;
            pitch = Mathf.Clamp(pitch, minPitch, maxPitch);
            transform.localRotation = Quaternion.Euler(pitch, 0f, 0f);

            if (playerBody != null) playerBody.Rotate(0f, smoothedDelta.x, 0f, Space.Self);
        }

        /// <summary>Looks straight ahead (used after teleporting).</summary>
        public void ResetPitch()
        {
            pitch = 0f;
            smoothedDelta = Vector2.zero;
            transform.localRotation = Quaternion.identity;
        }
    }
}
