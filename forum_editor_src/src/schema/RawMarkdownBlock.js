import { Node } from '@tiptap/core';

export const RAW_BLOCK_TITLE = 'Этот фрагмент редактируется в режиме Markdown';

export const RawMarkdownBlock = Node.create({
  name: 'rawMarkdownBlock',
  group: 'block',
  atom: true,
  selectable: false,
  addAttributes() {
    return { source: { default: '', rendered: false } };
  },
  parseHTML() {
    return [
      {
        tag: 'div.forum-raw-md',
        getAttrs: (el) => ({ source: el.textContent }),
      },
    ];
  },
  renderHTML({ node }) {
    return [
      'div',
      { class: 'forum-raw-md', contenteditable: 'false', title: RAW_BLOCK_TITLE },
      ['pre', node.attrs.source],
    ];
  },
});
