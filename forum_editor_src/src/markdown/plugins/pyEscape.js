// Backslash escapes as the server honours them: Python-Markdown 2.6
// ESCAPED_CHARS plus the characters added by smarty (" '), tables (|),
// pymdown caret/tilde (^ ~ space), mark (=), keys (+) and emoji (:).
// Any other `\x` stays a literal backslash (markdown-it would escape every
// ASCII punctuation character, e.g. `\&`, `\<`, `\?`).
const PY_ESCAPED = '\\`*_{}[]()>#+-.!"\'|^~=: ';

export function pyEscapePlugin(md) {
  const rule = md.inline.ruler.__rules__.find((r) => r.name === 'escape');
  const original = rule.fn;
  md.inline.ruler.at('escape', (state, silent) => {
    const pos = state.pos;
    if (state.src.charCodeAt(pos) !== 0x5c /* \ */) return false;
    if (pos + 1 >= state.posMax) return false;
    const ch = state.src[pos + 1];
    if (ch === '\n') return original(state, silent); // hard break
    const escaped = PY_ESCAPED.indexOf(ch) !== -1;
    if (!silent) {
      const token = state.push('text_special', '', 0);
      token.content = escaped ? ch : '\\';
      token.markup = escaped ? '\\' + ch : '\\';
      token.info = 'escape';
    }
    state.pos = pos + (escaped ? 2 : 1);
    return true;
  });
}
