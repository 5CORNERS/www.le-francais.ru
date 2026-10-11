// Lists as Python-Markdown 2.6 starts them:
// - only after a blank line: `Texte\n- un` is one paragraph on the server
//   (markdown-it lets a list interrupt a paragraph). Inside a list item a
//   marker line still ends the item (next item) or starts a nested list.
// - ordered markers are `1.` only: `1)` is plain text.
const PAREN_MARKER = /^\d{1,9}\)/;

export function pyListPlugin(md) {
  const rule = md.block.ruler.__rules__.find((r) => r.name === 'list');
  const original = rule.fn;
  md.block.ruler.at('list', (state, startLine, endLine, silent) => {
    if (silent && state.parentType === 'paragraph' && state.listIndent < 0 &&
      state.sCount[startLine] >= state.blkIndent) return false;
    const text = state.src.slice(state.bMarks[startLine] + state.tShift[startLine], state.eMarks[startLine]);
    if (PAREN_MARKER.test(text)) return false;
    return original(state, startLine, endLine, silent);
  }, { alt: rule.alt.slice() });
}
