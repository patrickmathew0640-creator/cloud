using UnityEngine;

namespace VirtualMall
{
    /// <summary>
    /// First-person movement using Unity's CharacterController:
    /// WASD / arrow keys to move, Shift to run, Space to jump, gravity and wall collision.
    /// </summary>
    [RequireComponent(typeof(CharacterController))]
    [DisallowMultipleComponent]
    public class PlayerController : MonoBehaviour
    {
        [Header("Movement")]
        [SerializeField] private float walkSpeed = 4f;
        [SerializeField] private float runSpeed = 7f;
        [Tooltip("How quickly the player reaches the target speed (m/s²). Higher = snappier.")]
        [SerializeField] private float acceleration = 25f;

        [Header("Jumping & Gravity")]
        [SerializeField] private float jumpHeight = 1.1f;
        [SerializeField] private float gravity = -20f;
        [Tooltip("If the player ever falls below this height they are returned to the spawn point.")]
        [SerializeField] private float fallResetHeight = -15f;

        private CharacterController controller;
        private MouseLook mouseLook;
        private Vector3 planarVelocity;
        private float verticalVelocity;
        private Vector3 spawnPosition;
        private Quaternion spawnRotation;

        private void Awake()
        {
            controller = GetComponent<CharacterController>();
            spawnPosition = transform.position;
            spawnRotation = transform.rotation;
        }

        private void Start()
        {
            mouseLook = GetComponentInChildren<MouseLook>();
        }

        private void Update()
        {
            if (controller == null || !controller.enabled) return;

            float dt = Time.deltaTime;
            bool grounded = controller.isGrounded;
            if (grounded && verticalVelocity < 0f) verticalVelocity = -2f; // keep snapped to the floor

            Vector2 input = InputReader.Move;
            float speed = InputReader.SprintHeld ? runSpeed : walkSpeed;
            Vector3 targetVelocity = (transform.right * input.x + transform.forward * input.y) * speed;
            planarVelocity = Vector3.MoveTowards(planarVelocity, targetVelocity, acceleration * dt);

            if (grounded && InputReader.JumpPressed)
            {
                verticalVelocity = Mathf.Sqrt(jumpHeight * -2f * gravity);
            }
            verticalVelocity += gravity * dt;

            CollisionFlags flags = controller.Move((planarVelocity + Vector3.up * verticalVelocity) * dt);
            if ((flags & CollisionFlags.Above) != 0 && verticalVelocity > 0f) verticalVelocity = 0f;

            if (transform.position.y < fallResetHeight) ResetToSpawn();
        }

        /// <summary>Moves the player instantly (CharacterController must be disabled while doing so).</summary>
        public void Teleport(Vector3 position, Quaternion rotation)
        {
            if (controller == null) controller = GetComponent<CharacterController>();
            controller.enabled = false;
            transform.SetPositionAndRotation(position, Quaternion.Euler(0f, rotation.eulerAngles.y, 0f));
            controller.enabled = true;
            planarVelocity = Vector3.zero;
            verticalVelocity = 0f;

            if (mouseLook == null) mouseLook = GetComponentInChildren<MouseLook>();
            if (mouseLook != null) mouseLook.ResetPitch();
        }

        public void ResetToSpawn()
        {
            Teleport(spawnPosition, spawnRotation);
        }
    }
}
