// pymdown keys: ++ctrl+c++ -> a single `kbd` token, content = inner text verbatim.
export function keysPlugin(md) {
  md.inline.ruler.before('emphasis', 'kbd', (state, silent) => {
    const start = state.pos;
    const src = state.src;
    if (src.charCodeAt(start) !== 0x2b || src.charCodeAt(start + 1) !== 0x2b) return false;
    const contentStart = start + 2;
    const end = src.indexOf('++', contentStart);
    if (end === -1 || end >= state.posMax || end === contentStart) return false;
    const content = src.slice(contentStart, end);
    if (content.indexOf('\n') !== -1) return false;

    if (!silent) {
      const token = state.push('kbd', 'kbd', 0);
      token.content = content;
      token.markup = '++';
    }
    state.pos = end + 2;
    return true;
  });
  md.renderer.rules.kbd = (tokens, idx) =>
    '<kbd>' + md.utils.escapeHtml(tokens[idx].content) + '</kbd>';
}
