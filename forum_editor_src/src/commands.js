import { Selection, TextSelection } from '@tiptap/pm/state';
import {
  wrapSelection,
  prefixLines,
  removeFormatting,
  toggleCode,
  insertSpoilerTemplate,
} from './markdownMode.js';
import { trimEnd, trimStart } from './blockRange.js';
import { toggleSpoiler } from './spoilerCommands.js';

/** Toolbar commands, in toolbar order (`data-cmd` values). */
export const COMMANDS = ['bold', 'italic', 'underline', 'strikethrough', 'mark', 'code', 'kbd', 'superscript', 'subscript', 'removeFormat', 'h2', 'h3', 'quote', 'ul', 'ol', 'spoiler', 'link', 'image'];

// Visual-mode mark per command; marks toggle stored marks on a collapsed caret.
const MARKS = {
  bold: 'bold',
  italic: 'italic',
  underline: 'underline',
  strikethrough: 'strike',
  mark: 'highlight',
  kbd: 'kbd',
  superscript: 'superscript',
  subscript: 'subscript',
};

// Markdown-mode syntax and placeholders (legacy executeMarkdownCommand).
const MD_WRAPS = {
  bold: ['**', '**', 'жирный текст'],
  // '*' (not legacy '_'): works inside words and matches the serializer.
  italic: ['*', '*', 'курсив'],
  underline: ['^^', '^^', 'подчеркнутый текст'],
  strikethrough: ['~~', '~~', 'зачеркнутый текст'],
  mark: ['==', '==', 'выделенный текст'],
  kbd: ['++', '++', 'Ctrl+C'],
  superscript: ['^', '^', '2'],
  subscript: ['~', '~', '2'],
};

const HEADING_PREFIX = /^#{1,6} /;
const LIST_PREFIX = /^(?:[-*+]|\d+[.)]) /;

const MD_PREFIXES = {
  h2: ['## ', 'Заголовок', HEADING_PREFIX],
  h3: ['### ', 'Подзаголовок', HEADING_PREFIX],
  quote: ['> ', 'Текст цитаты', null],
  ul: ['- ', 'Элемент списка', LIST_PREFIX],
  ol: [function (i) { return (i + 1) + '. '; }, 'Первый пункт', LIST_PREFIX],
};

function call(fn) {
  if (typeof fn === 'function') fn();
}

// --- Visual: code -----------------------------------------------------------

function hardBreakText(leaf) {
  return leaf.type.name === 'hardBreak' ? '\n' : '';
}

function unwrapCodeBlock(editor, $pos) {
  const schema = editor.schema;
  const depth = $pos.depth;
  const block = $pos.parent;
  const paragraphs = block.textContent.split('\n').map(function (line) {
    return schema.nodes.paragraph.create(null, line ? schema.text(line) : null);
  });
  const tr = editor.state.tr.replaceWith($pos.before(depth), $pos.after(depth), paragraphs);
  const caret = Math.min($pos.before(depth) + 1 + $pos.parentOffset, $pos.before(depth) + paragraphs[0].nodeSize - 1);
  tr.setSelection(TextSelection.near(tr.doc.resolve(caret)));
  editor.view.dispatch(tr.scrollIntoView());
}

/**
 * Converts the textblocks spanned by the selection into one code block.
 * Unselected text before/after the selection stays in its own block.
 */
