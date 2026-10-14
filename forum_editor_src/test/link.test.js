import { describe, test, expect, beforeEach, afterEach } from 'vitest';
import { makeEditor, destroyEditors } from './helpers.js';

function typeText(ed, str) {
  for (const ch of str) {
    const view = ed.tiptap.view;
    const { from, to } = view.state.selection;
    const handled = view.someProp('handleTextInput', (f) => f(view, from, to, ch, () => view.state.tr.insertText(ch, from, to)));
    if (!handled) view.dispatch(view.state.tr.insertText(ch, from, to));
  }
}

const pasteEv = () => new Event('paste', { cancelable: true });

function hasLink(ed) {
  let found = false;
  ed.tiptap.state.doc.descendants((node) => {
    if (node.marks.some((m) => m.type.name === 'link')) found = true;
  });
  return found;
}

beforeEach(() => {
  localStorage.clear();
});

afterEach(() => {
  destroyEditors();
  document.body.innerHTML = '';
});

describe('link mark (no autoformat)', () => {
  test('typing a bare domain stays plain text', () => {
    const ed = makeEditor('');
    ed.tiptap.commands.focus();
    typeText(ed, 'voir le-francais.ru et main.py ok site.ru ');
    expect(hasLink(ed)).toBe(false);
    expect(ed.getMarkdown()).toBe('voir le-francais.ru et main.py ok site.ru');
  });

  test('pasting a plain URL stays plain text', () => {
    const ed = makeEditor('');
    ed.tiptap.view.pasteText('see https://example.com/a_b_c', pasteEv());
    expect(hasLink(ed)).toBe(false);
    expect(ed.getMarkdown()).toBe('see https://example.com/a_b_c');
  });

  test('pasted javascript: link becomes plain text', () => {
    const ed = makeEditor('');
    ed.tiptap.view.pasteHTML('<p><a href="javascript:alert(1)">t</a></p>', pasteEv());
    expect(hasLink(ed)).toBe(false);
    expect(ed.getMarkdown()).toBe('t');
  });

  test('pasted http and relative links are kept', () => {
    const ed = makeEditor('');
    ed.tiptap.view.pasteHTML('<p><a href="https://a.b/c">x</a> <a href="/forum/">y</a> <a href="mailto:a@b.c">z</a></p>', pasteEv());
    expect(ed.getMarkdown()).toBe('[x](https://a.b/c) [y](/forum/) [z](mailto:a@b.c)');
  });

  test('typing after a link does not extend it', () => {
    const ed = makeEditor('[x](https://a.b)');
    ed.tiptap.commands.focus('end');
    typeText(ed, 'y');
    expect(ed.getMarkdown()).toBe('[x](https://a.b)y');
  });
});
