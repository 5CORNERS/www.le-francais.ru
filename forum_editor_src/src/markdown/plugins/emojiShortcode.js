import { SHORTCODE_TO_CHAR } from '../../emoji.js';

// Known :code: shortcodes -> text token holding the emoji character.
// Inline rule, so shortcodes inside code spans are never touched.
export function emojiShortcodePlugin(md) {
  md.inline.ruler.push('emoji_shortcode', (state, silent) => {
    const src = state.src;
    const start = state.pos;
    if (src.charCodeAt(start) !== 0x3a) return false;
    const m = /^:([\w+-]+):/.exec(src.slice(start, state.posMax));
    if (!m) return false;
    const char = SHORTCODE_TO_CHAR[m[0]];
    if (!char) return false;
    if (!silent) {
      const token = state.push('text', '', 0);
      token.content = char;
    }
    state.pos = start + m[0].length;
    return true;
  });
}
