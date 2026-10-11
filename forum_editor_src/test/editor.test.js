import { describe, test, expect, beforeEach, afterEach, vi } from 'vitest';
import { createForumEditor } from '../src/editor.js';
import * as parser from '../src/markdown/parser.js';

let ta;
let form;
let editors;

const qs = (sel) => document.querySelector(sel);

function make(opts) {
  const ed = createForumEditor(Object.assign({ textarea: ta }, opts));
  editors.push(ed);
  return ed;
}

beforeEach(() => {
  localStorage.clear();
  document.body.innerHTML = '<form><textarea id="id_body" required></textarea></form>';
  form = qs('form');
  ta = qs('#id_body');
  editors = [];
});

afterEach(() => {
  editors.forEach((ed) => ed.destroy());
  vi.restoreAllMocks();
  document.body.innerHTML = '';
});

describe('createForumEditor', () => {
  test('initial markdown loads and syncs back unchanged', () => {
    ta.value = '**a** ^^b^^';
    const ed = make();
    expect(ed.element.innerHTML).toContain('<strong>a</strong>');
    const pos = ed.tiptap.state.doc.content.size - 1;
    // tr.insert adds an unmarked text node (insertContentAt would inherit the underline mark).
    ed.tiptap.chain().command(({ tr, state }) => {
      tr.insert(pos, state.schema.text('!'));
      return true;
    }).run();
    expect(ta.value).toBe('**a** ^^b^^!');
  });

  test('every update syncs synchronously and fires change', () => {
    const ed = make();
    const spy = vi.fn();
    const inputSpy = vi.fn();
    ta.addEventListener('change', spy);
    document.addEventListener('input', inputSpy);
    ed.tiptap.commands.insertContent('x');
    expect(ta.value).toBe('x');
    expect(spy).toHaveBeenCalled();
    expect(inputSpy).toHaveBeenCalled();
    document.removeEventListener('input', inputSpy);
  });

  test('submit listener flushes', () => {
    ta.value = 'old';
    const ed = make();
    const { state } = ed.tiptap;
    const tr = state.tr.insertText('new ', 1);
    ed.tiptap.view.updateState(state.apply(tr));
    expect(ta.value).toBe('old');
    let seen = null;
    form.addEventListener('submit', (e) => { seen = ta.value; e.preventDefault(); });
    form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
    expect(seen).toBe('new old');
    expect(ta.value).toBe('new old');
  });

  test('textarea setup', () => {
    make();
    expect(ta.classList.contains('no-markitup')).toBe(true);
    expect(ta.classList.contains('forum-markdown-textarea')).toBe(true);
    expect(ta.hasAttribute('required')).toBe(false);
    expect(form.getAttribute('novalidate')).toBe('novalidate');
    expect(ta.parentNode.classList.contains('forum-editor-container')).toBe(true);
  });

  test('element and api shape', () => {
    const ed = make();
    expect(ed.element.classList.contains('forum-visual-editor')).toBe(true);
    expect(ed.element.getAttribute('spellcheck')).toBe('true');
    expect(ed.element.getAttribute('contenteditable')).toBe('true');
    expect(ed.$visualEditor).toBeUndefined();
    expect(typeof ed.executeCommand).toBe('function');
    const d = ed.dom;
    ['wrapper', 'toolbar', 'container', 'visualHost', 'dropOverlay', 'uploadProgress', 'fileInput', 'charCounter', 'resizer']
      .forEach((k) => expect(d[k]).toBeInstanceOf(HTMLElement));
    ['overlay', 'title', 'body', 'submit', 'cancel', 'close'].forEach((k) => expect(d.modal[k]).toBeInstanceOf(HTMLElement));
    ['button', 'dropdown', 'grid', 'close'].forEach((k) => expect(d.emoji[k]).toBeInstanceOf(HTMLElement));
    expect(d.emoji.grid.querySelectorAll('.forum-emoji-item').length).toBeGreaterThan(10);
    expect(document.querySelectorAll('[contenteditable="true"]').length).toBe(1);
  });

  test('$visualEditor wraps element when jQuery exists', () => {
    const fake = vi.fn((el) => ({ 0: el, length: 1 }));
    window.jQuery = fake;
    try {
      const ed = make();
      expect(fake).toHaveBeenCalledWith(ed.element);
      expect(ed.$visualEditor[0]).toBe(ed.element);
    } finally {
      delete window.jQuery;
    }
  });

  test('initial mode defaults to localStorage, then visual', () => {
    localStorage.setItem('forum_editor_mode', 'markdown');
    const ed = make();
    expect(ed.currentMode).toBe('markdown');
    expect(ta.style.display).not.toBe('none');
    expect(ed.dom.visualHost.style.display).toBe('none');
    expect(ed.dom.wrapper.querySelector('.forum-mode-checkbox').checked).toBe(true);
  });

  test('mode switch round-trips and persists', () => {
    ta.value = 'a';
    const ed = make({ initialMode: 'visual' });
    ed.setMode('markdown');
    expect(localStorage.getItem('forum_editor_mode')).toBe('markdown');
    expect(ed.dom.wrapper.querySelector('.forum-mode-switch-btn.markdown').classList.contains('active')).toBe(true);
    ta.value = '## T';
    ed.setMode('visual');
    expect(ed.element.innerHTML).toBe('<h2>T</h2>');
    expect(localStorage.getItem('forum_editor_mode')).toBe('visual');
    expect(ed.dom.wrapper.querySelector('.forum-mode-checkbox').checked).toBe(false);
    expect(ed.dom.wrapper.querySelector('.forum-mode-switch-btn.visual').classList.contains('active')).toBe(true);
  });

  test('mode switch controls toggle the mode', () => {
    const ed = make({ initialMode: 'visual' });
    const cb = ed.dom.wrapper.querySelector('.forum-mode-checkbox');
    cb.checked = true;
    cb.dispatchEvent(new Event('change', { bubbles: true }));
    expect(ed.currentMode).toBe('markdown');
    ed.dom.wrapper.querySelector('.forum-mode-switch-btn.visual').dispatchEvent(new MouseEvent('click', { bubbles: true }));
    expect(ed.currentMode).toBe('visual');
  });

  test('parse failure falls back to markdown mode', () => {
    vi.spyOn(console, 'error').mockImplementation(() => {});
    vi.spyOn(parser, 'parseMarkdown').mockImplementation(() => { throw new Error('boom'); });
    ta.value = 'x';
    const ed = make({ initialMode: 'visual' });
    expect(ed.currentMode).toBe('markdown');
    expect(ta.value).toBe('x');
    expect(document.body.textContent).toContain('Не удалось открыть визуальный редактор');
    const notice = ed.dom.container.previousElementSibling;
    expect(notice.className).toBe('alert alert-warning py-1 px-2 mb-1 small');
    ed.setMode('visual');
    expect(ed.currentMode).toBe('markdown');
    expect(ta.value).toBe('x');
  });

  test('serialize failure keeps the old textarea value', async () => {
    const serializer = await import('../src/markdown/serializer.js');
    ta.value = 'keep';
    const ed = make();
    const err = vi.spyOn(console, 'error').mockImplementation(() => {});
    vi.spyOn(serializer, 'serializeMarkdown').mockImplementation(() => { throw new Error('boom'); });
    ed.tiptap.commands.insertContent('x');
    expect(ta.value).toBe('keep');
    expect(err).toHaveBeenCalled();
  });

  test('insertQuote in both modes', () => {
    ta.value = 'a';
    const ed = make({ initialMode: 'visual' });
    ed.insertQuote('> q');
    const doc = ed.tiptap.state.doc;
    expect(doc.childCount).toBe(3);
    expect(doc.child(0).textContent).toBe('a');
    expect(doc.child(1).type.name).toBe('blockquote');
    expect(doc.child(1).textContent).toBe('q');
    expect(doc.child(2).type.name).toBe('paragraph');
    expect(doc.child(2).content.size).toBe(0);
    const $from = ed.tiptap.state.selection.$from;
    expect($from.parent).toBe(doc.child(2));
    expect(ta.value).toBe('a\n\n> q');

    ed.setMode('markdown');
    ta.value = 'ab';
    ta.setSelectionRange(1, 1);
    ed.insertQuote('> q');
    // Legacy padding: "\n\n" before, "\n\n" after the quote, plus "\n\n" before following text.
    expect(ta.value).toBe('a\n\n> q\n\n\n\nb');
    expect(ta.value.indexOf('\n\n> q\n\n')).toBe(1);
    expect(ta.selectionStart).toBe('a\n\n> q\n\n'.length);
  });

  test('insertQuote at saved selection splits the paragraph', () => {
    ta.value = 'abcd';
    const ed = make({ initialMode: 'visual' });
    ed.tiptap.commands.focus();
    ed.tiptap.commands.setTextSelection(3);
    ed.tiptap.commands.blur();
    ed.insertQuote('> q');
    const doc = ed.tiptap.state.doc;
    expect(doc.childCount).toBe(3);
    expect(doc.child(0).textContent).toBe('ab');
    expect(doc.child(1).type.name).toBe('blockquote');
    expect(doc.child(2).textContent).toBe('cd');
    expect(ed.tiptap.state.selection.$from.parent).toBe(doc.child(2));
    expect(ed.tiptap.state.selection.$from.parentOffset).toBe(0);
  });

  test('insertQuote keeps selected draft text and lands after it', () => {
    ta.value = 'abcd';
    const ed = make({ initialMode: 'visual' });
    ed.tiptap.commands.setTextSelection({ from: 2, to: 4 }); // "bc"
    expect(ed.tiptap.state.selection.empty).toBe(false);
    ed.tiptap.commands.blur();
    ed.insertQuote('> q');
    const doc = ed.tiptap.state.doc;
    expect(doc.childCount).toBe(3);
    expect(doc.child(0).textContent).toBe('abc');
    expect(doc.child(1).type.name).toBe('blockquote');
    expect(doc.child(2).textContent).toBe('d');
    expect(ed.tiptap.state.selection.$from.parent).toBe(doc.child(2));
    expect(ta.value).toBe('abc\n\n> q\n\nd');
  });

  test('switching to markdown without edits keeps non-canonical Markdown', () => {
    ta.value = '_i_ __b__';
    const ed = make({ initialMode: 'visual' });
    ed.setMode('markdown');
    expect(ta.value).toBe('_i_ __b__');
    ed.setMode('visual');
    ed.tiptap.commands.focus();
    ed.setMode('markdown');
    expect(ta.value).toBe('_i_ __b__');
    // A real edit is still serialized.
    ed.setMode('visual');
    ed.tiptap.commands.insertContentAt(1, 'x');
    ed.setMode('markdown');
    expect(ta.value).toBe('*xi* **b**'); // typed at the start of the italic run inherits it
  });

  test('insertQuote with the caret in a spoiler title lands after the spoiler', () => {
    ta.value = '???- "Title"\n    body';
    const ed = make({ initialMode: 'visual' });
    ed.tiptap.commands.setTextSelection(4);
    expect(ed.tiptap.state.selection.$from.parent.type.name).toBe('spoilerSummary');
    ed.insertQuote('> q');
    const doc = ed.tiptap.state.doc;
    expect(doc.child(0).type.name).toBe('spoiler');
    expect(doc.child(1).type.name).toBe('blockquote');
    expect(doc.child(2).type.name).toBe('paragraph');
    expect(ed.tiptap.state.selection.$from.parent).toBe(doc.child(2));
  });

  test('insertQuote into an empty editor replaces the empty paragraph', () => {
    const ed = make({ initialMode: 'visual' });
    ed.insertQuote('> q');
    const doc = ed.tiptap.state.doc;
    expect(doc.childCount).toBe(2);
    expect(doc.child(0).type.name).toBe('blockquote');
    expect(ta.value).toBe('> q');
  });

  test('insertMarkdown inserts parsed content or delegates quotes', () => {
    ta.value = 'a';
    const ed = make({ initialMode: 'visual' });
    ed.tiptap.commands.focus('end');
    ed.insertMarkdown('**b**');
    expect(ta.value).toBe('a**b**');
    expect(ed.tiptap.state.doc.childCount).toBe(1);
    ed.insertMarkdown('> q');
    expect(ed.tiptap.state.doc.child(1).type.name).toBe('blockquote');
  });

  test('syncVisualFromMarkdown reloads the textarea', () => {
    const ed = make({ initialMode: 'visual' });
    ta.value = '**x**';
    ed.syncVisualFromMarkdown();
    expect(ed.element.innerHTML).toContain('<strong>x</strong>');
    expect(qs('.forum-char-counter').textContent).toBe('5 симв.');
  });

  test('spoiler data-empty decorations', () => {
    ta.value = '???- "T"\n    body';
    const ed = make({ initialMode: 'visual' });
    const summary = ed.element.querySelector('summary');
    const body = ed.element.querySelector('.spoiler-body');
    expect(summary.getAttribute('data-empty')).toBe('false');
    expect(body.getAttribute('data-empty')).toBe('false');
    expect(summary.getAttribute('data-placeholder')).toBe('Введите заголовок спойлера');
    ed.tiptap.chain().command(({ tr, state }) => {
      let from = null; let to = null;
      state.doc.descendants((n, p) => { if (n.type.name === 'spoilerSummary') { from = p + 1; to = p + 1 + n.content.size; } });
      tr.delete(from, to);
      return true;
    }).run();
    expect(ed.element.querySelector('summary').getAttribute('data-empty')).toBe('true');
  });

  test('placeholder on empty editor', () => {
    const ed = make({ initialMode: 'visual' });
    expect(ed.element.querySelector('p').getAttribute('data-placeholder'))
      .toBe('Напишите ответ или перетащите изображение сюда...');
  });

  test('char counter', () => {
    ta.value = 'abc';
    make();
    expect(qs('.forum-char-counter').textContent).toBe('3 симв.');
  });

  test('large post serializes fast (Review Focus 5)', () => {
    ta.value = Array.from({ length: 2000 }, (_, i) => `Paragraphe **${i}** avec du texte.`).join('\n\n');
    const ed = make();
    const t = performance.now();
    ed.syncMarkdownFromVisual();
    expect(performance.now() - t).toBeLessThan(100);
  });

  test('destroy restores the textarea', () => {
    const ed = createForumEditor({ textarea: ta });
    ed.destroy();
    expect(qs('.forum-editor-wrapper')).toBeNull();
    expect(ta.parentNode).toBe(form);
  });
});

