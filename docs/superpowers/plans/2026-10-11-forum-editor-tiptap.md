# Forum Editor Rewrite (TipTap) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the 2,531-line jQuery/`execCommand` forum editor with a modular TipTap editor plus an owned, unit-tested Markdown ↔ ProseMirror converter, with exact feature parity and identical look.

**Architecture:** A standalone package `forum_editor_src/` (esbuild + Vitest, modern Node) builds one IIFE bundle committed to `home/static/js/forum-editor.js`. `src/markdown/` is pure (markdown-it → ProseMirror doc, doc → Markdown) and carries the unit tests; `src/schema/` defines TipTap nodes/marks whose DOM matches today's CSS; `src/editor.js` wires TipTap to the `#id_body` textarea, which stays the submitted field. The old file is kept as `forum-editor-legacy.js` behind a `FORUM_EDITOR_LEGACY` setting for rollback.

**Tech Stack:** TipTap 3.x (`@tiptap/core`, `@tiptap/pm`, `@tiptap/starter-kit`, `@tiptap/extension-{highlight,superscript,subscript,image}`, `@tiptap/extensions` for Placeholder), `markdown-it` 14, `markdown-it-mark`, `markdown-it-sub`, `markdown-it-sup`, `prosemirror-markdown` 1.x, esbuild, Vitest + jsdom. Django 1.11 / Python 3.7 for the template switch and `parity.py`.

**Spec:** `docs/superpowers/specs/2026-10-11-forum-editor-tiptap-design.md`

## Global Constraints

- **Git:** base branch `render`. Work on `feature/forum-editor-tiptap`, branched from `render` once `feature/forum-wide-layout-toggle` is merged (otherwise branch from `feature/forum-wide-layout-toggle`). Commit steps run only once the user has authorized commits for this execution (AGENTS.md). Stage only the listed files; never use `git add .` or `-A`.
- **Python:** 3.7 syntax only. Run Python via `$env:MAMBA_ROOT_PREFIX = "$pwd\tools\mamba_root"; tools\bin\micromamba.exe run -p tools\env python ...`. Never run `python` directly.
- **JS:** source is ES modules. The bundle is IIFE with esbuild `target: 'es2018'`. No jQuery imports inside `src/`; jQuery is only touched to build the `$visualEditor` compatibility wrapper when `window.jQuery` exists. No CDN; all dependencies are bundled.
- **No `document.execCommand`** anywhere in `src/`.
- **Look:** reuse today's toolbar/modal/emoji/footer markup and class names verbatim (`forum-editor.js:816-922` on the legacy file). Changes to `home/static/css/forum-editor.css` are additive only, under a `/* TipTap editor */` section at the end.
- **Storage format:** Markdown for Python-Markdown 2.6.11 + pymdown-extensions 5.0 (`forum/markup_engines.py:64-84`). No server-side changes.
- **markdown-it options:** `{ html: false, breaks: true, linkify: false, typographer: false }`.
- **Serializer:** emphasis always uses `*` / `**`. U+00A0 is preserved. Spoilers are written as `???- "Title"` followed by a 4-space-indented body. Only headings 2 and 3 are editable; every other heading becomes `rawMarkdownBlock`.
- **localStorage key:** `forum_editor_mode`, values `'visual' | 'markdown'`. Default upload URL: `/forum/upload-image/`.
- **Russian UI copy** is copied verbatim from the legacy file. New strings: raw-block chip title `Этот фрагмент редактируется в режиме Markdown`, parse-failure notice `Не удалось открыть визуальный редактор — текст открыт в режиме Markdown.`

## Review Focus

These failure modes are implied by the spec but not covered elsewhere. Each has a test in the owning task.

1. **Typing Markdown syntax literally in visual mode** (`**not bold**`, `# 1`, `2*3*4`, `a_b_c`): it must come back as the same literal text after save and reload. Owned by Task 5.
2. **Pasting from Google Docs/Word** (`<b style="font-weight:normal">` wrapping everything, `<span style>` soup): only real formatting survives, and the whole paste must not turn bold. Owned by Task 2.
3. **Stored posts with `\r\n` line endings** (older posts in the database): they parse exactly like `\n` and the serializer emits `\n`. Owned by Task 4.
4. **Switching mode while an upload is in flight**: the image lands in whichever mode is active when the upload finishes, and no placeholder text is ever left in the textarea. Owned by Task 10.
5. **Large posts (~2,000 paragraphs) with per-keystroke sync**: serialize must stay fast enough to type into (under 100 ms in jsdom). Owned by Task 7.

---

## File Map

```
forum_editor_src/
  package.json, package-lock.json, build.mjs, vitest.config.mjs, .gitignore
  scripts/parity.py
  src/index.js                 auto-init + window.forumEditor
  src/editor.js                createForumEditor(): TipTap + textarea sync + modes + public API
  src/commands.js              runVisualCommand / runMarkdownCommand / isCommandActive
  src/markdownMode.js          pure textarea string transforms
  src/keymap.js                matchShortcut / bindShortcuts
  src/upload.js                getCsrfToken / uploadImage / bindUploadHandlers
  src/emoji.js                 EMOJIS, SHORTCODE_TO_CHAR (ported verbatim)
  src/markdown/md.js           createMarkdownIt()
  src/markdown/plugins/{underline,keys,spoiler,rawBlock,emojiShortcode}.js
  src/markdown/parser.js       parseMarkdown()
  src/markdown/serializer.js   serializeMarkdown()
  src/schema/index.js          extensions, getForumSchema()
  src/schema/{Kbd,CodeBlock,Image,Spoiler,RawMarkdownBlock,Lists,Paste}.js
  src/ui/toolbar.js            buildEditorDom(), updateActiveStates()
  src/ui/linkModal.js, src/ui/emojiPicker.js, src/ui/resizeHandle.js
  test/*.test.js, test/fixtures/*.md
home/static/js/forum-editor.js          (built bundle)
home/static/js/forum-editor.js.map      (built source map)
home/static/js/forum-editor-legacy.js   (renamed legacy editor)
home/static/css/forum-editor.css        (additive TipTap section)
home/templates/pybb/post_form.html      (bundle switch, reply/quote use API)
le_francais/settings/base.py            (FORUM_EDITOR_LEGACY)
le_francais/context_processors.py       (forum_editor_legacy)
forum/tests.py                          (editor switch tests)
```

---

### Task 1: Package scaffold, legacy rename, and editor switch

**Files:**
- Create: `forum_editor_src/package.json`, `build.mjs`, `vitest.config.mjs`, `.gitignore`, `src/index.js` (stub), `test/smoke.test.js`
- Rename: `home/static/js/forum-editor.js` → `home/static/js/forum-editor-legacy.js` (`git mv`)
- Modify: `le_francais/settings/base.py` (add next to the other `os.environ.get` flags), `le_francais/context_processors.py`, the `context_processors` list at `le_francais/settings/base.py:181-194`, `home/templates/pybb/post_form.html:63`
- Test: `forum/tests.py`

