import { MarkdownParser } from 'prosemirror-markdown';
import { getForumSchema } from '../schema/index.js';
import { createMarkdownIt } from './md.js';

// Same logic as prosemirror-markdown's listIsTight.
function listIsTight(tokens, i) {
  while (++i < tokens.length) {
    if (tokens[i].type !== 'list_item_open') return tokens[i].hidden;
  }
  return false;
}

function inlineText(tokens) {
  let out = '';
  for (const t of tokens || []) out += t.children ? inlineText(t.children) : t.content;
  return out;
}

const TOKEN_SPEC = {
  paragraph: { block: 'paragraph' },
  blockquote: { block: 'blockquote' },
  list_item: { block: 'listItem' },
  bullet_list: { block: 'bulletList', getAttrs: (tok) => ({ tight: tok.meta.tight }) },
  ordered_list: {
    block: 'orderedList',
    getAttrs: (tok) => ({ start: +tok.attrGet('start') || 1, tight: tok.meta.tight }),
  },
  heading: { block: 'heading', getAttrs: (tok) => ({ level: +tok.tag.slice(1) }) },
  code_block: { block: 'codeBlock', getAttrs: () => ({ language: null }), noCloseToken: true },
  fence: { block: 'codeBlock', getAttrs: (tok) => ({ language: tok.info || null }), noCloseToken: true },
  spoiler: { block: 'spoiler' },
  spoiler_summary: { block: 'spoilerSummary' },
  spoiler_body: { block: 'spoilerBody' },
  raw_block: { node: 'rawMarkdownBlock', getAttrs: (tok) => ({ source: tok.content }) },
  image: {
    node: 'image',
    getAttrs: (tok) => ({
      src: tok.attrGet('src'),
      alt: inlineText(tok.children) || null,
      title: tok.attrGet('title') || null,
    }),
  },
  softbreak: { node: 'hardBreak' },
  hardbreak: { node: 'hardBreak' },
  em: { mark: 'italic' },
  strong: { mark: 'bold' },
  underline: { mark: 'underline' },
  s: { mark: 'strike' },
  mark: { mark: 'highlight' },
  sub: { mark: 'subscript' },
  sup: { mark: 'superscript' },
  kbd: { mark: 'kbd', noCloseToken: true },
  code_inline: { mark: 'code', noCloseToken: true },
  link: { mark: 'link', getAttrs: (tok) => ({ href: tok.attrGet('href') }) },
};

function synthetic(Token, type, nesting, extra) {
  const tok = new Token(type, '', nesting);
  tok.block = true;
  return Object.assign(tok, extra);
}

// Splits paragraph inline children around images. Marks open at a split
// point are closed before it and reopened after it.
function splitAroundImages(children) {
  const segments = [];
  let current = [];
  const open = [];
  for (const tok of children) {
    if (tok.type === 'image') {
      if (open.some((t) => t.type === 'link_open')) {
        throw new Error('Linked images are not supported by the visual editor');
      }
      for (let i = open.length - 1; i >= 0; i--) {
        current.push(Object.assign(Object.create(Object.getPrototypeOf(open[i])), open[i], {
          type: open[i].type.replace(/_open$/, '_close'), nesting: -1,
        }));
      }
      segments.push(current, tok);
      current = open.slice();
    } else {
      if (tok.nesting === 1) open.push(tok);
      else if (tok.nesting === -1) open.pop();
      current.push(tok);
    }
  }
  segments.push(current);
  return segments;
}

function isFiller(t) {
  return t.type === 'softbreak' || t.type === 'hardbreak' || (t.type === 'text' && !t.content.trim());
}

// Drops line breaks and whitespace-only text at both edges of a segment
// (mark open/close tokens are kept). Returns null when nothing remains.
function trimSegment(tokens) {
  const keep = tokens.map(() => true);
  for (let i = 0; i < tokens.length && (tokens[i].nesting !== 0 || isFiller(tokens[i])); i++) {
    if (tokens[i].nesting === 0) keep[i] = false;
  }
  for (let i = tokens.length - 1; i >= 0 && (tokens[i].nesting !== 0 || isFiller(tokens[i])); i--) {
    if (tokens[i].nesting === 0) keep[i] = false;
  }
  const out = tokens.filter((_, i) => keep[i]);
  return out.some((t) => t.nesting === 0) ? out : null;
}

function assertNoImages(children) {
  for (const tok of children) {
    if (tok.type === 'image') throw new Error('Images are only supported at paragraph level');
  }
  return children;
}

// Rewrites the markdown-it block stream into tokens the MarkdownParser spec
// understands: spoiler body wrappers, block-level images, empty bodies.
function transformTokens(tokens, Token) {
  const out = [];
  for (let i = 0; i < tokens.length; i++) {
    const tok = tokens[i];
    if (tok.type === 'bullet_list_open' || tok.type === 'ordered_list_open') {
      // Computed on the original stream: image lifting may replace paragraphs.
      tok.meta = Object.assign({}, tok.meta, { tight: listIsTight(tokens, i) });
      out.push(tok);
    } else if (tok.type === 'spoiler_summary') {
      out.push(synthetic(Token, 'spoiler_summary_open', 1));
      out.push(Object.assign(synthetic(Token, 'inline', 0), { children: assertNoImages(tok.children) }));
      out.push(synthetic(Token, 'spoiler_summary_close', -1));
      out.push(synthetic(Token, 'spoiler_body_open', 1));
      if (tokens[i + 1] && tokens[i + 1].type === 'spoiler_close') {
        out.push(synthetic(Token, 'paragraph_open', 1), synthetic(Token, 'paragraph_close', -1));
      }
    } else if (tok.type === 'spoiler_close') {
      out.push(synthetic(Token, 'spoiler_body_close', -1), tok);
    } else if (tok.type === 'paragraph_open' && tokens[i + 1].children.some((t) => t.type === 'image')) {
      const inline = tokens[i + 1];
      const close = tokens[i + 2];
      for (const seg of splitAroundImages(inline.children)) {
        if (!Array.isArray(seg)) {
          out.push(seg);
        } else {
          const children = trimSegment(seg);
          if (children) out.push(tok, Object.assign(synthetic(Token, 'inline', 0), { children }), close);
        }
      }
      i += 2;
    } else if (tok.type === 'inline') {
      assertNoImages(tok.children);
      out.push(tok);
    } else {
      out.push(tok);
    }
  }
  return out;
}

let parser = null;
function getParser() {
  if (!parser) {
    const md = createMarkdownIt();
    const Token = md.core.State.prototype.Token;
    // MarkdownParser tokenizes through this object, so it sees the
    // transformed token stream.
    const tokenizer = {
      parse(src, env) {
        const tokens = transformTokens(md.parse(src, env), Token);
        if (!tokens.length) tokens.push(new Token('paragraph_open', 'p', 1), new Token('paragraph_close', 'p', -1));
        return tokens;
      },
    };
    parser = new MarkdownParser(getForumSchema(), tokenizer, TOKEN_SPEC);
  }
  return parser;
}

export function parseMarkdown(md) {
  const source = String(md == null ? '' : md).replace(/\r\n?/g, '\n');
  const doc = getParser().parse(source, {});
  doc.check();
  return doc;
}
