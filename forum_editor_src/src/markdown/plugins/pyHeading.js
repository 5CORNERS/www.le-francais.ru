// Python-Markdown 2.6 reads `#Titre` (no space after the hashes) as a
// heading; CommonMark does not. Wraps the `heading` rule so the no-space
// form yields the same tokens. Must run before rawBlock wraps `heading`.
const NO_SPACE = /^(#{1,6})([^#\s].*)$/;

export function pyHeadingPlugin(md) {
  const rule = md.block.ruler.__rules__.find((r) => r.name === 'heading');
  const original = rule.fn;
  md.block.ruler.at('heading', (state, startLine, endLine, silent) => {
    if (original(state, startLine, endLine, silent)) return true;
    if (state.sCount[startLine] - state.blkIndent >= 4) return false;
    const m = NO_SPACE.exec(state.src.slice(state.bMarks[startLine] + state.tShift[startLine], state.eMarks[startLine]));
    if (!m) return false;
    if (silent) return true;
    const tag = 'h' + m[1].length;
    const open = state.push('heading_open', tag, 1);
    open.markup = m[1];
    open.map = [startLine, startLine + 1];
    const inline = state.push('inline', '', 0);
    // Like Python-Markdown: trailing hashes are dropped.
    inline.content = m[2].replace(/#+\s*$/, '').trim();
    inline.map = [startLine, startLine + 1];
    inline.children = [];
    state.push('heading_close', tag, -1).markup = m[1];
    state.line = startLine + 1;
    return true;
  }, { alt: rule.alt.slice() });
}
