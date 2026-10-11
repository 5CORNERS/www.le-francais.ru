// Visual-mode spoiler editing: insert, wrap a selection, unwrap (toggle).
// Imports nothing from the parser or schema (see blockRange.js).
import { Selection, TextSelection } from '@tiptap/pm/state';
import { trimEnd, trimStart } from './blockRange.js';

const SPOILER_PARTS = ['spoiler', 'spoilerSummary', 'spoilerBody'];
// Nodes whose children a new spoiler may be cut from.
const CONTAINERS = ['doc', 'spoilerBody'];

function emptySpoiler(schema, bodyNodes) {
  return schema.nodes.spoiler.create(null, [
    schema.nodes.spoilerSummary.create(),
    schema.nodes.spoilerBody.create(null, bodyNodes || schema.nodes.paragraph.create()),
  ]);
}

/** Depth of the innermost spoiler around `$pos`, or -1. */
export function spoilerDepth($pos) {
  for (let d = $pos.depth; d > 0; d--) {
    if ($pos.node(d).type.name === 'spoiler') return d;
  }
  return -1;
}

/**
 * Replaces the innermost spoiler around `$pos` by its summary (as a
 * paragraph, omitted when empty) followed by the body's blocks; the caret
 * goes to the start of the first resulting block. Returns false if `$pos` is
 * not inside a spoiler.
 */
export function unwrapSpoilerAt(editor, $pos) {
  const depth = spoilerDepth($pos);
  if (depth < 0) return false;
  const state = editor.state;
  const schema = state.schema;
  const spoiler = $pos.node(depth);
  const summary = spoiler.firstChild;
  const nodes = [];
  if (summary.content.size) nodes.push(schema.nodes.paragraph.create(null, summary.content));
  spoiler.lastChild.forEach(function (node) { nodes.push(node); });

  const start = $pos.before(depth);
  const tr = state.tr.replaceWith(start, $pos.after(depth), nodes);
  try {
    tr.doc.check();
  } catch (e) {
    return false;
  }
  const $start = tr.doc.resolve(start);
  tr.setSelection(Selection.findFrom($start, 1, true) || TextSelection.near($start));
  editor.view.dispatch(tr.scrollIntoView());
  return true;
}

/** Inserts an empty spoiler at the caret; the caret goes into its summary. */
function insertSpoiler(editor) {
  const state = editor.state;
  const schema = state.schema;
  const sel = state.selection;
  const spoiler = emptySpoiler(schema);
  const emptyP = function () { return schema.nodes.paragraph.create(); };

  // Each plan edits `tr` and returns the spoiler's position.
  function atCaret(tr) {
    const $pos = tr.doc.resolve(sel.to);
    const parent = $pos.parent;
    const depth = $pos.depth;
    if (!parent.isTextblock || depth === 0) throw new Error('no text caret');
    const before = $pos.before(depth);
    if (sel.empty && parent.type.name === 'paragraph' && parent.content.size === 0) {
      tr.replaceWith(before, $pos.after(depth), [spoiler, emptyP()]);
      return before;
    }
    if ($pos.parentOffset === 0) {
      tr.insert(before, spoiler);
      return before;
    }
    if ($pos.parentOffset === parent.content.size) {
      const at = $pos.after(depth);
      tr.insert(at, [spoiler, emptyP()]);
      return at;
    }
    tr.split(sel.to);
    tr.insert(sel.to + 1, spoiler);
    return sel.to + 1;
  }

  function afterTopLevelBlock(tr) {
    const at = sel.$to.depth > 0 ? sel.$to.after(1) : sel.to;
    tr.insert(at, [spoiler, emptyP()]);
    return at;
  }

  const plans = [atCaret, afterTopLevelBlock];
  for (let i = 0; i < plans.length; i++) {
    const tr = state.tr;
    try {
      const at = plans[i](tr);
      tr.doc.check();
      if (tr.doc.nodeAt(at).type.name !== 'spoiler') throw new Error('spoiler not placed');
      // Inside spoiler (+1), inside summary (+1).
      tr.setSelection(TextSelection.create(tr.doc, at + 2)).scrollIntoView();
    } catch (e) {
      continue;
    }
    editor.view.dispatch(tr);
    return;
  }
}

/**
 * The selection with spoiler summaries clamped away: a range starting in a
 * summary and running into the same spoiler's body starts at the body; a range
 * ending in a summary stops before that spoiler. Null when nothing is left.
 */
