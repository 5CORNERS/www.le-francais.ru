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
    // Container prefixes are kept as typed (final review 3: was normalised to '- ').
    expect(removeFormatting('* item1\n* item2', 0, 15).text).toBe('* item1\n* item2');
    expect(removeFormatting('my_var_name **b**', 0, 17).text).toBe('my_var_name b');
  });

  const whole = (s) => removeFormatting(s, 0, s.length).text;

  test('removeFormatting keeps spoiler body indentation (final review 3)', () => {
    expect(whole('    **a** one\n    **b** two')).toBe('    a one\n    b two');
    expect(whole('???- "Titre"\n    **a** one')).toBe('???- "Titre"\n    a one');
  });

  test('removeFormatting keeps nested list structure (final review 3)', () => {
    expect(whole('- **x**\n    - *nested*')).toBe('- x\n    - nested');
    expect(whole('1. **x**\n2. ~~y~~')).toBe('1. x\n2. y');
  });

  test('removeFormatting keeps quote prefixes (final review 3)', () => {
    expect(whole('**bob**:\n> some *quoted* text')).toBe('bob:\n> some quoted text');
    expect(whole('> > **deep**')).toBe('> > deep');
  });

  test('removeFormatting leaves fenced code untouched (final review 3)', () => {
    expect(whole('**a**\n```\n**code**\n```\n*b*')).toBe('a\n```\n**code**\n```\nb');
    // A fence opened before the selection still protects its lines.
    const text = '```\n**code**\n```\n**z**';
    expect(removeFormatting(text, 4, text.length).text).toBe('```\n**code**\n```\nz');
  });

  test('removeFormatting on a partial line keeps the rest of the line', () => {
    const r = removeFormatting('- **a** and **b**', 12, 17);
    expect(r.text).toBe('- **a** and b');
    expect([r.selStart, r.selEnd]).toEqual([12, 13]);
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

  test('italic twice on an in-word selection unwraps again (Task 8 minor)', () => {
    const r1 = wrapSelection('motifs', 3, 6, '*', '*', 'курсив');
    expect(r1.text).toBe('mot*ifs*');
    expect(r1.text.slice(r1.selStart, r1.selEnd)).toBe('ifs');
    const r2 = wrapSelection(r1.text, r1.selStart, r1.selEnd, '*', '*', 'курсив');
    expect(r2.text).toBe('motifs');
    expect(r2.text.slice(r2.selStart, r2.selEnd)).toBe('ifs');
    expect(wrapSelection('mot**ifs**s', 5, 8, '**', '**', 'жирный текст').text).toBe('motifss');
    // Selection including the markers.
    expect(wrapSelection('mot*ifs*', 3, 8, '*', '*', 'курсив').text).toBe('motifs');
  });

  test('in-word markers that are not an emphasis pair stay literal', () => {
    expect(wrapSelection('a*b*c`x*y*z`', 8, 9, '*', '*', 'курсив').text).toBe('a*b*c`x**y**z`');
    expect(wrapSelection('my_var_name', 3, 6, '_', '_', 'x').text).toBe('my__var__name');
    expect(wrapSelection('2^3^4', 2, 3, '^', '^', '2').text).toBe('2^^3^^4');
  });

  test('prefixLines quote over a blank line makes one blockquote (Task 8 minor)', () => {
    expect(prefixLines('a\n\nb', 0, 4, '> ').text).toBe('> a\n>\n> b');
    expect(prefixLines('> a\n>\n> b', 0, 10, '> ').text).toBe('a\n\nb');
    expect(prefixLines('a\n\nb', 0, 4, '- ').text).toBe('- a\n\n- b');
  });

  test('insertSpoilerTemplate indents selected lines under the title', () => {
    const r = insertSpoilerTemplate('before\n\nl1\nl2\n\nl3\n\nafter', 8, 17);
    expect(r.text).toBe('before\n\n???- "Заголовок спойлера"\n    l1\n    l2\n\n    l3\n\nafter');
    expect(r.text.slice(r.selStart, r.selEnd)).toBe('Заголовок спойлера');
  });

  test('insertSpoilerTemplate indents the selection', () => {
    const r = insertSpoilerTemplate('x\ny', 0, 3);
    expect(r.text.startsWith('???- "Заголовок спойлера"\n    x\n    y')).toBe(true);
    expect(r.text.slice(r.selStart, r.selEnd)).toBe('Заголовок спойлера');
  });
});
