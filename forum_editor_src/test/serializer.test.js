import { describe, expect, test } from 'vitest';
import { getForumSchema } from '../src/schema/index.js';
import { parseMarkdown } from '../src/markdown/parser.js';
import { serializeMarkdown } from '../src/markdown/serializer.js';

const text = (s, marks = []) => ({ type: 'text', text: s, marks: marks.map((m) => (typeof m === 'string' ? { type: m } : m)) });
const para = (...content) => ({ type: 'paragraph', content });
const doc = (...content) => ({ type: 'doc', content });
const codeBlock = (s) => ({ type: 'codeBlock', content: [text(s)] });
const ser = (json) => serializeMarkdown(getForumSchema().nodeFromJSON(json));
const rt = (md) => serializeMarkdown(parseMarkdown(md));

describe('serializeMarkdown', () => {
  test('emphasis always uses asterisks (review bug 7)', () => {
    expect(ser(doc(para(text('mot'), text('ifs', ['italic']))))).toBe('mot*ifs*');
    expect(rt('_i_ __b__')).toBe('*i* **b**');
  });
  test('italic inside bold uses `_` where Python-Markdown needs it', () => {
    // Python-Markdown 2.6 renders `**a *b* c**` as `<em><em>a *b</em> c</em>*`.
    expect(rt('**a *b* c**')).toBe('**a _b_ c**');
    expect(rt('**a *b***')).toBe('**a _b_**');
    expect(rt('**a (*b*), *c* d**')).toBe('**a (_b_), _c_ d**');
    // Cases the server renders fine with `*` stay as they are.
    expect(rt('***a*** **b**')).toBe('***a*** **b**');
    expect(rt('***a***')).toBe('***a***');
    expect(rt('*a **b** c*')).toBe('*a **b** c*');
    expect(rt('**a *b*c**')).toBe('**a *b*c**');
    expect(rt('**a*b* c**')).toBe('**a*b* c**');
    expect(rt('**a *b* c** *d*')).toBe('**a _b_ c** *d*');
  });
  test('nbsp preserved (review bug 8)', () => expect(rt('Bonjour !')).toBe('Bonjour !'));
  test('literal syntax typed in visual mode stays literal (Review Focus 1)', () => {
    // `\n` in a probe = a hard break in the visual paragraph.
    for (const s of ['**not bold**', '# 1', '2*3*4', 'a_b_c', 'my_var_name', '- not a list', '1. not a list', '> not quote', '==x==', '++x++', ':smile:',
      '| a |\n|---|', 'a | b\n|---|---|']) {
      const parts = [];
      s.split('\n').forEach((line, i) => { if (i) parts.push({ type: 'hardBreak' }); parts.push(text(line)); });
      const md = ser(doc(para(...parts)));
      const reparsed = parseMarkdown(md);
      expect(reparsed.textContent).toBe(s.replace(/\n/g, ''));
      expect(reparsed.firstChild.type.name).toBe('paragraph');
      expect(reparsed.firstChild.firstChild.marks).toHaveLength(0);
      expect(serializeMarkdown(reparsed)).toBe(md);
    }
  });
  test('no gratuitous escapes', () => {
    expect(ser(doc(para(text('my_var_name 2*3 a ~ b'))))).toBe('my_var_name 2*3 a ~ b');
  });
  test('runs of three or more stars are escaped (Python-Markdown: `a *** b` is `a <em>*</em> b`)', () => {
    expect(ser(doc(para(text('a *** b **** c'))))).toBe('a \\*\\*\\* b \\*\\*\\*\\* c');
    expect(rt('a \\*\\*\\* b')).toBe('a \\*\\*\\* b');
    expect(ser(doc(para(text('a ** b'))))).toBe('a ** b');
  });
  test('literal stars are escaped when the block has another star (Python-Markdown pairs any two)', () => {
    // Server: `*ehmi, *h1 et *am*` renders `<em>ehmi, </em>h1 et <em>am</em>`-like garbage.
    expect(ser(doc(para(text('*ehmi, de *h1 et '), text('am', ['italic']))))).toBe('\\*ehmi, de \\*h1 et *am*');
    expect(ser(doc(para(text('2*3 '), text('a', ['italic']))))).toBe('2\\*3 *a*');
    // markdown-it pairs these too: escaping the first settles both servers.
    expect(ser(doc(para(text('2*3 et 4*5'))))).toBe('2\\*3 et 4*5');
    // `**` pairs do not count: Python-Markdown matches them first.
    expect(ser(doc(para(text('2*3 '), text('a', ['bold']))))).toBe('2*3 **a**');
  });
  test('code is literal', () => {
    expect(ser(doc(para(text('a `b` c', ['code']))))).toBe('`` a `b` c ``');
    expect(ser(doc(codeBlock('x\n```\ny')))).toBe('````\nx\n```\ny\n````');
  });
  test('hard break is a bare newline', () => expect(rt('a\nb')).toBe('a\nb'));
  test('spoiler format', () => expect(rt('???- "T"\n    - a\n    - b')).toBe('???- "T"\n    - a\n    - b'));
  test('raw block verbatim', () => expect(rt('x\n\n| a |\n|---|\n\ny')).toBe('x\n\n| a |\n|---|\n\ny'));
  test('upload placeholders are not serialized', () =>
    expect(ser(doc(para(text('a')), { type: 'image', attrs: { src: '', uploadId: 'u1' } }))).toBe('a'));
  test('idempotent', () => { const n1 = rt('*a* _b_\n\n* x\n* y'); expect(rt(n1)).toBe(n1); });

  // Additional coverage beyond the brief.
  test('every mark', () => {
    const md = '**b** *i* ^^u^^ ~~s~~ ==m== ++ctrl+c++ x^p^ x~b~ `c` [t](https://x.y)';
    expect(rt(md)).toBe(md);
  });
  test('superscript / subscript spaces are backslash-escaped', () => {
    expect(ser(doc(para(text('x'), text('a b', ['superscript']))))).toBe('x^a\\ b^');
    expect(rt('x~a\\ b~')).toBe('x~a\\ b~');
  });
  test('headings, quotes, lists, code fences round-trip', () => {
    for (const md of ['## A\n\n### B', '> q\n>\n> r', '- a\n- b', '- a\n\n- b', '3. a\n4. b',
      '- a\n    - b\n    - c\n- d', '```py\nx = 1\n```', '> - a\n> - b', '- a\n\n    ```\n    code\n    ```'])
      expect(rt(md)).toBe(md);
  });
  test('list item starting with an image', () => {
    expect(rt('- ![a](x)')).toBe('- ![a](x)');
    expect(rt('- ![a](x)\n- b')).toBe('- ![a](x)\n- b');
  });
  test('destinations: parentheses escaped, non-ASCII kept as written', () => {
    // Python-Markdown 2.6 cuts `![](/a_(1250).jpg)` at the first `)`.
    expect(rt('![](/x_\\(1250\\).jpg)')).toBe('![](/x_\\(1250\\).jpg)');
    expect(rt('[a](/x_(1250).jpg)')).toBe('[a](/x_\\(1250\\).jpg)');
    expect(rt('[a](/le%C3%A7ons/ça)')).toBe('[a](/le%C3%A7ons/ça)');
  });
  test('images', () => {
    expect(rt('![a](/m/a.png "t")')).toBe('![a](/m/a.png "t")');
    expect(rt('a\n\n![my_photo](/x.png)\n\nb')).toBe('a\n\n![my_photo](/x.png)\n\nb');
    expect(rt('![a\\*b\\*c](/x.png)')).toBe('![a\\*b\\*c](/x.png)');
  });
  test('link titles are kept', () => {
    expect(rt('voir [la page](/forum/ "Le forum") ici')).toBe('voir [la page](/forum/ "Le forum") ici');
    expect(rt('[a](/x "say \\"hi\\"")')).toBe('[a](/x "say \\"hi\\"")');
    expect(rt('[a](/x "t") [b](/x)')).toBe('[a](/x "t") [b](/x)');
  });
  test('raw blocks nested in containers are re-indented', () => {
    for (const md of ['- x\n\n    | a |\n    |---|', '> # H1\n>\n> after', '???- "T"\n    | a |\n    |---|\n\n    ---'])
      expect(rt(md)).toBe(md);
  });
  test('spoiler body blank lines carry no trailing spaces', () => {
    expect(rt('???- "T"\n    a\n\n    b\n\nafter')).toBe('???- "T"\n    a\n\n    b\n\nafter');
    expect(rt('???- "**B** t"\n    x')).toBe('???- "**B** t"\n    x');
    expect(rt('- item\n\n    ???- "T"\n        x')).toBe('- item\n\n    ???- "T"\n        x');
  });
  test('literal text needing server-specific escapes', () => {
    const cases = {
      '#hashtag': '\\#hashtag', // Python-Markdown headings need no space
      // Character references are shown literally by the server (safe_mode).
      '???- "T"': '???\\- "T"',
      '??? "T"': '???\\ "T"',
      '??? note': '???\\ note', // `\ ` is an escaped space on the server
      '<http://a.b>': '<http\\://a.b>',
      'a\\ b': 'a\\\\ b', // `\ ` is an escaped space on the server
      '[x]: http://y': '\\[x]: http://y',
      '[ ] todo': '[ ] todo',
      '!!! note': '\\!!! note',
      '!': '!',
      '[a](b)': '\\[a](b)',
    };
    for (const [s, md] of Object.entries(cases)) {
      expect(ser(doc(para(text(s))))).toBe(md);
      expect(parseMarkdown(md).textContent).toBe(s);
    }
  });
  test('`???word` has no server escape: a visible backslash, but never a spoiler', () => {
    const md = ser(doc(para(text('???note'))));
    expect(md).toBe('\\???note');
    expect(parseMarkdown(md).firstChild.type.name).toBe('paragraph');
  });
  test('character references are literal, as on the server (safe_mode)', () => {
    expect(rt('AT&amp;T')).toBe('AT&amp;T');
    expect(parseMarkdown('AT&amp;T').textContent).toBe('AT&amp;T');
    expect(ser(doc(para(text('a &lt; b &#63;'))))).toBe('a &lt; b &#63;');
  });
  test('backslash escapes follow the server (Python-Markdown ESCAPED_CHARS)', () => {
    expect(parseMarkdown('\\& \\< \\? \\*').textContent).toBe('\\& \\< \\? *');
    expect(ser(doc(para(text('\\& \\*'))))).toBe('\\& \\\\*');
    expect(rt('\\& \\< \\?')).toBe('\\& \\< \\?');
  });
  test('trailing hashes in headings survive both renderers', () => {
    const h = (s) => ser(doc({ type: 'heading', attrs: { level: 2 }, content: [text(s)] }));
    expect(h('C#')).toBe('## C# ');
    expect(h('a ##')).toBe('## a \\## ');
    expect(rt('## C# ')).toBe('## C# ');
    expect(parseMarkdown('## a \\## ').textContent).toBe('a ##');
  });
  test('headings of every level are written as ATX with a space', () => {
    const h = (level, s) => ser(doc({ type: 'heading', attrs: { level }, content: [text(s)] }));
    expect(h(1, 'Titre')).toBe('# Titre');
    expect(h(5, 'cinq')).toBe('##### cinq');
    expect(h(6, '# seven')).toBe('###### # seven'); // server: h6 `# seven`
    expect(parseMarkdown(h(6, '# seven')).textContent).toBe('# seven');
    expect(rt('#Titre\n\n#### four')).toBe('# Titre\n\n#### four');
    expect(rt('Titre\n=====\n\nSous\n---')).toBe('# Titre\n\n## Sous');
    expect(rt('# 1\n\n## 2\n\n### 3\n\n#### 4\n\n##### 5\n\n###### 6')).toBe('# 1\n\n## 2\n\n### 3\n\n#### 4\n\n##### 5\n\n###### 6');
  });
  test('task-like text at the start of a list item stays literal', () => {
    const md = ser(doc({ type: 'bulletList', content: [{ type: 'listItem', content: [para(text('[ ] todo'))] }] }));
    expect(md).toBe('- \\[ ] todo');
    expect(parseMarkdown(md).firstChild.type.name).toBe('bulletList');
  });
  test('literal syntax after a hard break stays literal', () => {
    const md = ser(doc(para(text('a'), { type: 'hardBreak' }, text('- b'), { type: 'hardBreak' }, text('---'))));
    // `- b` after a line break is no list (Python-Markdown needs a blank line).
    expect(md).toBe('a\n- b\n\\---');
    expect(rt(md)).toBe(md);
  });
  test('output has no trailing newline and empty doc is empty', () => {
    expect(rt('')).toBe('');
    expect(rt('a\n\n')).toBe('a');
    expect(rt('```\nx\n```\n')).toBe('```\nx\n```');
  });
  // Timing-sensitive under a loaded machine: retried (controller ruling), bound unchanged.
  test('2,000 paragraphs serialize in under 100 ms', { retry: 2 }, () => {
    const src = Array.from({ length: 2000 }, (_, i) => `Paragraphe **${i}** avec du texte_x et 2*3.`).join('\n\n');
    const d = parseMarkdown(src);
    expect(serializeMarkdown(d)).toBe(src);
    // Median of five after a warm-up run: the full suite runs files in
    // parallel, and single runs can lose their CPU slice to another worker.
    serializeMarkdown(d);
    const times = [];
    for (let i = 0; i < 5; i++) {
      const t0 = performance.now();
      serializeMarkdown(d);
      times.push(performance.now() - t0);
    }
    times.sort((x, y) => x - y);
    expect(times[2]).toBeLessThan(100);
  });
});
