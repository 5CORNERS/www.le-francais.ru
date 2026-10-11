import { describe, test, expect, beforeEach, afterEach, vi } from 'vitest';
import { COMMANDS, runVisualCommand, runMarkdownCommand, isCommandActive } from '../src/commands.js';
import { updateActiveStates } from '../src/ui/toolbar.js';
import { AllSelection } from '@tiptap/pm/state';
import { makeEditor, destroyEditors, selectText } from './helpers.js';

let ed;
let ctx;

beforeEach(() => {
  localStorage.clear();
  ed = makeEditor('');
  ctx = { openLinkModal: vi.fn(), openFilePicker: vi.fn() };
});

afterEach(() => {
  destroyEditors();
  vi.restoreAllMocks();
  document.body.innerHTML = '';
});

describe('visual commands', () => {
  test('COMMANDS lists the 18 toolbar commands', () => {
    expect(COMMANDS).toEqual(['bold', 'italic', 'underline', 'strikethrough', 'mark', 'code', 'kbd', 'superscript', 'subscript', 'removeFormat', 'h2', 'h3', 'quote', 'ul', 'ol', 'spoiler', 'link', 'image']);
    const cmds = Array.from(ed.dom.toolbar.querySelectorAll('[data-cmd]')).map((b) => b.getAttribute('data-cmd'));
    expect(cmds).toEqual(COMMANDS);
  });

  test('multi-block code keeps unselected text (review bug 3)', () => {
    ed.setMarkdown('alpha beta\n\ngamma delta');
    selectText(ed, 'beta', 'gamma');
    runVisualCommand(ed.tiptap, 'code', ctx);
    expect(ed.getMarkdown()).toBe('alpha\n\n```\nbeta\ngamma\n```\n\ndelta');
  });

  test('code across two list items converts only those items', () => {
    ed.setMarkdown('- a\n- b\n- c\n- d');
    selectText(ed, 'b', 'c');
    runVisualCommand(ed.tiptap, 'code', ctx);
    expect(ed.getMarkdown()).toBe('- a\n\n```\nb\nc\n```\n\n- d');
  });

  test('code on AllSelection over two paragraphs makes one code block (review fix 3)', () => {
    ed.setMarkdown('p1 one\n\np2 two');
    ed.tiptap.view.dispatch(ed.tiptap.state.tr.setSelection(new AllSelection(ed.tiptap.state.doc)));
    runVisualCommand(ed.tiptap, 'code', ctx);
    expect(ed.getMarkdown()).toBe('```\np1 one\np2 two\n```');
  });

  test('code on AllSelection over one paragraph toggles the inline mark', () => {
    ed.setMarkdown('word');
    ed.tiptap.view.dispatch(ed.tiptap.state.tr.setSelection(new AllSelection(ed.tiptap.state.doc)));
    runVisualCommand(ed.tiptap, 'code', ctx);
    expect(ed.getMarkdown()).toBe('`word`');
  });

  test('multi-block code over a block image is a no-op (review fix 4)', () => {
    const md = 'aa\n\n![x](http://i/x.png)\n\nbb';
    ed.setMarkdown(md);
    selectText(ed, 'aa', 'bb');
    runVisualCommand(ed.tiptap, 'code', ctx);
    expect(ed.getMarkdown()).toBe(md);
  });

  test('code from spoiler summary into body only converts the body (review fix 5)', () => {
    ed.setMarkdown('???- "title"\n    one\n\n    two');
    selectText(ed, 'itle', 'two');
    runVisualCommand(ed.tiptap, 'code', ctx);
    const spoiler = ed.tiptap.state.doc.firstChild;
    expect(spoiler.type.name).toBe('spoiler');
    expect(spoiler.firstChild.textContent).toBe('title');
    expect(ed.getMarkdown()).toBe('???- "title"\n    ```\n    one\n    two\n    ```');
  });

  test('code from outside a spoiler into its body is a no-op', () => {
    const md = 'intro\n\n???- "title"\n    one';
    ed.setMarkdown(md);
    selectText(ed, 'intro', 'one');
    runVisualCommand(ed.tiptap, 'code', ctx);
    expect(ed.getMarkdown()).toBe(md);
  });

  test('code inside a code block unwraps it into paragraphs', () => {
    ed.setMarkdown('```\nx\ny\n```');
    ed.tiptap.commands.setTextSelection(2);
    runVisualCommand(ed.tiptap, 'code', ctx);
    expect(ed.getMarkdown()).toBe('x\n\ny');
  });

  test('ctrl+b inside bold toggles stored mark, caret stays (review bug 10)', () => {
    ed.setMarkdown('**abcdef**');
    ed.tiptap.commands.setTextSelection(4);
    runVisualCommand(ed.tiptap, 'bold', ctx);
    ed.tiptap.commands.insertContent('X');
    expect(ed.getMarkdown()).toBe('**abc**X**def**');
  });

  test('empty spoiler survives an input event (review bug 2)', () => {
    ed.setMarkdown('');
    runVisualCommand(ed.tiptap, 'spoiler', ctx);
    ed.element.dispatchEvent(new Event('input', { bubbles: true }));
    expect(ed.tiptap.state.doc.firstChild.type.name).toBe('spoiler');
    expect(ed.tiptap.state.selection.$from.parent.type.name).toBe('spoilerSummary');
  });

  test('spoiler after text is inserted after the paragraph', () => {
    ed.setMarkdown('hello');
    ed.tiptap.commands.setTextSelection(6);
    runVisualCommand(ed.tiptap, 'spoiler', ctx);
    const doc = ed.tiptap.state.doc;
    expect(doc.child(0).textContent).toBe('hello');
    expect(doc.child(1).type.name).toBe('spoiler');
    expect(ed.tiptap.state.selection.$from.parent.type.name).toBe('spoilerSummary');
  });

  test('removeFormat clears marks and blocks', () => {
    ed.setMarkdown('## **a** b');
    selectText(ed, 'a', 'b');
    runVisualCommand(ed.tiptap, 'removeFormat', ctx);
    expect(ed.getMarkdown()).toBe('a b');
  });

  test('link and image delegate to ctx', () => {
    runVisualCommand(ed.tiptap, 'link', ctx);
    runVisualCommand(ed.tiptap, 'image', ctx);
    expect(ctx.openLinkModal).toHaveBeenCalledTimes(1);
    expect(ctx.openFilePicker).toHaveBeenCalledTimes(1);
  });

  test.each(COMMANDS.filter((c) => !['link', 'image', 'removeFormat', 'spoiler'].includes(c)))('%s toggles and is active', (cmd) => {
    ed.setMarkdown('word');
    selectText(ed, 'word', 'word');
    runVisualCommand(ed.tiptap, cmd, ctx);
    expect(isCommandActive(ed.tiptap, cmd)).toBe(true);
  });
});

