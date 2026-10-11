import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { describe, expect, test } from 'vitest';
import { parseMarkdown } from '../src/markdown/parser.js';
import { serializeMarkdown } from '../src/markdown/serializer.js';

// Fixture convention: `name.md` alone is canonical (round-trips unchanged);
// with a sibling `name.expected.md` it is normalizing.
const dir = path.join(path.dirname(fileURLToPath(import.meta.url)), 'fixtures');
const read = (file) => fs.readFileSync(path.join(dir, file), 'utf8').replace(/\r?\n$/, '');
const rt = (md) => serializeMarkdown(parseMarkdown(md));

const sources = fs.readdirSync(dir).filter((f) => f.endsWith('.md') && !f.endsWith('.expected.md')).sort();
const canonical = sources.filter((f) => !fs.existsSync(path.join(dir, f.replace(/\.md$/, '.expected.md'))));
const normalizing = sources.filter((f) => !canonical.includes(f));

describe('round-trip fixtures', () => {
  test('fixtures are present', () => {
    expect(canonical.length).toBeGreaterThan(0);
    expect(normalizing.length).toBeGreaterThan(0);
  });

  test.each(canonical)('canonical %s', (file) => {
    const src = read(file);
    expect(rt(src)).toBe(src);
  });

  test.each(normalizing)('normalizing %s', (file) => {
    const src = read(file);
    const expected = read(file.replace(/\.md$/, '.expected.md'));
    expect(rt(src)).toBe(expected);
    expect(rt(expected)).toBe(expected);
  });
});
