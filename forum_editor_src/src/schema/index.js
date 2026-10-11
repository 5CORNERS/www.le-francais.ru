import { getSchema } from '@tiptap/core';
import StarterKit from '@tiptap/starter-kit';
import Highlight from '@tiptap/extension-highlight';
import Subscript from '@tiptap/extension-subscript';
import Superscript from '@tiptap/extension-superscript';
import { Kbd } from './Kbd.js';
import { ForumCodeBlock } from './CodeBlock.js';
import { ForumImage } from './Image.js';
import { Spoiler, SpoilerSummary, SpoilerBody } from './Spoiler.js';
import { RawMarkdownBlock } from './RawMarkdownBlock.js';
import { ForumBulletList, ForumOrderedList } from './Lists.js';
import { ForumLink } from './Link.js';
import { ForumBold, BOLD_PASTE_RULES } from './Paste.js';
import { ForumKeys } from '../keymap.js';

export { BOLD_PASTE_RULES };

// Legacy parity: formatting shortcuts exist only in keymap.js (through
// executeCommand). TipTap's built-in Mod-… shortcuts (Mod-E code, Mod-. sup,
// Mod-Shift-B quote, Mod-Alt-2 heading, Mod-Shift-7 list…) are removed; the
// editing keys of the same extensions (Enter, Backspace, Tab, arrows) stay.
function withoutModShortcuts(ext) {
  return ext.extend({
    addKeyboardShortcuts() {
      const map = Object.assign({}, this.parent ? this.parent() : {});
      Object.keys(map).forEach(function (k) {
        if (/(^|-)Mod-/.test(k)) delete map[k];
      });
      return map;
    },
  });
}

// StarterKit parts with formatting shortcuts. Undo/redo, hard break and the
// list-item/list keymaps keep theirs.
const STARTER_KIT_STRIPPED = ['blockquote', 'code', 'heading', 'italic', 'strike', 'underline', 'paragraph'];

const ForumStarterKit = StarterKit.extend({
  addExtensions() {
    return this.parent().map(function (ext) {
      return STARTER_KIT_STRIPPED.indexOf(ext.name) >= 0 ? withoutModShortcuts(ext) : ext;
    });
  },
});

export const extensions = [
  ForumStarterKit.configure({
    heading: { levels: [1, 2, 3, 4, 5, 6] },
    horizontalRule: false,
    bulletList: false,
    orderedList: false,
    codeBlock: false,
    bold: false,
    link: false,
  }),
  withoutModShortcuts(ForumBold),
  ForumLink,
  withoutModShortcuts(ForumBulletList),
  withoutModShortcuts(ForumOrderedList),
  withoutModShortcuts(ForumCodeBlock),
  ForumImage,
  withoutModShortcuts(Highlight),
  withoutModShortcuts(Subscript),
  withoutModShortcuts(Superscript),
  Kbd,
  Spoiler,
  SpoilerSummary,
  SpoilerBody,
  RawMarkdownBlock,
  ForumKeys,
];

let cached = null;
export function getForumSchema() {
  if (!cached) cached = getSchema(extensions);
  return cached;
}