describe('index.js start-up', () => {
  test('mounts on DOMContentLoaded once, only when #id_body exists', async () => {
    delete window.forumEditor;
    document.body.innerHTML = '';
    await import('../src/index.js');
    document.dispatchEvent(new Event('DOMContentLoaded'));
    expect(window.forumEditor).toBeUndefined();

    document.body.innerHTML = '<form><textarea id="id_body"></textarea></form>';
    document.dispatchEvent(new Event('DOMContentLoaded'));
    const first = window.forumEditor;
    expect(first.element.classList.contains('forum-visual-editor')).toBe(true);
    expect(first.uploadUrl).toBe('/forum/upload-image/');

    document.dispatchEvent(new Event('DOMContentLoaded'));
    expect(window.forumEditor).toBe(first);
    expect(document.querySelectorAll('.forum-editor-wrapper').length).toBe(1);
    first.destroy();
    delete window.forumEditor;
  });
});

describe('history is reset on every load (final review 2)', () => {
  test('markdown -> visual, then undo keeps the content', () => {
    ta.value = 'start';
    const ed = make({ initialMode: 'markdown' });
    ed.setMode('visual');
    ed.tiptap.commands.undo();
    expect(ed.tiptap.state.doc.textContent).toBe('start');
    expect(ta.value).toBe('start');
  });

  test('visual edits, markdown edits, visual, then undo keeps the markdown edits', () => {
    ta.value = 'a';
    const ed = make({ initialMode: 'visual' });
    ed.tiptap.commands.focus('end');
    ed.tiptap.commands.insertContent('b');
    expect(ta.value).toBe('ab');
    ed.setMode('markdown');
    ta.value = 'ab c';
    ed.setMode('visual');
    expect(ed.tiptap.commands.undo()).toBe(false);
    expect(ta.value).toBe('ab c');
    expect(ed.tiptap.state.doc.textContent).toBe('ab c');
  });

  test('undo right after the initial load or setMarkdown is a no-op', () => {
    ta.value = 'x';
    const ed = make({ initialMode: 'visual' });
    expect(ed.tiptap.commands.undo()).toBe(false);
    ed.setMarkdown('y');
    expect(ed.tiptap.commands.undo()).toBe(false);
    expect(ed.tiptap.state.doc.textContent).toBe('y');
    expect(ta.value).toBe('y');
  });

  test('editing still records history after a load', () => {
    ta.value = 'a';
    const ed = make({ initialMode: 'markdown' });
    ed.setMode('visual');
    ed.tiptap.commands.focus('end');
    ed.tiptap.commands.insertContent('b');
    expect(ed.tiptap.commands.undo()).toBe(true);
    expect(ta.value).toBe('a');
  });
});

describe('insertQuote with unparseable Markdown (final review 4)', () => {
  const QUOTE = '> **bob**:\n> [![pic](x)](y)';

  test('falls back to a raw Markdown block holding the whole quote', () => {
    ta.value = 'draft';
    const ed = make({ initialMode: 'visual' });
    const err = vi.spyOn(console, 'error').mockImplementation(() => {});
    ed.insertQuote(QUOTE);
    const doc = ed.tiptap.state.doc;
    expect(doc.child(0).textContent).toBe('draft');
    expect(doc.child(1).type.name).toBe('rawMarkdownBlock');
    expect(doc.child(1).attrs.source).toBe(QUOTE);
    expect(doc.child(2).type.name).toBe('paragraph');
    expect(doc.child(2).content.size).toBe(0);
    expect(ed.tiptap.state.selection.$from.parent).toBe(doc.child(2));
    expect(ta.value).toBe('draft\n\n' + QUOTE);
    expect(err).toHaveBeenCalled();
  });

  test('works in an empty editor too', () => {
    const ed = make({ initialMode: 'visual' });
    vi.spyOn(console, 'error').mockImplementation(() => {});
    ed.insertQuote(QUOTE + '\n');
    expect(ta.value).toBe(QUOTE);
  });
});
