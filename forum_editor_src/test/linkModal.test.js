import { describe, test, expect, afterEach, vi } from 'vitest';
import { NodeSelection } from '@tiptap/pm/state';
import { openLinkModal } from '../src/ui/linkModal.js';
import { buildEditorDom } from '../src/ui/toolbar.js';
import { makeEditor, destroyEditors, selectText } from './helpers.js';

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

const urlInput = (m) => m.body.querySelector('#forum-modal-link-url');
const textInput = (m) => m.body.querySelector('#forum-modal-link-text');
const keydown = (el, k) => el.dispatchEvent(new KeyboardEvent('keydown', { key: k, bubbles: true, cancelable: true }));

describe('openLinkModal', () => {
  test('submit resolves {text, url}', async () => {
    const m = modalDom();
    const p = openLinkModal(m, { text: 'ici', url: '' });
    expect(m.overlay.classList.contains('d-none')).toBe(false);
    expect(m.title.textContent).toBe('Вставить ссылку');
    expect(textInput(m).value).toBe('ici');
    expect(urlInput(m).value).toBe('https://');
    urlInput(m).value = 'https://x.y';
    m.submit.click();
    await expect(p).resolves.toEqual({ text: 'ici', url: 'https://x.y' });
    expect(m.overlay.classList.contains('d-none')).toBe(true);
  });

  test('submit with an empty URL keeps the modal open; Enter in an input submits', async () => {
    const m = modalDom();
    const p = openLinkModal(m, { text: '' });
    const spy = vi.fn();
    p.then(spy);
    m.submit.click();
    await Promise.resolve();
    expect(spy).not.toHaveBeenCalled();
    expect(m.overlay.classList.contains('d-none')).toBe(false);
    urlInput(m).value = '  https://a.b  ';
    keydown(urlInput(m), 'Enter');
    await expect(p).resolves.toEqual({ text: '', url: 'https://a.b' });
  });

  test('Esc resolves null and hides the modal', async () => {
    const m = modalDom();
    const p = openLinkModal(m, { text: 'ici' });
    keydown(urlInput(m), 'Escape');
    await expect(p).resolves.toBe(null);
    expect(m.overlay.classList.contains('d-none')).toBe(true);
  });

  test.each(['cancel', 'close'])('%s button resolves null', async (btn) => {
    const m = modalDom();
    const p = openLinkModal(m, {});
    m[btn].click();
    await expect(p).resolves.toBe(null);
    expect(m.overlay.classList.contains('d-none')).toBe(true);
  });

  test('overlay click resolves null; clicks inside the dialog do not', async () => {
    const m = modalDom();
    const p = openLinkModal(m, {});
    const spy = vi.fn();
    p.then(spy);
    m.body.click();
    await Promise.resolve();
    expect(spy).not.toHaveBeenCalled();
    m.overlay.click();
    await expect(p).resolves.toBe(null);
  });

  test('a closed modal can be reopened; old listeners are gone', async () => {
    const m = modalDom();
    const p = openLinkModal(m, {});
    m.cancel.click();
    await p;
    const p2 = openLinkModal(m, { text: 't' });
    urlInput(m).value = 'https://q.r';
    m.submit.click();
    await expect(p2).resolves.toEqual({ text: 't', url: 'https://q.r' });
  });

  test('reopening while open cancels the previous request', async () => {
    const m = modalDom();
    const p1 = openLinkModal(m, {});
    const p2 = openLinkModal(m, {});
    await expect(p1).resolves.toBe(null);
    m.cancel.click();
    await expect(p2).resolves.toBe(null);
  });
});

