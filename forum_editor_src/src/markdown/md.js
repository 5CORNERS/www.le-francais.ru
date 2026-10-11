import MarkdownIt from 'markdown-it';
import mark from 'markdown-it-mark';
import sub from 'markdown-it-sub';
import sup from 'markdown-it-sup';
import { underlinePlugin } from './plugins/underline.js';
import { keysPlugin } from './plugins/keys.js';
import { emojiShortcodePlugin } from './plugins/emojiShortcode.js';

export function createMarkdownIt() {
  const md = new MarkdownIt({ html: false, breaks: true, linkify: false, typographer: false });
  // Built-in `~~` strikethrough is enabled by default and runs before `~` (sub).
  md.use(mark).use(sub).use(sup);
  // Registered before `emphasis`, hence before `sup`: `^^` wins over `^`.
  md.use(underlinePlugin).use(keysPlugin).use(emojiShortcodePlugin);
  return md;
}
