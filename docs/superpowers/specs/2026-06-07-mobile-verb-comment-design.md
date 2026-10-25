# Design Spec: Show Verb Article Comment on Mobile

Enable the "verb-article-comment" section to be visible in the dictionary translation on mobile devices, matching its desktop behavior.

## Current State
- The JavaScript `renderDictionary` function appends the comment to the container regardless of platform.
- CSS rules in `dictionary.css` explicitly hide the `.verb-article-comment` element when the screen width is less than 768px or when using a coarse pointer (touch device).
- A comment in the JavaScript code incorrectly states that this section is "Desktop only".

## Proposed Changes

### CSS Update (`conjugation/static/conjugation/css/dictionary.css`)
Remove the media queries and pointer-based rules that hide the comment:
```css
/* Remove these blocks */
@media (max-width: 768px) {
    .verb-article-comment {
        display: none !important;
    }
}
@media (pointer: coarse) {
    .verb-article-comment {
        display: none !important;
    }
}
```

### JavaScript Update (`conjugation/static/conjugation/js/dictionary.js`)
Update the comment at the end of `renderDictionary` to remove the desktop-only restriction note.

## Verification Plan
1. Open the dictionary section on a desktop browser.
2. Verify the comment is visible.
3. Use browser developer tools to simulate a mobile device (e.g., iPhone or Pixel).
4. Verify the comment is now visible at the bottom of the translation section.
5. Check if the styling (border, background, padding) remains consistent and readable on smaller screens.
