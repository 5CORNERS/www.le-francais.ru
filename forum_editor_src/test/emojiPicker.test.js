import { describe, test, expect, afterEach, vi } from 'vitest';
import { initEmojiPicker } from '../src/ui/emojiPicker.js';
import { buildEditorDom } from '../src/ui/toolbar.js';
import { makeEditor, destroyEditors } from './helpers.js';

afterEach(() => {
  destroyEditors();
  vi.restoreAllMocks();
  document.body.innerHTML = '';
  localStorage.clear();
});

function emojiDom() {
  const form = document.createElement('form');
  const ta = document.createElement('textarea');
  form.appendChild(ta);
  document.body.appendChild(form);
  return buildEditorDom(ta).emoji;
}

const click = (el) => el.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
// jsdom's selector engine does not match astral characters in attribute values.
const item = (root, ch) => Array.from(root.querySelectorAll('[data-emoji]')).find((el) => el.getAttribute('data-emoji') === ch);
const isOpen = (e) => !e.dropdown.classList.contains('d-none');

describe('initEmojiPicker', () => {
  test('button toggles the dropdown', () => {
    const e = emojiDom();
    initEmojiPicker(e, vi.fn());
    expect(isOpen(e)).toBe(false);
    click(e.button);
    expect(isOpen(e)).toBe(true);
    click(e.button);
    expect(isOpen(e)).toBe(false);
  });

  test('clicking [data-emoji="😀"] calls onPick and closes', () => {
    const e = emojiDom();
    const onPick = vi.fn();
    initEmojiPicker(e, onPick);
    click(e.button);
    click(item(e.grid, '😀'));
    expect(onPick).toHaveBeenCalledWith('😀');
    expect(isOpen(e)).toBe(false);
  });

  test('clicking outside closes the dropdown; clicks inside do not', () => {
    const e = emojiDom();
    initEmojiPicker(e, vi.fn());
    click(e.button);
    click(e.grid);
    expect(isOpen(e)).toBe(true);
    click(document.body);
    expect(isOpen(e)).toBe(false);
  });

  test('Esc and the close button close the dropdown', () => {
    const e = emojiDom();
    initEmojiPicker(e, vi.fn());
    click(e.button);
    document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }));
    expect(isOpen(e)).toBe(false);
    click(e.button);
    click(e.close);
    expect(isOpen(e)).toBe(false);
  });

  test('destroy removes the listeners', () => {
    const e = emojiDom();
    const onPick = vi.fn();
    const destroy = initEmojiPicker(e, onPick);
    destroy();
    click(e.button);
    expect(isOpen(e)).toBe(false);
    click(item(e.grid, '😀'));
    expect(onPick).not.toHaveBeenCalled();
  });
});

describe('emoji in the editor', () => {
  test('visual mode inserts the character at the caret', () => {
    const ed = makeEditor('ab');
    ed.tiptap.commands.setTextSelection(2);
    click(ed.dom.emoji.button);
    click(item(ed.dom.emoji.grid, '😀'));
    expect(ed.getMarkdown()).toBe('a😀b');
  });

  test('markdown mode replaces the selection with the character', () => {
    const ed = makeEditor('a xx b', 'markdown');
    const ta = ed.dom.container.querySelector('textarea');
    ta.setSelectionRange(2, 4);
    click(item(ed.dom.emoji.grid, '😀'));
    expect(ta.value).toBe('a 😀 b');
    expect(ta.selectionStart).toBe(2 + '😀'.length);
  });
});