function blocksToCodeBlock(editor, $from, $to) {
  const state = editor.state;
  const schema = state.schema;
  const sel = { from: $from.pos, to: $to.pos };

  const lines = [];
  state.doc.nodesBetween(sel.from, sel.to, function (node, pos) {
    if (node.type.name === 'rawMarkdownBlock') {
      lines.push(node.attrs.source || '');
      return false;
    }
    if (!node.isTextblock) return true;
    const start = Math.max(sel.from - pos - 1, 0);
    const end = Math.min(sel.to - pos - 1, node.content.size);
    lines.push(node.textBetween(start, end, '\n', hardBreakText));
    return false;
  });
  const codeText = lines.join('\n');

  const nodes = [];
  const fromBlock = $from.parent;
  const toBlock = $to.parent;
  const beforeEnd = fromBlock.isTextblock ? trimEnd(fromBlock, $from.parentOffset) : 0;
  const afterStart = toBlock.isTextblock ? trimStart(toBlock, $to.parentOffset) : toBlock.content.size;
  const hasBefore = beforeEnd > 0;
  const hasAfter = afterStart < toBlock.content.size;
  if (hasBefore) nodes.push(fromBlock.type.create(fromBlock.attrs, fromBlock.content.cut(0, beforeEnd)));
  nodes.push(schema.nodes.codeBlock.create(null, codeText ? schema.text(codeText) : null));
  if (hasAfter) nodes.push(toBlock.type.create(toBlock.attrs, toBlock.content.cut(afterStart)));

  // Replace whole textblocks; climb out of wrappers (list items…) that are
  // entirely covered so they are converted rather than left empty.
  const shared = $from.sharedDepth(sel.to);
  let d = $from.depth;
  let start = $from.before(d);
  if (!hasBefore) {
    while (d - 1 > shared && $from.index(d - 1) === 0) {
      d--;
      start = $from.before(d);
    }
  }
  d = $to.depth;
  let end = $to.after(d);
  if (!hasAfter) {
    while (d - 1 > shared && $to.index(d - 1) === $to.node(d - 1).childCount - 1) {
      d--;
      end = $to.after(d);
    }
  }

  const tr = state.tr.replaceWith(start, end, nodes);
  let codePos = -1;
  tr.doc.nodesBetween(start, tr.doc.content.size, function (node, pos) {
    if (codePos >= 0) return false;
    if (pos >= start && node.type.name === 'codeBlock' && node.textContent === codeText) {
      codePos = pos;
      return false;
    }
    return true;
  });
  if (codePos >= 0) {
    tr.setSelection(TextSelection.create(tr.doc, codePos + 1, codePos + 1 + codeText.length));
  }
  editor.view.dispatch(tr.scrollIntoView());
}

// Nodes a multi-block conversion may cut through or swallow. Anything else
// (images, spoilers) would be lost or restructured, so the command is a no-op.
const CODE_SAFE = ['text', 'hardBreak', 'rawMarkdownBlock', 'blockquote', 'bulletList', 'orderedList', 'listItem'];

function rangeIsCodeSafe(doc, from, to) {
  let safe = true;
  doc.nodesBetween(from, to, function (node, pos) {
    if (!safe) return false;
    // Ancestors of the whole range (e.g. the spoiler body holding it) are untouched.
    if (pos < from && pos + node.nodeSize > to) return true;
    if (node.isTextblock) return false;
    if (CODE_SAFE.indexOf(node.type.name) < 0) safe = false;
    return safe;
  });
  return safe;
}

/**
 * The selection as textblock positions: AllSelection / NodeSelection are
 * narrowed to the first and last text positions they cover, and a range that
 * starts in a spoiler summary and runs into the body is clamped to the body
 * (likewise a range ending in a summary stops before the spoiler).
 * Returns null when there is no usable text range.
 */
function codeRange(state) {
  const doc = state.doc;
  const sel = state.selection;
  let $from = sel.$from;
  let $to = sel.$to;
  if (!$from.parent.isTextblock || !$to.parent.isTextblock) {
    const t = TextSelection.between(doc.resolve(sel.from), doc.resolve(sel.to));
    $from = t.$from;
    $to = t.$to;
    if (!$from.parent.isTextblock || !$to.parent.isTextblock) return null;
  }
  if ($from.sameParent($to)) return { $from: $from, $to: $to };

  if ($from.parent.type.name === 'spoilerSummary') {
    const next = Selection.findFrom(doc.resolve($from.after()), 1, true);
    if (!next || next.from >= $to.pos) return null;
    $from = next.$from;
  }
  if ($to.parent.type.name === 'spoilerSummary') {
    const prev = Selection.findFrom(doc.resolve($to.before($to.depth - 1)), -1, true);
    if (!prev || prev.to <= $from.pos) return null;
    $to = prev.$to;
  }
  if (!$from.parent.isTextblock || !$to.parent.isTextblock) return null;
  return { $from: $from, $to: $to };
}

function toggleVisualCode(editor) {
  const range = codeRange(editor.state);
  if (!range) return;
  const $from = range.$from;
  const $to = range.$to;
  if ($from.sameParent($to)) {
    if ($from.parent.type.name === 'codeBlock') {
      unwrapCodeBlock(editor, $from);
      return;
    }
    const sel = editor.state.selection;
    if (sel.from !== $from.pos || sel.to !== $to.pos || !(sel instanceof TextSelection)) {
      editor.view.dispatch(editor.state.tr.setSelection(TextSelection.create(editor.state.doc, $from.pos, $to.pos)));
    }
    editor.commands.toggleMark('code');
    return;
  }
  if (!rangeIsCodeSafe(editor.state.doc, $from.pos, $to.pos)) return;
  blocksToCodeBlock(editor, $from, $to);
}

