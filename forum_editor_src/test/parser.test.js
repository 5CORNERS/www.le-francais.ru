import { describe, expect, test } from 'vitest';
import { DOMSerializer } from '@tiptap/pm/model';
import { getForumSchema } from '../src/schema/index.js';
import { parseMarkdown } from '../src/markdown/parser.js';

const p = (md) => parseMarkdown(md).toJSON();
function html(md) {
  const doc = parseMarkdown(md);
  const div = document.createElement('div');
  div.appendChild(DOMSerializer.fromSchema(getForumSchema()).serializeFragment(doc.content));
  return div.innerHTML;
}

describe('parseMarkdown', () => {
  test('every mapping row', () => {
    expect(html('**b** *i* ^^u^^ ~~s~~ ==m== ++k++ ^p^ ~b~ `c` [t](https://x.y)')).toBe(
      '<p><strong>b</strong> <em>i</em> <u>u</u> <s>s</s> <mark>m</mark> <kbd class="editor-key">k</kbd> <sup>p</sup> <sub>b</sub> <code>c</code> <a href="https://x.y" target="_blank" rel="noopener">t</a></p>');
    expect(html('## A\n\n### B')).toBe('<h2>A</h2><h3>B</h3>');
    expect(html('> q')).toBe('<blockquote><p>q</p></blockquote>');
    expect(html('```py\nx = 1\n```')).toBe('<pre class="editor-code-block"><code class="language-py">x = 1</code></pre>');
    expect(html('![a](/m/a.png "t")')).toBe('<img src="/m/a.png" alt="a" title="t" class="forum-embedded-img">');
    expect(html('a\nb')).toBe('<p>a<br>b</p>');
  });
  test('spoiler with nested blocks', () => {
    const d = p('???- "Titre"\n    - a\n    - b\n\n    ```\n    code\n    ```\n\n    > q\n\n    ???- "In"\n        deep');
    const body = d.content[0].content[1].content;
    expect(d.content[0].type).toBe('spoiler');
    expect(d.content[0].content[0].content[0].text).toBe('Titre');
    expect(body.map(n => n.type)).toEqual(['bulletList', 'codeBlock', 'blockquote', 'spoiler']);
  });
  test.each(['| a | b |\n|---|---|\n| 1 | 2 |', '!!! note "N"\n    body', '[^1]: foot', 'Term\n: def',
    '*[HTML]: Hyper', '- [ ] todo\n- [x] done', '# H1', '#### H4', 'Setext\n======'])
    ('raw block %#', src => {
      const d = p('before\n\n' + src + '\n\nafter');
      expect(d.content[1]).toEqual({ type: 'rawMarkdownBlock', attrs: { source: src } });
    });
  test('tight vs loose lists', () => {
    expect(p('- a\n- b').content[0].attrs.tight).toBe(true);
    expect(p('- a\n\n- b').content[0].attrs.tight).toBe(false);
    expect(p('1. a\n\n2. b').content[0].attrs.tight).toBe(false);
  });
  test('CRLF parses like LF', () => expect(p('a\r\nb\r\n\r\n- x\r\n- y')).toEqual(p('a\nb\n\n- x\n- y')));
  test('raw HTML is literal text', () => expect(html('<iframe src=x>')).toBe('<p>&lt;iframe src=x&gt;</p>'));
  test('inline code and fences survive bold-like underscores (review bug 1)', () => {
    expect(html('`a` and `b`')).toBe('<p><code>a</code> and <code>b</code></p>');
    const d = p('```\none\n```\n\n___text___\n\n```\ntwo\n```');
    expect(d.content.map(n => n.type)).toEqual(['codeBlock', 'paragraph', 'codeBlock']);
    expect(d.content[0].content[0].text).toBe('one');
    expect(d.content[2].content[0].text).toBe('two');
  });

  // Additional coverage beyond the brief.
  test('empty input gives one empty paragraph', () => {
    expect(p('')).toEqual({ type: 'doc', content: [{ type: 'paragraph' }] });
    expect(p('\n\n')).toEqual({ type: 'doc', content: [{ type: 'paragraph' }] });
  });
  test('spoiler title variants (pymdownx.details regex)', () => {
    const title = (src) => p(src + '\n    x').content[0].content[0].content[0].text;
    expect(title('???- "Titre"')).toBe('Titre');
    expect(title('???+ "Open"')).toBe('Open');
    expect(title('??? "Plain"')).toBe('Plain');
    expect(title('???- note "Classed"')).toBe('Classed');
    expect(title('??? note')).toBe('Note');
  });
  test('spoiler title has inline marks', () => {
    const s = p('???- "**B** t"\n    x').content[0].content[0];
    expect(s.content[0]).toEqual({ type: 'text', text: 'B', marks: [{ type: 'bold' }] });
  });
  test('spoiler without body gets an empty paragraph and validates', () => {
    const d = parseMarkdown('???- "T"\n\nafter');
    expect(() => d.check()).not.toThrow();
    expect(d.toJSON().content[0].content[1]).toEqual({ type: 'spoilerBody', content: [{ type: 'paragraph' }] });
    expect(d.toJSON().content[1].type).toBe('paragraph');
  });
  test('spoiler body ends at the first non-indented line', () => {
    const d = p('???- "T"\n    a\n\n    b\n\nafter');
    expect(d.content[0].content[1].content.map(n => n.content[0].text)).toEqual(['a', 'b']);
    expect(d.content[1].content[0].text).toBe('after');
  });
  test('spoiler inside a list item (4-space pymdown indentation)', () => {
    const item = p('- item\n\n    ???- "T"\n        x').content[0].content[0];
    expect(item.content.map(n => n.type)).toEqual(['paragraph', 'spoiler']);
    expect(item.content[1].content[1].content[0].content[0].text).toBe('x');
  });
  test('spoiler, admonition and footnote definition interrupt a paragraph (pymdown START.search)', () => {
    expect(p('t\n???- "T"\n    x').content.map(n => n.type)).toEqual(['paragraph', 'spoiler']);
    const d = p('Ex.3.\n???- "T"\n    1. a\n    2. b');
    expect(d.content[1].content[1].content.map(n => n.type)).toEqual(['orderedList']);
    expect(p('t\n!!! note\n    x').content[1]).toEqual({ type: 'rawMarkdownBlock', attrs: { source: '!!! note\n    x' } });
    expect(p('t\n[^1]: foot').content[1]).toEqual({ type: 'rawMarkdownBlock', attrs: { source: '[^1]: foot' } });
  });
  test('top-level spoiler must start at column 0', () => {
    expect(p('   ???- "T"\n    x').content[0].type).not.toBe('spoiler');
  });
  test('tab-indented spoiler body', () => {
    const d = p('???- "T"\n\tline');
    expect(d.content[0].content[1].content[0].content[0].text).toBe('line');
  });
  test('raw blocks keep their exact source, including inside spoilers', () => {
    const t = '| a |  b |\n|:--|--:|\n|1|2|';
    expect(p(t).content[0]).toEqual({ type: 'rawMarkdownBlock', attrs: { source: t } });
    expect(p('---').content[0]).toEqual({ type: 'rawMarkdownBlock', attrs: { source: '---' } });
    expect(p('{: .cls }').content[0]).toEqual({ type: 'rawMarkdownBlock', attrs: { source: '{: .cls }' } });
    const d = p('???- "T"\n    | a |\n    |---|\n    | 1 |');
    expect(d.content[0].content[1].content[0]).toEqual({ type: 'rawMarkdownBlock', attrs: { source: '| a |\n|---|\n| 1 |' } });
  });
  test('admonition and footnote bodies are captured', () => {
    const a = '!!! note\n    one\n\n    two';
    expect(p(a + '\n\nafter').content[0]).toEqual({ type: 'rawMarkdownBlock', attrs: { source: a } });
    const f = '[^1]: foot\n    more';
    expect(p(f).content[0]).toEqual({ type: 'rawMarkdownBlock', attrs: { source: f } });
  });
  test('editable headings 2/3 stay editable, others raw', () => {
    expect(p('## two').content[0].type).toBe('heading');
    expect(p('Setext\n---').content[0]).toEqual({ type: 'rawMarkdownBlock', attrs: { source: 'Setext\n---' } });
  });
  test('inline footnote reference stays literal', () => {
    expect(html('a[^1] b')).toBe('<p>a[^1] b</p>');
  });
  test('image mixed with text splits the paragraph', () => {
    const d = p('before ![a](/x.png) after');
    expect(d.content.map(n => n.type)).toEqual(['paragraph', 'image', 'paragraph']);
    expect(d.content[0].content[0].text).toBe('before ');
    expect(d.content[2].content[0].text).toBe(' after');
    expect(d.content[1].attrs).toMatchObject({ src: '/x.png', alt: 'a', title: null });
    expect(p('![a](/x.png)\n![b](/y.png)').content.map(n => n.type)).toEqual(['image', 'image']);
  });
  test('image split leaves no dangling hard breaks', () => {
    const noBreaks = (d) => JSON.stringify(d).indexOf('hardBreak') === -1;
    const d = p('a\n![i](x)\nb');
    expect(d.content.map(n => n.type)).toEqual(['paragraph', 'image', 'paragraph']);
    expect(d.content[0].content).toEqual([{ type: 'text', text: 'a' }]);
    expect(d.content[2].content).toEqual([{ type: 'text', text: 'b' }]);
    expect(noBreaks(d)).toBe(true);
    expect(noBreaks(p('> a\n> ![i](x)'))).toBe(true);
    expect(noBreaks(p('![](x)\nb'))).toBe(true);
  });
  test('image split keeps surrounding marks on the text', () => {
    const d = p('**x ![a](/x.png) y**');
    expect(d.content.map(n => n.type)).toEqual(['paragraph', 'image', 'paragraph']);
    expect(d.content[2].content[0]).toEqual({ type: 'text', text: ' y', marks: [{ type: 'bold' }] });
  });
  test('ordered list start', () => {
    expect(p('3. a\n4. b').content[0].attrs).toMatchObject({ start: 3, tight: true });
  });
  test('results always pass doc.check()', () => {
    for (const src of ['', 'a', '???- "T"\n    ???- "U"', '> ???- "T"\n>     x', '- ![a](/x.png)', '# H\n\n- [ ] t'])
      expect(() => parseMarkdown(src).check()).not.toThrow();
  });
});
