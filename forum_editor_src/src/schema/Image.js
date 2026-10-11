import Image from '@tiptap/extension-image';
import { mergeAttributes } from '@tiptap/core';

export const ForumImage = Image.extend({
  addAttributes() {
    return {
      ...this.parent?.(),
      uploadId: { default: null, rendered: false },
    };
  },
  renderHTML({ HTMLAttributes }) {
    // attribute order: src, alt, title, class
    return ['img', mergeAttributes(HTMLAttributes, this.options.HTMLAttributes)];
  },
}).configure({
  inline: false,
  HTMLAttributes: { class: 'forum-embedded-img' },
});
