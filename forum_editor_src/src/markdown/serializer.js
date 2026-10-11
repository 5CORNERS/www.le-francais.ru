import { MarkdownSerializer, MarkdownSerializerState } from 'prosemirror-markdown';
import { parseMarkdown } from './parser.js';
import { createMarkdownIt } from './md.js';

// ProseMirror doc -> Markdown for Python-Markdown 2.6.11 + pymdown-extensions 5.0.
//
// Escaping: while a textblock's inline content is rendered, every character
// that may be syntax is prefixed with SENT. `resolveEscapes` then picks the
// candidates that local rules cannot rule out and keeps only the escapes
// needed for `parseMarkdown` to give back the same inline content.

const SENT = '\uE000';
const SENT_RE = /\uE000/g;
const MARKED_RE = /[\\*_^~=+[\]`:<#>\-.)?!{|\uE000]/g;
// Backslash escapes honoured by the server (and by our parser: pyEscape.js).
const PY_ESCAPED = '\\`*_{}[]()>#+-.!"\'|^~=: ';
const ALNUM = /[\p{L}\p{N}]/u;
const WS = /\s/;
const SHORTCODE_AFTER = /^:[\w+-]+:/;
const SHORTCODE_BEFORE = /:[\w+-]+:$/;
// `<scheme:` starts an autolink (markdown-it: any scheme; Python-Markdown:
// http/ftp). Escaping the colon defeats both; `\<` is not a server escape.
const AUTOLINK_SCHEME = /^<[A-Za-z][A-Za-z0-9+.-]{1,31}:/;
// Characters after `???` whose backslash escape breaks the pymdownx.details
// START line on both sides (`\?` is not a Python-Markdown escape; `\ ` is an
// escaped space for pymdown caret/tilde).
const DETAILS_BREAKERS = '+-"_ ';
// Python-Markdown preprocessors drop these lines anywhere in a paragraph
// (reference / footnote / abbreviation definitions).
const PY_DEFINITION = /^\*?\[[^\]\n]*]:/;
const MAX_GREEDY = 32;

let mdIt = null;
function normalizeHref(href) {
  if (!mdIt) mdIt = createMarkdownIt();
  return mdIt.normalizeLink(href || '');
}

// ---------------------------------------------------------------------------
// Inline signature: what a textblock looks like once parsed, ignoring the
// whitespace Markdown cannot carry (around line breaks, at the ends, and the
// marks on whitespace, which the serializer moves outside delimiters).

function markKey(marks) {
  let key = '';
  for (const m of marks) key += m.type.name === 'link' ? 'link:' + normalizeHref(m.attrs.href) + ';' : m.type.name + ';';
  return key;
}

function rawSignature(node, singleLine, textOnly) {
  let out = '';
  let current = '';
  node.forEach((child) => {
    if (child.type.name === 'hardBreak') {
      out += singleLine ? ' ' : '\n';
    } else if (child.isText) {
      const key = textOnly ? '' : markKey(child.marks);
      for (const run of child.text.match(/\s+|\S+/g) || []) {
        if (!WS.test(run[0]) && key !== current) {
          out += '\u0001' + key + '\u0002';
          current = key;
        }
        out += run;
      }
    } else {
      out += '\u0003' + child.type.name + '\u0003';
    }
  });
  return out;
}

function normalizeSignature(sig) {
  return sig.replace(/[ \t]*\n[ \t]*/g, '\n').replace(/\n{3,}/g, '\n\n').replace(/^[ \t\n]+|[ \t\n]+$/g, '');
}

function paragraphsSignature(nodes, textOnly) {
  if (!nodes.length) return null;
  const parts = [];
  for (const n of nodes) {
    if (n.type.name !== 'paragraph') return null;
    parts.push(rawSignature(n, false, textOnly));
  }
  return normalizeSignature(parts.join('\n\n'));
}

function children(node) {
  const list = [];
  node.forEach((c) => list.push(c));
  return list;
}

// Per textblock kind: the Markdown context it is checked in, and how to read
// the textblock back from the parsed document.
const KINDS = {
  paragraph: {
    lineStarts: true,
    wrap: (s) => s,
    read: (d, node, textOnly) => paragraphsSignature(children(d), textOnly),
  },
  listItem: {
    lineStarts: true,
    wrap: (s) => '- ' + s,
    read: (d, node, textOnly) => {
      const list = d.firstChild;
      if (d.childCount !== 1 || list.type.name !== 'bulletList' || list.childCount !== 1) return null;
      return paragraphsSignature(children(list.firstChild), textOnly);
    },
  },
  heading: {
    singleLine: true,
    wrap: (s, node) => '#'.repeat(node.attrs.level) + ' ' + s,
    read: (d, node, textOnly) => {
      const h = d.firstChild;
      if (d.childCount !== 1 || h.type.name !== 'heading' || h.attrs.level !== node.attrs.level) return null;
      return normalizeSignature(rawSignature(h, true, textOnly));
    },
  },
  summary: {
    singleLine: true,
    wrap: (s) => '???- "' + s + '"',
    read: (d, node, textOnly) => {
      const s = d.firstChild;
      if (d.childCount !== 1 || s.type.name !== 'spoiler') return null;
      return normalizeSignature(rawSignature(s.firstChild, true, textOnly));
    },
  },
};

