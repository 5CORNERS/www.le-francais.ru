# Forum Editor Rewrite (TipTap + Owned Markdown Converter) — Design

**Date:** 2026-10-11
**Branch base:** `render`
**Replaces:** `home/static/js/forum-editor.js` (2,531-line jQuery/`execCommand` IIFE)

## 1. Goal & Success Criteria

Replace the hand-rolled forum WYSIWYG editor with a maintainable, modular editor built on TipTap (ProseMirror), with an owned, unit-tested Markdown ↔ document converter.

Success means:

1. **Exact feature parity** with the current editor (commands, shortcuts, modes, upload, emoji, resize, reply/quote integration). No new features.
2. **Identical look**: toolbar, modals, emoji picker, resize handle and the editing area render the same with the existing `home/static/css/forum-editor.css` (only ProseMirror-specific additive CSS allowed). Verified by old/new screenshot comparison.
3. **No content loss**: Markdown the editor cannot model is preserved byte-for-byte.
4. **Storage format unchanged**: posts remain Markdown rendered server-side by `forum/markup_engines.py` (`CustomMarkdownParser`, Python-Markdown 2.6.11 + pymdown-extensions 5.0). No server changes.
5. **Unit tests** for HTML ↔ Markdown conversion, including regression cases for every bug found in the 2026-10-11 review of `feature/forum-wide-layout-toggle`.

### Review bugs this design must eliminate

| # | Bug | Eliminated by |
|---|-----|---------------|
| 1 | `___`/`__` bold regex corrupts code placeholders | markdown-it tokenizer (no placeholder substitution) |
| 2 | Empty spoiler/blockquote deleted by "empty editor cleanup" | No cleanup handler; placeholders via decorations |
| 3 | Multi-block code toggle deletes unselected text | `code` command converts exactly the selected blocks |
| 4 | Delete with "select-all" heuristic wipes images | ProseMirror default deletion |
| 5 | Markdown-mode link duplicates selection | Link replaces selection |
| 6 | Enter after inline tag inserts `<p>` outside editor / into `<ul>` | ProseMirror default Enter |
| 7 | `<em>` serialized as `_x_` breaks in-word italics | Serializer always emits `*` |
| 8 | All U+00A0 replaced with spaces | NBSP preserved; no spacer characters inserted |
| 9 | Markdown-mode removeFormat strips list markers / snake_case | Parse→strip marks→serialize on selection |
| 10 | Ctrl+B inside bold run jumps caret | ProseMirror stored marks toggle |

## 2. Architecture

