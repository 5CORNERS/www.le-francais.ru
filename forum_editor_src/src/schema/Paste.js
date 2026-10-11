import Bold from '@tiptap/extension-bold';

// Paste rules: Google Docs wraps content in <b style="font-weight:normal">,
// which must not be treated as bold; spans with real weights are bold.
export const BOLD_PASTE_RULES = [
  { tag: 'strong' },
  {
    tag: 'b',
    getAttrs: (node) => {
      const w = node.style.fontWeight;
      return w !== 'normal' && w !== '400' ? null : false;
    },
  },
  {
    style: 'font-weight=400',
    clearMark: (mark) => mark.type.name === 'bold',
  },
  {
    style: 'font-weight',
    getAttrs: (value) => (/^(bold(er)?|[5-9]\d{2,})$/.test(value) ? null : false),
  },
];

export const ForumBold = Bold.extend({
  parseHTML() {
    return BOLD_PASTE_RULES;
  },
});
