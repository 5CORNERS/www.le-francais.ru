// pymdown caret: ^^text^^ -> underline_open / underline_close tokens.
export function underlinePlugin(md) {
  md.inline.ruler.before('emphasis', 'underline', (state, silent) => {
    const start = state.pos;
    const src = state.src;
    if (src.charCodeAt(start) !== 0x5e || src.charCodeAt(start + 1) !== 0x5e) return false;
    const contentStart = start + 2;
    if (contentStart >= state.posMax || /\s/.test(src.charAt(contentStart))) return false;
    let end = src.indexOf('^^', contentStart);
    while (end !== -1 && end < state.posMax) {
      if (end > contentStart && !/\s/.test(src.charAt(end - 1))) break;
      end = src.indexOf('^^', end + 1);
    }
    if (end === -1 || end >= state.posMax) return false;

    if (!silent) {
      const oldMax = state.posMax;
      state.pos = contentStart;
      state.posMax = end;
      state.push('underline_open', 'u', 1).markup = '^^';
      state.md.inline.tokenize(state);
      state.push('underline_close', 'u', -1).markup = '^^';
      state.pos = start;
      state.posMax = oldMax;
    }
    state.pos = end + 2;
    return true;
  });
  md.renderer.rules.underline_open = () => '<u>';
  md.renderer.rules.underline_close = () => '</u>';
}
