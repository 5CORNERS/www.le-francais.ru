import { Mark, mergeAttributes } from '@tiptap/core';

export const Kbd = Mark.create({
  name: 'kbd',
  parseHTML() {
    return [{ tag: 'kbd' }];
  },
  renderHTML({ HTMLAttributes }) {
    return ['kbd', mergeAttributes({ class: 'editor-key' }, HTMLAttributes), 0];
  },
});