**Interfaces:**
- Produces: `settings.FORUM_EDITOR_LEGACY: bool`; context var `forum_editor_legacy: bool`; `npm run build` writes `home/static/js/forum-editor.js` + `.map`; `npm test` runs Vitest.

- [ ] **Step 1: Write the failing Django tests** in `forum/tests.py`, in a new `ForumEditorSwitchTests(TestCase)` that renders the add-post page for a logged-in user (reuse the fixture setup of the existing upload test at `forum/tests.py:65`):

```python
@override_settings(FORUM_EDITOR_LEGACY=False)
def test_new_editor_by_default(self):
    html = self.client.get(self.topic_url).content.decode('utf-8')
    self.assertIn('js/forum-editor.js', html)
    self.assertNotIn('forum-editor-legacy.js', html)

@override_settings(FORUM_EDITOR_LEGACY=True)
def test_legacy_editor_by_setting(self):
    html = self.client.get(self.topic_url).content.decode('utf-8')
    self.assertIn('js/forum-editor-legacy.js', html)

@override_settings(FORUM_EDITOR_LEGACY=False)
def test_legacy_editor_by_query(self):
    html = self.client.get(self.topic_url + '?editor=legacy').content.decode('utf-8')
    self.assertIn('js/forum-editor-legacy.js', html)
```

- [ ] **Step 2: Run them and confirm they fail**
Run: `tools\bin\micromamba.exe run -p tools\env python manage.py test forum.tests.ForumEditorSwitchTests`
Expected: FAIL (`forum-editor-legacy.js` not in page).

- [ ] **Step 3: Implement the switch**
- In `base.py`, add `FORUM_EDITOR_LEGACY = os.environ.get("FORUM_EDITOR_LEGACY", "True") == "True"`. It defaults to `True` during development; Task 12 flips the default to `"False"`.
- Add `forum_editor_legacy(request)` to `context_processors.py`. It returns `{'forum_editor_legacy': settings.FORUM_EDITOR_LEGACY or request.GET.get('editor') == 'legacy'}`. Register it in the list.
- In `post_form.html`, pick `js/forum-editor-legacy.js?v=1.2.4` or `js/forum-editor.js?v=2.0.0` with `{% if forum_editor_legacy %}`.
- `git mv` the legacy file.

- [ ] **Step 4: Run the Django tests and confirm they pass** (same command; expected OK).

- [ ] **Step 5: Scaffold the JS package**
- `package.json`: `"private": true, "type": "module"`, `"engines": {"node": ">=20"}`, scripts `build` (`node build.mjs`), `test` (`vitest run`), `test:watch`.
- Install the Tech Stack packages as dependencies and `esbuild`, `vitest`, `jsdom` as devDependencies. Record the resolved versions; `package-lock.json` is committed.
- `build.mjs`: esbuild `entryPoints: ['src/index.js']`, `bundle: true`, `format: 'iife'`, `target: 'es2018'`, `minify: true`, `sourcemap: true`, `outfile: '../home/static/js/forum-editor.js'`, `legalComments: 'none'`. Log the output size.
- `vitest.config.mjs`: `environment: 'jsdom'`.
- `.gitignore`: `node_modules/`.
- `test/smoke.test.js`: `expect(1).toBe(1)`.
- `src/index.js`: empty IIFE body.

- [ ] **Step 6: Verify the build and tests**
Run in `forum_editor_src`: `npm test` (expected: 1 passed), then `npm run build` (expected: `home/static/js/forum-editor.js` and `.map` exist).

- [ ] **Step 7: Commit**
```bash
git add forum_editor_src/package.json forum_editor_src/package-lock.json forum_editor_src/build.mjs forum_editor_src/vitest.config.mjs forum_editor_src/.gitignore forum_editor_src/src/index.js forum_editor_src/test/smoke.test.js home/static/js/forum-editor-legacy.js home/static/js/forum-editor.js home/static/js/forum-editor.js.map le_francais/settings/base.py le_francais/context_processors.py home/templates/pybb/post_form.html forum/tests.py
git commit -m "chore(forum-editor): scaffold TipTap editor package and legacy switch"
```

---

### Task 2: Schema — TipTap extensions with today's DOM

**Files:**
- Create: `src/schema/index.js`, `src/schema/{Kbd,CodeBlock,Image,Spoiler,RawMarkdownBlock,Lists,Paste}.js`, `src/emoji.js`
- Test: `test/schema.test.js`

**Interfaces:**
- Produces:
  - `extensions: Extension[]`, the full configured list used by the editor.
  - `getForumSchema(): Schema`, cached `getSchema(extensions)` from `@tiptap/core`.
  - Node names: `doc, paragraph, text, hardBreak, heading{level:2|3}, blockquote, bulletList{tight}, orderedList{tight,start}, listItem, codeBlock{language}, image{src,alt,title,uploadId}, spoiler, spoilerSummary, spoilerBody, rawMarkdownBlock{source}`.
  - Mark names: `bold, italic, underline, strike, highlight, kbd, superscript, subscript, code, link{href}`.
  - `src/emoji.js` exports `EMOJIS` and `SHORTCODE_TO_CHAR`, ported verbatim from `forum-editor-legacy.js:10-167`.

Configuration decisions:
- StarterKit with `heading: {levels: [2,3]}`, `horizontalRule: false`, `bulletList: false`, `orderedList: false`, `codeBlock: false`, and `link: {openOnClick: false, HTMLAttributes: {target: '_blank', rel: 'noopener'}}`.
- `Lists.js` extends `BulletList` / `OrderedList` with `tight: {default: true}`.
- `Image` is a block node with `HTMLAttributes: {class: 'forum-embedded-img'}`.
- `spoiler` has content `spoilerSummary spoilerBody`. `spoilerSummary` has content `inline*` and renders `summary`. `spoilerBody` has content `block+` and renders `div.spoiler-body`.
- `rawMarkdownBlock` is an atom that is not selectable as text.
- `Paste.js` holds the paste rules.

- [ ] **Step 1: Write the failing tests.** The helper `toHTML(json)` builds a node with `getForumSchema().nodeFromJSON(json)` and returns the `DOMSerializer.fromSchema(schema).serializeFragment(node.content)` output as `innerHTML`.

