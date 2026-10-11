// Pure Markdown-mode transforms for the textarea. Each takes the full text and
// the selection [start, end) and returns {text, selStart, selEnd}.
import { parseMarkdown } from './markdown/parser.js';
import { serializeMarkdown } from './markdown/serializer.js';

function result(text, selStart, selEnd) {
  return { text: text, selStart: selStart, selEnd: selEnd };
}

// A single-character marker ('*', '~', '^') right next to the same character
// belongs to a longer marker ('**', '~~', '^^') and must not be unwrapped.
function markerTouchesSame(text, markerStart, markerEnd, marker) {
  if (marker.length !== 1) return false;
  return text.charAt(markerStart - 1) === marker || text.charAt(markerEnd) === marker;
}

const WORD_CHAR = /[\p{L}\p{N}_]/u;

// Markers are only delimiters when the character beyond them is not a word
// character: in my_var_name or 2^3^4 they are literal text.
function isWordChar(ch) {
  return !!ch && WORD_CHAR.test(ch);
}

/** Wraps the selection in prefix/suffix, or unwraps it if already wrapped. */
export function wrapSelection(text, start, end, prefix, suffix, placeholder) {
  const selected = text.slice(start, end);
  const before = text.slice(0, start);
  const after = text.slice(end);

  // Selection includes the markers: **b**
  if (selected.length >= prefix.length + suffix.length && prefix && suffix &&
      selected.startsWith(prefix) && selected.endsWith(suffix) &&
      !markerTouchesSame(selected, 0, prefix.length, prefix) &&
      !markerTouchesSame(selected, selected.length - suffix.length, selected.length, suffix) &&
      !isWordChar(text.charAt(start - 1)) && !isWordChar(text.charAt(end))) {
    const inner = selected.slice(prefix.length, selected.length - suffix.length);
    return result(before + inner + after, start, start + inner.length);
  }

  // Markers sit just outside the selection: **|b|**
  if (prefix && suffix && before.endsWith(prefix) && after.startsWith(suffix) &&
      !markerTouchesSame(text, start - prefix.length, start, prefix) &&
      !markerTouchesSame(text, end, end + suffix.length, suffix) &&
      !isWordChar(text.charAt(start - prefix.length - 1)) && !isWordChar(text.charAt(end + suffix.length))) {
    const newStart = start - prefix.length;
    return result(before.slice(0, newStart) + selected + after.slice(suffix.length), newStart, newStart + selected.length);
  }

  const inner = selected || placeholder || '';
  const selStart = start + prefix.length;
  return result(before + prefix + inner + suffix + after, selStart, selStart + inner.length);
}

/**
 * Prefixes every line touched by the selection with `prefix` (a string or
 * (index) => string); removes the prefixes instead if every line has them.
 * `strip` (optional RegExp) removes a competing prefix first (e.g. '## ' when
 * applying '### '). `placeholder` (optional) is inserted on an empty line.
 */
export function prefixLines(text, start, end, prefix, placeholder, strip) {
  const prefixFor = typeof prefix === 'function' ? prefix : function () { return prefix; };
  const lineStart = text.lastIndexOf('\n', start - 1) + 1;
  let blockEnd = end;
  if (end > start && text.charAt(end - 1) === '\n') blockEnd = end - 1;
  let lineEnd = text.indexOf('\n', Math.max(blockEnd, lineStart));
  if (lineEnd < 0) lineEnd = text.length;

  const lines = text.slice(lineStart, lineEnd).split('\n');
  const before = text.slice(0, lineStart);
  const after = text.slice(lineEnd);

  if (lines.length === 1 && lines[0] === '' && placeholder) {
    const p = prefixFor(0);
    return result(before + p + placeholder + after, lineStart + p.length, lineStart + p.length + placeholder.length);
  }

  // Blank lines separate blocks: they get no prefix (so 'a\n\nb' becomes two
  // list items, not three) and numbering skips them.
  const skipBlank = lines.some(function (line) { return line.trim() !== ''; });
  const isSkipped = function (line) { return skipBlank && line.trim() === ''; };
  const numbers = [];
  let n = 0;
  lines.forEach(function (line) { numbers.push(isSkipped(line) ? -1 : n++); });
  const allPrefixed = lines.every(function (line, j) {
    return isSkipped(line) || line.startsWith(prefixFor(numbers[j]));
  });
  const deltas = [];
  const out = lines.map(function (line, j) {
    if (isSkipped(line)) {
      deltas.push(0);
      return line;
    }
    const i = numbers[j];
    if (allPrefixed) {
      deltas.push(-prefixFor(i).length);
      return line.slice(prefixFor(i).length);
    }
    let rest = line;
    if (strip) {
      const m = rest.match(strip);
      if (m && m.index === 0) rest = rest.slice(m[0].length);
    }
    const p = prefixFor(i);
    deltas.push(p.length - (line.length - rest.length));
    return p + rest;
  });
  const block = out.join('\n');
  const newText = before + block + after;

  if (start === end) {
    const caret = Math.max(lineStart, start + deltas[0]);
    return result(newText, caret, caret);
  }
  return result(newText, lineStart, lineStart + block.length);
}