New standalone package, own toolchain, modern Node (independent of `static_src/`'s Node 14 gulp pipeline). Production never runs Node: the built bundle is committed.

```
forum_editor_src/
├── package.json          # esbuild, vitest, jsdom, @tiptap/*, markdown-it, prosemirror-markdown
├── build.mjs             # esbuild → ../home/static/js/forum-editor.js (+ .map); IIFE; target es2018
├── scripts/parity.py     # server-render parity check (manual, via micromamba)
├── src/
│   ├── index.js          # entry: createForumEditor(options); auto-init on #id_body; window.forumEditor
│   ├── markdown/         # PURE: no live editor; unit-tested in Node
│   │   ├── parser.js     # markdown-it + plugins → ProseMirror doc (via schema)
│   │   ├── serializer.js # ProseMirror doc → Markdown
│   │   └── plugins/      # underline, mark, keys, supsub, details (spoiler), emojiShortcode, rawBlock
│   ├── schema/           # TipTap extensions; renderHTML matches current DOM exactly
│   ├── editor.js         # TipTap Editor assembly, mode switching, textarea sync
│   ├── commands.js       # toolbar command id → TipTap chain; active-state map
│   ├── keymap.js         # shortcut table (incl. Cyrillic-layout keys)
│   ├── ui/               # toolbar.js, linkModal.js, emojiPicker.js, resizeHandle.js
│   └── upload.js         # paste / drop / button → POST uploadUrl
└── test/
    ├── parser.test.js
    ├── serializer.test.js
    ├── roundtrip.test.js
    └── fixtures/         # *.md (canonical) and *.md + *.expected.md (normalizing)
```

**Data flow.** `<textarea id="id_body">` remains the submitted form field and the source of truth.
- Visual mode: every TipTap `update` synchronously serializes → `textarea.value` (no debounce; posts are small) and dispatches `input`/`change` on the textarea.
- Safety net: a capture-phase `submit` listener on the parent `<form>` serializes once more before submission. (Programmatic `form.submit()` fires no `submit` event; the synchronous sync covers that case.)
- Switch to Markdown: flush, hide editor, show textarea.
- Switch to visual: parse `textarea.value` → `editor.commands.setContent(doc)`.

**No jQuery inside the editor.** The bundle includes all dependencies (no CDN).

**Public API (`window.forumEditor`):**
- Kept for compatibility: `currentMode` (`'visual' | 'markdown'`), `$visualEditor` (jQuery wrapper of the editing element, only if `window.jQuery` exists), `restoreSelection()`, `focus()`.
- New: `insertQuote(markdown)`, `getMarkdown()`, `setMarkdown(markdown)`, `destroy()`.
- `post_form.html` reply/quote handlers switch to `insertQuote` instead of touching editor DOM.

## 3. Markdown Conversion

Target dialect: what `CustomMarkdownParser` renders — Python-Markdown 2.6.11 with `nl2br`, `smarty`, `pymdownx.{extra, emoji, tasklist, details, superfences, tilde, caret, keys, mark, smartsymbols}`, `safe_mode='escape'`.

markdown-it is initialized with `{ html: false, breaks: true, linkify: false, typographer: false }`. `html: false` mirrors `safe_mode='escape'` (raw HTML such as `<script>` becomes literal text); `breaks: true` mirrors `nl2br`, and the parser maps `softbreak` tokens to `hardBreak`.

### Mapping

| Markdown | Node/mark | Editor DOM (must match current CSS) |
|---|---|---|
| `**b**` (also parse `__b__`) | `bold` | `<strong>` |
| `*i*` (also parse `_i_`) | `italic` | `<em>` |
| `^^u^^` | `underline` | `<u>` |
| `~~s~~` | `strike` | `<s>` |
| `==m==` | `mark` | `<mark>` |
| `++ctrl+c++` | `kbd` | `<kbd class="editor-key">` |
| `^x^` / `~x~` | `superscript` / `subscript` | `<sup>` / `<sub>` |
| `` `c` `` | `code` | `<code>` |
| fenced ```` ```lang ```` | `codeBlock` (attr `language`) | `<pre class="editor-code-block"><code>` |
| `## ` / `### ` | `heading` (levels 1–6; toolbar offers only H2/H3; user decision 2026-10-12) | `<h2>` / `<h3>` |
| `> ` | `blockquote` | `<blockquote>` |
| `- ` / `1. ` | `bulletList` / `orderedList` (TipTap list extensions extended with attr `tight: boolean`) / `listItem` | `<ul>` / `<ol>` / `<li>` |
| `[t](url)` | `link` | `<a href target="_blank" rel="noopener">` |
| `![alt](url "title")` | `image` (block) | `<img class="forum-embedded-img" alt title>` |
| `???- "Title"` + 4-space-indented body (parse also `??? `, `???+ `, unquoted title) | `spoiler` → `spoilerSummary` + `spoilerBody` | `<details class="forum-spoiler" open><summary>…</summary><div class="spoiler-body">…</div></details>` (always open in editor, as today) |
| single `\n` inside paragraph | `hardBreak` | `<br>` |
| `:shortcode:` (known codes) | text: Unicode emoji char | as today |
| Tables, footnotes, `!!!` admonitions, definition lists, abbreviations, attr_list `{: }`, task lists, any other unrecognized block | `rawMarkdownBlock` (attr `source`, atom, non-editable) | read-only chip showing source; editable only in Markdown mode |

Spoiler schema: `spoilerSummary` content `inline*`; `spoilerBody` content `block+` (paragraphs, lists, code blocks, blockquotes, images, nested spoilers). The markdown-it spoiler plugin de-indents the 4-space body and tokenizes it with the full block parser.

Spoilers serialize as `???- "Title"` followed by the body indented 4 spaces, matching the current `htmlToMarkdown` (`forum-editor.js:445`); fixtures lock this.

### Serializer rules

1. **Context-sensitive escaping**: escape `\ * _ ^ ~ = + [ ] \`` and line-leading `#`, `>`, `-`, `+`, `N.` only where they would otherwise be parsed as syntax. `my_var_name`, `2*3`, `a ~ b` stay unescaped.
2. **NBSP preserved** (U+00A0 written as-is).
3. **Emphasis uses `*` / `**`**, never `_` — except italic opened inside bold, which uses `_` unless it touches a word character (Python-Markdown 2.6 mis-renders `**a *b* c**`; server-verified in Task 6).
4. **Code is literal**: inline code uses a backtick run longer than any inside; code blocks use a fence longer than any backtick run inside; contents never escaped.
5. **Breaks**: `hardBreak` → `\n` (nl2br); blocks separated by one blank line; lists serialized tight or loose per their `tight` attr (parsed from source; new lists default to tight).
6. **Idempotence**: `serialize(parse(serialize(doc))) === serialize(doc)`.
7. **rawMarkdownBlock** emits `source` verbatim.

### Round-trip guarantees (tested)

- **Canonical Markdown** (editor output form): `serialize(parse(md)) === md`.
- **Any Markdown**: `n1 = serialize(parse(md))` is stable (`serialize(parse(n1)) === n1`), and server-rendered HTML of `md` and `n1` is equivalent modulo whitespace (checked by `scripts/parity.py`).

## 4. Editing Behaviour

All editing goes through TipTap commands; no `document.execCommand`.

### Commands (`data-cmd` → behaviour)

| Command | Visual mode | Markdown mode |
|---|---|---|
| bold, italic, underline, strikethrough, mark, kbd, superscript, subscript | `toggleMark`; collapsed caret toggles stored mark | wrap/unwrap selection with syntax (placeholder text if empty) |
| code | single-block selection or caret → toggle inline `code`; selection spanning multiple blocks → convert exactly those blocks into one `codeBlock`, preserving all text | inline backticks for single line; fenced block for multi-line |
| h2, h3 | `toggleHeading` | prefix line(s) |
| quote | `toggleBlockquote` | prefix `> ` |
| ul, ol | `toggleBulletList` / `toggleOrderedList` | prefix `- ` / `1. ` |
| link | existing modal; selection → apply link mark; none → insert text with mark | replace selection with `[sel](url)` |
| image | file picker → upload → insert `image` | upload → insert `![alt](url)` at caret |
| spoiler | insert `spoiler` with caret in summary; empty summary/body show placeholders via decorations (never auto-removed) | insert `???- ` template |
| removeFormat | `unsetAllMarks` + `clearNodes` on selection | parse selection → strip marks → serialize (only real emphasis removed) |

Toolbar active states come from `editor.isActive(...)` per command, updated on `selectionUpdate`/`transaction`.

### Keyboard shortcuts (parity — `keymap.js`)

Matched by `event.code` with `event.key` fallback, including Cyrillic-layout keys, in both modes:

| Shortcut | Command |
|---|---|
| Ctrl/Cmd+B / I / U | bold / italic / underline |
| Ctrl/Cmd+K | link |
| Ctrl/Cmd+Shift+X, Alt+Shift+5 | strikethrough |
| Ctrl/Cmd+Shift+M | code |
| Ctrl/Cmd+Shift+P | spoiler |
| Ctrl/Cmd+Shift+. | quote |
| Ctrl/Cmd+Shift+N, Ctrl/Cmd+\ | removeFormat |
| Ctrl/Cmd+6, `^` | never intercepted (dead key) |

The full list must be extracted from the current `handleKeydown` during implementation and checked off one-to-one.

Enter, Backspace, Delete, select-all, undo/redo: ProseMirror/TipTap defaults. ArrowRight at the end of a mark exits it via stored marks (no spacer characters). Enter in spoiler summary moves caret into spoiler body.

TipTap's Markdown input rules (autoformat-as-you-type: `# `…`###### `, `> `, `- `, `1. `, ``` ```` ``` ```, `**x**`, `*x*`, `` `x` ``, `~~x~~`, `==x==`) are kept — user decision 2026-10-12 (supersedes the original "none, for parity"). No live `:shortcode:` conversion.

### Other features (parity)

- **Mode switch** buttons; mode persisted in `localStorage['forum_editor_mode']`.
- **Emoji picker**: same list and UI; inserts the Unicode char at caret (both modes).
- **Upload**: paste, drag-drop, toolbar button → `fetch` POST (`credentials: 'same-origin'`) of `FormData` to `options.uploadUrl` (default `/forum/upload-image/`). CSRF token is read from the form's hidden `csrfmiddlewaretoken` input, falling back to the `csrftoken` cookie, and sent both as the `X-CSRFToken` header and the `csrfmiddlewaretoken` form field (as the current code does). Visual mode shows a placeholder image node with spinner, replaced on success, removed on failure with the existing error message. Only `uploadUrl` is contacted.
- **Resize handle**: mouse + touch, same behaviour.
- **Form**: textarea gets `no-markitup forum-markdown-textarea`, `required` removed, form `novalidate` — as now. `jquery.are-you-sure` keeps working via textarea sync + `change` event dispatch.
- **Wide-layout toggle** from `feature/forum-wide-layout-toggle`: unaffected (outside editor).

## 5. Error Handling

- Parse throws → open in Markdown mode with a small notice; textarea content untouched.
- Serialize throws during sync → textarea keeps last good value; error logged to console.
- Bundle fails to load → plain textarea form still works.
- Upload failure → placeholder removed, error message shown, editor content otherwise unchanged.

## 6. Testing

**Unit (Vitest + jsdom, `npm test` in `forum_editor_src/`):**
- `parser.test.js`: every mapping row, plus nesting (marks in spoiler, code block in quote, lists / code block / quote / nested spoiler in spoiler body, image in spoiler); single newline → `hardBreak`; raw `<script>` / `<iframe>` → literal text.
- Tight vs loose lists (bullet and ordered) round-trip unchanged.
- `serializer.test.js`: each serializer rule.
- `roundtrip.test.js`: all fixtures — canonical (`x.md` round-trips identically) and normalizing (`x.md` → `x.expected.md`, then stable).
- Fixtures include regression cases for review bugs 1, 5, 7, 8, 9 (converter-level) and several real anonymized posts from the local DB covering raw blocks (tables, footnotes, admonitions).

**Parity (manual):** `scripts/parity.py` run with `tools\bin\micromamba.exe run -p tools\env python forum_editor_src/scripts/parity.py` — renders each fixture and its normalized output with `CustomMarkdownParser`, reports HTML differences.

**Manual verification before switch:**
- Screenshot old vs new with one sample post containing every element.
- Checklist: all 17 commands in both modes, every shortcut, upload via paste/drop/button, mode switching, reply/quote buttons, resize, unsaved-changes warning, behaviour for review bugs 2, 3, 4, 6, 10.
- Browsers: desktop Chrome, Firefox; mobile Safari, mobile Chrome.

## 7. Rollout & Rollback

- Current file moves to `home/static/js/forum-editor-legacy.js` (kept one release).
- New bundle builds to `home/static/js/forum-editor.js` (+ `.map`).
- `post_form.html` selects bundle by setting `FORUM_EDITOR_LEGACY` (default `False`), overridable per request with `?editor=legacy`; cache-busting `?v=` bumped.
- Rollback = set `FORUM_EDITOR_LEGACY=True` (env var on Render), no JS rebuild.
- Follow-up cleanup commit: delete legacy file, setting, query override, and stale `forum-editor.min.js` / `.min.js.map`.

## 8. Constraints & Out of Scope

- Browser target ES2018 (evergreen browsers, last ~2 years). No IE.
- Python 3.7 / Django 1.11 constraints apply to the setting + template change and `parity.py`.
- Out of scope: new editor features (tables, task lists, live autoformat), server-side Markdown changes, CSS redesign, `mass_mailer` templates.
