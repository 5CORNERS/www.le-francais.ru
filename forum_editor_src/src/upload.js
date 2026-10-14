// Image upload: paste, drag-and-drop and the toolbar file picker.
// Server endpoint: forum/views.py upload_image_ajax (form key 'file').

import { Plugin, PluginKey } from '@tiptap/pm/state';

export const ACCEPTED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
export const MAX_UPLOAD_SIZE = 10 * 1024 * 1024;
export const UPLOAD_ERROR = 'Ошибка при загрузке изображения.';
export const UPLOAD_PENDING_CONFIRM = 'Изображение ещё загружается. Отправить сообщение без него?';

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
 * Inserts block-level Markdown (an image) after the textarea selection, on
 * its own paragraph: blank lines are added before and after as needed. The
 * caret goes after the inserted text; `input` is dispatched.
 */
export function insertBlockMarkdown(textarea, md) {
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

/**
 * Wires paste, drop and the hidden file input of `dom` to uploads into the
 * editor `api`. Returns `{ openFilePicker, uploadFile, pendingCount, destroy }`.
 */
export function bindUploadHandlers(api, dom) {
  const textarea = api.textarea;
  let pending = 0;
  let queue = Promise.resolve();
  let dragCounter = 0;
  let destroyed = false;
  // uploadId -> true while uploading; finished uploads map to their final attrs.
  const pendingIds = Object.create(null);
  const finished = Object.create(null);
  let anyUpload = false;
  const pluginKey = new PluginKey('forumUploadPlaceholders');

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

  // Undo/redo of neighbouring edits can still bring back a placeholder whose
  // upload has settled (history steps are not rebased onto the quiet ones).
  // After every doc change, such placeholders become the final image, or are
  // removed when the upload failed.
  const placeholderGuard = new Plugin({
    key: pluginKey,
    appendTransaction(transactions, oldState, newState) {
      if (!anyUpload || !transactions.some((t) => t.docChanged)) return null;
      const stale = [];
      newState.doc.descendants((node, pos) => {
        if (node.type.name === 'image' && node.attrs.uploadId !== null && !pendingIds[node.attrs.uploadId]) {
          stale.push({ node: node, pos: pos });
        }
        return true;
      });
      if (!stale.length) return null;
      const tr = newState.tr;
      // Back to front, so earlier positions stay valid.
      for (let i = stale.length - 1; i >= 0; i--) {
        const item = stale[i];
        const final = finished[item.node.attrs.uploadId];
        if (final) tr.setNodeMarkup(item.pos, null, Object.assign({}, item.node.attrs, final));
        else tr.delete(item.pos, item.pos + item.node.nodeSize);
      }
      tr.setMeta('addToHistory', false);
      return tr;
    },
  });
  api.tiptap.registerPlugin(placeholderGuard);

  function insertPlaceholder(uploadId, blobUrl, filename) {
    const editor = api.tiptap;
    // Selected content is removed in a normal (undoable) step, like a paste.
    if (!editor.state.selection.empty) editor.view.dispatch(editor.state.tr.deleteSelection());
    const node = editor.schema.nodes.image.create({ src: blobUrl, alt: 'Загрузка ' + filename + '...', uploadId: uploadId });
    dispatchQuiet(editor.state.tr.replaceSelectionWith(node, false).scrollIntoView());
  }

  function onUploaded(uploadId, result) {
    if (api.currentMode === 'visual') {
      const editor = api.tiptap;
      const attrs = finished[uploadId];
      const found = findPlaceholder(uploadId);
      if (found) {
        dispatchQuiet(editor.state.tr.setNodeMarkup(found.pos, null, Object.assign({}, found.node.attrs, attrs)));
      } else {
        // The placeholder was dropped (mode switch, reload, or deleted by the
        // author): append the image. This is a new edit with no placeholder
        // behind it, so it goes into the history like any other insertion and
        // can be undone.
        const tr = editor.state.tr;
        tr.insert(tr.doc.content.size, editor.schema.nodes.image.create(attrs));
        editor.view.dispatch(tr);
      }
    } else {
      insertBlockMarkdown(textarea, '![' + result.filename + '](' + result.url + ')');
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

  /**
   * Uploads one file. Returns a promise for this file's own upload: it resolves
   * with `{url, filename}` once the upload has settled successfully, or with
   * null when it failed or was rejected up front (the error has been shown).
   * It never rejects.
   */
  function uploadFile(file) {
    const filename = file.name || 'image.jpg';
    if (file.size > MAX_UPLOAD_SIZE) {
      window.alert('Файл «' + filename + '» превышает 10 МБ. Пожалуйста, сожмите изображение или используйте сторонний сервис.');
      return Promise.resolve(null);
    }
    const uploadId = 'upload_' + Math.random().toString(36).slice(2, 11);
    pendingIds[uploadId] = true;
    anyUpload = true;
    let blobUrl = null;
    if (api.currentMode === 'visual') {
      blobUrl = URL.createObjectURL(file);
      insertPlaceholder(uploadId, blobUrl, filename);
    }
    pending++;
    updateProgress();

    function settle(handler, value) {
      delete pendingIds[uploadId];
      pending--;
      updateProgress();
      if (blobUrl) URL.revokeObjectURL(blobUrl);
      if (destroyed) return;
      try {
        handler(uploadId, value);
      } catch (e) {
        // One broken completion must not stall the uploads queued after it.
        console.error('forum-editor: image upload handler failed', e);
      }
    }

    // Uploads run one at a time; each file already has its placeholder.
    const done = queue.then(() => uploadImage(file, api.uploadUrl).then(
      (result) => {
        finished[uploadId] = { src: result.url, alt: result.filename, uploadId: null };
        settle(onUploaded, result);
        return result;
      },
      (err) => {
        settle(onFailed, err);
        return null;
      }
    ));
    queue = done;
    return done;
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
    if (!api.tiptap.isDestroyed) api.tiptap.unregisterPlugin(pluginKey);
    dom.fileInput.removeEventListener('change', onFileChange);
    wrapper.removeEventListener('dragenter', onDragEnter, true);
    wrapper.removeEventListener('dragover', onDragOver, true);
    wrapper.removeEventListener('dragleave', onDragLeave, true);
    wrapper.removeEventListener('drop', onDrop, true);
    wrapper.removeEventListener('paste', onPaste, true);
  }

  return {
    openFilePicker: openFilePicker,
    uploadFile: uploadFile,
    /** Number of uploads not yet settled. */
    pendingCount: function () { return pending; },
    destroy: destroy,
  };
}
