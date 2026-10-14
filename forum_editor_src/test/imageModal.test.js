import { describe, test, expect, afterEach, vi } from 'vitest';
import { openImageModal, IMAGE_MODAL_TITLE } from '../src/ui/imageModal.js';
import { buildEditorDom } from '../src/ui/toolbar.js';
import { makeEditor, destroyEditors } from './helpers.js';

afterEach(() => {
  destroyEditors();
  vi.restoreAllMocks();
  document.body.innerHTML = '';
  localStorage.clear();
});

function modalDom() {
  const form = document.createElement('form');
  const ta = document.createElement('textarea');
  form.appendChild(ta);
  document.body.appendChild(form);
  return buildEditorDom(ta).modal;
}

const urlInput = (m) => m.body.querySelector('#forum-modal-img-url');
const titleInput = (m) => m.body.querySelector('#forum-modal-img-title');
const chooseBtn = (m) => m.body.querySelector('.forum-modal-choose-file-btn');
const keydown = (el, k) => el.dispatchEvent(new KeyboardEvent('keydown', { key: k, bubbles: true, cancelable: true }));

describe('openImageModal', () => {
  test('legacy markup and copy', () => {
    const m = modalDom();
    openImageModal(m, {});
    expect(IMAGE_MODAL_TITLE).toBe('Вставить изображение');
    expect(m.title.textContent).toBe('Вставить изображение');
    expect(urlInput(m).getAttribute('placeholder')).toBe('https://example.com/image.jpg');
    expect(m.body.querySelector('label[for="forum-modal-img-url"]').textContent).toBe('URL изображения');
    expect(m.body.querySelector('label[for="forum-modal-img-title"]').textContent).toBe('Подпись / заголовок (title & alt)');
    expect(titleInput(m).getAttribute('placeholder')).toBe('Описание изображения (необязательно)');
    expect(chooseBtn(m).textContent.trim()).toBe('Выбрать файл на устройстве');
    expect(m.body.textContent).toContain('— или —');
    expect(m.overlay.classList.contains('d-none')).toBe(false);
  });

  test('submit resolves {url, title}; an empty URL keeps the modal open', async () => {
    const m = modalDom();
    const p = openImageModal(m, {});
    const spy = vi.fn();
    p.then(spy);
    m.submit.click();
    await Promise.resolve();
    expect(spy).not.toHaveBeenCalled();
    urlInput(m).value = '  https://a.b/i.png ';
    titleInput(m).value = ' Pic ';
    keydown(titleInput(m), 'Enter');
    await expect(p).resolves.toEqual({ url: 'https://a.b/i.png', title: 'Pic' });
    expect(m.overlay.classList.contains('d-none')).toBe(true);
  });

  test.each(['cancel', 'close'])('%s resolves null', async (btn) => {
    const m = modalDom();
    const p = openImageModal(m, {});
    m[btn].click();
    await expect(p).resolves.toBe(null);
  });

  test('Esc and overlay click resolve null', async () => {
    const m = modalDom();
    const p = openImageModal(m, {});
    keydown(urlInput(m), 'Escape');
    await expect(p).resolves.toBe(null);
    const p2 = openImageModal(m, {});
    m.overlay.click();
    await expect(p2).resolves.toBe(null);
  });

  test('reopening supersedes the previous request', async () => {
    const m = modalDom();
    const p1 = openImageModal(m, {});
    const p2 = openImageModal(m, {});
    await expect(p1).resolves.toBe(null);
    m.cancel.click();
    await expect(p2).resolves.toBe(null);
  });

  test('"choose file" closes the modal and calls onChooseFile synchronously', async () => {
    const m = modalDom();
    const onChooseFile = vi.fn();
    const p = openImageModal(m, { onChooseFile: onChooseFile });
    chooseBtn(m).click();
    expect(onChooseFile).toHaveBeenCalledTimes(1);
    expect(m.overlay.classList.contains('d-none')).toBe(true);
    await expect(p).resolves.toBe(null);
  });
});

