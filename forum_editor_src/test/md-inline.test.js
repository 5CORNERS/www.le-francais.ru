import { describe, expect, test } from 'vitest';
import { createMarkdownIt } from '../src/markdown/md.js';

const r = s => createMarkdownIt().renderInline(s);

describe('markdown-it inline syntax', () => {
  test.each([
    ['^^u^^', '<u>u</u>'], ['~~s~~', '<s>s</s>'], ['==m==', '<mark>m</mark>'],
    ['^sup^', '<sup>sup</sup>'], ['~sub~', '<sub>sub</sub>'], ['++ctrl+c++', '<kbd>ctrl+c</kbd>'],
    ['a ^^b^^ ^c^', 'a <u>b</u> <sup>c</sup>'], ['__b__', '<strong>b</strong>'], ['_i_', '<em>i</em>'],
    [':smile: :nope:', '😄 :nope:'], ['`:smile:`', '<code>:smile:</code>'],
    ['<script>x</script>', '&lt;script&gt;x&lt;/script&gt;'],
  ])('%s', (src, html) => expect(r(src)).toBe(html));

  test('single newline is a hard break', () =>
    expect(createMarkdownIt().render('a\nb')).toBe('<p>a<br>\nb</p>\n'));

  test('token names', () => {
    const types = s => createMarkdownIt().parseInline(s, {})[0].children.map(t => t.type);
    expect(types('^^u^^')).toEqual(['underline_open', 'text', 'underline_close']);
    expect(types('==m==')).toEqual(['mark_open', 'text', 'mark_close']);
    expect(types('~~s~~')).toEqual(['s_open', 'text', 's_close']);
    expect(types('++k++')).toEqual(['kbd']);
    expect(types(':smile:')).toEqual(['text']);
  });
});
