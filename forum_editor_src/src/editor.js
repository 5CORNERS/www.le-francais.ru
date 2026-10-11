import { Editor } from '@tiptap/core';
import { Placeholder } from '@tiptap/extensions';
import { TextSelection } from '@tiptap/pm/state';
import { extensions } from './schema/index.js';
import { parseMarkdown } from './markdown/parser.js';
import { serializeMarkdown } from './markdown/serializer.js';
import { buildEditorDom, updateActiveStates } from './ui/toolbar.js';
import { runVisualCommand, runMarkdownCommand } from './commands.js';

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

  const api = {
    currentMode: 'markdown',
    uploadUrl: uploadUrl,
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

  /** Parses `md` into the editor without emitting `update`. Returns false on parse failure. */
  function loadMarkdown(md) {
    let json;
    try {
      json = parseMarkdown(md || '').toJSON();
    } catch (e) {
      console.error('forum-editor: cannot parse Markdown', e);
      return false;
    }
    api.tiptap.commands.setContent(json, { emitUpdate: false });
    syncedDoc = api.tiptap.state.doc;
    selectionTouched = false;
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
    if (api.currentMode !== 'visual') return;
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

  function insertQuoteVisual(md) {
    const fragment = parseFragment(md);
    if (!fragment) return;
    const editor = api.tiptap;
    const schema = editor.schema;
    const blocks = [];
    fragment.forEach((n) => blocks.push(toEditorNode(n)));
    let quote;
    if (blocks.length === 1 && blocks[0].type.name === 'blockquote') {
      quote = blocks[0];
    } else {
      if (!blocks.length) return;
      quote = schema.nodes.blockquote.create(null, blocks);
    }
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
      return;
    }
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

  // Link modal (Task 9) and file picker (Task 10) plug in here.
  const commandContext = {
    openLinkModal: function () {},
    openFilePicker: function () {},
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

  const onSubmit = () => syncMarkdownFromVisual();
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

  function destroy() {
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
