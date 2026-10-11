// Image upload: paste, drag-and-drop and the toolbar file picker.
// Server endpoint: forum/views.py upload_image_ajax (form key 'file').

export const ACCEPTED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
export const MAX_UPLOAD_SIZE = 10 * 1024 * 1024;
export const UPLOAD_ERROR = 'Ошибка при загрузке изображения.';

/** Django CSRF token: the hidden form field first, then the `csrftoken` cookie. */
export function getCsrfToken(doc = document) {
  const input = doc.querySelector('input[name="csrfmiddlewaretoken"]');
  if (input && input.value) return input.value;
  const match = (doc.cookie || '').match(/(?:^|;\s*)csrftoken=([^;]+)/);
  return match ? match[1] : '';
}

/** Uploads `file`; resolves with `{url, filename}` or rejects with the server's message. */
export function uploadImage(file, uploadUrl) {
  const token = getCsrfToken();
  const body = new FormData();
  body.append('file', file);
  body.append('csrfmiddlewaretoken', token);
  return fetch(uploadUrl, {
    method: 'POST',
    credentials: 'same-origin',
    headers: { 'X-CSRFToken': token },
    body: body,
  })
    .then(
      (res) => res.json().catch(() => null),
      () => { throw new Error(UPLOAD_ERROR); }
    )
    .then((json) => {
      if (json && json.success && json.url) {
        return { url: json.url, filename: json.filename || file.name || 'image.jpg' };
      }
      throw new Error((json && json.error) || UPLOAD_ERROR);
    });
}

function isAcceptedImage(file) {
  return !!file && ACCEPTED_IMAGE_TYPES.indexOf(file.type) !== -1;
}

function hasFiles(dataTransfer) {
  return !!dataTransfer && !!dataTransfer.types && Array.prototype.indexOf.call(dataTransfer.types, 'Files') !== -1;
}

function imageFilesFromClipboard(data) {
  const out = [];
  if (!data) return out;
  if (data.items && data.items.length) {
    for (let i = 0; i < data.items.length; i++) {
      const item = data.items[i];
      if (item.kind && item.kind !== 'file') continue;
      if (ACCEPTED_IMAGE_TYPES.indexOf(item.type) === -1) continue;
      const f = item.getAsFile();
      if (f) out.push(f);
    }
    return out;
  }
  const files = data.files || [];
  for (let i = 0; i < files.length; i++) {
    if (isAcceptedImage(files[i])) out.push(files[i]);
  }
  return out;
}

function countNewlines(text, fromEnd) {
  let n = 0;
  while (n < text.length && text.charAt(fromEnd ? text.length - 1 - n : n) === '\n') n++;
  return n;
}

function newlines(n) {
  return n > 0 ? '\n'.repeat(n) : '';
}

/**
 * Wires paste, drop and the hidden file input of `dom` to uploads into the
 * editor `api`. Returns `{ openFilePicker, uploadFile, destroy }`.
 */
