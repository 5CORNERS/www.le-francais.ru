# Manual verification checklist: TipTap forum editor

Start: `start.bat` (or runserver per AGENTS.md), open a topic as a logged-in user.
Compare modes: default (TipTap) vs `?editor=legacy`. Browsers: desktop Chrome and Firefox; Safari (desktop or iOS) and mobile Chrome (real device or devtools device mode; note which).

## Look
- [ ] Create a sample post: every mapping row, a spoiler with a nested list, a code block, an image, a table.
- [ ] Screenshot the editor area in visual mode with `?editor=legacy` and without; compare. Toolbar, modals, emoji picker and footer pixel-identical; editing area matches apart from the raw-block chip.
- [ ] Raw-block chip for the table looks acceptable (title "Этот фрагмент редактируется в режиме Markdown").
- [ ] Placeholder text is visible in an empty editor.

## Toolbar and shortcuts (both modes)
- [ ] All 18 `data-cmd` buttons work.
- [ ] Every shortcut row, in Latin and Russian layout.
- [ ] Ctrl+B toggles bold exactly once (Chrome, Firefox, Safari).
- [ ] Link dialog (open, insert, edit, remove) and emoji picker (open, insert, close on outside click).

## Spoiler
- [ ] Select text, click spoiler: the selection is wrapped (code blocks stay whole).
- [ ] Spoiler removal: Backspace at the start of the title; toolbar toggle inside a spoiler.

## Upload
- [ ] Upload by paste, drop and button.
- [ ] Selection/caret is sane after pasting an image.
- [ ] Repeated drag-enter/leave over the editor: overlay shows and hides correctly, never sticks.
- [ ] Upload error (e.g. block `/forum/upload-image/` or upload a bad file) shows the legacy alert.

## Modes and content
- [ ] Visual <-> Markdown switching preserves content.
- [ ] Submit a post, then edit it: same Markdown.
- [ ] Unsaved-changes warning appears after typing.
- [ ] Resize handle by mouse and by touch emulation.

## Reply / Quote
- [ ] Reply button inserts the `**user**, ` greeting (also with existing draft text) and shows the reply indicator.
- [ ] Quote whole post and quote selected text.
- [ ] Quote button with selected draft text in the editor keeps that text.

## Review bugs
- [ ] Bugs 2, 3, 10 cannot be reproduced.
- [ ] Bug 4: paragraph plus images, select the paragraph text, press Delete: images stay.
- [ ] Bug 6: bold inside H2, press Enter: the new paragraph appears inside the editor.

## Rollback
- [ ] `?editor=legacy` loads the legacy editor; reply and quote still work there. Env var `FORUM_EDITOR_LEGACY=True` does the same site-wide.

Any failure: add a failing test in the owning task's test file, fix, re-run.
