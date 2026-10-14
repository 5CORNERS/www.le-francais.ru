# Forum editor

Source of the forum post editor (visual + Markdown modes) used on the post form
(`home/templates/pybb/post_form.html`). Built with [TipTap 3](https://tiptap.dev)
(ProseMirror) and an owned Markdown ↔ document converter that matches the
server-side renderer.

The build output, `home/static/js/forum-editor.js` (+ `.map`), **is committed**.
Production and backend development never run Node; only rebuild when you change
something in this directory.

## Commands

Requires Node ≥ 20. Run inside `forum_editor_src/`:

```bash
npm install          # once
npm test             # Vitest + jsdom, all unit/round-trip tests
npm run test:watch
npm run build        # → ../home/static/js/forum-editor.js and .map
```

After `npm run build`, commit the rebuilt bundle and map together with the
source change. Locally, Django serves the unhashed file name in `DEBUG`, so
hard-reload the page (Ctrl+Shift+R) to pick up a new build; in production
`collectstatic` content-hashes the file name (don't add `?v=` query strings).

## How it works

```
textarea#id_body  ← the submitted form field and source of truth
      ▲  serialize on every edit          │  parse on load / mode switch
      │                                   ▼
  serializer.js  ◄── ProseMirror doc ──►  parser.js (markdown-it + plugins)
                         │
                  TipTap editor (visual mode)
```

- Visual mode edits a ProseMirror document; every change is serialized into the
  textarea synchronously. Markdown mode is the plain textarea.
- The stored format is unchanged: Markdown for Python-Markdown 2.6.11 +
  pymdown-extensions 5.0, rendered by `forum/markup_engines.py`
  (`CustomMarkdownParser`, with `nl2br`, `smarty`, `safe_mode='escape'`).
- Markdown the editor can't model (tables, footnotes, admonitions, task lists,
  linked images, …) is kept verbatim as a read-only *raw block* chip and saved
  back byte-for-byte.
- If parsing fails, the editor opens in Markdown mode with a notice; the
  textarea is never overwritten.
- In visual mode, Markdown typed as you go is converted on the fly (TipTap
  input rules): `# `…`###### `, `> `, `- `, `1. `, ```` ``` ````, `**bold**`,
  `*italic*`, `` `code` ``, `~~strike~~`, `==mark==`. Ctrl+Z right after
  undoes the conversion. The toolbar offers only H2/H3, but headings of all
  levels are editable.
- Undo in visual mode survives a trip to Markdown mode and back (the Markdown
  edits are one undo step); the initial load is never undoable. Markdown mode
  uses the browser's own textarea undo.

## Layout

| Path | Responsibility |
|---|---|
| `src/index.js` | Auto-init on `#id_body`, exposes `window.forumEditor` |
| `src/editor.js` | `createForumEditor()`: TipTap setup, textarea sync, mode switching, undo history, public API |
| `src/commands.js` | Toolbar commands (`data-cmd`) for both modes, active states |
| `src/markdownMode.js` | Pure textarea string transforms used by Markdown-mode commands |
| `src/keymap.js` | Keyboard shortcuts (Latin + Cyrillic layouts), Enter/ArrowRight/Backspace rules |
| `src/spoilerCommands.js`, `src/blockRange.js` | Spoiler wrap/unwrap, shared block-range helpers |
| `src/upload.js` | Image paste / drop / file picker → `POST /forum/upload-image/` |
| `src/url.js` | URL allow-list for links and images |
| `src/ui/` | Toolbar markup (copied from the legacy editor), link/image modals, emoji picker, resize handle |
| `src/schema/` | TipTap nodes and marks; their DOM must match `home/static/css/forum-editor.css` |
| `src/markdown/md.js` | markdown-it instance configured like the server |
| `src/markdown/plugins/` | Syntax plugins: `^^u^^`, `++kbd++`, `???-` spoilers, raw blocks, emoji shortcodes, and `py*` plugins that mimic Python-Markdown quirks (escapes, headings, lists, link destinations) |
| `src/markdown/parser.js` / `serializer.js` | Markdown → document / document → Markdown |
| `src/stubs/` | Build-time stubs (keeps TipTap's Link + linkifyjs out of the bundle) |
| `test/` | Vitest suites; `test/fixtures/*.md` round-trip fixtures |
| `scripts/parity.py`, `scripts/normalize.mjs` | Server parity check (see below) |

### Public API (`window.forumEditor`)

Used by the reply/quote handlers in `post_form.html`:
`currentMode`, `$visualEditor`, `focus()`, `restoreSelection()`,
`getMarkdown()`, `setMarkdown(md)`, `insertQuote(md)`, `insertMarkdown(md)`,
`syncVisualFromMarkdown()`, `syncMarkdownFromVisual()`, `setMode(mode)`,
`executeCommand(cmd)`, `destroy()`.

## Converter rules worth knowing

- Emphasis is written with `*` / `**` (`_` doesn't work inside a word on the
  server); italic opened inside bold uses `_`, because the server mis-renders
  `**a *b* c**`.
- Escapes are added only where text would otherwise parse as syntax, and only
  escapes the server honours (`plugins/pyEscape.js`). HTML entities are not
  decoded (the server shows them literally).
- A single newline inside a paragraph is a hard break (`nl2br`).
- Spoilers are written as `???- "Title"` + a 4-space-indented body.
- Non-breaking spaces are preserved (French typography).
- Code blocks are always written fenced, with a fence longer than any backtick
  run inside.

## Tests and server parity

- `test/roundtrip.test.js` runs every fixture in `test/fixtures/`:
  `name.md` alone must round-trip unchanged; `name.md` + `name.expected.md`
  must normalize to the expected file and then stay stable.
  `crlf.md` keeps CRLF bytes (`.gitattributes`).
- `scripts/parity.py` renders fixtures (and optionally real posts) with the real
  server parser before and after a parse→serialize pass and compares the HTML.
  Run it from the repository root through micromamba (see `AGENTS.md`):

  ```powershell
  $env:MAMBA_ROOT_PREFIX = "$pwd\tools\mamba_root"
  tools\bin\micromamba.exe run -p tools\env python forum_editor_src/scripts/parity.py
  # also sample N posts from the local database (nothing is written to disk):
  tools\bin\micromamba.exe run -p tools\env python forum_editor_src/scripts/parity.py --db 500
  ```

When you change the parser or serializer, run both `npm test` and the parity
script.

## Adding a new Markdown syntax

1. Schema: add the node/mark in `src/schema/` with DOM that the existing CSS
   styles (or add CSS to the `/* TipTap editor */` section of
   `forum-editor.css`).
2. Parser: a markdown-it plugin in `src/markdown/plugins/` and the token mapping
   in `parser.js`.
3. Serializer: the node/mark writer in `serializer.js`, plus any escaping its
   delimiter needs.
4. Tests: parser + serializer cases and a round-trip fixture; check with
   `parity.py`.

## Rollback to the legacy editor

The previous jQuery editor is kept as `home/static/js/forum-editor-legacy.js`.
Set `FORUM_EDITOR_LEGACY=True` (also accepts `true`, `1`, `yes`) in the
environment, or append `?editor=legacy` to a page URL, to serve it instead —
no rebuild needed.
