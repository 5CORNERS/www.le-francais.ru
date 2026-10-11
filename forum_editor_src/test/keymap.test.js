import { describe, test, expect, afterEach, vi } from 'vitest';
import { NodeSelection, AllSelection } from '@tiptap/pm/state';
import { matchShortcut, bindShortcuts } from '../src/keymap.js';
import { makeEditor, destroyEditors, selectText } from './helpers.js';

afterEach(() => {
  destroyEditors();
  vi.restoreAllMocks();
  document.body.innerHTML = '';
  localStorage.clear();
});

function key(code, k, mods) {
  return new KeyboardEvent('keydown', Object.assign({ code: code, key: k, cancelable: true, bubbles: true }, mods || {}));
}

const CTRL = { ctrlKey: true };
const CTRL_SHIFT = { ctrlKey: true, shiftKey: true };

// [label, code, latin key, cyrillic key (or null), modifiers, command]
const ROWS = [
  ['Mod+B', 'KeyB', 'b', 'и', CTRL, 'bold'],
  ['Mod+I', 'KeyI', 'i', 'ш', CTRL, 'italic'],
  ['Mod+U', 'KeyU', 'u', 'г', CTRL, 'underline'],
  ['Mod+K', 'KeyK', 'k', 'л', CTRL, 'link'],
  ['Mod+Shift+X', 'KeyX', 'X', 'Ч', CTRL_SHIFT, 'strikethrough'],
  ['Alt+Shift+5', 'Digit5', '5', null, { altKey: true, shiftKey: true }, 'strikethrough'],
  ['Mod+Shift+M', 'KeyM', 'M', 'Ь', CTRL_SHIFT, 'code'],
  ['Mod+Shift+P', 'KeyP', 'P', 'З', CTRL_SHIFT, 'spoiler'],
  ['Mod+Shift+.', 'Period', '>', 'Ю', CTRL_SHIFT, 'quote'],
  ['Mod+Shift+N', 'KeyN', 'N', 'Т', CTRL_SHIFT, 'removeFormat'],
  ['Mod+\\', 'Backslash', '\\', null, CTRL, 'removeFormat'],
  ['Mod+6', 'Digit6', '6', null, CTRL, null],
  ['Mod+Shift+6 (^)', 'Digit6', '^', null, CTRL_SHIFT, null],
  ['^ alone', 'Digit6', '^', null, { shiftKey: true }, null],
];

describe('matchShortcut', () => {
  test.each(ROWS)('%s by code', (label, code, latin, cyr, mods, cmd) => {
    expect(matchShortcut(key(code, latin, mods))).toBe(cmd);
  });

  test.each(ROWS)('%s by key only (no code), Latin and Cyrillic', (label, code, latin, cyr, mods, cmd) => {
    expect(matchShortcut(key('', latin, mods))).toBe(cmd);
    if (cyr) expect(matchShortcut(key('', cyr, mods))).toBe(cmd);
  });

  test.each(ROWS.filter((r) => r[3]))('%s on a Cyrillic layout (physical code + Cyrillic key)', (label, code, latin, cyr, mods, cmd) => {
    expect(matchShortcut(key(code, cyr, mods))).toBe(cmd);
  });

  test('Mod+Shift+. also matches the "." and "ю" keys', () => {
    expect(matchShortcut(key('', '.', CTRL_SHIFT))).toBe('quote');
    expect(matchShortcut(key('', 'ю', CTRL_SHIFT))).toBe('quote');
  });

  test('legacy keyCode is the last fallback', () => {
    expect(matchShortcut(key('', '', { ctrlKey: true, keyCode: 66 }))).toBe('bold');
    expect(matchShortcut(key('', 'Unidentified', { ctrlKey: true, shiftKey: true, keyCode: 190 }))).toBe('quote');
    expect(matchShortcut(key('', '', { altKey: true, shiftKey: true, keyCode: 53 }))).toBe('strikethrough');
    expect(matchShortcut(key('', '', { ctrlKey: true, shiftKey: true, keyCode: 66 }))).toBe(null);
  });

  test('metaKey works like ctrlKey', () => {
    expect(matchShortcut(key('KeyB', 'b', { metaKey: true }))).toBe('bold');
    expect(matchShortcut(key('KeyP', 'P', { metaKey: true, shiftKey: true }))).toBe('spoiler');
  });

  test('plain keys, Shift-less shift rows and Alt variants are not shortcuts', () => {
    expect(matchShortcut(key('KeyB', 'b'))).toBe(null);
    expect(matchShortcut(key('KeyX', 'x', CTRL))).toBe(null);
    expect(matchShortcut(key('KeyB', 'B', CTRL_SHIFT))).toBe(null);
    expect(matchShortcut(key('KeyB', 'b', { ctrlKey: true, altKey: true }))).toBe(null);
    expect(matchShortcut(key('KeyA', 'a', CTRL))).toBe(null);
    expect(matchShortcut(key('KeyZ', 'z', CTRL))).toBe(null);
  });
});

