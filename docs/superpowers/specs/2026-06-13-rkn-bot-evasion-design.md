# Design Spec: Roskomnadzor (RKN) / GRFC Bot Evasion for Foreign OAuth (Advanced Evasion)

## Overview
Automated scanners and crawlers used by Russian regulators (Roskomnadzor/GRFC) routinely check public pages for forbidden or fined functionality, such as foreign OAuth systems (Google, Facebook). Rather than blocking known IP addresses (which is fragile, incomplete, and easily bypassed using commercial hosting/residential proxies), we will implement a multi-layered interaction-based dynamic injection system using AJAX and Backend proxying.

To any automated scanner that does not execute realistic user interactions, the Google and Facebook OAuth buttons will simply **not exist in the DOM or the source code**. When a real human visits the page and performs any standard interaction (moving the mouse, scrolling, pressing a key, or touching a screen), the buttons are fetched via AJAX from the backend on-demand and seamlessly injected.

## 1. On-Demand AJAX Button Delivery (Level 1 & 2)
Instead of embedding the buttons or the button HTML inside static frontend scripts (which can be read via static code analysis), we will query a dedicated, generic-looking backend endpoint: `/accounts/login/options/`.
- This endpoint will render `oauth-buttons.html` with a special context variable `force_render=True`.
- It will deliver the actual HTML of Google, Facebook, VK, Mail.ru, and Yandex buttons only to active, human-triggered sessions.

## 2. Shared `oauth-buttons.html` Evasion Template
- On normal page load, if the user is in Russia (`request.session.geoip.country_code == 'RU'`) and `force_render` is NOT active:
  - Google and Facebook buttons are omitted entirely from the server HTML.
  - An inline, anonymous JS script is rendered.
  - The script has **no** references to "google", "facebook", or "oauth". It only contains a `fetch('/accounts/login/options/')` URL.
  - When the first user-interaction (mousemove, scroll, keydown, touchstart) is detected, the listeners are unbound, and the fetch is initiated.
  - The resulting HTML replaces the initial `.oauth-buttons-row` container with the full, original social buttons list.
- Outside of Russia or when `force_render` is active:
  - All buttons render statically as normal.
  - The script block is not rendered.

## 3. Registering the URL Routing and Views
- Register `/accounts/login/options/` in `custom_user/urls.py` leading to `custom_user/views.py:login_options`.
- Implement `login_options` in `custom_user/views.py`.
