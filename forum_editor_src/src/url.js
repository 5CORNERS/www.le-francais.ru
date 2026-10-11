// URL checks shared by the link mark, the link modal and the image modal.

// Whitespace and control characters browsers ignore inside a scheme
// ("java\nscript:" is still javascript:).
const IGNORED = /[\s\x00-\x1F]/g;
const SCHEME = /^([a-z][a-z0-9+.-]*):/i;
const ALLOWED_SCHEMES = ['http', 'https', 'mailto'];

/** Whether `href` may be stored on a link mark: http(s), mailto or a relative URL. */
export function isAllowedHref(href) {
  if (!href) return false;
  const m = String(href).replace(IGNORED, '').match(SCHEME);
  return !m || ALLOWED_SCHEMES.indexOf(m[1].toLowerCase()) >= 0;
}

/**
 * Legacy sanitizeUrl (forum-editor-legacy.js): a URL typed in the link/image
 * modal is kept (trimmed) only if it starts with http:, https:, /, mailto: or #;
 * anything else becomes '#'.
 */
export function sanitizeUrl(url) {
  if (!url) return '#';
  const trimmed = String(url).trim();
  return /^(https?:|\/|mailto:|#)/i.test(trimmed) ? trimmed : '#';
}