describe('link command integration', () => {
  test('visual: link on a selection gives [ici](url)', async () => {
    const ed = makeEditor('voir ici');
    ed.commandContext.showLinkModal = vi.fn(() => Promise.resolve({ text: 'ici', url: 'https://x.y' }));
    selectText(ed, 'ici', 'ici');
    ed.executeCommand('link');
    await vi.waitFor(() => expect(ed.getMarkdown()).toBe('voir [ici](https://x.y)'));
  });

  test('visual: the real modal links the selected text', async () => {
    const ed = makeEditor('voir ici');
    selectText(ed, 'ici', 'ici');
    ed.executeCommand('link');
    const m = ed.dom.modal;
    expect(textInput(m).value).toBe('ici');
    urlInput(m).value = 'https://x.y';
    m.submit.click();
    await vi.waitFor(() => expect(ed.getMarkdown()).toBe('voir [ici](https://x.y)'));
  });

  test('visual: link without a selection inserts the URL as text; typing after it is not linked', async () => {
    const ed = makeEditor('a b');
    ed.tiptap.commands.setTextSelection(3);
    ed.commandContext.showLinkModal = vi.fn(() => Promise.resolve({ text: '', url: 'https://x.y' }));
    ed.executeCommand('link');
    await vi.waitFor(() => expect(ed.getMarkdown()).toBe('a [https://x.y](https://x.y)b'));
    ed.tiptap.commands.insertContent('!');
    expect(ed.getMarkdown()).toBe('a [https://x.y](https://x.y)!b');
  });

  test('visual: changed link text replaces the selection', async () => {
    const ed = makeEditor('voir ici');
    selectText(ed, 'ici', 'ici');
    ed.commandContext.showLinkModal = vi.fn(() => Promise.resolve({ text: 'là', url: 'https://x.y' }));
    ed.executeCommand('link');
    await vi.waitFor(() => expect(ed.getMarkdown()).toBe('voir [là](https://x.y)'));
  });

  test('visual: link on a selected image keeps the image', async () => {
    const ed = makeEditor('![i](http://i/x.png)');
    ed.tiptap.view.dispatch(ed.tiptap.state.tr.setSelection(NodeSelection.create(ed.tiptap.state.doc, 0)));
    ed.commandContext.showLinkModal = vi.fn(() => Promise.resolve({ text: 'ici', url: 'https://x.y' }));
    ed.executeCommand('link');
    await vi.waitFor(() => expect(ed.getMarkdown()).toBe('![i](http://i/x.png)\n\n[ici](https://x.y)'));
  });

  test('cancel leaves the text unchanged', async () => {
    const ed = makeEditor('voir ici');
    selectText(ed, 'ici', 'ici');
    const openModal = vi.fn(() => Promise.resolve(null));
    ed.commandContext.showLinkModal = openModal;
    ed.executeCommand('link');
    await vi.waitFor(() => expect(openModal).toHaveBeenCalled());
    await Promise.resolve();
    expect(ed.getMarkdown()).toBe('voir ici');
  });

  test('markdown: link replaces the selection with [sel](url)', async () => {
    const ed = makeEditor('voir ici', 'markdown');
    const ta = ed.dom.container.querySelector('textarea');
    ta.setSelectionRange(5, 8);
    const openModal = vi.fn(() => Promise.resolve({ text: 'ici', url: 'https://x.y' }));
    ed.commandContext.showLinkModal = openModal;
    ed.executeCommand('link');
    await vi.waitFor(() => expect(ta.value).toBe('voir [ici](https://x.y)'));
    expect(openModal.mock.calls[0][0]).toBe(ed.dom.modal);
    expect(openModal.mock.calls[0][1]).toEqual({ text: 'ici', url: '' });
  });
});

describe('link URL validation (final review 7, legacy sanitizeUrl)', () => {
  test.each([
    ['javascript:alert(1)', '#'],
    ['  JavaScript:alert(1)', '#'],
    ['data:text/html,x', '#'],
    ['example.com', '#'],
    ['HTTPS://a.b', 'HTTPS://a.b'],
    ['/forum/', '/forum/'],
    ['mailto:a@b.c', 'mailto:a@b.c'],
    ['#top', '#top'],
  ])('visual: %s is stored as %s', async (url, href) => {
    const ed = makeEditor('voir ici');
    selectText(ed, 'ici', 'ici');
    ed.commandContext.showLinkModal = vi.fn(() => Promise.resolve({ text: 'ici', url: url }));
    ed.executeCommand('link');
    await vi.waitFor(() => expect(ed.getMarkdown()).toBe('voir [ici](' + href + ')'));
  });

  test('markdown: a disallowed scheme becomes #', async () => {
    const ed = makeEditor('voir ici', 'markdown');
    const ta = ed.dom.container.querySelector('textarea');
    ta.setSelectionRange(5, 8);
    ed.commandContext.showLinkModal = vi.fn(() => Promise.resolve({ text: 'ici', url: 'javascript:alert(1)' }));
    ed.executeCommand('link');
    await vi.waitFor(() => expect(ta.value).toBe('voir [ici](#)'));
  });

  test('without link text the typed URL is the display text', async () => {
    const ed = makeEditor('', 'markdown');
    const ta = ed.dom.container.querySelector('textarea');
    ed.commandContext.showLinkModal = vi.fn(() => Promise.resolve({ text: '', url: 'ftp://x' }));
    ed.executeCommand('link');
    await vi.waitFor(() => expect(ta.value).toBe('[ftp://x](#)'));
  });
});
