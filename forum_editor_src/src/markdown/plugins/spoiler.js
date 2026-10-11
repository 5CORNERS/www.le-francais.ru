// pymdownx.details spoilers:
//   ???- "Title"
//       indented body (4 spaces or a tab)
// Emits spoiler_open, spoiler_summary (inline children = parsed title),
// the recursively tokenized body, spoiler_close.

// Mirrors pymdownx.details 5.0 DetailsProcessor.START (Python `\w` is Unicode-aware).
const W = '[\\p{L}\\p{N}_\\-]';
const START = new RegExp(
  '^\\?{3}(\\+)? ?(?:(' + W + '+(?: +' + W + '+)*?)?(?: +"(.*?)")|(' + W + '+(?: +' + W + '+)*?)) *$',
  'u'
);

// Same title derivation as pymdownx.details.
function titleFromMatch(m) {
  if (m[4]) {
    const first = m[4].toLowerCase().replace(/ {2,}/g, ' ').split(' ')[0];
    return first.charAt(0).toUpperCase() + first.slice(1);
  }
  return m[3];
}

// Text of a body line with `indent` columns of leading whitespace removed
// (tabs expand to the next multiple of 4, as in markdown-it).
function stripColumns(state, line, indent) {
  const extra = state.sCount[line] - indent;
  return ' '.repeat(Math.max(extra, 0)) + state.src.slice(state.bMarks[line] + state.tShift[line], state.eMarks[line]);
}

export function spoilerPlugin(md) {
  md.block.ruler.before('table', 'spoiler', (state, startLine, endLine, silent) => {
    if (state.sCount[startLine] - state.blkIndent >= 4) return false;
    const pos = state.bMarks[startLine] + state.tShift[startLine];
    if (state.src.charCodeAt(pos) !== 0x3f /* ? */) return false;
    const m = START.exec(state.src.slice(pos, state.eMarks[startLine]));
    if (!m) return false;
    if (silent) return true;

    // Body is indented 4 columns relative to the `???` line (pymdown detab).
    const bodyIndent = state.sCount[startLine] + 4;
    let last = startLine; // last non-blank body line
    for (let line = startLine + 1; line < endLine; line++) {
      if (state.isEmpty(line)) continue;
      if (state.sCount[line] < bodyIndent) break;
      last = line;
    }

    const lines = [];
    for (let line = startLine + 1; line <= last; line++) {
      lines.push(state.isEmpty(line) ? '' : stripColumns(state, line, bodyIndent));
    }

    const open = state.push('spoiler_open', 'details', 1);
    open.markup = '???';
    open.block = true;
    open.map = [startLine, last + 1];

    const summary = state.push('spoiler_summary', 'summary', 0);
    summary.block = true;
    summary.content = titleFromMatch(m);
    summary.children = [];
    state.md.inline.parse(summary.content, state.md, state.env, summary.children);

    if (lines.length) state.md.block.parse(lines.join('\n'), state.md, state.env, state.tokens);

    const close = state.push('spoiler_close', 'details', -1);
    close.markup = '???';
    close.block = true;

    state.line = last + 1;
    return true;
  });
}
