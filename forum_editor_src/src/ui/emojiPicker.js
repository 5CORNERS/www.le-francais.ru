// Emoji dropdown (markup from toolbar.js; behaviour from the legacy bindings,
// forum-editor-legacy.js:1208-1239).

/**
 * Wires the emoji button, close button and items. `onPick(char)` gets the
 * Unicode character of a clicked `.forum-emoji-item`. The dropdown closes on
 * pick, outside click and Esc. Returns a function that removes the listeners.
 */
export function initEmojiPicker(emojiDom, onPick) {
  const button = emojiDom.button;
  const dropdown = emojiDom.dropdown;
  const group = button.closest('.forum-emoji-group') || button.parentNode;

  function close() {
    dropdown.classList.add('d-none');
  }

  function onButtonClick(e) {
    e.preventDefault();
    e.stopPropagation();
    dropdown.classList.toggle('d-none');
  }

  function onDropdownClick(e) {
    const closeBtn = e.target.closest('.forum-emoji-close');
    if (closeBtn) {
      e.preventDefault();
      e.stopPropagation();
      close();
      return;
    }
    const item = e.target.closest('.forum-emoji-item');
    if (!item || !dropdown.contains(item)) return;
    e.preventDefault();
    e.stopPropagation();
    close();
    onPick(item.getAttribute('data-emoji'));
  }

  function onDocumentClick(e) {
    if (!group.contains(e.target)) close();
  }

  function onDocumentKeydown(e) {
    if ((e.key === 'Escape' || e.keyCode === 27) && !dropdown.classList.contains('d-none')) close();
  }

  button.addEventListener('click', onButtonClick);
  dropdown.addEventListener('click', onDropdownClick);
  document.addEventListener('click', onDocumentClick);
  document.addEventListener('keydown', onDocumentKeydown);

  return function destroy() {
    button.removeEventListener('click', onButtonClick);
    dropdown.removeEventListener('click', onDropdownClick);
    document.removeEventListener('click', onDocumentClick);
    document.removeEventListener('keydown', onDocumentKeydown);
  };
}