describe('toolbar wiring', () => {
  test('clicking a toolbar button runs the command and sets active state', () => {
    ed.setMarkdown('word');
    selectText(ed, 'word', 'word');
    const btn = ed.dom.toolbar.querySelector('[data-cmd="bold"]');
    btn.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
    expect(ed.getMarkdown()).toBe('**word**');
    expect(btn.classList.contains('active')).toBe(true);
    expect(ed.dom.toolbar.querySelector('[data-cmd="italic"]').classList.contains('active')).toBe(false);
  });

  test('mousedown on toolbar buttons and emoji items is prevented', () => {
    ['.forum-editor-btn', '.forum-emoji-item', '.forum-emoji-close'].forEach((sel) => {
      const ev = new MouseEvent('mousedown', { bubbles: true, cancelable: true });
      ed.dom.wrapper.querySelector(sel).dispatchEvent(ev);
      expect(ev.defaultPrevented).toBe(true);
    });
  });

  test('updateActiveStates clears active without an editor', () => {
    const btn = ed.dom.toolbar.querySelector('[data-cmd="bold"]');
    btn.classList.add('active');
    updateActiveStates(ed.dom.toolbar, null);
    expect(btn.classList.contains('active')).toBe(false);
  });

  test('executeCommand in markdown mode edits the textarea', () => {
    ed.setMode('markdown');
    const ta = ed.dom.container.querySelector('textarea');
    ta.value = 'a b';
    ta.setSelectionRange(2, 3);
    const onInput = vi.fn();
    ta.addEventListener('input', onInput);
    ed.executeCommand('bold');
    expect(ta.value).toBe('a **b**');
    expect([ta.selectionStart, ta.selectionEnd]).toEqual([4, 5]);
    expect(onInput).toHaveBeenCalled();
  });

  test('markdown-mode italic inside a word uses * (review fix 1)', () => {
    ed.setMode('markdown');
    const ta = ed.dom.container.querySelector('textarea');
    ta.value = 'motifs';
    ta.setSelectionRange(3, 6);
    ed.executeCommand('italic');
    expect(ta.value).toBe('mot*ifs*');
  });

  test('runMarkdownCommand link delegates to ctx', () => {
    const ta = document.createElement('textarea');
    document.body.appendChild(ta);
    runMarkdownCommand(ta, 'link', ctx);
    runMarkdownCommand(ta, 'image', ctx);
    expect(ctx.openLinkModal).toHaveBeenCalledTimes(1);
    expect(ctx.openFilePicker).toHaveBeenCalledTimes(1);
  });
});
