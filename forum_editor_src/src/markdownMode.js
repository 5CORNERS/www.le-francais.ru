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

// Emphasis markers ('*', '**') may sit inside a word: visual mode writes
// `mot*ifs*`. There they are unwrapped only when parsing the line(s) confirms
// that the pair opening at `open` and closing at `close` delimits real emphasis
// around exactly its content. Other markers ('_', '^', '~'…) next to word
// characters always stay literal (my_var_name, 2^3^4).
const EMPHASIS_MARKS = { '*': 'italic', '**': 'bold' };

function markRuns(doc, markName) {
  const runs = [];
  doc.descendants(function (node) {
    if (!node.isTextblock) return true;
    let run = null;
    node.forEach(function (child) {
      const marked = child.isText && child.marks.some(function (m) { return m.type.name === markName; });
      if (marked) {
        run = (run || '') + child.text;
      } else if (run !== null) {
        runs.push(run);
        run = null;
      }
    });
    if (run !== null) runs.push(run);
    return false;
  });
  return runs;
}

function isEmphasisPair(text, open, close, marker) {
  const markName = EMPHASIS_MARKS[marker];
  if (!markName) return false;
  const lineStart = text.lastIndexOf('\n', open - 1) + 1;
  let lineEnd = text.indexOf('\n', close + marker.length);
  if (lineEnd < 0) lineEnd = text.length;
  const line = text.slice(lineStart, lineEnd);
  const o = open - lineStart;
  const c = close - lineStart;
  const inner = line.slice(o + marker.length, c);
  const unwrapped = line.slice(0, o) + inner + line.slice(c + marker.length);
  try {
    const doc = parseMarkdown(line);
    // Literal markers are visible text; real delimiters are not.
    if (doc.textContent !== parseMarkdown(unwrapped).textContent) return false;
    return markRuns(doc, markName).indexOf(parseMarkdown(inner).textContent) >= 0;
  } catch (e) {
    return false;
  }
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
      ((!isWordChar(text.charAt(start - 1)) && !isWordChar(text.charAt(end))) ||
       (prefix === suffix && isEmphasisPair(text, start, end - suffix.length, prefix)))) {
    const inner = selected.slice(prefix.length, selected.length - suffix.length);
    return result(before + inner + after, start, start + inner.length);
  }

  // Markers sit just outside the selection: **|b|**
  if (prefix && suffix && before.endsWith(prefix) && after.startsWith(suffix) &&
      !markerTouchesSame(text, start - prefix.length, start, prefix) &&
      !markerTouchesSame(text, end, end + suffix.length, suffix) &&
      ((!isWordChar(text.charAt(start - prefix.length - 1)) && !isWordChar(text.charAt(end + suffix.length))) ||
       (prefix === suffix && isEmphasisPair(text, start - prefix.length, end, prefix)))) {
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
  // list items, not three) and numbering skips them. A quote instead marks
  // them with a bare '>' so 'a\n\nb' stays one blockquote.
  const quote = prefix === '> ';
  const isBlank = function (line) { return line.trim() === '' || (quote && /^>\s*$/.test(line)); };
  const skipBlank = lines.some(function (line) { return !isBlank(line); });
  const isSkipped = function (line) { return skipBlank && isBlank(line); };
  const numbers = [];
  let n = 0;
  lines.forEach(function (line) { numbers.push(isSkipped(line) ? -1 : n++); });
  const allPrefixed = lines.every(function (line, j) {
    return isSkipped(line) || line.startsWith(prefixFor(numbers[j]));
  });
  const deltas = [];
  const out = lines.map(function (line, j) {
    if (isSkipped(line)) {
      let kept = line;
      if (quote) kept = allPrefixed ? '' : (line.trim() === '' ? '>' : line);
      deltas.push(kept.length - line.length);
      return kept;
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

// Container prefix of a Markdown line: indentation (spoiler bodies, nested
// lists), quote markers, then a list or heading marker.
const LINE_PREFIX = /^\s*(?:>\s?)*\s*(?:(?:[-*+]|\d+[.)])\s+|#{1,6}\s+)?/;
// A code fence, once indentation and quote markers are removed.
const FENCE_LINE = /^[\s>]*(?:```|~~~)/;

/**
 * Strips the marks of one inline run (no container prefix). Only a run that
 * parses as a single paragraph is changed; anything else is returned as is.
 * The whitespace around the run, which serializing would trim, is kept.
 */
function stripInline(run) {
  const lead = run.match(/^\s*/)[0];
  if (lead.length === run.length) return run;
  const trail = run.slice(lead.length).match(/\s*$/)[0];
  const doc = parseMarkdown(run);
  if (doc.childCount !== 1 || doc.firstChild.type.name !== 'paragraph') return run;
  return lead + serializeMarkdown(doc.type.schema.nodeFromJSON(stripMarks(doc.toJSON()))) + trail;
}

/**
 * Removes inline formatting from the selection line by line: each line's
 * container prefix (indentation, '>', list or heading marker) is kept as typed
 * and only the selected inline remainder is parsed, stripped of marks and
 * serialized again, so only real emphasis is removed (snake_case survives).
 * Lines of fenced code blocks (even one opened before the selection) are
 * left untouched.
 */
export function removeFormatting(text, start, end) {
  if (start === end) return result(text, start, end);
  const lines = text.split('\n');
  const out = [];
  let pos = 0;
  let inFence = false;
  let delta = 0;
  try {
    lines.forEach(function (line) {
      const ls = pos;
      const le = ls + line.length;
      pos = le + 1;
      const isFence = FENCE_LINE.test(line);
      const fenced = inFence || isFence;
      if (isFence) inFence = !inFence;
      const segStart = Math.max(start, ls + line.match(LINE_PREFIX)[0].length);
      const segEnd = Math.min(end, le);
      if (fenced || segStart >= segEnd) {
        out.push(line);
        return;
      }
      const seg = text.slice(segStart, segEnd);
      const cleaned = stripInline(seg);
      delta += cleaned.length - seg.length;
      out.push(text.slice(ls, segStart) + cleaned + text.slice(segEnd, le));
    });
  } catch (e) {
    console.error('forum-editor: cannot remove formatting', e);
    return result(text, start, end);
  }
  return result(out.join('\n'), start, end + delta);
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
