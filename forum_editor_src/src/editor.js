import { Editor } from '@tiptap/core';
import { Placeholder } from '@tiptap/extensions';
import { EditorState, Selection, TextSelection } from '@tiptap/pm/state';
import { closeHistory } from '@tiptap/pm/history';
import { extensions } from './schema/index.js';
import { parseMarkdown } from './markdown/parser.js';
import { serializeMarkdown } from './markdown/serializer.js';
import { buildEditorDom, updateActiveStates } from './ui/toolbar.js';
import { runVisualCommand, runMarkdownCommand } from './commands.js';
import { bindShortcuts } from './keymap.js';
import { openLinkModal } from './ui/linkModal.js';
import { openImageModal } from './ui/imageModal.js';
import { sanitizeUrl } from './url.js';
import { initEmojiPicker } from './ui/emojiPicker.js';
import { bindUploadHandlers, insertBlockMarkdown, UPLOAD_PENDING_CONFIRM } from './upload.js';
import { initResizeHandle } from './ui/resizeHandle.js';

export const MODE_STORAGE_KEY = 'forum_editor_mode';
export const EDITOR_PLACEHOLDER = 'Напишите ответ или перетащите изображение сюда...';
export const PARSE_FAILURE_NOTICE = 'Не удалось открыть визуальный редактор — текст открыт в режиме Markdown.';

function readStoredMode() {
  try {
    return window.localStorage.getItem(MODE_STORAGE_KEY);
  } catch (e) {
    return null;
  }
}

function storeMode(mode) {
  try {
    window.localStorage.setItem(MODE_STORAGE_KEY, mode);
  } catch (e) {
    // Storage may be unavailable (private mode); the mode just isn't remembered.
  }
}

// The editor never adds content the author didn't write: StarterKit's
// TrailingNode would append an empty paragraph after a final heading/quote and
// rewrite the textarea on load.
function editorExtensions() {
  const list = extensions.map((ext) => (ext.name === 'starterKit' ? ext.configure({ trailingNode: false }) : ext));
  return list.concat([Placeholder.configure({ placeholder: EDITOR_PLACEHOLDER })]);
}

function fire(el, type) {
  el.dispatchEvent(new Event(type, { bubbles: true }));
}

/**
 * Mounts the TipTap forum editor on `textarea` (normally #id_body).
 * The textarea stays the form field: it is kept in sync with the visual doc.
 */