// --- Visual: remove formatting ------------------------------------------------

/**
 * Drops every mark (links included) from the selection; block structure is
 * kept. A selection inside one code block unwraps it (legacy parity).
 */
function removeFormatVisual(editor) {
  const sel = editor.state.selection;
  if (sel.$from.sameParent(sel.$to) && sel.$from.parent.type.name === 'codeBlock') {
    unwrapCodeBlock(editor, sel.$from);
    return;
  }
  editor.commands.unsetAllMarks();
}

// --- Public API -------------------------------------------------------------

/** Runs a toolbar command on the TipTap editor. */
export function runVisualCommand(editor, cmd, ctx) {
  const c = ctx || {};
  if (cmd === 'link') { call(c.openLinkModal); return; }
  if (cmd === 'image') { call(c.openFilePicker); return; }

  editor.commands.focus();
  if (MARKS[cmd]) {
    editor.commands.toggleMark(MARKS[cmd]);
    return;
  }
  switch (cmd) {
    case 'code': toggleVisualCode(editor); break;
    case 'removeFormat': removeFormatVisual(editor); break;
    case 'h2': editor.commands.toggleHeading({ level: 2 }); break;
    case 'h3': editor.commands.toggleHeading({ level: 3 }); break;
    case 'quote': editor.commands.toggleBlockquote(); break;
    case 'ul': editor.commands.toggleBulletList(); break;
    case 'ol': editor.commands.toggleOrderedList(); break;
    case 'spoiler': toggleSpoiler(editor); break;
    default: break;
  }
}

/** Computes the Markdown-mode transform for `cmd`, or null if it has none. */
function markdownTransform(cmd, text, start, end) {
  if (MD_WRAPS[cmd]) {
    const w = MD_WRAPS[cmd];
    return wrapSelection(text, start, end, w[0], w[1], w[2]);
  }
  if (MD_PREFIXES[cmd]) {
    const p = MD_PREFIXES[cmd];
    return prefixLines(text, start, end, p[0], p[1], p[2]);
  }
  switch (cmd) {
    case 'code': return toggleCode(text, start, end);
    case 'removeFormat': return removeFormatting(text, start, end);
    case 'spoiler': return insertSpoilerTemplate(text, start, end);
    default: return null;
  }
}

/**
 * Writes `newText` into the textarea by replacing only the changed span
 * (setRangeText), then dispatches `input`.
 */
function applyToTextarea(textarea, newText, selStart, selEnd) {
  const old = textarea.value;
  if (old !== newText) {
    let pre = 0;
    const max = Math.min(old.length, newText.length);
    while (pre < max && old.charCodeAt(pre) === newText.charCodeAt(pre)) pre++;
    let suf = 0;
    while (suf < max - pre && old.charCodeAt(old.length - 1 - suf) === newText.charCodeAt(newText.length - 1 - suf)) suf++;
    textarea.setRangeText(newText.slice(pre, newText.length - suf), pre, old.length - suf);
  }
  textarea.focus();
  textarea.setSelectionRange(selStart, selEnd);
  if (old !== newText) textarea.dispatchEvent(new Event('input', { bubbles: true }));
}

/** Runs a toolbar command on the Markdown textarea. */
export function runMarkdownCommand(textarea, cmd, ctx) {
  const c = ctx || {};
  if (cmd === 'link') { call(c.openLinkModal); return; }
  if (cmd === 'image') { call(c.openFilePicker); return; }
  const text = textarea.value;
  const start = textarea.selectionStart;
  const end = textarea.selectionEnd;
  const r = markdownTransform(cmd, text, Math.min(start, end), Math.max(start, end));
  if (!r) return;
  applyToTextarea(textarea, r.text, r.selStart, r.selEnd);
}

/** Whether the toolbar button for `cmd` should show as active. */
export function isCommandActive(editor, cmd) {
  if (!editor) return false;
  if (MARKS[cmd]) return editor.isActive(MARKS[cmd]);
  switch (cmd) {
    case 'code': return editor.isActive('code') || editor.isActive('codeBlock');
    case 'h2': return editor.isActive('heading', { level: 2 });
    case 'h3': return editor.isActive('heading', { level: 3 });
    case 'quote': return editor.isActive('blockquote');
    case 'ul': return editor.isActive('bulletList');
    case 'ol': return editor.isActive('orderedList');
    case 'spoiler': return editor.isActive('spoiler');
    case 'link': return editor.isActive('link');
    default: return false;
  }
}
