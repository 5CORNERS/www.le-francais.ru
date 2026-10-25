# Fix Origin Validation Security Issue Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Update the `message` event listener in `user-table.js` to "fail closed" if `COURSES_BASE_URL` is missing or invalid, preventing unauthorized cross-origin messages.

**Architecture:** Modify the origin validation logic to return immediately if `COURSES_BASE_URL` is not defined or is an invalid URL. This replaces the current logic that "fails open" when the variable is missing.

**Tech Stack:** JavaScript (jQuery environment)

---

### Task 1: Update Origin Validation Logic

**Files:**
- Modify: `le_francais_dictionary/static/dictionary/js/user-table.js`

- [ ] **Step 1: Replace the current message listener logic**

The current logic (lines 620-639) needs to be replaced with the "fail closed" implementation.

```javascript
    window.addEventListener('message', function (event) {
        const trustedOriginUrl = typeof COURSES_BASE_URL !== 'undefined' && COURSES_BASE_URL ? COURSES_BASE_URL : null;
        if (!trustedOriginUrl) { // Fail closed if no trusted origin is configured
            return;
        }
        try {
            if (event.origin !== new URL(trustedOriginUrl).origin) {
                return;
            }
        } catch (e) {
            return; // Fail closed on invalid URL
        }

        if (event.data && typeof event.data === 'object' && getCrossSiteKey()) {
            if (event.data.action === 'addIgnored') {
                $('#markWords').click();
            } else if (event.data.action === 'removeIgnored') {
                $('#unmarkWords').click();
            }
        }
    });
```

- [ ] **Step 2: Commit the change**

```bash
git add le_francais_dictionary/static/dictionary/js/user-table.js
git commit -m "security: fail closed on origin validation in message listener"
```
