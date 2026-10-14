// Offset helpers for cutting textblocks at a selection edge (code and spoiler
// commands). Kept free of parser/schema imports: keymap.js depends on this
// through spoilerCommands.js and is loaded by schema/index.js.

/** Offset in `node` after dropping whitespace that precedes `offset`. */
export function trimEnd(node, offset) {
  let o = offset;
  while (o > 0 && /\s/.test(node.textBetween(o - 1, o, '', '￼'))) o--;
  return o;
}

/** Offset in `node` after skipping whitespace that follows `offset`. */
export function trimStart(node, offset) {
  let o = offset;
  const size = node.content.size;
  while (o < size && /\s/.test(node.textBetween(o, o + 1, '', '￼'))) o++;
  return o;
}
