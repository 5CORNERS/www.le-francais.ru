// Image destinations as Python-Markdown 2.6 reads them: parentheses do not
// nest, the destination ends at whitespace or at the first unescaped `)`.
// So `![a](/photo%20(1250\).jpg "t")` (written by the legacy editor) is an
// image, and `![a](/photo_(1250).jpg)` stops at `(1250`, as on the server.
// Link destinations keep the CommonMark rules (balanced parentheses), which
// is what the server does for links.
function imageDestination(original, unescapeAll) {
  return (str, start, max) => {
    if (str.charCodeAt(start) === 0x3c /* < */) return original(str, start, max);
    let pos = start;
    while (pos < max) {
      const code = str.charCodeAt(pos);
      if (code <= 0x20 || code === 0x7f || code === 0x29 /* ) */) break;
      pos += code === 0x5c /* \ */ && pos + 1 < max ? 2 : 1;
    }
    if (pos === start) return { ok: false, pos: 0, str: '' };
    return { ok: true, pos, str: unescapeAll(str.slice(start, pos)) };
  };
}

export function pyLinkDestinationPlugin(md) {
  const rule = md.inline.ruler.__rules__.find((r) => r.name === 'image');
  const originalRule = rule.fn;
  const original = md.helpers.parseLinkDestination;
  const forImages = imageDestination(original, md.utils.unescapeAll);
  md.inline.ruler.at('image', (state, silent) => {
    // Restores the previous value: the rule re-enters itself (label parsing).
    const helpers = state.md.helpers;
    const previous = helpers.parseLinkDestination;
    helpers.parseLinkDestination = forImages;
    try {
      return originalRule(state, silent);
    } finally {
      helpers.parseLinkDestination = previous;
    }
  });
}