```js
test('marks render with legacy tags/classes', () => {
  expect(toHTML(para(text('k', ['kbd'])))).toBe('<p><kbd class="editor-key">k</kbd></p>');
  for (const [m, tag] of [['underline','u'],['strike','s'],['highlight','mark'],['superscript','sup'],['subscript','sub'],['bold','strong'],['italic','em'],['code','code']])
    expect(toHTML(para(text('x', [m])))).toBe(`<p><${tag}>x</${tag}></p>`);
});
test('link', () => expect(toHTML(para(text('t', [{type:'link',attrs:{href:'https://a.b'}}]))))
  .toBe('<p><a href="https://a.b" target="_blank" rel="noopener">t</a></p>'));
test('code block', () => expect(toHTML({type:'codeBlock',attrs:{language:'py'},content:[{type:'text',text:'x'}]}))
  .toBe('<pre class="editor-code-block"><code class="language-py">x</code></pre>'));
test('image', () => expect(toHTML({type:'image',attrs:{src:'/m/a.png',alt:'a',title:'t'}}))
  .toBe('<img src="/m/a.png" alt="a" title="t" class="forum-embedded-img">'));
test('spoiler', () => expect(toHTML(spoiler('T', [para(text('b'))])))
  .toBe('<details class="forum-spoiler" open=""><summary>T</summary><div class="spoiler-body"><p>b</p></div></details>'));
test('spoiler body accepts nested blocks', () => {
  const n = getForumSchema().nodeFromJSON(spoiler('T', [bulletList(['a']), codeBlock('x'), spoiler('In', [para(text('y'))])]));
  expect(() => n.check()).not.toThrow();
});
test('raw block chip', () => expect(toHTML({type:'rawMarkdownBlock',attrs:{source:'| a |\n|---|'}}))
  .toBe('<div class="forum-raw-md" contenteditable="false" title="Этот фрагмент редактируется в режиме Markdown"><pre>| a |\n|---|</pre></div>'));
test('Google Docs bold wrapper is not bold', () => {
  const doc = parseClipboardHTML('<b style="font-weight:normal" id="docs-internal-guid-1"><p><span>plain</span> <span style="font-weight:700">bold</span></p></b>');
  expect(JSON.stringify(doc)).toContain('"text":"plain"');
  expect(doc.firstChild.firstChild.marks).toHaveLength(0);
  expect(doc.firstChild.lastChild.marks.map(m => m.type.name)).toEqual(['bold']);
});
```

`parseClipboardHTML(html)` is a test helper that runs `DOMParser.fromSchema(getForumSchema()).parse()` over a jsdom fragment. The paste rules go on the Bold extension's `parseHTML` and must also be exported for this test: `<b>`/`<strong>` with `font-weight: normal|400` gives no bold, and `span[style*=font-weight:700|bold]` gives bold.

- [ ] **Step 2: Run** `npx vitest run test/schema.test.js`. Expected: FAIL (module not found).
- [ ] **Step 3: Implement the schema files** to the interfaces above.
- [ ] **Step 4: Run** `npx vitest run test/schema.test.js`. Expected: all pass.
- [ ] **Step 5: Commit** `forum_editor_src/src/schema/*`, `src/emoji.js`, `test/schema.test.js` with message `feat(forum-editor): TipTap schema matching legacy DOM`.

---

### Task 3: markdown-it with pymdown inline syntax

**Files:**
- Create: `src/markdown/md.js`, `src/markdown/plugins/{underline,keys,emojiShortcode}.js`
- Test: `test/md-inline.test.js`

**Interfaces:**
- Consumes: `SHORTCODE_TO_CHAR` (Task 2).
- Produces: `createMarkdownIt(): MarkdownIt`, configured with the Global Constraints options and plugins: `markdown-it-mark` (`==`), `markdown-it-sub` (`~`), `markdown-it-sup` (`^`), the built-in strikethrough (`~~`), `underline` (`^^x^^` → tokens `underline_open/close`), `keys` (`++x++` → a single `kbd` token with `content` = the inner text verbatim), and `emojiShortcode` (known `:code:` outside code → text token with the character).
- Rule order: `^^` before `^`, and `~~` before `~`.

- [ ] **Step 1: Write the failing tests.** They assert `createMarkdownIt().renderInline(src)`:

```js
const r = s => createMarkdownIt().renderInline(s);
test.each([
  ['^^u^^', '<u>u</u>'], ['~~s~~', '<s>s</s>'], ['==m==', '<mark>m</mark>'],
  ['^sup^', '<sup>sup</sup>'], ['~sub~', '<sub>sub</sub>'], ['++ctrl+c++', '<kbd>ctrl+c</kbd>'],
  ['a ^^b^^ ^c^', 'a <u>b</u> <sup>c</sup>'], ['__b__', '<strong>b</strong>'], ['_i_', '<em>i</em>'],
  [':smile: :nope:', '😄 :nope:'], ['`:smile:`', '<code>:smile:</code>'],
  ['<script>x</script>', '&lt;script&gt;x&lt;/script&gt;'],
])('%s', (src, html) => expect(r(src)).toBe(html));
test('single newline is a hard break', () =>
  expect(createMarkdownIt().render('a\nb')).toBe('<p>a<br>\nb</p>\n'));
```

The `<s>` and `<kbd>` render rules can be set in this file. Only the token names matter to later tasks.

- [ ] **Step 2: Run** `npx vitest run test/md-inline.test.js`. Expected: FAIL.
- [ ] **Step 3: Implement** `md.js` and the three plugins.
- [ ] **Step 4: Run.** Expected: pass.
- [ ] **Step 5: Commit** with message `feat(forum-editor): markdown-it with pymdown inline syntax`.

---

### Task 4: Block plugins (spoiler, raw blocks) and `parseMarkdown`

**Files:**
- Create: `src/markdown/plugins/{spoiler,rawBlock}.js`, `src/markdown/parser.js`
- Modify: `src/markdown/md.js` (register block plugins)
- Test: `test/parser.test.js`

**Interfaces:**
- Consumes: `createMarkdownIt()` (Task 3), `getForumSchema()` (Task 2).
- Produces: `parseMarkdown(md: string): Node`, a ProseMirror doc. It throws `Error` on internal failure. It normalizes `\r\n` and `\r` to `\n` first. Empty input gives a doc with one empty paragraph.

Block rules:
- **`spoiler`** matches `???- ` / `??? ` / `???+ ` followed by an optional quoted or unquoted title. The body is the following lines indented by 4 or more spaces or a tab, plus blank lines between them. The body is de-indented and tokenized with `state.md.block.parse` into nested tokens. It emits `spoiler_open`, `spoiler_summary` (with inline children from the title), the body tokens, and `spoiler_close`.
- **`rawBlock`** captures the whole source slice, verbatim, of:
  - tables (a line containing `|` followed by a `|---|`-style delimiter line);
  - footnote definitions `[^x]:`;
  - admonitions `!!! `, plus their indented body;
  - definition lists (a line followed by `: `);
  - abbreviations `*[X]:`;
  - lines that are only an `attr_list` `{: ...}`;
  - task-list items `- [ ]` / `- [x]`, capturing the whole list;
  - headings with level 1 or 4–6 and setext headings.
- **Unsupported inline syntax:** an inline footnote reference `[^1]` stays as literal text.

Token → node mapping uses `prosemirror-markdown`'s `MarkdownParser(schema, md, tokens)` with this spec:
- `softbreak` → `hardBreak`; `hardbreak` → `hardBreak`.
- `bullet_list`/`ordered_list` set `tight` from the token's `hidden` flag on its paragraphs (the same logic as prosemirror-markdown's `listIsTight`).
- `fence`/`code_block` → `codeBlock{language: info||null}`.
- `image` is lifted to block level: an image alone in a paragraph becomes an image node. An image inline with text is split into paragraph / image / paragraph.
- `kbd` → `kbd` mark; `underline_open` → `underline`; `mark_open` → `highlight`; `sub`/`sup` → `subscript`/`superscript`; `s_open` → `strike`.