export function bindUploadHandlers(api, dom) {
  const textarea = api.textarea;
  let pending = 0;
  let queue = Promise.resolve();
  let dragCounter = 0;
  let destroyed = false;

  function updateProgress() {
    dom.uploadProgress.classList.toggle('d-none', pending === 0);
  }

  function findPlaceholder(uploadId) {
    let found = null;
    api.tiptap.state.doc.descendants((node, pos) => {
      if (found) return false;
      if (node.type.name === 'image' && node.attrs.uploadId === uploadId) {
        found = { node: node, pos: pos };
        return false;
      }
      return true;
    });
    return found;
  }

  // Placeholder steps stay out of the undo history: undoing back to a
  // placeholder would resurrect a revoked blob URL.
  function dispatchQuiet(tr) {
    tr.setMeta('addToHistory', false);
    api.tiptap.view.dispatch(tr);
  }

  function insertPlaceholder(uploadId, blobUrl, filename) {
    const editor = api.tiptap;
    const node = editor.schema.nodes.image.create({ src: blobUrl, alt: 'Загрузка ' + filename + '...', uploadId: uploadId });
    dispatchQuiet(editor.state.tr.replaceSelectionWith(node, false).scrollIntoView());
  }

  function insertMarkdownAtCaret(md) {
    const val = textarea.value;
    let pos = textarea.selectionEnd;
    if (typeof pos !== 'number' || pos < 0 || pos > val.length) pos = val.length;
    const before = val.slice(0, pos);
    const after = val.slice(pos);
    const prefix = before.length ? newlines(2 - countNewlines(before, true)) : '';
    const suffix = newlines(2 - countNewlines(after, false));
    textarea.setRangeText(prefix + md + suffix, pos, pos, 'end');
    textarea.dispatchEvent(new Event('input', { bubbles: true }));
  }

  function onUploaded(uploadId, result) {
    if (api.currentMode === 'visual') {
      const editor = api.tiptap;
      const attrs = { src: result.url, alt: result.filename, uploadId: null };
      const found = findPlaceholder(uploadId);
      if (found) {
        dispatchQuiet(editor.state.tr.setNodeMarkup(found.pos, null, Object.assign({}, found.node.attrs, attrs)));
      } else {
        // The placeholder was dropped (mode switch or reload): append the image.
        const tr = editor.state.tr;
        tr.insert(tr.doc.content.size, editor.schema.nodes.image.create(attrs));
        editor.view.dispatch(tr);
      }
    } else {
      insertMarkdownAtCaret('![' + result.filename + '](' + result.url + ')');
    }
    api.updateCharCounter();
  }

  function onFailed(uploadId, err) {
    if (api.currentMode === 'visual') {
      const found = findPlaceholder(uploadId);
      if (found) dispatchQuiet(api.tiptap.state.tr.delete(found.pos, found.pos + found.node.nodeSize));
    }
    window.alert((err && err.message) || UPLOAD_ERROR);
    api.updateCharCounter();
  }

  function uploadFile(file) {
    const filename = file.name || 'image.jpg';
    if (file.size > MAX_UPLOAD_SIZE) {
      window.alert('Файл «' + filename + '» превышает 10 МБ. Пожалуйста, сожмите изображение или используйте сторонний сервис.');
      return Promise.resolve();
    }
    const uploadId = 'upload_' + Math.random().toString(36).slice(2, 11);
    let blobUrl = null;
    if (api.currentMode === 'visual') {
      blobUrl = URL.createObjectURL(file);
      insertPlaceholder(uploadId, blobUrl, filename);
    }
    pending++;
    updateProgress();

    function settle(handler, value) {
      pending--;
      updateProgress();
      if (blobUrl) URL.revokeObjectURL(blobUrl);
      if (!destroyed) handler(uploadId, value);
    }

    // Uploads run one at a time; each file already has its placeholder.
    queue = queue.then(() => uploadImage(file, api.uploadUrl).then(
      (result) => settle(onUploaded, result),
      (err) => settle(onFailed, err)
    ));
    return queue;
  }

  function uploadAll(files) {
    for (let i = 0; i < files.length; i++) uploadFile(files[i]);
  }

  function openFilePicker() {
    dom.fileInput.click();
  }

  const onFileChange = () => {
    const files = dom.fileInput.files;
    if (files && files.length) {
      uploadAll(Array.prototype.slice.call(files));
      dom.fileInput.value = '';
    }
  };

  const onDragEnter = (e) => {
    if (!hasFiles(e.dataTransfer)) return;
    e.preventDefault();
    dragCounter++;
    dom.dropOverlay.classList.remove('d-none');
  };
  const onDragOver = (e) => {
    if (!hasFiles(e.dataTransfer)) return;
    e.preventDefault();
  };
  const onDragLeave = (e) => {
    if (!hasFiles(e.dataTransfer)) return;
    dragCounter--;
    if (dragCounter <= 0) {
      dragCounter = 0;
      dom.dropOverlay.classList.add('d-none');
    }
  };
  // Capture phase so ProseMirror's own drop/paste handling sees defaultPrevented.
  const onDrop = (e) => {
    if (!hasFiles(e.dataTransfer)) return;
    // A file drop is never left to the browser (it would navigate to the file).
    e.preventDefault();
    e.stopPropagation();
    dragCounter = 0;
    dom.dropOverlay.classList.add('d-none');
    const files = e.dataTransfer.files || [];
    const images = [];
    for (let i = 0; i < files.length; i++) {
      if (isAcceptedImage(files[i])) images.push(files[i]);
    }
    uploadAll(images);
  };
  const onPaste = (e) => {
    const images = imageFilesFromClipboard(e.clipboardData);
    if (!images.length) return;
    e.preventDefault();
    uploadAll(images);
  };

  const wrapper = dom.wrapper;
  dom.fileInput.addEventListener('change', onFileChange);
  wrapper.addEventListener('dragenter', onDragEnter, true);
  wrapper.addEventListener('dragover', onDragOver, true);
  wrapper.addEventListener('dragleave', onDragLeave, true);
  wrapper.addEventListener('drop', onDrop, true);
  wrapper.addEventListener('paste', onPaste, true);

  function destroy() {
    destroyed = true;
    dom.fileInput.removeEventListener('change', onFileChange);
    wrapper.removeEventListener('dragenter', onDragEnter, true);
    wrapper.removeEventListener('dragover', onDragOver, true);
    wrapper.removeEventListener('dragleave', onDragLeave, true);
    wrapper.removeEventListener('drop', onDrop, true);
    wrapper.removeEventListener('paste', onPaste, true);
  }

  return { openFilePicker: openFilePicker, uploadFile: uploadFile, destroy: destroy };
}
