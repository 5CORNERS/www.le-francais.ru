import { describe, test, expect, beforeEach, afterEach, vi } from 'vitest';
import { getCsrfToken, uploadImage } from '../src/upload.js';
import { TextSelection } from '@tiptap/pm/state';
import { makeEditor, destroyEditors, selectText } from './helpers.js';

const file = new File(['x'], 'a.png', { type: 'image/png' });

function deferred() {
  let resolve;
  let reject;
  const promise = new Promise((res, rej) => { resolve = res; reject = rej; });
  return { promise, resolve, reject };
}

const flush = () => new Promise((r) => setTimeout(r, 0));

function images(ed) {
  const out = [];
  ed.tiptap.state.doc.descendants((n) => {
    if (n.type.name === 'image') out.push(n.attrs);
  });
  return out;
}

function okResponse() {
  return { json: async () => ({ success: true, url: '/m/a.png', filename: 'a.png' }) };
}

function pasteEvent(files) {
  const ev = new Event('paste', { bubbles: true, cancelable: true });
  ev.clipboardData = {
    items: files.map((f) => ({ kind: 'file', type: f.type, getAsFile: () => f })),
    files: files,
    types: ['Files'],
    getData: () => '',
  };
  return ev;
}

let alertSpy;

beforeEach(() => {
  localStorage.clear();
  vi.stubGlobal('fetch', vi.fn());
  let n = 0;
  class FakeURL extends URL {}
  FakeURL.createObjectURL = vi.fn(() => 'blob:test/' + (++n));
  FakeURL.revokeObjectURL = vi.fn();
  vi.stubGlobal('URL', FakeURL);
  alertSpy = vi.fn();
  vi.stubGlobal('alert', alertSpy);
  document.body.innerHTML = '<input name="csrfmiddlewaretoken" value="F">';
});

afterEach(() => {
  destroyEditors();
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
  document.body.innerHTML = '';
  document.cookie = 'csrftoken=; expires=Thu, 01 Jan 1970 00:00:00 GMT';
});

describe('getCsrfToken / uploadImage', () => {
  test('csrf token from hidden input, falling back to cookie', () => {
    document.body.innerHTML = '<input name="csrfmiddlewaretoken" value="F">'; document.cookie = 'csrftoken=C';
    expect(getCsrfToken()).toBe('F'); document.body.innerHTML = ''; expect(getCsrfToken()).toBe('C');
  });

  test('upload sends header and form field', async () => {
    fetch.mockResolvedValue({ json: async () => ({ success: true, url: '/m/a.png', filename: 'a.png' }) });
    await uploadImage(new File(['x'], 'a.png', { type: 'image/png' }), '/forum/upload-image/');
    const [url, opts] = fetch.mock.calls[0];
    expect(url).toBe('/forum/upload-image/'); expect(opts.headers['X-CSRFToken']).toBe('F');
    expect(opts.body.get('csrfmiddlewaretoken')).toBe('F'); expect(opts.credentials).toBe('same-origin');
    expect(opts.body.get('file')).toBeInstanceOf(File); // key 'file': forum/views.py:142, legacy forum-editor.js:2401
  });

  test('server error rejects with its message', async () => {
    fetch.mockResolvedValue({ json: async () => ({ success: false, error: 'Файл изображения не был передан.' }) });
    await expect(uploadImage(file, '/u/')).rejects.toThrow('Файл изображения не был передан.');
  });

  test('default error message is the legacy string', async () => {
    fetch.mockResolvedValueOnce({ json: async () => ({ success: false }) });
    await expect(uploadImage(file, '/u/')).rejects.toThrow('Ошибка при загрузке изображения.');
    fetch.mockResolvedValueOnce({ json: async () => { throw new SyntaxError('not JSON'); } });
    await expect(uploadImage(file, '/u/')).rejects.toThrow('Ошибка при загрузке изображения.');
    fetch.mockRejectedValueOnce(new TypeError('Failed to fetch'));
    await expect(uploadImage(file, '/u/')).rejects.toThrow('Ошибка при загрузке изображения.');
  });

  test('network error rejects', async () => {
    fetch.mockRejectedValue(new TypeError('Failed to fetch'));
    await expect(uploadImage(file, '/u/')).rejects.toThrow();
  });
});

