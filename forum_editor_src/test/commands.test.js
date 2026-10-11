import { describe, test, expect, beforeEach, afterEach, vi } from 'vitest';
import { COMMANDS, runVisualCommand, runMarkdownCommand, isCommandActive } from '../src/commands.js';
import { updateActiveStates } from '../src/ui/toolbar.js';
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
    expect(ed.getMarkdown()).toContain('- a');
    expect(ed.getMarkdown()).toContain('- d');
    expect(ed.getMarkdown()).toContain('```\nb\nc\n```');
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

  test('runMarkdownCommand link delegates to ctx', () => {
    const ta = document.createElement('textarea');
    document.body.appendChild(ta);
    runMarkdownCommand(ta, 'link', ctx);
    runMarkdownCommand(ta, 'image', ctx);
    expect(ctx.openLinkModal).toHaveBeenCalledTimes(1);
    expect(ctx.openFilePicker).toHaveBeenCalledTimes(1);
  });
});
