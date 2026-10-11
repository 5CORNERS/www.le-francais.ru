// ATX headings as Python-Markdown 2.6 reads them (server-probed). Its rule is
// `(^|\n)(?P<level>#{1,6})(?P<header>.*?)#*(\n|$)` with the text stripped:
// no space is needed after the hashes (`#Titre`, `#5`), a seventh `#` is
// heading text (`####### a` is h6 `# a`), and any trailing run of hashes is
// dropped (`# C#` is h1 `C`). Replaces markdown-it's `heading` rule; must run
// before rawBlock wraps `heading`.
//
// Lines indented relative to their container are a paragraph on the server
// at top level but a heading in list items (pymdown detabs by 4): when
// either reading sees a heading, the token gets `meta.raw` and rawBlock keeps
// the source. Such lines never interrupt a paragraph (server: same <p>).
const PY_ATX = /^(#{1,6})(.*?)#*$/;

function lineText(state, line) {
  return state.src.slice(state.bMarks[line] + state.tShift[line], state.eMarks[line]);
}

export function pyHeadingPlugin(md) {
  const rule = md.block.ruler.__rules__.find((r) => r.name === 'heading');
  const original = rule.fn;
  md.block.ruler.at('heading', (state, startLine, endLine, silent) => {
    const indent = state.sCount[startLine] - state.blkIndent;
    if (indent >= 4) return false;
    if (indent > 0) {
      if (silent) return false;
      const first = state.tokens.length;
      if (!original(state, startLine, endLine, false)) {
        if (!PY_ATX.test(lineText(state, startLine))) return false;
        state.push('heading_open', 'h1', 1);
        state.push('heading_close', 'h1', -1);
        state.line = startLine + 1;
      }
      state.tokens[first].meta = { raw: true };
      return true;
    }
    const m = PY_ATX.exec(lineText(state, startLine));
    if (!m) return false;
    if (silent) return true;
    const tag = 'h' + m[1].length;
    const open = state.push('heading_open', tag, 1);
    open.markup = m[1];
    open.map = [startLine, startLine + 1];
    const inline = state.push('inline', '', 0);
    inline.content = m[2].trim();
    inline.map = [startLine, startLine + 1];
    inline.children = [];
    state.push('heading_close', tag, -1).markup = m[1];
    state.line = startLine + 1;
    return true;
  }, { alt: rule.alt.slice() });
}
