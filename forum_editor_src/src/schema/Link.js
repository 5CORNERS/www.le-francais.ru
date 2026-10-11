import Link from '@tiptap/extension-link';

// Same as the stock Link, but href is rendered first
// (<a href target rel>) to match the legacy DOM attribute order.
export const ForumLink = Link.extend({
  renderHTML(props) {
    const [tag, attrs, hole] = this.parent(props);
    const { href, ...rest } = attrs;
    return [tag, { href, ...rest }, hole];
  },
}).configure({
  openOnClick: false,
  HTMLAttributes: { target: '_blank', rel: 'noopener' },
});
