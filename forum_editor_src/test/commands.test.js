import { describe, test, expect, beforeEach, afterEach, vi } from 'vitest';
import { COMMANDS, runVisualCommand, runMarkdownCommand, isCommandActive } from '../src/commands.js';
import { updateActiveStates } from '../src/ui/toolbar.js';
import { AllSelection } from '@tiptap/pm/state';
import { Node as PMNode } from '@tiptap/pm/model';
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

  test('spoiler wraps a multi-block selection; edge text stays outside; caret in summary', () => {
    ed.setMarkdown('alpha beta\n\ngamma delta');
    selectText(ed, 'beta', 'gamma');
    runVisualCommand(ed.tiptap, 'spoiler', ctx);
    expect(ed.getMarkdown()).toBe('alpha\n\n???- ""\n    beta\n\n    gamma\n\ndelta');
    const sel = ed.tiptap.state.selection;
    expect(sel.empty).toBe(true);
    expect(sel.$from.parent.type.name).toBe('spoilerSummary');
  });

  test('spoiler wraps part of one paragraph and keeps marks', () => {
    ed.setMarkdown('a **bold** *it* c');
    selectText(ed, 'bold', 'it');
    runVisualCommand(ed.tiptap, 'spoiler', ctx);
    expect(ed.getMarkdown()).toBe('a\n\n???- ""\n    **bold** *it*\n\nc');
  });

  test('spoiler wraps a whole paragraph without empty neighbours', () => {
    ed.setMarkdown('one\n\ntwo\n\nthree');
    selectText(ed, 'two', 'two');
    runVisualCommand(ed.tiptap, 'spoiler', ctx);
    expect(ed.getMarkdown()).toBe('one\n\n???- ""\n    two\n\nthree');
  });

  test('spoiler moves lists, images, quotes and spoilers intact', () => {
    ed.setMarkdown('x\n\n- a\n- b\n\n![i](http://i/x.png)\n\n> q\n\n???- "T"\n    s\n\ny z');
    selectText(ed, 'b', 'y');
    runVisualCommand(ed.tiptap, 'spoiler', ctx);
    expect(ed.getMarkdown()).toBe('x\n\n???- ""\n    - a\n    - b\n\n    ![i](http://i/x.png)\n\n    > q\n\n    ???- "T"\n        s\n\n    y\n\nz');
  });

  test('spoiler on a selection inside a spoiler body nests within that body', () => {
    ed.setMarkdown('???- "T"\n    one two\n\n    three');
    selectText(ed, 'two', 'two');
    runVisualCommand(ed.tiptap, 'spoiler', ctx);
    expect(ed.getMarkdown()).toBe('???- "T"\n    one\n\n    ???- ""\n        two\n\n    three');
    expect(ed.tiptap.state.selection.$from.parent.type.name).toBe('spoilerSummary');
  });

  test('spoiler from a summary into its body wraps only body content', () => {
    ed.setMarkdown('???- "title"\n    one\n\n    two');
    selectText(ed, 'itle', 'one');
    runVisualCommand(ed.tiptap, 'spoiler', ctx);
    expect(ed.getMarkdown()).toBe('???- "title"\n    ???- ""\n        one\n\n    two');
  });

  test.each([
    ['outside into a spoiler body', 'intro\n\n???- "title"\n    one', 'intro', 'one'],
    ['a spoiler body out of it', '???- "title"\n    one\n\nafter', 'one', 'after'],
    ['one spoiler into another', '???- "A"\n    one\n\n???- "B"\n    two', 'one', 'two'],
    ['inside one summary', '???- "title"\n    one', 'it', 'le'],
  ])('spoiler crossing a spoiler boundary is a no-op: %s', (label, md, a, b) => {
    ed.setMarkdown(md);
    selectText(ed, a, b);
    runVisualCommand(ed.tiptap, 'spoiler', ctx);
    expect(ed.getMarkdown()).toBe(md);
  });

  test('spoiler with a caret inside a spoiler unwraps it (toggle) and is active there', () => {
    ed.setMarkdown('a\n\n???- "Title"\n    body\n\n    more\n\nz');
    selectText(ed, 'more', 'more');
    ed.tiptap.commands.setTextSelection(ed.tiptap.state.selection.from + 1);
    expect(isCommandActive(ed.tiptap, 'spoiler')).toBe(true);
    runVisualCommand(ed.tiptap, 'spoiler', ctx);
    expect(ed.getMarkdown()).toBe('a\n\nTitle\n\nbody\n\nmore\n\nz');
    expect(isCommandActive(ed.tiptap, 'spoiler')).toBe(false);
    const $from = ed.tiptap.state.selection.$from;
    expect($from.parent.textContent).toBe('Title');
    expect($from.parentOffset).toBe(0);
  });

  test('spoiler moves a code block at a selection edge whole, keeping indentation', () => {
    ed.setMarkdown('```\nline1\n  line2\n```\n\npara');
    selectText(ed, 'line2', 'para');
    runVisualCommand(ed.tiptap, 'spoiler', ctx);
    expect(ed.getMarkdown()).toBe('???- ""\n    ```\n    line1\n      line2\n    ```\n\n    para');
  });

  test('spoiler ending inside a code block moves it whole', () => {
    ed.setMarkdown('intro text\n\n```\n  a\n  b\n```');
    selectText(ed, 'text', 'a');
    runVisualCommand(ed.tiptap, 'spoiler', ctx);
    expect(ed.getMarkdown()).toBe('intro\n\n???- ""\n    text\n\n    ```\n      a\n      b\n    ```');
  });

  test('a failed unwrap does nothing (no spoiler is inserted instead)', () => {
    ed.setMarkdown('???- "T"\n    body');
    selectText(ed, 'body', 'body');
    ed.tiptap.commands.setTextSelection(ed.tiptap.state.selection.from);
    const before = ed.tiptap.state.doc;
    vi.spyOn(PMNode.prototype, 'check').mockImplementationOnce(() => { throw new Error('invalid'); });
    runVisualCommand(ed.tiptap, 'spoiler', ctx);
    expect(ed.tiptap.state.doc.eq(before)).toBe(true);
  });

  test('spoiler toggle in a nested spoiler unwraps the innermost one', () => {
    ed.setMarkdown('???- "outer"\n    ???- "inner"\n        deep');
    selectText(ed, 'deep', 'deep');
    ed.tiptap.commands.setTextSelection(ed.tiptap.state.selection.from);
    runVisualCommand(ed.tiptap, 'spoiler', ctx);
    expect(ed.getMarkdown()).toBe('???- "outer"\n    inner\n\n    deep');
  });

  test('spoiler toggle on an empty spoiler leaves an empty paragraph', () => {
    ed.setMarkdown('a');
    ed.tiptap.commands.setTextSelection(2);
    runVisualCommand(ed.tiptap, 'spoiler', ctx);
    expect(ed.tiptap.state.selection.$from.parent.type.name).toBe('spoilerSummary');
    runVisualCommand(ed.tiptap, 'spoiler', ctx);
    const doc = ed.tiptap.state.doc;
    expect(doc.childCount).toBe(3);
    expect(doc.child(1).type.name).toBe('paragraph');
    expect(doc.child(1).content.size).toBe(0);
    expect(ed.tiptap.state.selection.$from.parent).toBe(doc.child(1));
  });

  test('removeFormat clears marks but keeps block structure (final review 3)', () => {
    ed.setMarkdown('## **a** [b](https://x.y)');
    selectText(ed, 'a', 'b');
    runVisualCommand(ed.tiptap, 'removeFormat', ctx);
    expect(ed.getMarkdown()).toBe('## a b');
  });

  test('removeFormat inside a list keeps the list (final review 3)', () => {
    ed.setMarkdown('- **one**\n- two');
    selectText(ed, 'one', 'one');
    runVisualCommand(ed.tiptap, 'removeFormat', ctx);
    expect(ed.getMarkdown()).toBe('- one\n- two');
  });

  test('removeFormat inside a quote keeps the quote (final review 3)', () => {
    ed.setMarkdown('> **bob**: x');
    selectText(ed, 'bob', 'bob');
    runVisualCommand(ed.tiptap, 'removeFormat', ctx);
    expect(ed.getMarkdown()).toBe('> bob: x');
  });

  test('removeFormat inside a code block unwraps it (legacy parity)', () => {
    ed.setMarkdown('```\nx\ny\n```');
    selectText(ed, 'x', 'x');
    runVisualCommand(ed.tiptap, 'removeFormat', ctx);
    expect(ed.tiptap.state.doc.child(0).type.name).toBe('paragraph');
    expect(ed.getMarkdown()).toBe('x\n\ny');
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