/** Replaces the selection with `insert`; the caret goes after it. */
export function replaceSelection(text, start, end, insert) {
  const caret = start + insert.length;
  return result(text.slice(0, start) + insert + text.slice(end), caret, caret);
}

function stripMarks(json) {
  const copy = Object.assign({}, json);
  delete copy.marks;
  if (copy.content) copy.content = copy.content.map(stripMarks);
  return copy;
}

/**
 * Removes inline formatting from the selection by parsing it, dropping every
 * mark and serializing again; block structure (lists, quotes…) is kept and
 * only real emphasis is removed (snake_case survives).
 */
export function removeFormatting(text, start, end) {
  if (start === end) return result(text, start, end);
  const selected = text.slice(start, end);
  let cleaned;
  try {
    const doc = parseMarkdown(selected);
    cleaned = serializeMarkdown(doc.type.schema.nodeFromJSON(stripMarks(doc.toJSON())));
  } catch (e) {
    console.error('forum-editor: cannot remove formatting', e);
    return result(text, start, end);
  }
  // Keep the whitespace around the selection that serializing would trim.
  const lead = selected.match(/^\s*/)[0];
  const trail = selected.slice(lead.length).match(/\s*$/)[0];
  cleaned = lead + cleaned + trail;
  return result(text.slice(0, start) + cleaned + text.slice(end), start, start + cleaned.length);
}

const FENCED = /^```[a-zA-Z0-9_-]*\n[\s\S]*```$/;

/** Inline backticks for a single line; a fenced block for several lines. */
export function toggleCode(text, start, end) {
  const selected = text.slice(start, end);
  if (start === end || selected.indexOf('\n') === -1) {
    return wrapSelection(text, start, end, '`', '`', 'код');
  }
  const before = text.slice(0, start);
  const after = text.slice(end);
  const trimmed = selected.trim();
  if (FENCED.test(trimmed)) {
    const unwrapped = trimmed.replace(/^```[a-zA-Z0-9_-]*\n?/, '').replace(/\n?```$/, '');
    return result(before + unwrapped + after, start, start + unwrapped.length);
  }
  const prefix = (start > 0 && text.charAt(start - 1) !== '\n') ? '\n```\n' : '```\n';
  const suffix = (end < text.length && text.charAt(end) !== '\n') ? '\n```\n' : '\n```';
  const replacement = prefix + selected + suffix;
  return result(before + replacement + after, start, start + replacement.length);
}

// Legacy copy (forum-editor-legacy.js executeMarkdownCommand 'spoiler').
export const SPOILER_TITLE = 'Заголовок спойлера';
export const SPOILER_BODY = 'Текст спойлера';

/** Inserts `???- "Заголовок спойлера"` with the selection as its indented body; selects the title. */
export function insertSpoilerTemplate(text, start, end) {
  const before = text.slice(0, start);
  const after = text.slice(end);
  const body = (text.slice(start, end) || SPOILER_BODY).split('\n').map(function (line) {
    return line ? '    ' + line : line;
  }).join('\n').replace(/^ {4}/, '');

  // The block must start on its own line, after a blank line.
  let lead = '';
  if (before.length && !before.endsWith('\n\n')) lead = before.endsWith('\n') ? '\n' : '\n\n';
  const leadingNewlines = after.match(/^\n{0,2}/)[0].length;
  const trail = after.length ? '\n\n'.slice(leadingNewlines) : '\n\n';

  const head = '???- "';
  const template = head + SPOILER_TITLE + '"\n    ' + body;
  const titleStart = start + lead.length + head.length;
  return result(before + lead + template + trail + after, titleStart, titleStart + SPOILER_TITLE.length);
}
