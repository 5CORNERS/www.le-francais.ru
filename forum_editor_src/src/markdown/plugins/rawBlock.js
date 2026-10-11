// Block constructs the visual editor cannot edit become a single `raw_block`
// token whose `content` is the exact source slice (lines joined with \n).
//
// Own detection (rule `raw_block`, before `table`): footnote definitions,
// admonitions, definition lists, abbreviations, attr_list-only lines.
// Wrapped markdown-it rules: tables, horizontal rules, headings other than
// h2/h3 (or containing an image), setext headings, and lists that contain a
// task item.

const FOOTNOTE_DEF = /^\[\^[^\]\s]+]:/;
const ADMONITION = /^!!! ?[\p{L}\p{N}_-]/u;
const ABBREVIATION = /^\*\[[^\]]+]:/;
const ATTR_LIST = /^\{:[^}]*}\s*$/;
const DEF_LINE = /^: {1,3}\S/;
const TASK_ITEM = /^\[[ xX]]\s/;

function lineText(state, line) {
  return state.src.slice(state.bMarks[line] + state.tShift[line], state.eMarks[line]);
}

function isIndentedCode(state, line) {
  return state.sCount[line] - state.blkIndent >= 4;
}

// Source of one line relative to the current block context.
function sourceLine(state, line) {
  if (state.blkIndent === 0) return state.src.slice(state.bMarks[line], state.eMarks[line]);
  if (state.isEmpty(line)) return '';
  return ' '.repeat(Math.max(state.sCount[line] - state.blkIndent, 0)) + lineText(state, line);
}

function pushRaw(state, startLine, nextLine) {
  let end = nextLine;
  while (end > startLine + 1 && state.isEmpty(end - 1)) end--;
  const lines = [];
  for (let line = startLine; line < end; line++) lines.push(sourceLine(state, line));
  const token = state.push('raw_block', '', 0);
  token.block = true;
  token.content = lines.join('\n');
  token.map = [startLine, end];
  state.line = nextLine;
}

// End (exclusive) of a body made of lines indented 4+ columns, with blank
// lines between them. With `lazy`, unindented lines directly following
// `from` (until the first blank line) belong to the body as well.
function bodyEnd(state, from, endLine, lazy) {
  let line = from;
  let last = from - 1;
  if (lazy) {
    while (line < endLine && !state.isEmpty(line)) last = line++;
  }
  for (; line < endLine; line++) {
    if (state.isEmpty(line)) continue;
    if (!isIndentedCode(state, line)) break;
    last = line;
  }
  return last + 1;
}

function isDefinitionStart(state, line, endLine) {
  return line + 1 < endLine && !state.isEmpty(line) && !state.isEmpty(line + 1) &&
    !isIndentedCode(state, line + 1) && DEF_LINE.test(lineText(state, line + 1));
}

function definitionListEnd(state, startLine, endLine) {
  let next = startLine;
  for (;;) {
    while (next < endLine && !state.isEmpty(next)) next++;
    let line = next;
    while (line < endLine && state.isEmpty(line)) line++;
    if (line >= endLine) return next;
    const continues = isIndentedCode(state, line) || DEF_LINE.test(lineText(state, line)) ||
      isDefinitionStart(state, line, endLine);
    if (!continues) return next;
    next = line;
  }
}

function detectRaw(state, startLine, endLine) {
  const text = lineText(state, startLine);
  if (FOOTNOTE_DEF.test(text)) return bodyEnd(state, startLine + 1, endLine, true);
  if (ADMONITION.test(text)) return bodyEnd(state, startLine + 1, endLine, false);
  if (ABBREVIATION.test(text)) {
    let line = startLine + 1;
    while (line < endLine && !isIndentedCode(state, line) && ABBREVIATION.test(lineText(state, line))) line++;
    return line;
  }
  if (ATTR_LIST.test(text)) return startLine + 1;
  if (isDefinitionStart(state, startLine, endLine)) return definitionListEnd(state, startLine, endLine);
  return -1;
}

function wrapRule(md, name, isRaw) {
  const rule = md.block.ruler.__rules__.find((r) => r.name === name);
  const original = rule.fn;
  md.block.ruler.at(name, (state, startLine, endLine, silent) => {
    if (silent) return original(state, startLine, endLine, true);
    const first = state.tokens.length;
    if (!original(state, startLine, endLine, false)) return false;
    const produced = state.tokens.slice(first);
    if (isRaw(produced)) {
      const nextLine = state.line;
      state.tokens.length = first;
      pushRaw(state, startLine, nextLine);
    }
    return true;
  }, { alt: rule.alt.slice() });
}

function hasTaskItem(tokens) {
  for (let i = 2; i < tokens.length; i++) {
    if (tokens[i].type === 'inline' && tokens[i - 2].type === 'list_item_open' &&
      TASK_ITEM.test(tokens[i].content)) return true;
  }
  return false;
}

export function rawBlockPlugin(md) {
  md.block.ruler.before('table', 'raw_block', (state, startLine, endLine, silent) => {
    if (isIndentedCode(state, startLine)) return false;
    const next = detectRaw(state, startLine, endLine);
    if (next < 0) return false;
    if (!silent) pushRaw(state, startLine, next);
    return true;
  });

  const always = () => true;
  wrapRule(md, 'table', always);
  wrapRule(md, 'hr', always);
  wrapRule(md, 'lheading', always);
  wrapRule(md, 'heading', (tokens) =>
    (tokens[0].tag !== 'h2' && tokens[0].tag !== 'h3') || tokens[1].content.indexOf('![') !== -1);
  wrapRule(md, 'list', hasTaskItem);
}