describe('bindShortcuts', () => {
  test('runs the command and prevents the default', () => {
    const el = document.createElement('div');
    document.body.appendChild(el);
    const onCommand = vi.fn();
    const unbind = bindShortcuts(el, onCommand);
    const ev = key('KeyB', 'b', CTRL);
    el.dispatchEvent(ev);
    expect(onCommand).toHaveBeenCalledWith('bold');
    expect(ev.defaultPrevented).toBe(true);
    const other = key('KeyZ', 'z', CTRL);
    el.dispatchEvent(other);
    expect(other.defaultPrevented).toBe(false);
    unbind();
    el.dispatchEvent(key('KeyB', 'b', CTRL));
    expect(onCommand).toHaveBeenCalledTimes(1);
  });

  test('Ctrl+B in the visual editor toggles bold exactly once', () => {
    const ed = makeEditor('word');
    selectText(ed, 'word', 'word');
    ed.element.dispatchEvent(key('KeyB', 'b', CTRL));
    expect(ed.getMarkdown()).toBe('**word**');
  });

  test('Ctrl+Shift+X with a Cyrillic layout strikes in the visual editor', () => {
    const ed = makeEditor('word');
    selectText(ed, 'word', 'word');
    ed.element.dispatchEvent(key('KeyX', 'Ч', CTRL_SHIFT));
    expect(ed.getMarkdown()).toBe('~~word~~');
  });

  test('shortcuts work in the Markdown textarea', () => {
    const ed = makeEditor('a b', 'markdown');
    const ta = ed.dom.container.querySelector('textarea');
    ta.setSelectionRange(2, 3);
    const ev = key('KeyB', 'b', CTRL);
    ta.dispatchEvent(ev);
    expect(ta.value).toBe('a **b**');
    expect(ev.defaultPrevented).toBe(true);
  });

  test.each([
    ['Ctrl+E', 'KeyE', 'e', CTRL],
    ['Ctrl+.', 'Period', '.', CTRL],
    ['Ctrl+,', 'Comma', ',', CTRL],
    ['Ctrl+Shift+B', 'KeyB', 'B', CTRL_SHIFT],
    ['Ctrl+Shift+S', 'KeyS', 'S', { ctrlKey: true, shiftKey: true, keyCode: 83 }],
    ['Ctrl+Shift+H', 'KeyH', 'H', { ctrlKey: true, shiftKey: true, keyCode: 72 }],
    ['Ctrl+Shift+7', 'Digit7', '&', { ctrlKey: true, shiftKey: true, keyCode: 55 }],
    ['Ctrl+Shift+8', 'Digit8', '*', { ctrlKey: true, shiftKey: true, keyCode: 56 }],
    ['Ctrl+Alt+2', 'Digit2', '2', { ctrlKey: true, altKey: true }],
    ['Ctrl+Alt+0', 'Digit0', '0', { ctrlKey: true, altKey: true }],
    ['Ctrl+Alt+C', 'KeyC', 'c', { ctrlKey: true, altKey: true }],
  ])('TipTap built-in shortcut %s does nothing (legacy parity)', (label, code, k, mods) => {
    const ed = makeEditor('- word');
    selectText(ed, 'word', 'word');
    ed.element.dispatchEvent(key(code, k, mods));
    expect(ed.getMarkdown()).toBe('- word');
  });

  test('Ctrl+B/I/U and Ctrl+Z/Ctrl+Y still work in the visual editor', () => {
    const ed = makeEditor('word');
    selectText(ed, 'word', 'word');
    ed.element.dispatchEvent(key('KeyI', 'i', CTRL));
    ed.element.dispatchEvent(key('KeyU', 'u', CTRL));
    expect(ed.getMarkdown()).toBe('*^^word^^*');
    ed.element.dispatchEvent(key('KeyZ', 'z', CTRL));
    ed.element.dispatchEvent(key('KeyZ', 'z', CTRL));
    expect(ed.getMarkdown()).toBe('word');
    ed.element.dispatchEvent(key('KeyY', 'y', CTRL));
    expect(ed.getMarkdown()).not.toBe('word');
  });

  test('Enter in a list item still splits it', () => {
    const ed = makeEditor('- ab');
    ed.tiptap.commands.setTextSelection(4);
    ed.tiptap.view.someProp('handleKeyDown', (f) => f(ed.tiptap.view, new KeyboardEvent('keydown', { key: 'Enter' })));
    expect(ed.tiptap.state.doc.firstChild.childCount).toBe(2);
  });

  test('Ctrl+6 is never intercepted', () => {
    const ed = makeEditor('a', 'markdown');
    const ta = ed.dom.container.querySelector('textarea');
    const ev = key('Digit6', '6', CTRL);
    ta.dispatchEvent(ev);
    expect(ev.defaultPrevented).toBe(false);
  });
});

