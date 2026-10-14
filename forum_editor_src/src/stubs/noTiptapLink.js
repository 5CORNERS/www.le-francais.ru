// Build-time stand-in for @tiptap/extension-link (see build.mjs). StarterKit
// imports it statically, but the forum configures `link: false` and uses its
// own mark (schema/Link.js), so this keeps linkifyjs out of the bundle.
export const Link = null;
export default null;
