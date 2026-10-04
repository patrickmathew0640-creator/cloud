namespace VirtualMall
{
    /// <summary>
    /// Anything the player can aim at and press E on. Implemented by <see cref="InteractableProduct"/>
    /// and <see cref="ShopInteraction"/>. A VR ray interactor can call the same methods later.
    /// </summary>
    public interface IInteractable
    {
        /// <summary>Text shown in the prompt, e.g. "Press E to Interact".</summary>
        string PromptText { get; }

        /// <summary>Name shown under the prompt, e.g. "Smartphone".</summary>
        string TargetName { get; }

        void Interact();

        void SetFocused(bool focused);
    }
}