- [ ] **Step 1: Write the failing tests.** `p(md)` = `parseMarkdown(md).toJSON()`; `html(md)` serializes to DOM as in Task 2.

```js
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
```

- [ ] **Step 2: Run** `npx vitest run test/parser.test.js`. Expected: FAIL.
- [ ] **Step 3: Implement** both plugins and `parser.js`.
- [ ] **Step 4: Run.** Expected: pass.
- [ ] **Step 5: Commit** with message `feat(forum-editor): markdown parser with spoilers and raw block preservation`.

---

### Task 5: `serializeMarkdown`

**Files:**
- Create: `src/markdown/serializer.js`
- Test: `test/serializer.test.js`

**Interfaces:**
- Consumes: `getForumSchema()`, `parseMarkdown()`.
- Produces: `serializeMarkdown(doc: Node): string`. The output has no trailing newline. Images with a non-null `uploadId` are skipped.

Implemented with `prosemirror-markdown`'s `MarkdownSerializer`:
- Marks: `bold` `**`, `italic` `*`, `underline` `^^`, `strike` `~~`, `highlight` `==`, `kbd` `++`, `superscript` `^`, `subscript` `~`, `code` (a backtick run longer than any inside, with space padding when the content starts or ends with a backtick), `link` `[..](href)`.
- Nodes: `hardBreak` `\n`, with no trailing spaces and no backslash. `spoiler` is written as `???- "Title"` followed by the body rendered recursively and indented 4 spaces. `rawMarkdownBlock` is written as `source` verbatim. `codeBlock` uses a fence longer than any backtick run inside. Lists use `-` and `1.` and are tight or loose per `tight`.
- Escaping: override `esc()` so characters are escaped only where they would parse as syntax. Each candidate escape is checked by re-parsing: if `parseMarkdown` of the unescaped text produces any mark or block that differs from the plain-text node, escape it. Otherwise leave the text as-is.

- [ ] **Step 1: Write the failing tests.** `rt(md)` = `serializeMarkdown(parseMarkdown(md))`; `ser(json)` serializes a doc built from JSON.

```js
test('emphasis always uses asterisks (review bug 7)', () => {
  expect(ser(doc(para(text('mot'), text('ifs', ['italic']))))).toBe('mot*ifs*');
  expect(rt('_i_ __b__')).toBe('*i* **b**');
});
test('nbsp preserved (review bug 8)', () => expect(rt('Bonjour !')).toBe('Bonjour !'));
test('literal syntax typed in visual mode stays literal (Review Focus 1)', () => {
  for (const s of ['**not bold**', '# 1', '2*3*4', 'a_b_c', 'my_var_name', '- not a list', '1. not a list', '> not quote', '==x==', '++x++', ':smile:']) {
    const md = ser(doc(para(text(s))));
    const reparsed = parseMarkdown(md);
    expect(reparsed.textContent).toBe(s);
    expect(reparsed.firstChild.type.name).toBe('paragraph');
    expect(reparsed.firstChild.firstChild.marks).toHaveLength(0);
    expect(serializeMarkdown(reparsed)).toBe(md);
  }
});
test('no gratuitous escapes', () => {
  expect(ser(doc(para(text('my_var_name 2*3 a ~ b'))))).toBe('my_var_name 2*3 a ~ b');
});
test('code is literal', () => {
  expect(ser(doc(para(text('a `b` c', ['code']))))).toBe('`` a `b` c ``');
  expect(ser(doc(codeBlock('x\n```\ny')))).toBe('````\nx\n```\ny\n````');
});
test('hard break is a bare newline', () => expect(rt('a\nb')).toBe('a\nb'));
test('spoiler format', () => expect(rt('???- "T"\n    - a\n    - b')).toBe('???- "T"\n    - a\n    - b'));
test('raw block verbatim', () => expect(rt('x\n\n| a |\n|---|\n\ny')).toBe('x\n\n| a |\n|---|\n\ny'));
test('upload placeholders are not serialized', () =>
  expect(ser(doc(para(text('a')), {type:'image', attrs:{src:'', uploadId:'u1'}}))).toBe('a'));
test('idempotent', () => { const n1 = rt('*a* _b_\n\n* x\n* y'); expect(rt(n1)).toBe(n1); });
```

- [ ] **Step 2: Run** `npx vitest run test/serializer.test.js`. Expected: FAIL.
- [ ] **Step 3: Implement** `serializer.js`.
- [ ] **Step 4: Run.** Expected: pass.
- [ ] **Step 5: Commit** with message `feat(forum-editor): Python-Markdown-safe serializer`.

---

### Task 6: Round-trip fixtures and server parity check

**Files:**
- Create: `test/roundtrip.test.js`, `test/fixtures/*.md`, `test/fixtures/*.expected.md`, `scripts/parity.py`

**Interfaces:**
- Consumes: `parseMarkdown`, `serializeMarkdown`.
- Produces: fixture convention. `name.md` without a sibling `name.expected.md` is canonical. With one, `name.md` is normalizing.

- [ ] **Step 1: Write the fixtures.**
  - **Canonical:** `all-elements.md` (every mapping row); `nested-spoilers.md`; `lists-tight-loose.md`; `french-typography.md` (nbsp before `! ? : ;`, `« »`); `code-with-backticks.md`; `raw-blocks.md` (table, footnote, admonition, task list next to normal paragraphs).
  - **Normalizing:** `underscore-emphasis.md` → `*`; `star-bullets.md` → `-`; `crlf.md` (CRLF bytes) → LF; `review-regressions.md`, which covers two code blocks with text between them, "`a` and `b`", in-word italics written with `_`, and `snake_case` text.
  - **Real posts:** export 5 real posts from the local DB (`SELECT body FROM pybb_post ORDER BY random() LIMIT ...` filtered for tables, spoilers, code, images, quotes). Anonymize names and URLs, then save them as `real-1.md` … `real-5.md`. Add `.expected.md` files only where normalization is legitimate.
- [ ] **Step 2: Write `roundtrip.test.js`.** It globs fixtures. For canonical files, `expect(rt(src)).toBe(src)`. For normalizing files, `expect(rt(src)).toBe(expected)` and `expect(rt(expected)).toBe(expected)`. Files are read as UTF-8 and the trailing newline is trimmed.
- [ ] **Step 3: Run** `npm test`. Expected: pass. For any failure, fix the parser or serializer (Tasks 4–5); never fix the fixture, unless the fixture's expectation contradicts the spec.
- [ ] **Step 4: Write `scripts/parity.py`.** It is Python 3.7. It sets `DJANGO_SETTINGS_MODULE=le_francais.settings.dev` and calls `django.setup()`. For each normalizing fixture it renders `x.md` and `x.expected.md` with `forum.markup_engines.CustomMarkdownParser().format(...)`. It compares the HTML with all whitespace runs collapsed, prints `OK name` or a unified diff, and exits 1 on any difference.
- [ ] **Step 5: Run parity**
Run: `tools\bin\micromamba.exe run -p tools\env python forum_editor_src/scripts/parity.py`
Expected: every line `OK`, exit 0. If a normalization changes the rendered HTML, fix the serializer.
- [ ] **Step 6: Commit** the fixtures, the test and `parity.py` with message `test(forum-editor): round-trip fixtures and server parity check`.

