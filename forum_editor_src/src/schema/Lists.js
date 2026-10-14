import { BulletList, OrderedList } from '@tiptap/extension-list';

const tight = { default: true, rendered: false };

export const ForumBulletList = BulletList.extend({
  addAttributes() {
    return { ...this.parent?.(), tight };
  },
});

export const ForumOrderedList = OrderedList.extend({
  addAttributes() {
    return { ...this.parent?.(), tight };
  },
});