export function createForumEditor(options) {
  const opts = options || {};
  const textarea = opts.textarea;
  const uploadUrl = opts.uploadUrl || '/forum/upload-image/';
  const requestedMode = opts.initialMode || readStoredMode() || 'visual';
  const form = textarea.form || textarea.closest('form');

  textarea.classList.add('no-markitup', 'forum-markdown-textarea');
  textarea.removeAttribute('required');
  if (form) form.setAttribute('novalidate', 'novalidate');

  const dom = buildEditorDom(textarea);
  let notice = null;
  let selectionTouched = false;
  // The doc whose Markdown is currently in the textarea (set on load and after
  // each serialization); an unchanged doc is never re-serialized, so switching
  // modes without editing keeps the author's original Markdown.
  let syncedDoc = null;
  // False until the editor holds the post (initial visual mount or the first
  // switch to visual); that load stays out of the undo history.
  let historyStarted = false;
  // True while a load is dispatched: its update must not rewrite the textarea.
  let loading = false;

  const api = {
    currentMode: 'markdown',
    uploadUrl: uploadUrl,
    textarea: textarea,
    tiptap: null,
    dom: dom,
    element: null,
    $visualEditor: undefined,
  };

  // --- Markdown <-> visual -------------------------------------------------

  function hideNotice() {
    if (notice && notice.parentNode) notice.parentNode.removeChild(notice);
    notice = null;
  }

  function showNotice() {
    if (notice) return;
    notice = document.createElement('div');
    notice.className = 'alert alert-warning py-1 px-2 mb-1 small';
    notice.textContent = PARSE_FAILURE_NOTICE;
    dom.container.parentNode.insertBefore(notice, dom.container);
  }

  /**
   * Parses `md` into the editor. Returns false on parse failure. The first
   * load recreates the state (same plugins) so undo can never empty the post;
   * every later load that changes the doc is one undoable history step. The
   * load never rewrites the textarea: it is the source of the new doc.
   */
  function loadMarkdown(md) {
    let doc;
    try {
      doc = api.tiptap.schema.nodeFromJSON(parseMarkdown(md || '').toJSON());
    } catch (e) {
      console.error('forum-editor: cannot parse Markdown', e);
      return false;
    }
    const view = api.tiptap.view;
    if (!historyStarted) {
      view.updateState(EditorState.create({ doc: doc, plugins: view.state.plugins }));
      historyStarted = true;
    } else if (!doc.eq(view.state.doc)) {
      // Own history groups: the load neither merges with the edits before it
      // nor with the typing after it.
      const tr = closeHistory(view.state.tr.replaceWith(0, view.state.doc.content.size, doc.content));
      tr.setSelection(Selection.atStart(tr.doc));
      loading = true;
      try {
        view.dispatch(tr);
        view.dispatch(closeHistory(view.state.tr));
      } finally {
        loading = false;
      }
    }
    syncedDoc = api.tiptap.state.doc;
    selectionTouched = false;
    // updateState emits no transaction, so refresh the toolbar here.
    refreshActiveStates();
    return true;
  }

  function serializeDoc() {
    const doc = api.tiptap.state.doc;
    const md = serializeMarkdown(doc);
    syncedDoc = doc;
    return md;
  }

  function syncMarkdownFromVisual() {
    if (api.currentMode !== 'visual') return;
    if (api.tiptap.state.doc === syncedDoc) return;
    try {
      textarea.value = serializeDoc();
    } catch (e) {
      console.error('forum-editor: cannot serialize document', e);
    }
  }

  function updateCharCounter() {
    const len = (textarea.value || '').length;
    dom.charCounter.textContent = len > 0 ? len + ' симв.' : '';
  }

  function onUpdate() {
    if (loading || api.currentMode !== 'visual') return;
    let md;
    try {
      md = serializeDoc();
    } catch (e) {
      console.error('forum-editor: cannot serialize document', e);
      return;
    }
    textarea.value = md;
    fire(textarea, 'input');
    fire(textarea, 'change');
    updateCharCounter();
  }

  // --- Modes ----------------------------------------------------------------

  function updateModeButtons() {
    const isVisual = api.currentMode === 'visual';
    dom.wrapper.querySelector('.forum-mode-checkbox').checked = !isVisual;
    dom.wrapper.querySelector('.forum-mode-switch-btn.visual').classList.toggle('active', isVisual);
    dom.wrapper.querySelector('.forum-mode-switch-btn.markdown').classList.toggle('active', !isVisual);
  }

  function showVisual(visible) {
    dom.visualHost.style.display = visible ? '' : 'none';
    textarea.style.display = visible ? 'none' : '';
  }

  function enterVisual() {
    if (!loadMarkdown(textarea.value)) {
      showNotice();
      return false;
    }
    hideNotice();
    api.currentMode = 'visual';
    showVisual(true);
    return true;
  }

  function enterMarkdown() {
    api.currentMode = 'markdown';
    showVisual(false);
  }

  function setMode(newMode) {
    if (newMode !== 'visual' && newMode !== 'markdown') return;
    if (newMode === api.currentMode) return;

    if (newMode === 'markdown') {
      const visualH = api.element.offsetHeight;
      if (visualH > 0) {
        textarea.style.height = visualH + 'px';
        textarea.style.maxHeight = 'none';
      }
      syncMarkdownFromVisual();
      enterMarkdown();
      textarea.focus();
    } else {
      const textH = textarea.offsetHeight;
      if (!enterVisual()) {
        updateModeButtons();
        updateCharCounter();
        return;
      }
      if (textH > 0) {
        api.element.style.height = textH + 'px';
        api.element.style.maxHeight = 'none';
      }
      api.tiptap.commands.focus();
    }

    storeMode(api.currentMode);
    updateModeButtons();
    refreshActiveStates();
    updateCharCounter();
  }

  function syncVisualFromMarkdown() {
    if (api.currentMode === 'visual' && !loadMarkdown(textarea.value)) {
      showNotice();
      enterMarkdown();
      updateModeButtons();
      refreshActiveStates();
    }
    updateCharCounter();
  }

  // --- Insertion ------------------------------------------------------------

  function parseFragment(md) {
    try {
      return parseMarkdown(md).content;
    } catch (e) {
      console.error('forum-editor: cannot parse Markdown', e);
      return null;
    }
  }

  // Converts a node built by the parser's schema into the editor's schema.
  function toEditorNode(node) {
    return api.tiptap.schema.nodeFromJSON(node.toJSON());
  }

  /**
   * The quote as one block: the parsed blockquote, or (when the Markdown can't
   * be parsed or held by the schema) a raw Markdown block with its source.
   */
  function quoteNode(md) {
    const schema = api.tiptap.schema;
    const raw = () => schema.nodes.rawMarkdownBlock.create({ source: md.trim() });
    const fragment = parseFragment(md);
    if (!fragment) return raw();
    try {
      const blocks = [];
      fragment.forEach((n) => blocks.push(toEditorNode(n)));
      if (!blocks.length) return null;
      if (blocks.length === 1 && blocks[0].type.name === 'blockquote') return blocks[0];
      return schema.nodes.blockquote.create(null, blocks);
    } catch (e) {
      console.error('forum-editor: cannot build the quote', e);
      return raw();
    }
  }

  function insertQuoteVisual(md) {
    const quote = quoteNode(md);
    if (!quote) return;
    if (placeQuote(quote) || quote.type.name === 'rawMarkdownBlock') return;
    placeQuote(api.tiptap.schema.nodes.rawMarkdownBlock.create({ source: md.trim() }));
  }

  /** Inserts the quote block followed by a paragraph holding the caret. Returns false if no placement fits. */
  function placeQuote(quote) {
    const editor = api.tiptap;
    const schema = editor.schema;
    const emptyP = () => schema.nodes.paragraph.create();
    const state = editor.state;
    const sel = state.selection;
    const $from = sel.$from;

    // Each plan builds a transaction and returns the caret position inside the
    // trailing paragraph; it throws when the schema rejects the result.
    function atCaret(tr) {
      const parent = $from.parent;
      const depth = $from.depth;
      if (!parent.isTextblock || depth === 0) throw new Error('no text caret');
      const before = $from.before(depth);
      if (sel.empty && parent.type.name === 'paragraph' && parent.content.size === 0) {
        // Empty paragraph: replace it with the quote and a fresh paragraph.
        tr.replaceWith(before, $from.after(depth), [quote, emptyP()]);
        return before + quote.nodeSize + 1;
      }
      // Insert after the selection end; selected draft text is kept (legacy
      // splits at the range end too).
      const pos = sel.to;
      const $pos = tr.doc.resolve(pos);
      if (!$pos.parent.isTextblock) throw new Error('selection does not end in text');
      if ($pos.parentOffset === 0) {
        // Caret at block start: the quote goes before the block.
        const at = $pos.before($pos.depth);
        tr.insert(at, quote);
        return at + quote.nodeSize + 1;
      }
      if ($pos.parentOffset === $pos.parent.content.size) {
        const at = $pos.after($pos.depth);
        tr.insert(at, [quote, emptyP()]);
        return at + quote.nodeSize + 1;
      }
      // Mid-block: split; the text after the caret becomes the trailing paragraph.
      tr.split(pos);
      tr.insert(pos + 1, quote);
      return pos + 1 + quote.nodeSize + 1;
    }

    function afterTopLevelBlock(tr) {
      const at = $from.depth > 0 ? $from.after(1) : sel.to;
      tr.insert(at, [quote, emptyP()]);
      return at + quote.nodeSize + 1;
    }

    function atEnd(tr) {
      const doc = tr.doc;
      const last = doc.lastChild;
      if (last && last.type.name === 'paragraph' && last.content.size === 0) {
        const at = doc.content.size - last.nodeSize;
        tr.replaceWith(at, doc.content.size, [quote, emptyP()]);
        return at + quote.nodeSize + 1;
      }
      const at = doc.content.size;
      tr.insert(at, [quote, emptyP()]);
      return at + quote.nodeSize + 1;
    }

    const plans = selectionTouched ? [atCaret, afterTopLevelBlock, atEnd] : [atEnd];
    for (let i = 0; i < plans.length; i++) {
      const tr = state.tr;
      try {
        const caret = plans[i](tr);
        tr.doc.check();
        const $caret = tr.doc.resolve(caret);
        if (!$caret.parent.isTextblock) throw new Error('caret outside a textblock');
        tr.setSelection(TextSelection.create(tr.doc, caret)).scrollIntoView();
      } catch (e) {
        continue;
      }
      editor.view.dispatch(tr);
      selectionTouched = true;
      editor.commands.focus();
      return true;
    }
    return false;
  }

  function insertQuoteMarkdown(md) {
    const val = textarea.value;
    let start = textarea.selectionStart;
    if (typeof start !== 'number' || start < 0 || start > val.length) start = val.length;
    const before = val.substring(0, start);
    const after = val.substring(start);
    let prefix = '';
    if (before.length > 0 && !before.endsWith('\n')) prefix = '\n\n';
    let suffix = '';
    if (after.length > 0 && !after.startsWith('\n')) suffix = '\n\n';
    const clean = md.trim();
    textarea.value = before + prefix + clean + '\n\n' + suffix + after;
    const newPos = before.length + prefix.length + clean.length + 2;
    textarea.focus();
    textarea.setSelectionRange(newPos, newPos);
    fire(textarea, 'input');
    updateCharCounter();
  }

  function insertQuote(md) {
    if (!md) return;
    if (api.currentMode === 'visual') insertQuoteVisual(md);
    else insertQuoteMarkdown(md);
  }

  function insertMarkdown(md) {
    if (!md) return;
    if (md.trim().startsWith('>') || api.currentMode !== 'visual') {
      insertQuote(md);
      return;
    }
    const fragment = parseFragment(md);
    if (!fragment) return;
    let content;
    if (fragment.childCount === 1 && fragment.firstChild.type.name === 'paragraph') {
      // Single paragraph: insert inline so the current paragraph isn't split.
      content = fragment.firstChild.content.toJSON() || [];
    } else {
      content = [];
      fragment.forEach((n) => content.push(n.toJSON()));
    }
    if (!content.length) return;
    api.tiptap.chain().focus().insertContent(content).run();
  }

  // --- Selection & focus ---------------------------------------------------

  function restoreSelection() {
    if (api.currentMode === 'visual') api.tiptap.view.focus();
  }

  function focus() {
    if (api.currentMode === 'visual') api.tiptap.commands.focus();
    else textarea.focus();
  }

  // --- Toolbar commands -------------------------------------------------------

  // `openFilePicker` is set once the upload handlers are bound. `showLinkModal` and
  // `showImageModal` are the dialogs used by the link and image commands
  // (replaceable, e.g. in tests).
  const commandContext = {
    openLinkModal: function () {},
    openImageModal: function () {},
    openFilePicker: function () {},
    showLinkModal: openLinkModal,
    showImageModal: openImageModal,
  };

  function refreshActiveStates() {
    updateActiveStates(dom.toolbar, api.currentMode === 'visual' ? api.tiptap : null);
  }

  function executeCommand(cmd) {
    if (api.currentMode === 'visual') runVisualCommand(api.tiptap, cmd, commandContext);
    else runMarkdownCommand(textarea, cmd, commandContext);
    updateCharCounter();
    refreshActiveStates();
  }

  // --- Link & emoji -----------------------------------------------------------

  /** Sets the link on the selection if its text is unchanged, else inserts linked text. */
  function applyLinkVisual(range, selectedText, link) {
    const editor = api.tiptap;
    const state = editor.state;
    const size = state.doc.content.size;
    const from = Math.min(range.from, size);
    const to = Math.min(range.to, size);
    const linkType = state.schema.marks.link;
    const linkMark = linkType.create({ href: link.url });
    const display = link.text || link.url;
    const tr = state.tr;
    let end;
    if (from < to && display === selectedText.trim()) {
      tr.addMark(from, to, linkMark);
      end = to;
    } else {
      const $from = state.doc.resolve(from);
      const around = from < to ? ($from.marksAcross(state.doc.resolve(to)) || []) : $from.marks();
      tr.replaceWith(from, to, state.schema.text(display, linkMark.addToSet(around)));
      end = from + display.length;
    }
    const $end = tr.doc.resolve(end);
    tr.setSelection(TextSelection.create(tr.doc, end));
    // Typing after the link must not extend it.
    tr.setStoredMarks(linkType.removeFromSet($end.marks()));
    editor.view.dispatch(tr.scrollIntoView());
    editor.view.focus();
  }

  function applyLinkMarkdown(range, link) {
    const len = textarea.value.length;
    const insert = '[' + (link.text || link.url) + '](' + link.url + ')';
    textarea.focus();
    textarea.setRangeText(insert, Math.min(range.from, len), Math.min(range.to, len), 'end');
    fire(textarea, 'input');
  }

  /** The `link` command: asks for text and URL, then applies them in the current mode. */
  function linkCommand() {
    const mode = api.currentMode;
    let range;
    let text;
    if (mode === 'visual') {
      const sel = api.tiptap.state.selection;
      text = api.tiptap.state.doc.textBetween(sel.from, sel.to, ' ');
      // A selection without text (a selected image) is kept; the link goes after it.
      range = { from: text ? sel.from : sel.to, to: sel.to };
    } else {
      range = { from: textarea.selectionStart, to: textarea.selectionEnd };
      text = textarea.value.slice(range.from, range.to);
    }
    return Promise.resolve(commandContext.showLinkModal(dom.modal, { text: text, url: '' })).then(function (link) {
      if (api.currentMode !== mode) return;
      if (!link || !link.url) {
        focus();
        return;
      }
      // Legacy sanitizeUrl: only http(s):, /, mailto: and # links; others become '#'.
      // The display text stays what the author typed.
      const safe = { text: link.text || link.url, url: sanitizeUrl(link.url) };
      if (mode === 'visual') applyLinkVisual(range, text, safe);
      else applyLinkMarkdown(range, safe);
      updateCharCounter();
      refreshActiveStates();
    });
  }
  commandContext.openLinkModal = linkCommand;

  /** The `image` command: asks for a URL and caption (or a file to upload). */
  function imageCommand() {
    const mode = api.currentMode;
    const options = { onChooseFile: function () { commandContext.openFilePicker(); } };
    return Promise.resolve(commandContext.showImageModal(dom.modal, options)).then(function (image) {
      if (api.currentMode !== mode) return;
      if (!image || !image.url) {
        focus();
        return;
      }
      const src = sanitizeUrl(image.url);
      const title = image.title || '';
      if (mode === 'visual') {
        // A block image at the selection, like upload placeholders.
        const editor = api.tiptap;
        const node = editor.schema.nodes.image.create({ src: src, alt: title, title: title || null });
        editor.view.dispatch(editor.state.tr.replaceSelectionWith(node, false).scrollIntoView());
        editor.view.focus();
      } else {
        textarea.focus();
        insertBlockMarkdown(textarea, '![' + title + '](' + src + (title ? ' "' + title + '"' : '') + ')');
      }
      updateCharCounter();
      refreshActiveStates();
    });
  }
  commandContext.openImageModal = imageCommand;

  function insertEmoji(char) {
    if (api.currentMode === 'visual') {
      const editor = api.tiptap;
      editor.view.dispatch(editor.state.tr.insertText(char).scrollIntoView());
      editor.view.focus();
    } else {
      const start = textarea.selectionStart;
      const end = textarea.selectionEnd;
      textarea.focus();
      textarea.setRangeText(char, start, end, 'end');
      fire(textarea, 'input');
    }
    updateCharCounter();
  }

  // --- Mount ------------------------------------------------------------------

  const startVisual = requestedMode === 'visual';
  let initialContent = null;
  let parseFailed = false;
  if (startVisual) {
    try {
      initialContent = parseMarkdown(textarea.value || '').toJSON();
    } catch (e) {
      console.error('forum-editor: cannot parse Markdown', e);
      parseFailed = true;
    }
  }

  const tiptap = new Editor({
    element: dom.visualHost,
    extensions: editorExtensions(),
    content: initialContent,
    editorProps: {
      attributes: { class: 'forum-visual-editor', spellcheck: 'true' },
    },
  });
  api.tiptap = tiptap;
  api.element = tiptap.view.dom;
  if (window.jQuery) api.$visualEditor = window.jQuery(api.element);

  syncedDoc = tiptap.state.doc;
  tiptap.on('update', onUpdate);
  // Any focus or caret move makes the current selection the insertion point.
  tiptap.on('focus', () => { selectionTouched = true; });
  tiptap.on('selectionUpdate', () => { selectionTouched = true; });
  tiptap.on('transaction', () => {
    if (api.currentMode === 'visual') refreshActiveStates();
  });

  if (startVisual && !parseFailed) {
    historyStarted = true;
    api.currentMode = 'visual';
    showVisual(true);
  } else {
    if (parseFailed) showNotice();
    enterMarkdown();
  }
  updateModeButtons();
  updateCharCounter();
  refreshActiveStates();

  // --- DOM events -------------------------------------------------------------

  // Capture phase: runs before the page's own submit handlers.
  const onSubmit = (e) => {
    if (uploads.pendingCount() > 0 && !window.confirm(UPLOAD_PENDING_CONFIRM)) {
      e.preventDefault();
      return;
    }
    syncMarkdownFromVisual();
  };
  const onTextareaInput = () => {
    if (api.currentMode === 'markdown') updateCharCounter();
  };
  const onCheckbox = (e) => setMode(e.target.checked ? 'markdown' : 'visual');
  const onSwitchClick = (e) => {
    const btn = e.target.closest('.forum-mode-switch-btn');
    if (!btn || !dom.wrapper.contains(btn)) return;
    e.preventDefault();
    e.stopPropagation();
    setMode(btn.getAttribute('data-mode'));
  };
  // Toolbar buttons and emoji items must not steal focus from the editor.
  const onWrapperMousedown = (e) => {
    const target = e.target.closest('.forum-editor-btn, .forum-emoji-item, .forum-emoji-close');
    if (target && dom.wrapper.contains(target)) e.preventDefault();
  };
  const onToolbarClick = (e) => {
    const btn = e.target.closest('.forum-editor-btn[data-cmd]');
    if (!btn || !dom.toolbar.contains(btn)) return;
    e.preventDefault();
    executeCommand(btn.getAttribute('data-cmd'));
  };
  const checkbox = dom.wrapper.querySelector('.forum-mode-checkbox');
  const modeSwitch = dom.wrapper.querySelector('.forum-mode-switch');

  if (form) form.addEventListener('submit', onSubmit, true);
  textarea.addEventListener('input', onTextareaInput);
  checkbox.addEventListener('change', onCheckbox);
  modeSwitch.addEventListener('click', onSwitchClick);
  dom.wrapper.addEventListener('mousedown', onWrapperMousedown);
  dom.toolbar.addEventListener('click', onToolbarClick);
  const unbindVisualKeys = bindShortcuts(api.element, executeCommand);
  const unbindTextareaKeys = bindShortcuts(textarea, executeCommand);
  const destroyEmojiPicker = initEmojiPicker(dom.emoji, insertEmoji);
  const uploads = bindUploadHandlers(api, dom);
  const destroyResizer = initResizeHandle(dom.resizer, function () {
    return [api.element, textarea];
  });
  commandContext.openFilePicker = uploads.openFilePicker;

  let destroyed = false;

  /** Unmounts the editor and puts the textarea back. Safe to call twice. */
  function destroy() {
    if (destroyed) return;
    destroyed = true;
    unbindVisualKeys();
    unbindTextareaKeys();
    destroyEmojiPicker();
    uploads.destroy();
    destroyResizer();
    if (form) form.removeEventListener('submit', onSubmit, true);
    textarea.removeEventListener('input', onTextareaInput);
    checkbox.removeEventListener('change', onCheckbox);
    modeSwitch.removeEventListener('click', onSwitchClick);
    dom.wrapper.removeEventListener('mousedown', onWrapperMousedown);
    dom.toolbar.removeEventListener('click', onToolbarClick);
    syncMarkdownFromVisual();
    tiptap.destroy();
    textarea.style.display = '';
    dom.wrapper.parentNode.insertBefore(textarea, dom.wrapper);
    dom.wrapper.parentNode.removeChild(dom.wrapper);
    hideNotice();
    if (window.forumEditor === api) delete window.forumEditor;
  }

  Object.assign(api, {
    setMode: setMode,
    getMarkdown: function () {
      if (api.currentMode === 'visual') syncMarkdownFromVisual();
      return textarea.value;
    },
    setMarkdown: function (md) {
      textarea.value = md || '';
      syncVisualFromMarkdown();
    },
    syncMarkdownFromVisual: syncMarkdownFromVisual,
    syncVisualFromMarkdown: syncVisualFromMarkdown,
    insertQuote: insertQuote,
    insertMarkdown: insertMarkdown,
    restoreSelection: restoreSelection,
    focus: focus,
    executeCommand: executeCommand,
    commandContext: commandContext,
    destroy: destroy,
    updateCharCounter: updateCharCounter,
  });

  return api;
}
