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

export const extensions = [
  StarterKit.configure({
    heading: { levels: [2, 3] },
    horizontalRule: false,
    bulletList: false,
    orderedList: false,
    codeBlock: false,
    bold: false,
    link: false,
  }),
  ForumBold,
  ForumLink,
  ForumBulletList,
  ForumOrderedList,
  ForumCodeBlock,
  ForumImage,
  Highlight,
  Subscript,
  Superscript,
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
