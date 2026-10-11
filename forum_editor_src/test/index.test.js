import { describe, test, expect, afterEach, vi } from 'vitest';

function setReadyState(value) {
  Object.defineProperty(document, 'readyState', { get: () => value, configurable: true });
}

async function freshIndex() {
  vi.resetModules();
  return import('../src/index.js');
}

afterEach(() => {
  if (window.forumEditor) window.forumEditor.destroy();
  delete window.forumEditor;
  delete document.readyState; // back to jsdom's own getter
  vi.doUnmock('../src/editor.js');
  vi.restoreAllMocks();
  document.body.innerHTML = '';
  localStorage.clear();
});

describe('index.js start-up (final review 8)', () => {
  test('mounts immediately when the document has already loaded (defer)', async () => {
    setReadyState('interactive');
    document.body.innerHTML = '<form><textarea id="id_body"></textarea></form>';
    await freshIndex();
    expect(window.forumEditor).toBeDefined();
    expect(window.forumEditor.element.classList.contains('forum-visual-editor')).toBe(true);
    expect(window.forumEditor.uploadUrl).toBe('/forum/upload-image/');
  });

  test('waits for DOMContentLoaded while loading; mounts once', async () => {
    setReadyState('loading');
    document.body.innerHTML = '<form><textarea id="id_body"></textarea></form>';
    await freshIndex();
    expect(window.forumEditor).toBeUndefined();
    document.dispatchEvent(new Event('DOMContentLoaded'));
    const first = window.forumEditor;
    expect(first).toBeDefined();
    document.dispatchEvent(new Event('DOMContentLoaded'));
    expect(window.forumEditor).toBe(first);
    expect(document.querySelectorAll('.forum-editor-wrapper').length).toBe(1);
  });

  test('does nothing without #id_body', async () => {
    setReadyState('complete');
    await freshIndex();
    expect(window.forumEditor).toBeUndefined();
  });

  test('a start-up error is logged and the plain textarea survives', async () => {
    setReadyState('complete');
    document.body.innerHTML = '<form><textarea id="id_body">text</textarea></form>';
    vi.doMock('../src/editor.js', () => ({
      createForumEditor: () => { throw new Error('boom'); },
    }));
    const err = vi.spyOn(console, 'error').mockImplementation(() => {});
    await expect(freshIndex()).resolves.toBeDefined();
    expect(err).toHaveBeenCalled();
    expect(window.forumEditor).toBeUndefined();
    expect(document.getElementById('id_body').value).toBe('text');
  });
});
