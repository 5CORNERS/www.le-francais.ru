import { Extension } from '@tiptap/core';
import { Selection, TextSelection } from '@tiptap/pm/state';
import { unwrapSpoilerAt } from './spoilerCommands.js';

// Toolbar shortcuts (legacy handleKeydown, forum-editor-legacy.js:1274-1360).
// `shift`: true = Shift required, false = Shift forbidden. `alt`: false =
// Alt forbidden, undefined = either. Keys are lower-cased `e.key` values,
// Latin and Cyrillic (ЙЦУКЕН) layouts.
const SHORTCUTS = [
  { cmd: 'strikethrough', shift: true, codes: ['KeyX'], keys: ['x', 'ч'] },
  { cmd: 'code', shift: true, codes: ['KeyM'], keys: ['m', 'ь'] },
  { cmd: 'spoiler', shift: true, codes: ['KeyP'], keys: ['p', 'з'] },
  { cmd: 'quote', shift: true, codes: ['Period'], keys: ['.', '>', 'ю'] },
  { cmd: 'removeFormat', shift: true, codes: ['KeyN'], keys: ['n', 'т'] },
  { cmd: 'removeFormat', shift: false, codes: ['Backslash'], keys: ['\\'] },
  { cmd: 'link', shift: false, alt: false, codes: ['KeyK'], keys: ['k', 'л'] },
  { cmd: 'bold', shift: false, alt: false, codes: ['KeyB'], keys: ['b', 'и'] },
  { cmd: 'italic', shift: false, alt: false, codes: ['KeyI'], keys: ['i', 'ш'] },
  { cmd: 'underline', shift: false, alt: false, codes: ['KeyU'], keys: ['u', 'г'] },
];

function modifiersMatch(row, e) {
  if (row.shift !== !!e.shiftKey) return false;
  if (row.alt === false && e.altKey) return false;
  return true;
}

/**
 * The toolbar command for a keydown event, or null. Matched by `e.code`
 * first (physical key, any layout), then by `e.key` (including the Cyrillic
 * letter). Ctrl/Cmd+6 and `^` are never intercepted (dead key).
 */
export function matchShortcut(e) {
  const code = e.code || '';
  const key = (e.key || '').toLowerCase();
  if (key === '6' || key === '^' || code === 'Digit6' || e.keyCode === 54) return null;

  // Google Docs: Alt+Shift+5 (with or without Ctrl/Cmd).
  if (e.altKey && e.shiftKey && (code === 'Digit5' || key === '5' || e.keyCode === 53)) return 'strikethrough';

  if (!e.ctrlKey && !e.metaKey) return null;
  let i;
  for (i = 0; i < SHORTCUTS.length; i++) {
    if (SHORTCUTS[i].codes.indexOf(code) >= 0 && modifiersMatch(SHORTCUTS[i], e)) return SHORTCUTS[i].cmd;
  }
  for (i = 0; i < SHORTCUTS.length; i++) {
    if (SHORTCUTS[i].keys.indexOf(key) >= 0 && modifiersMatch(SHORTCUTS[i], e)) return SHORTCUTS[i].cmd;
  }
  return null;
}

/**
 * Runs `onCommand(cmd)` for shortcut keydowns on `el`. The listener is on the
 * capture phase so it runs before ProseMirror's own keydown handling (which
 * then ignores the prevented event). Returns an unbind function.
 */
export function bindShortcuts(el, onCommand) {
  const handler = function (e) {
    if (e.isComposing) return;
    const cmd = matchShortcut(e);
    if (!cmd) return;
    e.preventDefault();
    e.stopPropagation();
    onCommand(cmd);
  };
  el.addEventListener('keydown', handler, true);
  return function () {
    el.removeEventListener('keydown', handler, true);
  };
}

/** Enter in a spoiler summary: caret to the start of the spoiler body. */
function summaryEnter(editor) {
  const state = editor.state;
  const $from = state.selection.$from;
  if ($from.parent.type.name !== 'spoilerSummary') return false;
  const bodyStart = $from.after() + 1;
  const $body = state.doc.resolve(bodyStart);
  const target = Selection.findFrom($body, 1, true) || TextSelection.near($body);
  editor.view.dispatch(state.tr.setSelection(target).scrollIntoView());
  return true;
}

/** ArrowRight at the end of a textblock leaves the marks (stored marks). */
function exitMarks(editor) {
  const state = editor.state;
  const $cursor = state.selection.$cursor;
  if (!$cursor || $cursor.parentOffset !== $cursor.parent.content.size) return false;
  const marks = state.storedMarks || $cursor.marks();
  if (!marks.length) return false;
  editor.view.dispatch(state.tr.setStoredMarks([]));
  return true;
}

/** Backspace at the start of a spoiler summary unwraps that spoiler. */
function summaryBackspace(editor) {
  const $cursor = editor.state.selection.$cursor;
  if (!$cursor || $cursor.parentOffset !== 0 || $cursor.parent.type.name !== 'spoilerSummary') return false;
  return unwrapSpoilerAt(editor, $cursor);
}

export const ForumKeys = Extension.create({
  name: 'forumKeys',
  // Ahead of the core keymap (Backspace/Enter) and list/code-block keys.
  priority: 1000,
  addKeyboardShortcuts() {
    return {
      Enter: ({ editor }) => summaryEnter(editor),
      ArrowRight: ({ editor }) => exitMarks(editor),
      Backspace: ({ editor }) => summaryBackspace(editor),
    };
  },
});