function wrapRange(doc, sel) {
  let $from = sel.$from;
  let $to = sel.$to;
  if ($from.parent.type.name === 'spoilerSummary' && $to.pos > $from.end()) {
    $from = doc.resolve($from.after() + 1);
  }
  if ($to.parent.type.name === 'spoilerSummary' && $from.pos < $to.start()) {
    $to = doc.resolve($to.before($to.depth - 1));
  }
  if ($from.pos >= $to.pos) return null;
  if ($from.parent.type.name === 'spoilerSummary' || $to.parent.type.name === 'spoilerSummary') return null;
  return { $from: $from, $to: $to };
}

function crossesSpoiler($pos, containerDepth) {
  for (let d = containerDepth + 1; d <= $pos.depth; d++) {
    if (SPOILER_PARTS.indexOf($pos.node(d).type.name) >= 0) return true;
  }
  return false;
}

/** Cut of textblock `node` between offsets, whitespace-trimmed, or null if empty. */
function cutText(node, from, to) {
  const s = trimStart(node, from);
  const e = Math.max(s, trimEnd(node, to));
  if (s >= e) return null;
  return node.copy(node.content.cut(s, e));
}

/**
 * Moves the selected blocks of the innermost doc/spoiler body into a new
 * spoiler. Partially selected paragraphs at the edges are cut (the unselected
 * text stays outside); lists, quotes, images and spoilers are moved whole. A
 * selection crossing a spoiler boundary is a no-op.
 */
function wrapInSpoiler(editor) {
  const state = editor.state;
  const range = wrapRange(state.doc, state.selection);
  if (!range) return;
  const $from = range.$from;
  const $to = range.$to;

  let cd = $from.sharedDepth($to.pos);
  while (cd > 0 && CONTAINERS.indexOf($from.node(cd).type.name) < 0) cd--;
  if (crossesSpoiler($from, cd) || crossesSpoiler($to, cd)) return;

  const container = $from.node(cd);
  const i0 = $from.index(cd);
  const i1 = $to.depth === cd ? $to.index(cd) - 1 : $to.index(cd);
  if (i1 < i0 || i1 >= container.childCount) return;
  const first = container.child(i0);
  const last = container.child(i1);
  const fromInText = $from.depth === cd + 1 && first.isTextblock;
  const toInText = $to.depth === cd + 1 && last.isTextblock;

  const body = [];
  for (let i = i0; i <= i1; i++) {
    const node = container.child(i);
    const cutStart = i === i0 && fromInText;
    const cutEnd = i === i1 && toInText;
    if (!cutStart && !cutEnd) {
      body.push(node);
      continue;
    }
    const piece = cutText(node, cutStart ? $from.parentOffset : 0, cutEnd ? $to.parentOffset : node.content.size);
    if (piece) body.push(piece);
  }
  const schema = state.schema;
  const nodes = [];
  let spoilerOffset = 0;
  if (fromInText) {
    const beforeEnd = trimEnd(first, $from.parentOffset);
    if (beforeEnd > 0) {
      const before = first.copy(first.content.cut(0, beforeEnd));
      nodes.push(before);
      spoilerOffset = before.nodeSize;
    }
  }
  nodes.push(emptySpoiler(schema, body.length ? body : null));
  if (toInText) {
    const afterStart = trimStart(last, $to.parentOffset);
    if (afterStart < last.content.size) nodes.push(last.copy(last.content.cut(afterStart)));
  }

  const start = $from.posAtIndex(i0, cd);
  const end = $from.posAtIndex(i1, cd) + last.nodeSize;
  const tr = state.tr.replaceWith(start, end, nodes);
  const at = start + spoilerOffset;
  try {
    tr.doc.check();
    if (tr.doc.nodeAt(at).type.name !== 'spoiler') return;
  } catch (e) {
    return;
  }
  tr.setSelection(TextSelection.create(tr.doc, at + 2));
  editor.view.dispatch(tr.scrollIntoView());
}

/**
 * The `spoiler` command: a caret inside a spoiler unwraps the innermost one,
 * any other caret inserts an empty spoiler, a selection is wrapped.
 */
export function toggleSpoiler(editor) {
  const sel = editor.state.selection;
  if (sel.empty) {
    if (!unwrapSpoilerAt(editor, sel.$from)) insertSpoiler(editor);
    return;
  }
  wrapInSpoiler(editor);
}
