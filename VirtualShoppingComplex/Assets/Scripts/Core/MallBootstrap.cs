using UnityEngine;

namespace VirtualMall
{
    /// <summary>
    /// The only component the scene needs. On Play it generates the whole shopping complex,
    /// the player and the UI (unless they were already baked into the scene with
    /// the "Virtual Mall > Bake Mall Into Scene" editor menu).
    /// </summary>
    [DisallowMultipleComponent]
    public class MallBootstrap : MonoBehaviour
    {
        private void Awake()
        {
            if (FindAnyObjectByType<PlayerController>() == null)
            {
                MallBuilder.BuildAll(transform);
            }
            else
            {
                // Mall was baked into the scene in the editor: only (re)apply lighting settings.
                MallBuilder.ApplyRenderSettings();
            }
        }
    }
}
