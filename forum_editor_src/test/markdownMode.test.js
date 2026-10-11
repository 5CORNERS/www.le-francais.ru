import { describe, test, expect } from 'vitest';
import {
  wrapSelection,
  prefixLines,
  replaceSelection,
  removeFormatting,
  toggleCode,
  insertSpoilerTemplate,
} from '../src/markdownMode.js';

describe('markdownMode', () => {
  test('link replaces selection (review bug 5)', () =>
    expect(replaceSelection('voir ici', 5, 8, '[ici](https://x.y)').text).toBe('voir [ici](https://x.y)'));

  test('removeFormatting keeps list markers and snake_case (review bug 9)', () => {
    expect(removeFormatting('* item1\n* item2', 0, 15).text).toBe('- item1\n- item2');
    expect(removeFormatting('my_var_name **b**', 0, 17).text).toBe('my_var_name b');
  });

  test('removeFormatting only touches the selection', () => {
    const r = removeFormatting('**a** and **b**', 10, 15);
    expect(r.text).toBe('**a** and b');
    expect([r.selStart, r.selEnd]).toEqual([10, 11]);
  });

  test('wrap and unwrap', () => {
    expect(wrapSelection('a b', 2, 3, '**', '**', 'текст').text).toBe('a **b**');
    expect(wrapSelection('a **b**', 4, 5, '**', '**', 'текст').text).toBe('a b');
  });

  test('wrap uses the placeholder and selects it', () => {
    const r = wrapSelection('a ', 2, 2, '**', '**', 'текст');
    expect(r.text).toBe('a **текст**');
    expect(r.text.slice(r.selStart, r.selEnd)).toBe('текст');
  });

  test('unwrap a selection that includes the markers', () => {
    expect(wrapSelection('a **b**', 2, 7, '**', '**', 'текст').text).toBe('a b');
  });

  test('single-char marker does not unwrap a double marker', () => {
    expect(wrapSelection('a ~~b~~', 4, 5, '~', '~', '2').text).toBe('a ~~~b~~~');
  });

  test('markers next to word characters are literal, never unwrapped (review fix 2)', () => {
    expect(wrapSelection('my_var_name', 3, 6, '_', '_', 'x').text).toBe('my__var__name');
    expect(wrapSelection('2^3^4', 2, 3, '^', '^', '2').text).toBe('2^^3^^4');
    expect(wrapSelection('my_var_name', 2, 7, '_', '_', 'x').text).toBe('my__var__name');
  });

  test('italic * unwraps what visual mode writes', () => {
    expect(wrapSelection('*x*', 1, 2, '*', '*', 'курсив').text).toBe('x');
    expect(wrapSelection('a **b**', 4, 5, '*', '*', 'курсив').text).toBe('a ***b***');
  });

  test('toggleCode single vs multi line', () => {
    expect(toggleCode('x', 0, 1).text).toBe('`x`');
    expect(toggleCode('x\ny', 0, 3).text).toBe('```\nx\ny\n```');
  });

  test('toggleCode unwraps', () => {
    expect(toggleCode('`x`', 1, 2).text).toBe('x');
    expect(toggleCode('```\nx\ny\n```', 0, 11).text).toBe('x\ny');
  });

  test('prefixLines toggles quote', () => expect(prefixLines('a\nb', 0, 3, '> ').text).toBe('> a\n> b'));

  test('prefixLines toggles off and supports numbering', () => {
    expect(prefixLines('> a\n> b', 0, 7, '> ').text).toBe('a\nb');
    expect(prefixLines('a\nb', 0, 3, (i) => (i + 1) + '. ').text).toBe('1. a\n2. b');
  });

  test('prefixLines skips blank lines (review fix 6)', () => {
    expect(prefixLines('a\n\nb', 0, 4, '- ').text).toBe('- a\n\n- b');
    expect(prefixLines('a\n\nb', 0, 4, (i) => (i + 1) + '. ').text).toBe('1. a\n\n2. b');
    expect(prefixLines('> a\n\n> b', 0, 8, '> ').text).toBe('a\n\nb');
  });

  test('prefixLines with a caret keeps the caret on its text', () => {
    const r = prefixLines('ab', 1, 1, '## ');
    expect(r.text).toBe('## ab');
    expect([r.selStart, r.selEnd]).toEqual([4, 4]);
  });

  test('insertSpoilerTemplate indents the selection', () => {
    const r = insertSpoilerTemplate('x\ny', 0, 3);
    expect(r.text.startsWith('???- "Заголовок спойлера"\n    x\n    y')).toBe(true);
    expect(r.text.slice(r.selStart, r.selEnd)).toBe('Заголовок спойлера');
  });
});
