# Message Listener Origin Validation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add origin validation to the `message` listener in `user-table.js` to only accept messages from `COURSES_BASE_URL`.

**Architecture:** Wrap existing message handling logic with a check against `event.origin`.

**Tech Stack:** JavaScript (jQuery)

---

### Task 1: Update Message Listener in user-table.js

**Files:**
- Modify: `le_francais_dictionary/static/dictionary/js/user-table.js:744-752`

- [ ] **Step 1: Replace the existing message listener with the version including origin validation**

```javascript
    window.addEventListener('message', function (event) {
        // Verify origin
        const trustedOrigin = typeof COURSES_BASE_URL !== 'undefined' && COURSES_BASE_URL ? COURSES_BASE_URL : null;
        if (trustedOrigin) {
            try {
                if (event.origin !== new URL(trustedOrigin).origin) {
                    return;
                }
            } catch (e) {
                console.error('Invalid COURSES_BASE_URL:', trustedOrigin);
                return;
            }
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

- [ ] **Step 2: Verify the change manually**
Since I cannot run a browser, I will ensure the code is syntactically correct and matches the requirement.

- [ ] **Step 3: Commit the change**

```bash
git add le_francais_dictionary/static/dictionary/js/user-table.js
git commit -m "security: add origin validation to message listener in user-table.js"
```