function press(ed, k) {
  const view = ed.tiptap.view;
  return view.someProp('handleKeyDown', (f) => f(view, new KeyboardEvent('keydown', { key: k })));
}

describe('ForumKeys', () => {
  test('Enter in spoiler summary jumps into body', () => {
    const ed = makeEditor('???- "T"\n    body'); ed.tiptap.commands.setTextSelection(3); // inside summary text
    ed.tiptap.view.someProp('handleKeyDown', f => f(ed.tiptap.view, new KeyboardEvent('keydown', { key: 'Enter' })));
    expect(ed.tiptap.state.selection.$from.parent.textContent).toBe('body');
    expect(ed.getMarkdown()).toBe('???- "T"\n    body');
  });

  test('Enter in a summary whose body starts with an image goes to the first text in the body', () => {
    const ed = makeEditor('???- "T"\n    ![i](http://i/x.png)\n\n    after\n\nout');
    ed.tiptap.commands.setTextSelection(2);
    press(ed, 'Enter');
    expect(ed.tiptap.state.selection.$from.parent.textContent).toBe('after');
  });

  test('Enter in a summary whose body is only an image selects the image', () => {
    const ed = makeEditor('???- "T"\n    ![i](http://i/x.png)\n\nout');
    ed.tiptap.commands.setTextSelection(2);
    press(ed, 'Enter');
    const sel = ed.tiptap.state.selection;
    expect(sel.node && sel.node.type.name).toBe('image');
    expect(ed.getMarkdown()).toBe('???- "T"\n    ![i](http://i/x.png)\n\nout');
  });

  test('ArrowRight at end of bold exits the mark without inserting characters', () => {
    const ed = makeEditor('**ab**'); ed.tiptap.commands.setTextSelection(3);
    ed.tiptap.view.someProp('handleKeyDown', f => f(ed.tiptap.view, new KeyboardEvent('keydown', { key: 'ArrowRight' })));
    ed.tiptap.commands.insertContent('c');
    expect(ed.getMarkdown()).toBe('**ab**c');
  });

  test('ArrowRight is left alone mid-text and after the marks were cleared', () => {
    const ed = makeEditor('**ab**\n\nx');
    ed.tiptap.commands.setTextSelection(2);
    expect(press(ed, 'ArrowRight')).toBeFalsy();
    ed.tiptap.commands.setTextSelection(3);
    expect(press(ed, 'ArrowRight')).toBe(true);
    // Second press: marks already cleared, default caret movement applies.
    expect(press(ed, 'ArrowRight')).toBeFalsy();
  });

  test('Backspace at the start of a spoiler summary unwraps the spoiler', () => {
    const ed = makeEditor('a\n\n???- "T *i*"\n    body\n\n    - x\n\nz');
    ed.tiptap.commands.setTextSelection(5); // start of summary
    expect(ed.tiptap.state.selection.$from.parent.type.name).toBe('spoilerSummary');
    expect(press(ed, 'Backspace')).toBe(true);
    expect(ed.getMarkdown()).toBe('a\n\nT *i*\n\nbody\n\n- x\n\nz');
    const $from = ed.tiptap.state.selection.$from;
    expect($from.parent.textContent).toBe('T i');
    expect($from.parentOffset).toBe(0);
  });

  test('Backspace in an empty summary drops it; caret goes to the first body block', () => {
    const ed = makeEditor('???- ""\n    body');
    ed.tiptap.commands.setTextSelection(2);
    expect(ed.tiptap.state.selection.$from.parent.type.name).toBe('spoilerSummary');
    expect(press(ed, 'Backspace')).toBe(true);
    expect(ed.getMarkdown()).toBe('body');
    expect(ed.tiptap.state.selection.$from.parent.textContent).toBe('body');
  });

  test('Backspace in a fully empty spoiler leaves one empty paragraph', () => {
    const ed = makeEditor('');
    ed.executeCommand('spoiler');
    // insertSpoiler on an empty doc: [spoiler, paragraph]; drop the trailing paragraph check.
    expect(press(ed, 'Backspace')).toBe(true);
    const doc = ed.tiptap.state.doc;
    expect(doc.firstChild.type.name).toBe('paragraph');
    expect(doc.firstChild.content.size).toBe(0);
    expect(doc.textContent).toBe('');
    let spoilers = 0;
    doc.descendants((n) => { if (n.type.name === 'spoiler') spoilers++; });
    expect(spoilers).toBe(0);
  });

  test('Backspace in a nested spoiler summary unwraps only the inner spoiler', () => {
    const ed = makeEditor('???- "outer"\n    ???- "inner"\n        deep');
    let innerSummary = -1;
    ed.tiptap.state.doc.descendants((n, pos) => {
      if (n.type.name === 'spoilerSummary' && n.textContent === 'inner') innerSummary = pos;
    });
    ed.tiptap.commands.setTextSelection(innerSummary + 1);
    expect(press(ed, 'Backspace')).toBe(true);
    expect(ed.getMarkdown()).toBe('???- "outer"\n    inner\n\n    deep');
  });

  test('Backspace inside summary text (not at start) keeps the default', () => {
    const ed = makeEditor('???- "Tx"\n    body');
    ed.tiptap.commands.setTextSelection(3);
    // No key handler claims it: the browser deletes the character natively.
    expect(press(ed, 'Backspace')).toBeFalsy();
    expect(ed.getMarkdown()).toBe('???- "Tx"\n    body');
  });

  test('a selected spoiler is removed by Backspace (default behaviour)', () => {
    const ed = makeEditor('a\n\n???- "T"\n    body\n\nb');
    const pos = ed.tiptap.state.doc.firstChild.nodeSize;
    ed.tiptap.view.dispatch(ed.tiptap.state.tr.setSelection(NodeSelection.create(ed.tiptap.state.doc, pos)));
    press(ed, 'Backspace');
    expect(ed.getMarkdown()).toBe('a\n\nb');
  });

  test('a text selection from before to after a spoiler is removed by Delete', () => {
    const ed = makeEditor('xa\n\n???- "T"\n    body\n\nqy');
    selectText(ed, 'a', 'q');
    press(ed, 'Delete');
    expect(ed.getMarkdown()).toBe('xy');
  });

  test('select-all + Backspace removes a spoiler', () => {
    const ed = makeEditor('???- "T"\n    body');
    ed.tiptap.view.dispatch(ed.tiptap.state.tr.setSelection(new AllSelection(ed.tiptap.state.doc)));
    press(ed, 'Backspace');
    expect(ed.getMarkdown()).toBe('');
  });
});
