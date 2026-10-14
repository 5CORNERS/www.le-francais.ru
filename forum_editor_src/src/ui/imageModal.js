// Image dialog on the shared editor modal (markup from toolbar.js). Body form
// and copy are ported from legacy openImageModal (forum-editor-legacy.js:1771-1831).

export const IMAGE_MODAL_TITLE = 'Вставить изображение';

const BODY_HTML = [
  '<div class="form-group mb-2">',
      '<label for="forum-modal-img-url">URL изображения</label>',
      '<input type="text" id="forum-modal-img-url" class="form-control form-control-sm" placeholder="https://example.com/image.jpg">',
  '</div>',
  '<div class="form-group mb-3">',
      '<label for="forum-modal-img-title">Подпись / заголовок (title & alt)</label>',
      '<input type="text" id="forum-modal-img-title" class="form-control form-control-sm" placeholder="Описание изображения (необязательно)">',
  '</div>',
  '<div class="text-center my-2">',
      '<span class="text-muted small">— или —</span>',
  '</div>',
  '<div class="text-center mt-2">',
      '<button type="button" class="btn btn-outline-primary btn-sm forum-modal-choose-file-btn">',
          '<i class="fa fa-folder-open-o mr-1"></i> Выбрать файл на устройстве',
      '</button>',
  '</div>'
].join('');

// Closes the request currently shown on a modal (one at a time per modal).
const active = new WeakMap();

/**
 * Shows the image dialog. Resolves `{url, title}` (trimmed) on submit, or null
 * on cancel, close, Esc, a click on the overlay or "Выбрать файл на
 * устройстве"; the latter also calls `options.onChooseFile()` synchronously
 * (inside the click, so the browser lets it open the file picker).
 * Submitting without a URL keeps the dialog open with the URL field focused.
 */
export function openImageModal(modalDom, options) {
  const opts = options || {};
  const previous = active.get(modalDom);
  if (previous) previous(null);

  return new Promise(function (resolve) {
    const overlay = modalDom.overlay;
    modalDom.title.textContent = IMAGE_MODAL_TITLE;
    modalDom.body.innerHTML = BODY_HTML;
    const urlInput = modalDom.body.querySelector('#forum-modal-img-url');
    const titleInput = modalDom.body.querySelector('#forum-modal-img-title');

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
      if (!url) {
        urlInput.focus();
        return;
      }
      finish({ url: url, title: titleInput.value.trim() });
    }

    function onClick(e) {
      const t = e.target;
      if (t === overlay) {
        finish(null);
        return;
      }
      if (t.closest('.forum-modal-choose-file-btn')) {
        e.preventDefault();
        finish(null);
        if (typeof opts.onChooseFile === 'function') opts.onChooseFile();
      } else if (t.closest('.forum-editor-modal-close, .forum-editor-modal-cancel')) {
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
      if (!done) urlInput.focus();
    }, 50);
  });
}