---

### Task 7: Editor core — mount, modes, textarea sync, public API

**Files:**
- Create: `src/editor.js`, `src/ui/toolbar.js` (DOM build only)
- Modify: `src/index.js`
- Test: `test/editor.test.js`

**Interfaces:**
- Consumes: `extensions`, `parseMarkdown`, `serializeMarkdown`.
- Produces:
  - `buildEditorDom(textarea): Dom`. It inserts the legacy wrapper markup (legacy `forum-editor.js:820-922`, verbatim, minus the old contenteditable div) before the textarea and moves the textarea into `.forum-editor-container`. It returns `{wrapper, toolbar, container, visualHost, dropOverlay, uploadProgress, fileInput, charCounter, modal:{overlay,title,body,submit,cancel,close}, emoji:{button,dropdown,grid,close}, resizer}`.
  - `createForumEditor({textarea, uploadUrl='/forum/upload-image/', initialMode}) : Api`. `initialMode` defaults to `localStorage.forum_editor_mode` or else `'visual'`.
  - `Api = { currentMode, tiptap, dom, element, $visualEditor, setMode(mode), getMarkdown(), setMarkdown(md), syncMarkdownFromVisual(), syncVisualFromMarkdown(), insertQuote(md), insertMarkdown(md), restoreSelection(), focus(), executeCommand(cmd), destroy() }`.
    - `element` is the ProseMirror contenteditable, with classes `forum-visual-editor` and `spellcheck="true"`.
    - `$visualEditor` is `window.jQuery(element)` when jQuery exists, otherwise undefined.
    - `executeCommand` is a stub here; Task 8 fills it in.

Behaviour:
- **Textarea setup:** classes `no-markitup forum-markdown-textarea`, `required` removed, form `novalidate`.
- **Sync:** on every TipTap `update`, set `textarea.value = serializeMarkdown(doc)` and dispatch `input` and `change` (bubbling). The form has a capture-phase `submit` listener that calls `syncMarkdownFromVisual()` when in visual mode. If serialize throws, keep the old value and `console.error`.
- **`setMode`:** copies the height between textarea and editor (as legacy `setMode`), converts, toggles `display`, focuses, persists to localStorage, updates the mode-switch classes and checkbox, and updates the char counter (`N симв.` or empty).
- **Opening:** if `parseMarkdown` throws when opening or switching to visual, stay in markdown mode and show the parse-failure notice as `<div class="alert alert-warning py-1 px-2 mb-1 small">` above the container. The textarea is untouched.
- **Quotes:** `insertQuote(md)` inserts the parsed quote at the saved selection, or else at the end, followed by an empty paragraph, with the caret in that paragraph. In markdown mode it inserts at `textarea.selectionStart` with blank-line padding, as legacy does. `insertMarkdown(md)` delegates to `insertQuote` when `md` starts with `>`; otherwise it inserts the parsed content.
- **Selection:** `restoreSelection()` focuses the editor and keeps the current ProseMirror selection; ProseMirror keeps the selection across blur.
- **Placeholders:** the Placeholder extension, with text from the legacy `placeholder` attribute. Spoiler `data-empty` attributes come from node decorations in `Spoiler.js` (Task 2 file, extended here).
- **Start-up:** `src/index.js` runs on `DOMContentLoaded`. If `#id_body` exists, it calls `createForumEditor({textarea, uploadUrl: '/forum/upload-image/'})` and assigns `window.forumEditor`. It does nothing if `window.forumEditor` already exists.

- [ ] **Step 1: Write the failing tests** (jsdom, a fresh `<form><textarea id="id_body"></textarea></form>` per test, `localStorage.clear()`):

```js
test('initial markdown loads and syncs back unchanged', () => {
  ta.value = '**a** ^^b^^'; const ed = createForumEditor({ textarea: ta });
  expect(ed.element.innerHTML).toContain('<strong>a</strong>');
  ed.tiptap.commands.insertContentAt(ed.tiptap.state.doc.content.size - 1, '!');
  expect(ta.value).toBe('**a** ^^b^^!');
});
test('every update syncs synchronously and fires change', () => {
  const ed = createForumEditor({ textarea: ta }); const spy = vi.fn(); ta.addEventListener('change', spy);
  ed.tiptap.commands.insertContent('x'); expect(ta.value).toBe('x'); expect(spy).toHaveBeenCalled();
});
test('submit listener flushes', () => { /* stub serialize via ed.tiptap.state change without update event; dispatch submit; expect textarea updated */ });
test('mode switch round-trips and persists', () => {
  ta.value = 'a'; const ed = createForumEditor({ textarea: ta, initialMode: 'visual' });
  ed.setMode('markdown'); ta.value = '## T'; ed.setMode('visual');
  expect(ed.element.innerHTML).toBe('<h2>T</h2>'); expect(localStorage.getItem('forum_editor_mode')).toBe('visual');
});
test('parse failure falls back to markdown mode', () => {
  vi.spyOn(parser, 'parseMarkdown').mockImplementation(() => { throw new Error('boom'); });
  ta.value = 'x'; const ed = createForumEditor({ textarea: ta, initialMode: 'visual' });
  expect(ed.currentMode).toBe('markdown'); expect(ta.value).toBe('x');
  expect(document.body.textContent).toContain('Не удалось открыть визуальный редактор');
});
test('insertQuote in both modes', () => { /* visual: doc contains blockquote then empty paragraph; markdown: textarea contains "\n\n> q\n\n" at caret */ });
test('char counter', () => { ta.value = 'abc'; createForumEditor({ textarea: ta }); expect(qs('.forum-char-counter').textContent).toBe('3 симв.'); });
test('large post serializes fast (Review Focus 5)', () => {
  ta.value = Array.from({length: 2000}, (_, i) => `Paragraphe **${i}** avec du texte.`).join('\n\n');
  const ed = createForumEditor({ textarea: ta }); const t = performance.now();
  ed.syncMarkdownFromVisual(); expect(performance.now() - t).toBeLessThan(100);
});
```

Write the two commented tests with concrete assertions as described in their comments. For the submit test, set the doc through `ed.tiptap.view.updateState` so no `update` event fires.

- [ ] **Step 2: Run** `npx vitest run test/editor.test.js`. Expected: FAIL.
- [ ] **Step 3: Implement** `editor.js`, `toolbar.js` (`buildEditorDom` only), and `index.js`.
- [ ] **Step 4: Run** `npm test`. Expected: all pass.
- [ ] **Step 5: Commit** with message `feat(forum-editor): TipTap editor core with textarea sync and modes`.

---

### Task 8: Commands (both modes) and toolbar active states