describe('image command integration', () => {
  test('toolbar image button opens the image modal in both modes', () => {
    const ed = makeEditor('a');
    const show = vi.fn(() => Promise.resolve(null));
    ed.commandContext.showImageModal = show;
    ed.executeCommand('image');
    ed.setMode('markdown');
    ed.executeCommand('image');
    expect(show).toHaveBeenCalledTimes(2);
    expect(show.mock.calls[0][0]).toBe(ed.dom.modal);
  });

  test('visual: inserts a block image with alt and title', async () => {
    const ed = makeEditor('ab');
    ed.tiptap.commands.setTextSelection(2);
    ed.commandContext.showImageModal = vi.fn(() => Promise.resolve({ url: 'https://x.y/i.png', title: 'Pic' }));
    ed.executeCommand('image');
    await vi.waitFor(() => expect(ed.getMarkdown()).toBe('a\n\n![Pic](https://x.y/i.png "Pic")\n\nb'));
    let img = null;
    ed.tiptap.state.doc.descendants((n) => { if (n.type.name === 'image') img = n; });
    expect(img.attrs).toMatchObject({ src: 'https://x.y/i.png', alt: 'Pic', title: 'Pic', uploadId: null });
  });

  test('visual: no title gives an image without title', async () => {
    const ed = makeEditor('');
    ed.commandContext.showImageModal = vi.fn(() => Promise.resolve({ url: '/media/i.png', title: '' }));
    ed.executeCommand('image');
    await vi.waitFor(() => expect(ed.getMarkdown()).toBe('![](/media/i.png)'));
  });

  test('visual: a disallowed URL scheme becomes # (legacy sanitizeUrl)', async () => {
    const ed = makeEditor('');
    ed.commandContext.showImageModal = vi.fn(() => Promise.resolve({ url: 'javascript:alert(1)', title: '' }));
    ed.executeCommand('image');
    await vi.waitFor(() => expect(ed.getMarkdown()).toBe('![](#)'));
  });

  test('markdown: inserts ![alt](url "title") at the caret with blank-line padding', async () => {
    const ed = makeEditor('ab', 'markdown');
    const ta = ed.dom.container.querySelector('textarea');
    ta.setSelectionRange(1, 1);
    const onInput = vi.fn();
    ta.addEventListener('input', onInput);
    ed.commandContext.showImageModal = vi.fn(() => Promise.resolve({ url: 'https://x.y/i.png', title: 'Pic' }));
    ed.executeCommand('image');
    await vi.waitFor(() => expect(ta.value).toBe('a\n\n![Pic](https://x.y/i.png "Pic")\n\nb'));
    expect(onInput).toHaveBeenCalled();
  });

  test('markdown: empty title is omitted; bad scheme becomes #', async () => {
    const ed = makeEditor('', 'markdown');
    const ta = ed.dom.container.querySelector('textarea');
    ed.commandContext.showImageModal = vi.fn(() => Promise.resolve({ url: 'data:image/png;base64,xx', title: '' }));
    ed.executeCommand('image');
    await vi.waitFor(() => expect(ta.value).toBe('![](#)\n\n'));
  });

  test('"choose file" in the real modal opens the file picker', () => {
    const ed = makeEditor('');
    const click = vi.spyOn(ed.dom.fileInput, 'click').mockImplementation(() => {});
    ed.executeCommand('image');
    chooseBtn(ed.dom.modal).click();
    expect(click).toHaveBeenCalledTimes(1);
    expect(ed.dom.modal.overlay.classList.contains('d-none')).toBe(true);
  });

  test('cancel leaves the text unchanged', async () => {
    const ed = makeEditor('a');
    const show = vi.fn(() => Promise.resolve(null));
    ed.commandContext.showImageModal = show;
    ed.executeCommand('image');
    await vi.waitFor(() => expect(show).toHaveBeenCalled());
    await Promise.resolve();
    expect(ed.getMarkdown()).toBe('a');
  });
});
