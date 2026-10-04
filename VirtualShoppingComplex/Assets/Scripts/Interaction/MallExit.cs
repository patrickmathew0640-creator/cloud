using UnityEngine;

namespace VirtualMall
{
    /// <summary>
    /// Exit zone outside the mall's exit door. When the player walks into it the
    /// "Thank you for visiting" screen opens. Uses a simple bounds check, so it does
    /// not depend on trigger/physics settings.
    /// </summary>
    public class MallExit : MonoBehaviour
    {
        [SerializeField] private Vector3 zoneSize = new Vector3(12f, 4f, 6f);
        [Tooltip("Where the player is placed when choosing 'Continue Exploring'.")]
        [SerializeField] private Transform returnPoint;

        private PlayerController player;
        private bool playerInside;

        public void Setup(Vector3 size, Transform returnTo)
        {
            zoneSize = size;
            returnPoint = returnTo;
        }

        private void Update()
        {
            if (player == null)
            {
                player = FindAnyObjectByType<PlayerController>();
                if (player == null) return;
            }

            var zone = new Bounds(transform.position, zoneSize);
            bool inside = zone.Contains(player.transform.position + Vector3.up * 0.9f);
            if (inside && !playerInside && UIManager.Instance != null && UIManager.Instance.IsPlaying)
            {
                UIManager.Instance.ShowExitScreen(this);
            }
            playerInside = inside;
        }

        public void ReturnPlayerInside()
        {
            if (player == null) player = FindAnyObjectByType<PlayerController>();
            if (player == null || returnPoint == null) return;
            player.Teleport(returnPoint.position, returnPoint.rotation);
            playerInside = false;
        }

        private void OnDrawGizmos()
        {
            Gizmos.color = new Color(0.1f, 0.9f, 0.3f, 0.35f);
            Gizmos.DrawCube(transform.position, zoneSize);
        }
    }
}