describe('editor upload lifecycle', () => {
  test('visual placeholder never reaches textarea; success replaces it', async () => {
    const d = deferred();
    fetch.mockReturnValue(d.promise);
    const ed = makeEditor('a');
    const ta = ed.dom.container.querySelector('textarea');
    ed.element.dispatchEvent(pasteEvent([file]));
    expect(images(ed)).toHaveLength(1);
    expect(images(ed)[0].src).toBe('blob:test/1');
    expect(images(ed)[0].uploadId).toBeTruthy();
    expect(ta.value).toBe('a');
    expect(ed.dom.uploadProgress.classList.contains('d-none')).toBe(false);

    d.resolve(okResponse());
    await flush();
    expect(images(ed)).toEqual([expect.objectContaining({ src: '/m/a.png', alt: 'a.png', uploadId: null })]);
    expect(ta.value).toContain('![a.png](/m/a.png)');
    expect(ta.value).not.toContain('blob:');
    expect(URL.revokeObjectURL).toHaveBeenCalledWith('blob:test/1');
    expect(ed.dom.uploadProgress.classList.contains('d-none')).toBe(true);
  });

  test('failure removes placeholder', async () => {
    const d = deferred();
    fetch.mockReturnValue(d.promise);
    const ed = makeEditor('a');
    const ta = ed.dom.container.querySelector('textarea');
    ed.element.dispatchEvent(pasteEvent([file]));
    expect(images(ed)).toHaveLength(1);

    d.resolve({ json: async () => ({ success: false, error: 'Файл изображения не был передан.' }) });
    await flush();
    expect(images(ed)).toHaveLength(0);
    expect(ta.value).toBe('a');
    // Legacy handleUploadError reports the error with alert().
    expect(alertSpy).toHaveBeenCalledWith('Файл изображения не был передан.');
    expect(URL.revokeObjectURL).toHaveBeenCalledWith('blob:test/1');
    expect(ed.dom.uploadProgress.classList.contains('d-none')).toBe(true);
  });

  test('mode switch mid-upload lands image in markdown mode (Review Focus 4)', async () => {
    const d = deferred();
    fetch.mockReturnValue(d.promise);
    const ed = makeEditor('a');
    const ta = ed.dom.container.querySelector('textarea');
    ed.element.dispatchEvent(pasteEvent([file]));
    ed.setMode('markdown');
    expect(ta.value).toBe('a');

    d.resolve(okResponse());
    await flush();
    expect(ta.value.split('![a.png](/m/a.png)')).toHaveLength(2);
    expect(ta.value).not.toContain('blob:');
    expect(ta.value).toBe('a\n\n![a.png](/m/a.png)\n\n');
  });

  test('markdown mode inserts at the caret after upload only', async () => {
    const d = deferred();
    fetch.mockReturnValue(d.promise);
    const ed = makeEditor('one\n\ntwo', 'markdown');
    const ta = ed.dom.container.querySelector('textarea');
    ta.setSelectionRange(3, 3);
    const inputSpy = vi.fn();
    ta.addEventListener('input', inputSpy);
    ta.dispatchEvent(pasteEvent([file]));
    expect(ta.value).toBe('one\n\ntwo');

    d.resolve(okResponse());
    await flush();
    expect(ta.value).toBe('one\n\n![a.png](/m/a.png)\n\ntwo');
    expect(inputSpy).toHaveBeenCalled();
  });

  test('switch back to visual mid-upload appends image at the end of the doc', async () => {
    const d = deferred();
    fetch.mockReturnValue(d.promise);
    const ed = makeEditor('a');
    ed.element.dispatchEvent(pasteEvent([file]));
    ed.setMode('markdown');
    ed.setMode('visual');
    expect(images(ed)).toHaveLength(0);

    d.resolve(okResponse());
    await flush();
    expect(ed.tiptap.state.doc.lastChild.type.name).toBe('image');
    expect(ed.getMarkdown()).toBe('a\n\n![a.png](/m/a.png)');
  });

  test('non-image paste is not swallowed', async () => {
    const ed = makeEditor('a');
    const ev = pasteEvent([new File(['x'], 'a.txt', { type: 'text/plain' })]);
    ed.element.dispatchEvent(ev);
    expect(ev.defaultPrevented).toBe(false);
    await flush();
    expect(fetch).not.toHaveBeenCalled();
  });

  test('image paste is consumed', () => {
    fetch.mockReturnValue(new Promise(() => {}));
    const ed = makeEditor('a');
    const ev = pasteEvent([file]);
    ed.element.dispatchEvent(ev);
    expect(ev.defaultPrevented).toBe(true);
  });

  test('multiple files each get a placeholder and are uploaded in turn', async () => {
    const d1 = deferred();
    const d2 = deferred();
    fetch.mockReturnValueOnce(d1.promise).mockReturnValueOnce(d2.promise);
    const ed = makeEditor('a');
    const b = new File(['y'], 'b.gif', { type: 'image/gif' });
    ed.element.dispatchEvent(pasteEvent([file, b]));
    expect(images(ed)).toHaveLength(2);
    await flush();
    expect(fetch).toHaveBeenCalledTimes(1);

    d1.resolve(okResponse());
    await flush();
    expect(fetch).toHaveBeenCalledTimes(2);
    d2.resolve({ json: async () => ({ success: true, url: '/m/b.gif', filename: 'b.gif' }) });
    await flush();
    expect(images(ed).map((i) => i.src)).toEqual(['/m/a.png', '/m/b.gif']);
    expect(images(ed).every((i) => i.uploadId === null)).toBe(true);
  });

  test('drop shows and hides the overlay and uploads only images', async () => {
    fetch.mockReturnValue(new Promise(() => {}));
    const ed = makeEditor('a');
    const overlay = ed.dom.dropOverlay;
    const dt = { types: ['Files'], files: [file, new File(['x'], 'a.txt', { type: 'text/plain' })] };
    const enter = new Event('dragenter', { bubbles: true, cancelable: true });
    enter.dataTransfer = dt;
    ed.element.dispatchEvent(enter);
    expect(overlay.classList.contains('d-none')).toBe(false);
    const drop = new Event('drop', { bubbles: true, cancelable: true });
    drop.dataTransfer = dt;
    overlay.dispatchEvent(drop);
    expect(overlay.classList.contains('d-none')).toBe(true);
    expect(drop.defaultPrevented).toBe(true);
    await flush();
    expect(fetch).toHaveBeenCalledTimes(1);
    expect(images(ed)).toHaveLength(1);
  });

  test('image toolbar button, then "choose file", opens the file input; chosen files upload', async () => {
    fetch.mockReturnValue(new Promise(() => {}));
    const ed = makeEditor('a');
    const click = vi.spyOn(ed.dom.fileInput, 'click').mockImplementation(() => {});
    ed.dom.wrapper.querySelector('[data-cmd="image"]').click();
    expect(click).not.toHaveBeenCalled();
    ed.dom.modal.body.querySelector('.forum-modal-choose-file-btn').click();
    expect(click).toHaveBeenCalled();
    Object.defineProperty(ed.dom.fileInput, 'files', { value: [file], configurable: true });
    ed.dom.fileInput.dispatchEvent(new Event('change'));
    await flush();
    expect(fetch).toHaveBeenCalledTimes(1);
    expect(images(ed)).toHaveLength(1);
  });

  test('files over 10 MB are rejected before upload', async () => {
    const ed = makeEditor('a');
    const big = new File(['x'], 'big.png', { type: 'image/png' });
    Object.defineProperty(big, 'size', { value: 11 * 1024 * 1024 });
    ed.element.dispatchEvent(pasteEvent([big]));
    await flush();
    expect(fetch).not.toHaveBeenCalled();
    expect(alertSpy).toHaveBeenCalledWith('Файл «big.png» превышает 10 МБ. Пожалуйста, сожмите изображение или используйте сторонний сервис.');
    expect(images(ed)).toHaveLength(0);
  });

  test('undo after a successful upload never resurrects the placeholder', async () => {
    const d = deferred();
    fetch.mockReturnValue(d.promise);
    const ed = makeEditor('a');
    const end = ed.tiptap.state.doc.content.size - 1;
    ed.tiptap.view.dispatch(ed.tiptap.state.tr.setSelection(TextSelection.create(ed.tiptap.state.doc, end)));
    ed.element.dispatchEvent(pasteEvent([file]));
    ed.tiptap.commands.insertContent('XY');
    d.resolve(okResponse());
    await flush();
    ed.tiptap.commands.undo();
    const imgs = images(ed);
    expect(imgs.some((i) => i.uploadId !== null || /^blob:/.test(i.src))).toBe(false);
    // The uploaded image stays in the post, as the final image.
    expect(imgs).toEqual([expect.objectContaining({ src: '/m/a.png', alt: 'a.png', uploadId: null })]);
    expect(ed.getMarkdown()).toContain('![a.png](/m/a.png)');
    expect(ed.getMarkdown()).not.toContain('XY');
  });

  test('undo after a failed upload does not bring the placeholder back', async () => {
    const d = deferred();
    fetch.mockReturnValue(d.promise);
    const ed = makeEditor('a');
    const end = ed.tiptap.state.doc.content.size - 1;
    ed.tiptap.view.dispatch(ed.tiptap.state.tr.setSelection(TextSelection.create(ed.tiptap.state.doc, end)));
    ed.element.dispatchEvent(pasteEvent([file]));
    ed.tiptap.commands.insertContent('XY');
    d.resolve({ json: async () => ({ success: false, error: 'E' }) });
    await flush();
    ed.tiptap.commands.undo();
    expect(images(ed)).toHaveLength(0);
    expect(ed.getMarkdown()).toBe('a');
  });

  test('pasting over selected text deletes it in an undoable step', async () => {
    fetch.mockReturnValue(new Promise(() => {}));
    const ed = makeEditor('hello world');
    selectText(ed, 'world', 'world');
    ed.element.dispatchEvent(pasteEvent([file]));
    expect(ed.tiptap.state.doc.textContent).toBe('hello ');
    expect(images(ed)).toHaveLength(1);
    ed.tiptap.commands.undo();
    expect(ed.tiptap.state.doc.textContent).toBe('hello world');
  });

  test('an exception while finishing one upload does not stall the queue', async () => {
    const errSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
    fetch
      .mockResolvedValueOnce(okResponse())
      .mockResolvedValueOnce({ json: async () => ({ success: true, url: '/m/b.gif', filename: 'b.gif' }) });
    const ed = makeEditor('a');
    const counter = ed.updateCharCounter;
    let calls = 0;
    ed.updateCharCounter = function () {
      calls++;
      if (calls === 1) throw new Error('boom');
      return counter.apply(this, arguments);
    };
    const b = new File(['y'], 'b.gif', { type: 'image/gif' });
    ed.element.dispatchEvent(pasteEvent([file, b]));
    await flush();
    await flush();
    expect(fetch).toHaveBeenCalledTimes(2);
    expect(images(ed).map((i) => i.src)).toEqual(['/m/a.png', '/m/b.gif']);
    expect(ed.dom.uploadProgress.classList.contains('d-none')).toBe(true);
    expect(errSpy).toHaveBeenCalled();
  });
});

