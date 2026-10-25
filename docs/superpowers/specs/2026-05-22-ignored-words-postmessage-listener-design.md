# Design Spec: Ignored Words postMessage Listener

## Context
The parent window needs to be able to trigger "Add to Ignored" and "Remove from Ignored" actions within the dictionary iframe. It does this by sending `postMessage` calls with `action: 'addIgnored'` and `action: 'removeIgnored'`.

## Architecture & Data Flow
- We will modify `le_francais_dictionary/static/dictionary/js/user-table.js`.
- A global `message` event listener will be added to the `window` object.
- The listener will only execute logic if `getCrossSiteKey()` returns a truthy value, ensuring this behavior is restricted to standalone/iframe usage.
- When an `addIgnored` action is received, it will trigger the click event on the `#markWords` button.
- When a `removeIgnored` action is received, it will trigger the click event on the `#unmarkWords` button.

## Payload Handling
The listener will expect a message object:
```json
{
  "action": "addIgnored" | "removeIgnored"
}
```

## Modifications
**File: `le_francais_dictionary/static/dictionary/js/user-table.js`**
Inside `$(document).ready`, add:
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

## Minification
The change will be synced to `le_francais_dictionary/static/dictionary/js/user-table.min.js` using `uglifyjs`.
