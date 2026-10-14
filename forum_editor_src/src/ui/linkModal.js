// Link dialog on the shared editor modal (markup from toolbar.js). Body form
// and copy are ported from legacy openLinkModal (forum-editor-legacy.js:1704-1770).

export const LINK_MODAL_TITLE = 'Вставить ссылку';

const BODY_HTML = [
  '<div class="form-group mb-2">',
      '<label for="forum-modal-link-url">URL ссылки</label>',
      '<input type="text" id="forum-modal-link-url" class="form-control form-control-sm" placeholder="https://" value="https://">',
  '</div>',
  '<div class="form-group mb-0">',
      '<label for="forum-modal-link-text">Текст ссылки</label>',
      '<input type="text" id="forum-modal-link-text" class="form-control form-control-sm" placeholder="Отображаемый текст">',
  '</div>'
].join('');

// Closes the request currently shown on a modal (one at a time per modal).
const active = new WeakMap();

/**
 * Shows the link dialog prefilled with `text` (and `url`, default
 * `https://`). Resolves `{text, url}` (trimmed) on submit, or null on cancel,
 * close, Esc or a click on the overlay. Submitting without a URL keeps the
 * dialog open with the URL field focused.
 */
export function openLinkModal(modalDom, initial) {
  const init = initial || {};
  const previous = active.get(modalDom);
  if (previous) previous(null);

  return new Promise(function (resolve) {
    const overlay = modalDom.overlay;
    modalDom.title.textContent = LINK_MODAL_TITLE;
    modalDom.body.innerHTML = BODY_HTML;
    const urlInput = modalDom.body.querySelector('#forum-modal-link-url');
    const textInput = modalDom.body.querySelector('#forum-modal-link-text');
    if (init.url) urlInput.value = init.url;
    if (init.text) textInput.value = init.text;

    let done = false;
    function finish(value) {
      if (done) return;
      done = true;
      overlay.classList.add('d-none');
      overlay.removeEventListener('click', onClick);
      overlay.removeEventListener('keydown', onKeydown);
      active.delete(modalDom);
      resolve(value);
    }

    function submit() {
      const url = urlInput.value.trim();
      const text = textInput.value.trim();
      if (!url || url === 'https://' || url === 'http://') {
        urlInput.focus();
        return;
      }
      finish({ text: text, url: url });
    }

    function onClick(e) {
      const t = e.target;
      if (t === overlay) {
        finish(null);
        return;
      }
      if (t.closest('.forum-editor-modal-close, .forum-editor-modal-cancel')) {
        e.preventDefault();
        finish(null);
      } else if (t.closest('.forum-editor-modal-submit')) {
        e.preventDefault();
        submit();
      }
    }

    function onKeydown(e) {
      if (e.key === 'Escape' || e.keyCode === 27) {
        e.preventDefault();
        finish(null);
      } else if ((e.key === 'Enter' || e.keyCode === 13) && e.target.tagName === 'INPUT') {
        e.preventDefault();
        submit();
      }
    }

    overlay.addEventListener('click', onClick);
    overlay.addEventListener('keydown', onKeydown);
    active.set(modalDom, finish);
    overlay.classList.remove('d-none');

    setTimeout(function () {
      if (done) return;
      urlInput.focus();
      const len = urlInput.value.length;
      if (urlInput.setSelectionRange) urlInput.setSelectionRange(len, len);
    }, 50);
  });
}
