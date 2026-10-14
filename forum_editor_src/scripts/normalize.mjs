// Reads a JSON array of Markdown strings on stdin and writes a JSON array of
// { ok: true, out } | { ok: false, error } (out = serialize(parse(md))).
// Used by parity.py --db; also handy for ad-hoc checks.
import { parseMarkdown } from '../src/markdown/parser.js';
import { serializeMarkdown } from '../src/markdown/serializer.js';

let input = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', (chunk) => { input += chunk; });
process.stdin.on('end', () => {
  const results = JSON.parse(input).map((md) => {
    try {
      return { ok: true, out: serializeMarkdown(parseMarkdown(md)) };
    } catch (e) {
      return { ok: false, error: String((e && e.message) || e) };
    }
  });
  process.stdout.write(JSON.stringify(results));
});