// ---------------------------------------------------------------------------
// Candidate escapes.

function isWs(ch) {
  return ch === undefined || ch === '\n' || WS.test(ch);
}

// Returns null (never syntax), or { rep, forced }.
function candidate(c, p, kind) {
  const ch = c[p];
  const prev = c[p - 1];
  const next = c[p + 1];
  const lineStart = kind.lineStarts && (p === 0 || prev === '\n');
  const live = { rep: '\\' + ch, forced: false };
  const forced = { rep: '\\' + ch, forced: true };
  switch (ch) {
    case '\\':
      return next === undefined || next === '\n' || PY_ESCAPED.indexOf(next) !== -1 ? live : null;
    case '*':
      if (lineStart && PY_DEFINITION.test(c.slice(p, p + 200))) return forced;
      return lineStart || !(isWs(prev) && isWs(next)) ? live : null;
    case '_':
      if (isWs(prev) && isWs(next)) return null;
      return ALNUM.test(prev || '') && ALNUM.test(next || '') ? null : live;
    case '~':
    case '^':
      return isWs(prev) && isWs(next) ? null : live;
    case '=':
    case '+':
      return lineStart || prev === ch || next === ch ? live : null;
    case '[':
      if (lineStart && PY_DEFINITION.test(c.slice(p, p + 200))) return forced;
      return live;
    case ']':
    case '`':
      return live;
    case ':':
      return lineStart || SHORTCODE_AFTER.test(c.slice(p, p + 64)) ||
        SHORTCODE_BEFORE.test(c.slice(Math.max(0, p - 63), p + 1)) ? live : null;
    case '<': {
      const m = AUTOLINK_SCHEME.exec(c.slice(p, p + 40));
      return m ? { pos: p + m[0].length - 1, rep: '\\:', forced: false } : null;
    }
    case '#':
      if (lineStart) return forced; // Python-Markdown: `#x` is a heading
      // A trailing run preceded by a space is a closing sequence in markdown-it.
      // (Python-Markdown strips any trailing run: the heading writer adds a space.)
      if (kind === KINDS.heading && /[ \t]$/.test(c.slice(0, p)) && /^#+$/.test(c.slice(p))) return forced;
      return null;
    case '>':
    case '-':
      return lineStart ? live : null;
    case '.':
    case ')': {
      if (!kind.lineStarts) return null;
      const start = c.lastIndexOf('\n', p - 1) + 1;
      return p > start && /^\d{1,9}$/.test(c.slice(start, p)) ? live : null;
    }
    case '?': {
      if (!lineStart || !c.startsWith('???', p)) return null;
      const end = c.indexOf('\n', p);
      const line = c.slice(p + 3, end === -1 ? c.length : end);
      for (let i = 0; i < line.length; i++) {
        if (DETAILS_BREAKERS.indexOf(line[i]) !== -1) return { pos: p + 3 + i, rep: '\\' + line[i], forced: false };
      }
      return live; // `\?` shows a backslash on the server, but no spoiler
    }
    case '!':
      return next === '[' || (lineStart && c.startsWith('!!!', p)) ? live : null;
    case '|': {
      // Tables: a pipe at a line start, or on a line right after a line
      // with a pipe (header row + delimiter row).
      if (lineStart) return live;
      if (!kind.lineStarts) return null;
      const start = c.lastIndexOf('\n', p - 1);
      if (start === -1) return null;
      const prevLine = c.slice(c.lastIndexOf('\n', start - 1) + 1, start);
      return prevLine.indexOf('|') !== -1 ? live : null;
    }
    case '{':
      return lineStart && next === ':' ? live : null;
    default:
      return null;
  }
}

function build(clean, cands, escaped) {
  let out = '';
  let last = 0;
  for (let i = 0; i < cands.length; i++) {
    if (!escaped[i]) continue;
    out += clean.slice(last, cands[i].pos) + cands[i].rep;
    last = cands[i].pos + 1;
  }
  return out + clean.slice(last);
}

function resolveEscapes(marked, kind, node) {
  const s = marked.replace(/[ \t]+\n/g, '\n').replace(/\n[ \t]+/g, '\n').replace(/^[ \t\n]+|[ \t\n]+$/g, '');
  let clean = '';
  const positions = [];
  let from = 0;
  for (let i = s.indexOf(SENT); i !== -1; i = s.indexOf(SENT, from)) {
    clean += s.slice(from, i);
    if (s[i + 1] === SENT) {
      clean += SENT;
    } else {
      positions.push(clean.length);
      clean += s[i + 1];
    }
    from = i + 2;
  }
  clean += s.slice(from);

  // A candidate may move its escape to another character (`<`, `?`).
  const byPos = new Map();
  for (const pos of positions) {
    const cand = candidate(clean, pos, kind);
    if (!cand) continue;
    const at = cand.pos === undefined ? pos : cand.pos;
    if (!byPos.has(at)) byPos.set(at, { pos: at, rep: cand.rep, forced: cand.forced });
  }
  if (!byPos.size) return clean;
  const cands = Array.from(byPos.values()).sort((a, b) => a.pos - b.pos);

  const expected = [];
  const matches = (escaped, textOnly) => {
    const k = textOnly ? 1 : 0;
    if (expected[k] === undefined) {
      expected[k] = normalizeSignature(rawSignature(node, kind.singleLine, textOnly));
    }
    let parsed;
    try {
      parsed = parseMarkdown(kind.wrap(build(clean, cands, escaped), node));
    } catch (e) {
      return false;
    }
    return kind.read(parsed, node, textOnly) === expected[k];
  };

  const escaped = cands.map((c) => c.forced);
  if (cands.every((c) => c.forced) || matches(escaped, false)) return build(clean, cands, escaped);
  const all = cands.map(() => true);
  if (cands.length > MAX_GREEDY) return build(clean, cands, all);
  // When even full escaping does not give the marks back, the mark layout
  // itself is not expressible for markdown-it (e.g. `**a.**b`, which
  // Python-Markdown renders fine): only keep the text literal.
  const textOnly = !matches(all, false);
  if (textOnly && !matches(all, true)) return build(clean, cands, all);
  // Greedy, from the end: openers stay escaped, which reads best.
  for (let i = cands.length - 1; i >= 0; i--) {
    if (cands[i].forced) continue;
    all[i] = false;
    all[i] = !matches(all, textOnly);
  }
  return build(clean, cands, all);
}

// ---------------------------------------------------------------------------
// Serializer state and node writers.

class ForumState extends MarkdownSerializerState {
  constructor(nodes, marks, options, inline) {
    super(nodes, marks, options);
    this.inline = !!inline;
    this.singleLine = false;
    this.escapeSpaces = false;
  }

  // Same as the base implementation, without the `![` hack (handled by the
  // `!` candidate) and keeping literal sentinels distinguishable.
  text(text, escape = true) {
    const lines = text.split('\n');
    for (let i = 0; i < lines.length; i++) {
      this.write();
      let line = lines[i];
      if (escape) line = this.esc(line);
      else if (this.inline) line = line.replace(SENT_RE, SENT + SENT);
      this.out += line;
      if (i !== lines.length - 1) this.out += '\n';
    }
  }

  esc(str) {
    let out = str.replace(MARKED_RE, (m) => (m === SENT ? SENT + SENT : SENT + m));
    if (this.escapeSpaces) out = out.replace(/ /g, '\\ ');
    return out;
  }
}

function inlineMarkdown(state, node, kindName) {
  const kind = KINDS[kindName];
  const sub = new ForumState(state.nodes, state.marks, state.options, true);
  sub.singleLine = !!kind.singleLine;
  sub.renderInline(node);
  return resolveEscapes(sub.out, kind, node);
}

// Writes block lines with the current prefix; blank lines get the prefix
// without trailing whitespace.
function writeLines(state, lines) {
  state.write(lines[0]);
  const blank = state.delim.replace(/\s+$/, '');
  for (let i = 1; i < lines.length; i++) state.out += '\n' + (lines[i] ? state.delim + lines[i] : blank);
}

function dedent(source) {
  const lines = source.split('\n');
  let min = Infinity;
  for (const line of lines) {
    if (!line.trim()) continue;
    min = Math.min(min, /^ */.exec(line)[0].length);
  }
  return min === Infinity || min === 0 ? lines : lines.map((l) => l.slice(Math.min(min, l.length)));
}

function longestRun(str, ch) {
  let max = 0;
  const re = new RegExp(ch === '`' ? '`+' : '\\' + ch + '+', 'g');
  let m;
  while ((m = re.exec(str))) max = Math.max(max, m[0].length);
  return max;
}

function codeTicks(node, open) {
  const content = node.isText ? node.text : '';
  const n = longestRun(content, '`');
  const ticks = '`'.repeat(n + 1);
  if (!n) return ticks;
  return open ? ticks + ' ' : ' ' + ticks;
}

function escapeUrl(url) {
  return String(url || '').replace(/ /g, '%20').replace(/[()]/g, '\\$&');
}

function imageAlt(alt) {
  if (!alt || !/[\\`*_[\]~^=+:<!]/.test(alt)) return alt || '';
  try {
    const d = parseMarkdown('![' + alt + '](x)');
    if (d.childCount === 1 && d.firstChild.type.name === 'image' && d.firstChild.attrs.alt === alt) return alt;
  } catch (e) {
    // fall through to full escaping
  }
  return alt.replace(/[\\`*_[\]~^=+:!]/g, '\\$&');
}

const isEmptyParagraph = (n) => n.type.name === 'paragraph' && n.childCount === 0;

const nodes = {
  paragraph(state, node, parent, index) {
    if (!node.childCount) return;
    const kind = parent.type.name === 'listItem' && index === 0 ? 'listItem' : 'paragraph';
    writeLines(state, inlineMarkdown(state, node, kind).split('\n'));
    state.closeBlock(node);
  },
  heading(state, node) {
    let content = inlineMarkdown(state, node, 'heading');
    // Python-Markdown strips trailing `#`s (escaped or not) unless the line
    // ends with something else.
    if (content.slice(-1) === '#') content += ' ';
    state.write('#'.repeat(node.attrs.level) + ' ' + content);
    state.closeBlock(node);
  },
  blockquote(state, node) {
    state.wrapBlock('> ', null, node, () => state.renderContent(node));
  },
  bulletList(state, node) {
    state.renderList(node, '    ', () => '- ');
  },
  orderedList(state, node) {
    const start = node.attrs.start == null ? 1 : node.attrs.start;
    const width = String(start + node.childCount - 1).length + 2;
    state.renderList(node, ' '.repeat(Math.max(4, width)), (i) => (start + i) + '. ');
  },
  listItem(state, node) {
    // A list item opening with an image (or code block) starts with an empty
    // paragraph in the schema; it has no Markdown of its own.
    node.forEach((child, _, i) => {
      if (i === 0 && node.childCount > 1 && isEmptyParagraph(child)) return;
      state.render(child, node, i);
    });
  },
  codeBlock(state, node) {
    const content = node.textContent;
    const fence = '`'.repeat(Math.max(3, longestRun(content, '`') + 1));
    const lines = [fence + (node.attrs.language || '')];
    if (content) lines.push(...content.split('\n'));
    lines.push(fence);
    writeLines(state, lines);
    state.closeBlock(node);
  },
  rawMarkdownBlock(state, node) {
    writeLines(state, dedent(node.attrs.source || ''));
    state.closeBlock(node);
  },
  image(state, node) {
    if (node.attrs.uploadId != null) return;
    const { src, alt, title } = node.attrs;
    state.write('![' + imageAlt(alt) + '](' + escapeUrl(src) +
      (title ? ' "' + title.replace(/["\\]/g, '\\$&') + '"' : '') + ')');
    state.closeBlock(node);
  },
  spoiler(state, node) {
    const title = inlineMarkdown(state, node.firstChild, 'summary');
    const old = state.delim;
    state.write('???- "' + title + '"');
    state.out += '\n';
    state.delim += '    ';
    state.renderContent(node.child(1));
    state.delim = old;
    state.closeBlock(node);
  },
  hardBreak(state) {
    state.out += state.singleLine ? ' ' : '\n';
  },
  text(state, node) {
    state.escapeSpaces = node.marks.some((m) => m.type.name === 'superscript' || m.type.name === 'subscript');
    state.text(node.text, true);
    state.escapeSpaces = false;
  },
};

const wrapMark = (delim) => ({ open: delim, close: delim, mixable: true, expelEnclosingWhitespace: true });

const marks = {
  bold: wrapMark('**'),
  italic: wrapMark('*'),
  underline: wrapMark('^^'),
  strike: wrapMark('~~'),
  highlight: wrapMark('=='),
  superscript: wrapMark('^'),
  subscript: wrapMark('~'),
  kbd: { open: '++', close: '++', escape: false, expelEnclosingWhitespace: true },
  code: {
    open: (_state, _mark, parent, index) => codeTicks(parent.child(index), true),
    close: (_state, _mark, parent, index) => codeTicks(parent.child(index - 1), false),
    escape: false,
  },
  link: {
    open: () => '[',
    close: (_state, mark) => '](' + escapeUrl(mark.attrs.href) + ')',
    mixable: true,
  },
};

const serializer = new MarkdownSerializer(nodes, marks, { hardBreakNodeName: 'hardBreak' });

export function serializeMarkdown(doc) {
  const state = new ForumState(serializer.nodes, serializer.marks, Object.assign({}, serializer.options));
  state.renderContent(doc);
  return state.out.replace(/\n+$/, '');
}