**Files:**
- Create: `src/commands.js`, `src/markdownMode.js`
- Modify: `src/ui/toolbar.js` (add `updateActiveStates`), `src/editor.js` (wire toolbar clicks, `executeCommand`; `mousedown` `preventDefault` on `.forum-editor-btn, .forum-emoji-item, .forum-emoji-close`, as legacy `bindEvents` does)
- Test: `test/commands.test.js`, `test/markdownMode.test.js`

**Interfaces:**
- Consumes: `Api` (Task 7), `parseMarkdown`/`serializeMarkdown`.
- Produces:
  - `COMMANDS = ['bold','italic','underline','strikethrough','mark','code','kbd','superscript','subscript','removeFormat','h2','h3','quote','ul','ol','spoiler','link','image']`
  - `runVisualCommand(editor: Editor, cmd: string, ctx): void`, where `ctx = {openLinkModal, openFilePicker}`. Task 9 supplies `openLinkModal` and Task 10 supplies `openFilePicker`; until then they are no-ops.
  - `runMarkdownCommand(textarea, cmd, ctx): void`
  - `isCommandActive(editor, cmd): boolean`
  - `updateActiveStates(toolbarEl, editor)`, which toggles the `active` class on `[data-cmd]` buttons.
  - Pure `markdownMode.js` functions, each returning `{text, selStart, selEnd}`:
    - `wrapSelection(text, start, end, prefix, suffix, placeholder)`: unwraps if the selection is already wrapped.
    - `prefixLines(text, start, end, prefix | (i)=>prefix)`: toggles off if every line already has the prefix.
    - `replaceSelection(text, start, end, insert)`
    - `removeFormatting(text, start, end)`: parses the selection, strips marks, serializes, and replaces.
    - `toggleCode(text, start, end)`: inline backticks for one line, a fenced block for several.
    - `insertSpoilerTemplate(text, start, end)`: produces `???- "Заголовок"\n    ` plus the selection, indented.

Visual semantics: see the spec §4 command table. Specific algorithms:
- **`code`:** if `$from.sameParent($to)`, toggle the `code` mark. Otherwise, collect the text of every textblock between `$from` and `$to`, cut at the selection edges. Text before the selection in the first block stays as a paragraph; text after it in the last block stays as a paragraph. The selected part becomes one `codeBlock`, with lines joined by `\n`. Replace the range in one transaction.
- **`removeFormat`:** `unsetAllMarks().clearNodes()`.
- **`spoiler`:** insert `spoiler{summary empty, body [empty paragraph]}` and an empty paragraph after it, then set the selection inside the summary.
- **Marks with a collapsed caret:** `toggleMark` toggles stored marks; the caret never moves.

- [ ] **Step 1: Write the failing tests.** Create the editor with `createForumEditor`. Put shared helpers in `test/helpers.js`: `makeEditor(md, mode='visual') -> Api`, and `selectText(ed, fromWord, toWord)`, which sets a TextSelection from the start of the first occurrence of `fromWord` to the end of the first occurrence of `toWord` in document order. Tasks 9–10 reuse them.

```js
test('multi-block code keeps unselected text (review bug 3)', () => {
  ed.setMarkdown('alpha beta\n\ngamma delta'); selectText(ed, 'beta', 'gamma');
  runVisualCommand(ed.tiptap, 'code', ctx);
  expect(ed.getMarkdown()).toBe('alpha\n\n```\nbeta\ngamma\n```\n\ndelta');
});
test('code across two list items converts only those items', () => {
  ed.setMarkdown('- a\n- b\n- c\n- d'); selectText(ed, 'b', 'c'); runVisualCommand(ed.tiptap, 'code', ctx);
  expect(ed.getMarkdown()).toContain('- a'); expect(ed.getMarkdown()).toContain('- d');
});
test('ctrl+b inside bold toggles stored mark, caret stays (review bug 10)', () => {
  ed.setMarkdown('**abcdef**'); ed.tiptap.commands.setTextSelection(4);
  runVisualCommand(ed.tiptap, 'bold', ctx); ed.tiptap.commands.insertContent('X');
  expect(ed.getMarkdown()).toBe('**abc**X**def**');
});
test('empty spoiler survives an input event (review bug 2)', () => {
  ed.setMarkdown(''); runVisualCommand(ed.tiptap, 'spoiler', ctx);
  ed.element.dispatchEvent(new Event('input', { bubbles: true }));
  expect(ed.tiptap.state.doc.firstChild.type.name).toBe('spoiler');
  expect(ed.tiptap.state.selection.$from.parent.type.name).toBe('spoilerSummary');
});
test.each(COMMANDS.filter(c => !['link','image','removeFormat','spoiler'].includes(c)))('%s toggles and is active', cmd => {
  ed.setMarkdown('word'); selectText(ed, 'word', 'word'); runVisualCommand(ed.tiptap, cmd, ctx);
  expect(isCommandActive(ed.tiptap, cmd)).toBe(true);
});
```

`markdownMode.test.js`:

```js
test('link replaces selection (review bug 5)', () =>
  expect(replaceSelection('voir ici', 5, 8, '[ici](https://x.y)').text).toBe('voir [ici](https://x.y)'));
test('removeFormatting keeps list markers and snake_case (review bug 9)', () => {
  expect(removeFormatting('* item1\n* item2', 0, 15).text).toBe('- item1\n- item2');
  expect(removeFormatting('my_var_name **b**', 0, 17).text).toBe('my_var_name b');
});
test('wrap and unwrap', () => {
  expect(wrapSelection('a b', 2, 3, '**', '**', 'текст').text).toBe('a **b**');
  expect(wrapSelection('a **b**', 4, 5, '**', '**', 'текст').text).toBe('a b');
});
test('toggleCode single vs multi line', () => {
  expect(toggleCode('x', 0, 1).text).toBe('`x`');
  expect(toggleCode('x\ny', 0, 3).text).toBe('```\nx\ny\n```');
});
test('prefixLines toggles quote', () => expect(prefixLines('a\nb', 0, 3, '> ').text).toBe('> a\n> b'));
```

`removeFormatting` normalizes the `*` bullets to `-` because it goes through the serializer. That is expected and covered by `star-bullets.md`.

- [ ] **Step 2: Run** both test files. Expected: FAIL.
- [ ] **Step 3: Implement** `commands.js`, `markdownMode.js`, active states, and the toolbar wiring.
- [ ] **Step 4: Run** `npm test`. Expected: all pass.
- [ ] **Step 5: Commit** with message `feat(forum-editor): toolbar commands for visual and markdown modes`.

---

### Task 9: Keyboard shortcuts, link modal, emoji picker

**Files:**
- Create: `src/keymap.js`, `src/ui/linkModal.js`, `src/ui/emojiPicker.js`
- Modify: `src/editor.js` (bind the keymap on `element` and the textarea; supply `ctx.openLinkModal`; init the emoji picker), `src/schema/index.js` (add `ForumKeys` to `extensions`)
- Test: `test/keymap.test.js`, `test/linkModal.test.js`, `test/emojiPicker.test.js`

