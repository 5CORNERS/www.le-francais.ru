# Mobile Verb Comment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Enable the "verb-article-comment" section to be visible in the dictionary translation on mobile devices.

**Architecture:** Remove CSS display:none restrictions for mobile/touch and update JS comments.

**Tech Stack:** CSS, JavaScript

---

### Task 1: Update CSS to allow mobile visibility

**Files:**
- Modify: `conjugation/static/conjugation/css/dictionary.css`

- [ ] **Step 1: Remove mobile display:none for .verb-article-comment**

Remove the following block from `conjugation/static/conjugation/css/dictionary.css` (approx lines 342-346):
```css
@media (max-width: 768px) {
    .verb-article-comment {
        display: none !important;
    }
}
```

- [ ] **Step 2: Remove touch pointer display:none for .verb-article-comment**

Remove the following block from `conjugation/static/conjugation/css/dictionary.css` (approx lines 347-351):
```css
@media (pointer: coarse) {
    .verb-article-comment {
        display: none !important;
    }
}
```

### Task 2: Update JS comment for clarity

**Files:**
- Modify: `conjugation/static/conjugation/js/dictionary.js`

- [ ] **Step 1: Update comment in renderDictionary**

Change the comment at line 472 from:
```javascript
    // 5. Postscript Comment (Desktop only, shown at the very end of section)
```
to:
```javascript
    // 5. Postscript Comment (Shown at the very end of section)
```
