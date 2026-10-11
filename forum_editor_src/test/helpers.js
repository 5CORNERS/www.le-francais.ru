import { TextSelection } from '@tiptap/pm/state';
import { createForumEditor } from '../src/editor.js';

const live = [];

/**
 * Mounts a forum editor on a fresh `<form><textarea>` holding `md`.
 * Call `destroyEditors()` in afterEach.
 */
export function makeEditor(md, mode) {
  const form = document.createElement('form');
  const textarea = document.createElement('textarea');
  textarea.id = 'id_body';
  textarea.value = md || '';
  form.appendChild(textarea);
  document.body.appendChild(form);
  const ed = createForumEditor({ textarea: textarea, initialMode: mode || 'visual' });
  live.push({ ed: ed, form: form });
  return ed;
}

export function destroyEditors() {
  while (live.length) {
    const item = live.pop();
    item.ed.destroy();
    if (item.form.parentNode) item.form.parentNode.removeChild(item.form);
  }
}

/**
 * Selects from the start of the first occurrence of `fromWord` to the end of
 * the first occurrence of `toWord` (document order). Textblocks are separated
 * by '\n' so words never match across block boundaries.
 */
export function selectText(ed, fromWord, toWord) {
  const doc = ed.tiptap.state.doc;
  let text = '';
  const positions = [];
  doc.descendants((node, pos) => {
    if (node.isTextblock && text.length) {
      text += '\n';
      positions.push(-1);
    }
    if (node.isText) {
      for (let i = 0; i < node.text.length; i++) {
        text += node.text[i];
        positions.push(pos + i);
      }
    }
    return true;
  });
  const a = text.indexOf(fromWord);
  const b = text.indexOf(toWord);
  if (a < 0 || b < 0) throw new Error('selectText: word not found');
  const from = positions[a];
  const to = positions[b + toWord.length - 1] + 1;
  const tr = ed.tiptap.state.tr.setSelection(TextSelection.create(doc, from, to));
  ed.tiptap.view.dispatch(tr);
}