**Interfaces:**
- Produces:
  - `matchShortcut(e: KeyboardEvent): string | null`
  - `bindShortcuts(el, onCommand)`
  - `openLinkModal(modalDom, {text, url}): Promise<{text, url} | null>`. It resolves `null` on cancel, Esc, close or overlay click. It reuses the legacy modal markup and the legacy body form (port the body HTML from legacy `openLinkModal`, `forum-editor-legacy.js:1704-1770`).
  - `initEmojiPicker(emojiDom, onPick(char))`: toggles the dropdown, closes on outside click and Esc, and picks on `.forum-emoji-item` click.

Shortcut table, matched by `e.code` first, then `e.key` (including the Cyrillic key):

| Keys | Cmd |
|---|---|
| Mod+B (`и`) / Mod+I (`ш`) / Mod+U (`г`) | bold / italic / underline |
| Mod+K (`л`) | link |
| Mod+Shift+X (`ч`), Alt+Shift+5 | strikethrough |
| Mod+Shift+M (`ь`) | code |
| Mod+Shift+P (`з`) | spoiler |
| Mod+Shift+. (`ю`, `>`) | quote |
| Mod+Shift+N (`т`), Mod+\ | removeFormat |
| Mod+6, `^` with or without modifiers | `null` (never intercepted) |

Before implementing, diff this table against legacy `handleKeydown` (`forum-editor-legacy.js:1274-1360`). Any shortcut found there and missing here is added, together with a test row. Ctrl+A in visual mode is left to ProseMirror (the legacy override existed only to work around contenteditable).

Two editor-level keybindings go in a TipTap `Extension.addKeyboardShortcuts` in `keymap.js` (exported as `ForumKeys` and added to `extensions`):
- **`Enter` in `spoilerSummary`** moves the caret to the start of the first block of `spoilerBody` and returns `true`.
- **`ArrowRight` with an empty selection at the end of a textblock** where `$cursor.marks()` is non-empty clears the stored marks (`tr.setStoredMarks([])`) and returns `true`. Anywhere else it returns `false`, leaving the default behaviour.

- [ ] **Step 1: Write the failing tests.** `keymap.test.js` uses `test.each` over every table row. Each row is built as `new KeyboardEvent('keydown', {code, key, ctrlKey, shiftKey, altKey})` in both Latin and Cyrillic `key` variants, and `matchShortcut` must return the command. Rows for `Mod+6` and `^` expect `null`. Also test that `metaKey` works like `ctrlKey`.

`linkModal.test.js` checks three things: submit resolves `{text:'ici', url:'https://x.y'}`; Esc resolves `null`; the modal gets `d-none` again after closing. In visual mode, an integration test in `editor.test.js` style checks that selecting `ici`, then running `link` with a stubbed modal that returns the URL, gives the Markdown `voir [ici](https://x.y)`.

`emojiPicker.test.js` checks two things: clicking `[data-emoji="😀"]` calls `onPick('😀')`; clicking outside closes the dropdown.

The editor keybinding tests go in `keymap.test.js` and use `makeEditor`:

```js
test('Enter in spoiler summary jumps into body', () => {
  const ed = makeEditor('???- "T"\n    body'); ed.tiptap.commands.setTextSelection(3); // inside summary text
  ed.tiptap.view.someProp('handleKeyDown', f => f(ed.tiptap.view, new KeyboardEvent('keydown', { key: 'Enter' })));
  expect(ed.tiptap.state.selection.$from.parent.textContent).toBe('body');
  expect(ed.getMarkdown()).toBe('???- "T"\n    body');
});
test('ArrowRight at end of bold exits the mark without inserting characters', () => {
  const ed = makeEditor('**ab**'); ed.tiptap.commands.setTextSelection(3);
  ed.tiptap.view.someProp('handleKeyDown', f => f(ed.tiptap.view, new KeyboardEvent('keydown', { key: 'ArrowRight' })));
  ed.tiptap.commands.insertContent('c');
  expect(ed.getMarkdown()).toBe('**ab**c');
});
```

- [ ] **Step 2: Run** the tests. Expected: FAIL.
- [ ] **Step 3: Implement** the three modules and wire them in.
- [ ] **Step 4: Run** `npm test`. Expected: all pass.
- [ ] **Step 5: Commit** with message `feat(forum-editor): shortcuts, link modal, emoji picker`.

---

### Task 10: Image upload (paste, drop, button)

**Files:**
- Create: `src/upload.js`
- Modify: `src/editor.js` (supply `ctx.openFilePicker`, call `bindUploadHandlers`)
- Test: `test/upload.test.js`

**Interfaces:**
- Produces:
  - `getCsrfToken(doc = document): string`: reads `input[name=csrfmiddlewaretoken]` first, then the `csrftoken` cookie, else `''`.
  - `uploadImage(file, uploadUrl): Promise<{url, filename}>`: sends `fetch(uploadUrl, {method:'POST', credentials:'same-origin', headers:{'X-CSRFToken': token}, body: FormData{file, csrfmiddlewaretoken}})`. It resolves when `json.success && json.url`; otherwise it rejects with `Error(json.error || 'Ошибка загрузки изображения')`. Network errors reject too.
  - `bindUploadHandlers(api, dom)`: handles paste of image files, drag-and-drop (showing and hiding `dropOverlay`), the hidden file input, and `uploadProgress` visibility. Accepted types are `image/jpeg, image/png, image/gif, image/webp`.

Placeholder lifecycle:
- **Visual mode:** insert `image{src: URL.createObjectURL(file), uploadId}`. The serializer skips it, so it never reaches the textarea. On success, find the node by `uploadId` and set `src` and `alt`, and `uploadId: null`. On failure, delete the node and show the error the way legacy `handleUploadError` does (`forum-editor-legacy.js:2454`).
- **Markdown mode:** insert nothing until the upload finishes, then insert `![filename](url)` at the caret.
- **Mode switch during upload:** if the mode changed before the upload finished, a visual placeholder is dropped by the serialize/parse cycle anyway. On completion, insert into whichever mode is active: in visual mode at the end of the document, in markdown mode at the caret.

- [ ] **Step 1: Write the failing tests**, with `fetch` mocked through `vi.stubGlobal`:

