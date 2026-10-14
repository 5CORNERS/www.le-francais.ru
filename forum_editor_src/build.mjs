import { build } from 'esbuild';
import { statSync } from 'node:fs';

const outfile = '../home/static/js/forum-editor.js';

await build({
  entryPoints: ['src/index.js'],
  bundle: true,
  format: 'iife',
  target: 'es2018',
  minify: true,
  sourcemap: true,
  outfile,
  legalComments: 'none',
  // StarterKit's unused Link extension (and linkifyjs with it) is not bundled.
  alias: { '@tiptap/extension-link': './src/stubs/noTiptapLink.js' },
});

console.log('Built ' + outfile + ' (' + statSync(outfile).size + ' bytes)');