describe('submit while an upload is pending (final review 10)', () => {
  const MSG = 'Изображение ещё загружается. Отправить сообщение без него?';

  function submitForm(ed) {
    const form = ed.textarea.form;
    const seen = vi.fn();
    form.addEventListener('submit', (e) => { seen(e.defaultPrevented); e.preventDefault(); });
    const ev = new Event('submit', { bubbles: true, cancelable: true });
    form.dispatchEvent(ev);
    return { ev: ev, seen: seen };
  }

  test('declining the confirm blocks the submit', async () => {
    fetch.mockReturnValue(new Promise(() => {}));
    const confirmSpy = vi.fn(() => false);
    vi.stubGlobal('confirm', confirmSpy);
    const ed = makeEditor('a');
    ed.element.dispatchEvent(pasteEvent([file]));
    const r = submitForm(ed);
    expect(confirmSpy).toHaveBeenCalledWith(MSG);
    expect(r.seen).toHaveBeenCalledWith(true);
  });

  test('accepting the confirm lets the submit through, synced', async () => {
    fetch.mockReturnValue(new Promise(() => {}));
    const confirmSpy = vi.fn(() => true);
    vi.stubGlobal('confirm', confirmSpy);
    const ed = makeEditor('a');
    ed.element.dispatchEvent(pasteEvent([file]));
    const r = submitForm(ed);
    expect(confirmSpy).toHaveBeenCalledTimes(1);
    expect(r.seen).toHaveBeenCalledWith(false);
    expect(ed.textarea.value).toBe('a');
  });

  test('no pending upload: no confirm', async () => {
    fetch.mockResolvedValue(okResponse());
    const confirmSpy = vi.fn(() => false);
    vi.stubGlobal('confirm', confirmSpy);
    const ed = makeEditor('a');
    ed.element.dispatchEvent(pasteEvent([file]));
    await flush();
    await flush();
    const r = submitForm(ed);
    expect(confirmSpy).not.toHaveBeenCalled();
    expect(r.seen).toHaveBeenCalledWith(false);
  });
});
