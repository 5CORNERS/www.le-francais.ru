# Ignored Words postMessage Listener Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a `postMessage` listener to the dictionary table to allow the parent window to trigger "Add to Ignored" and "Remove from Ignored" actions.

**Architecture:** We will add a `message` event listener to the `window` object in `le_francais_dictionary/static/dictionary/js/user-table.js`. This listener will check for specific actions and trigger existing button click handlers.

**Tech Stack:** JavaScript, jQuery.

---

### Task 1: Add Message Listener to user-table.js

**Files:**
- Modify: `le_francais_dictionary/static/dictionary/js/user-table.js`

- [ ] **Step 1: Add the window message listener**

In `le_francais_dictionary/static/dictionary/js/user-table.js`, find the `$(document).ready` block. Near the end of this block, add the message listener.

```javascript
    window.addEventListener('message', function (event) {
        if (getCrossSiteKey()) {
            if (event.data.action === 'addIgnored') {
                $('#markWords').click();
            } else if (event.data.action === 'removeIgnored') {
                $('#unmarkWords').click();
            }
        }
    });
```

- [ ] **Step 2: Commit changes**

```bash
git add le_francais_dictionary/static/dictionary/js/user-table.js
git commit -m "feat: add postMessage listener for add/remove ignored actions"
```

---

### Task 2: Update Minified JS

**Files:**
- Modify: `le_francais_dictionary/static/dictionary/js/user-table.min.js`
- Modify: `le_francais_dictionary/static/dictionary/js/user-table.map`

- [ ] **Step 1: Regenerate minified file and source map**

Run `uglifyjs` from the directory containing the file.

```bash
cd le_francais_dictionary/static/dictionary/js/
uglifyjs user-table.js -o user-table.min.js --source-map "root='',url=user-table.map,filename=user-table.min.js"
```

- [ ] **Step 2: Commit changes**

```bash
git add le_francais_dictionary/static/dictionary/js/user-table.min.js le_francais_dictionary/static/dictionary/js/user-table.map
git commit -m "chore: update minified user-table.min.js for postMessage listener"
```