```js
test('csrf token from hidden input, falling back to cookie', () => {
  document.body.innerHTML = '<input name="csrfmiddlewaretoken" value="F">'; document.cookie = 'csrftoken=C';
  expect(getCsrfToken()).toBe('F'); document.body.innerHTML = ''; expect(getCsrfToken()).toBe('C');
});
test('upload sends header and form field', async () => {
  fetch.mockResolvedValue({ json: async () => ({ success: true, url: '/m/a.png', filename: 'a.png' }) });
  await uploadImage(new File(['x'], 'a.png', { type: 'image/png' }), '/forum/upload-image/');
  const [url, opts] = fetch.mock.calls[0];
  expect(url).toBe('/forum/upload-image/'); expect(opts.headers['X-CSRFToken']).toBe('F');
  expect(opts.body.get('csrfmiddlewaretoken')).toBe('F'); expect(opts.credentials).toBe('same-origin');
  expect(opts.body.get('file')).toBeInstanceOf(File); // key 'file': forum/views.py:142, legacy forum-editor.js:2401
});
test('server error rejects with its message', async () => {
  fetch.mockResolvedValue({ json: async () => ({ success: false, error: 'Файл изображения не был передан.' }) });
  await expect(uploadImage(file, '/u/')).rejects.toThrow('Файл изображения не был передан.');
});
test('visual placeholder never reaches textarea; success replaces it', async () => { /* resolve deferred; before: ta.value === 'a'; after: contains '![a.png](/m/a.png)' */ });
test('failure removes placeholder', async () => { /* reject; doc has no image; error message element visible */ });
test('mode switch mid-upload lands image in markdown mode (Review Focus 4)', async () => {
  /* start upload in visual, setMode('markdown'), resolve; expect ta.value to contain '![a.png](/m/a.png)' exactly once and no blob: URL */
});
```

Write the three commented tests with the stated assertions.

- [ ] **Step 2: Run** `npx vitest run test/upload.test.js`. Expected: FAIL.
- [ ] **Step 3: Implement** `upload.js` and wire it in.
- [ ] **Step 4: Run** `npm test`. Expected: all pass.
- [ ] **Step 5: Commit** with message `feat(forum-editor): image upload via paste, drop and button`.

---

### Task 11: Resize handle and editor CSS

**Files:**
- Create: `src/ui/resizeHandle.js`
- Modify: `src/editor.js`, `home/static/css/forum-editor.css` (append the `/* TipTap editor */` section)
- Test: `test/resizeHandle.test.js`

**Interfaces:**
- Produces: `initResizeHandle(resizerEl, getTargets: () => HTMLElement[]): () => void`. It returns a cleanup function. Behaviour ports legacy `initResizer` (`forum-editor-legacy.js:2466-2520`): mouse and touch drag, the same minimum height, `user-select` disabled on body while dragging, and `max-height: none` applied to the targets. The targets are the editor element and the textarea.

CSS additions, nothing else:
- `.forum-visual-editor.ProseMirror { white-space: pre-wrap; word-wrap: break-word; }`
- The placeholder: `.forum-visual-editor p.is-editor-empty:first-child::before { content: attr(data-placeholder); float: left; height: 0; pointer-events: none; }`, using the same colour as the legacy `[placeholder]:empty:before` rule.
- `.forum-visual-editor img.ProseMirror-selectednode { outline: 2px solid #80bdff; }`
- `.forum-raw-md` (a muted bordered block with monospace `pre`, `cursor: default`) and `.forum-raw-md pre { margin: 0; white-space: pre-wrap; }`.
- `.forum-visual-editor .ProseMirror-gapcursor` (ProseMirror's own gapcursor CSS).

- [ ] **Step 1: Write the failing test:** a mousedown at y=100, mousemove at y=160 and mouseup on `document` increase the target height by 60px, and touch events do the same.
- [ ] **Step 2: Run** the test. Expected: FAIL.
- [ ] **Step 3: Implement** the handle and add the CSS.
- [ ] **Step 4: Run** `npm test`. Expected: all pass.
- [ ] **Step 5: Commit** with message `feat(forum-editor): resize handle and ProseMirror styles`.

---

### Task 12: Template integration, build, switch-over, manual verification

**Files:**
- Modify: `home/templates/pybb/post_form.html:66-260` (the reply and quote handlers), `le_francais/settings/base.py` (default `"False"`), `home/static/js/forum-editor.js` + `.map` (rebuilt)
- Test: `forum/tests.py` (update the defaults test)

**Interfaces:**
- Consumes: `window.forumEditor` `Api` (Task 7).

- [ ] **Step 1: Update the reply/quote code in `post_form.html`.**
  - Reply greeting (around lines 128–137): when `window.forumEditor && window.forumEditor.setMarkdown` exists, call `forumEditor.setMarkdown(greeting + (current ? '\n' + current : ''))` instead of `$textarea.val(...)` plus `syncVisualFromMarkdown()`.
  - Both quote paths (around lines 182 and 230): keep `insertQuote`. Delete the `insertMarkdown` and raw `$textarea.val` fallbacks only on the new-editor branch. The legacy editor still needs them, so keep them and guard them with `{% if forum_editor_legacy %}`, or leave them, since `insertQuote` exists in both editors.
  - `focusEditor` keeps using `$visualEditor.focus()` and `restoreSelection()`, which the compatibility API provides.
- [ ] **Step 2: Flip the default.** Set `FORUM_EDITOR_LEGACY = os.environ.get("FORUM_EDITOR_LEGACY", "False") == "True"`. Run `tools\bin\micromamba.exe run -p tools\env python manage.py test forum`. Expected: OK, including `ForumEditorSwitchTests`.
- [ ] **Step 3: Build.** Run `npm test && npm run build` in `forum_editor_src`. Expected: tests pass and the build logs a bundle size. Record the size; anything above ~350 KB minified needs explaining in the PR.
- [ ] **Step 4: Run the manual verification.** Start the dev server per AGENTS.md and open a topic as a logged-in user.
  - **Look:** create the sample post (every mapping row, a spoiler with a nested list, a code block, an image, a table). Screenshot the editor area in visual mode with `?editor=legacy` and without it, and compare. Toolbar, modals, emoji picker and footer must be pixel-identical, and the editing area must match apart from the raw-block chip.
  - **Checklist,** in both modes:
    - all 18 `data-cmd` buttons;
    - every shortcut row in Latin and in Russian layout;
    - upload by paste, drop and button;
    - visual ↔ markdown switching preserves the content;
    - Reply and Quote buttons, including quoting selected text;
    - the resize handle, by mouse and by touch emulation;
    - submitting a post, then editing it, gives the same Markdown;
    - the unsaved-changes warning appears after typing;
    - review bugs 2, 3, 4, 6 and 10 can't be reproduced. For 4: a paragraph plus images, select the paragraph text, press Delete, and the images stay. For 6: bold inside H2, then Enter, and the new paragraph appears inside the editor.
  - **Browsers:** desktop Chrome and Firefox; mobile Safari and Chrome (a real device or the devtools device mode, noting which).
  - **Recording:** record any failure as a new failing test in the owning task's test file, fix it, and re-run.
- [ ] **Step 5: Commit**
```bash
git add home/templates/pybb/post_form.html le_francais/settings/base.py forum/tests.py home/static/js/forum-editor.js home/static/js/forum-editor.js.map home/static/css/forum-editor.css
git commit -m "feat(forum-editor): switch forum to TipTap editor"
```

---

## Not in This Plan (spec §7 follow-up)

After one release without a rollback, a separate small change will:
- delete `forum-editor-legacy.js`, the stale `forum-editor.min.js`/`.min.js.map`, `FORUM_EDITOR_LEGACY`, the context processor and the `?editor=legacy` override;
- delete the legacy-only branches in `post_form.html`.
