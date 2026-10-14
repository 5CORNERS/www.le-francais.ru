import { describe, expect, test } from 'vitest';
import { DOMParser, DOMSerializer } from '@tiptap/pm/model';
import { getForumSchema } from '../src/schema/index.js';
import { EMOJIS, SHORTCODE_TO_CHAR } from '../src/emoji.js';

const text = (t, marks) => ({
  type: 'text',
  text: t,
  ...(marks ? { marks: marks.map((m) => (typeof m === 'string' ? { type: m } : m)) } : {}),
});
const para = (...content) => ({ type: 'paragraph', content });
const spoiler = (title, blocks) => ({
  type: 'spoiler',
  content: [
    { type: 'spoilerSummary', content: [text(title)] },
    { type: 'spoilerBody', content: blocks },
  ],
});
const bulletList = (items) => ({
  type: 'bulletList',
  content: items.map((i) => ({ type: 'listItem', content: [para(text(i))] })),
});
const codeBlock = (t) => ({ type: 'codeBlock', content: [text(t)] });

// Serialises a single node to its HTML string.
function toHTML(json) {
  const schema = getForumSchema();
  const node = schema.nodeFromJSON(json);
  const div = document.createElement('div');
  div.appendChild(DOMSerializer.fromSchema(schema).serializeNode(node));
  return div.innerHTML;
}
function parseClipboardHTML(html) {
  const el = document.createElement('div');
  el.innerHTML = html;
  return DOMParser.fromSchema(getForumSchema()).parse(el);
}

describe('schema', () => {
  test('marks render with legacy tags/classes', () => {
    expect(toHTML(para(text('k', ['kbd'])))).toBe('<p><kbd class="editor-key">k</kbd></p>');
    for (const [m, tag] of [['underline', 'u'], ['strike', 's'], ['highlight', 'mark'], ['superscript', 'sup'], ['subscript', 'sub'], ['bold', 'strong'], ['italic', 'em'], ['code', 'code']])
      expect(toHTML(para(text('x', [m])))).toBe(`<p><${tag}>x</${tag}></p>`);
  });
  test('link', () => expect(toHTML(para(text('t', [{ type: 'link', attrs: { href: 'https://a.b' } }]))))
    .toBe('<p><a href="https://a.b" target="_blank" rel="noopener">t</a></p>'));
  test('code block', () => expect(toHTML({ type: 'codeBlock', attrs: { language: 'py' }, content: [{ type: 'text', text: 'x' }] }))
    .toBe('<pre class="editor-code-block"><code class="language-py">x</code></pre>'));
  test('image', () => expect(toHTML({ type: 'image', attrs: { src: '/m/a.png', alt: 'a', title: 't' } }))
    .toBe('<img src="/m/a.png" alt="a" title="t" class="forum-embedded-img">'));
  test('spoiler', () => expect(toHTML(spoiler('T', [para(text('b'))])))
    .toBe('<details class="forum-spoiler" open=""><summary>T</summary><div class="spoiler-body"><p>b</p></div></details>'));
  test('spoiler body accepts nested blocks', () => {
    const n = getForumSchema().nodeFromJSON(spoiler('T', [bulletList(['a']), codeBlock('x'), spoiler('In', [para(text('y'))])]));
    expect(() => n.check()).not.toThrow();
  });
  test('raw block chip', () => expect(toHTML({ type: 'rawMarkdownBlock', attrs: { source: '| a |\n|---|' } }))
    .toBe('<div class="forum-raw-md" contenteditable="false" title="Этот фрагмент редактируется в режиме Markdown"><pre>| a |\n|---|</pre></div>'));
  test('Google Docs bold wrapper is not bold', () => {
    const doc = parseClipboardHTML('<b style="font-weight:normal" id="docs-internal-guid-1"><p><span>plain</span> <span style="font-weight:700">bold</span></p></b>');
    expect(JSON.stringify(doc)).toContain('"text":"plain ');
    expect(doc.firstChild.firstChild.marks).toHaveLength(0);
    expect(doc.firstChild.lastChild.marks.map((m) => m.type.name)).toEqual(['bold']);
  });
  test('node/mark names and attrs', () => {
    const s = getForumSchema();
    for (const n of ['doc', 'paragraph', 'text', 'hardBreak', 'heading', 'blockquote', 'bulletList', 'orderedList', 'listItem', 'codeBlock', 'image', 'spoiler', 'spoilerSummary', 'spoilerBody', 'rawMarkdownBlock'])
      expect(s.nodes[n], n).toBeDefined();
    for (const m of ['bold', 'italic', 'underline', 'strike', 'highlight', 'kbd', 'superscript', 'subscript', 'code', 'link'])
      expect(s.marks[m], m).toBeDefined();
    expect(s.nodes.horizontalRule).toBeUndefined();
    expect(s.nodes.bulletList.defaultAttrs.tight).toBe(true);
    expect(s.nodes.orderedList.defaultAttrs).toMatchObject({ tight: true, start: 1 });
    expect(s.nodes.image.defaultAttrs).toHaveProperty('uploadId');
    expect(s.nodes.image.isBlock).toBe(true);
    expect(s.nodes.rawMarkdownBlock.isAtom).toBe(true);
  });
  test('emoji exports', () => {
    expect(EMOJIS.length).toBeGreaterThan(50);
    expect(SHORTCODE_TO_CHAR[':thumbsup:']).toBe('👍');
    expect(SHORTCODE_TO_CHAR[EMOJIS[0].code]).toBe(EMOJIS[0].char);
  });
});
