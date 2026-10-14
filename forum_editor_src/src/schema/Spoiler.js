import { Node } from '@tiptap/core';
import { Plugin, PluginKey } from '@tiptap/pm/state';
import { Decoration, DecorationSet } from '@tiptap/pm/view';

// Placeholder copy from the legacy editor (forum-editor-legacy.js spoiler insert).
export const SPOILER_SUMMARY_PLACEHOLDER = 'Введите заголовок спойлера';
export const SPOILER_BODY_PLACEHOLDER = 'Введите текст спойлера — можно также вставлять изображения';

function hasVisibleContent(node) {
  if (node.textContent.trim()) return true;
  let found = false;
  node.descendants((child) => {
    if (found) return false;
    if (child.isLeaf && !child.isText && child.type.name !== 'hardBreak') found = true;
    return !found;
  });
  return found;
}

// Mirrors the legacy updateSpoilerPlaceholders(): data-empty / data-placeholder
// on <summary> and .spoiler-body, consumed by forum-editor.css.
function spoilerDecorations(doc) {
  const decos = [];
  doc.descendants((node, pos) => {
    const name = node.type.name;
    if (name === 'spoilerSummary' || name === 'spoilerBody') {
      decos.push(Decoration.node(pos, pos + node.nodeSize, {
        'data-empty': hasVisibleContent(node) ? 'false' : 'true',
        'data-placeholder': name === 'spoilerSummary' ? SPOILER_SUMMARY_PLACEHOLDER : SPOILER_BODY_PLACEHOLDER,
      }));
      return name === 'spoilerBody';
    }
    // Spoilers only live in block containers; skip inline content.
    return !node.isTextblock && !node.isAtom;
  });
  return DecorationSet.create(doc, decos);
}

const spoilerPlaceholderKey = new PluginKey('forumSpoilerPlaceholder');

export const Spoiler = Node.create({
  name: 'spoiler',
  group: 'block',
  content: 'spoilerSummary spoilerBody',
  defining: true,
  isolating: true,
  parseHTML() {
    return [{ tag: 'details' }];
  },
  renderHTML() {
    return ['details', { class: 'forum-spoiler', open: '' }, 0];
  },
  addProseMirrorPlugins() {
    return [
      new Plugin({
        key: spoilerPlaceholderKey,
        state: {
          init: (_, state) => spoilerDecorations(state.doc),
          apply: (tr, old) => (tr.docChanged ? spoilerDecorations(tr.doc) : old),
        },
        props: {
          decorations(state) {
            return spoilerPlaceholderKey.getState(state);
          },
        },
      }),
    ];
  },
});

export const SpoilerSummary = Node.create({
  name: 'spoilerSummary',
  content: 'inline*',
  defining: true,
  parseHTML() {
    return [{ tag: 'summary' }];
  },
  renderHTML() {
    return ['summary', 0];
  },
});

export const SpoilerBody = Node.create({
  name: 'spoilerBody',
  content: 'block+',
  defining: true,
  parseHTML() {
    return [{ tag: 'div.spoiler-body' }];
  },
  renderHTML() {
    return ['div', { class: 'spoiler-body' }, 0];
  },
});
