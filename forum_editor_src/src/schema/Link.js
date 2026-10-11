import { Mark } from '@tiptap/core';
import { isAllowedHref } from '../url.js';

// A plain link mark: no autolink, no link-on-paste, no click handling (the
// server has no magiclink, so the editor must not create links by itself).
// Rendered as <a href target rel> to match the legacy DOM attribute order.
export const ForumLink = Mark.create({
  name: 'link',
  inclusive: false,
  addAttributes() {
    return {
      href: { default: null, rendered: false },
      // Markdown `[t](url "title")`; kept so a round trip doesn't drop it.
      title: { default: null, rendered: false },
    };
  },
  parseHTML() {
    return [
      {
        tag: 'a[href]',
        getAttrs: (dom) => {
          const href = dom.getAttribute('href');
          return isAllowedHref(href) ? { href: href, title: dom.getAttribute('title') } : false;
        },
      },
    ];
  },
  renderHTML({ mark }) {
    const href = isAllowedHref(mark.attrs.href) ? mark.attrs.href : '';
    return ['a', { href: href, target: '_blank', rel: 'noopener' }, 0];
  },
});
