# Foreign OAuth Restriction Modal Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement a restriction modal and JS interception for Google and Facebook login buttons for users from RU (Russia) based on geoip country code on the Django login page.

**Architecture:** We will modify `home/templates/account/login.html` to add the Bootstrap modal markup and insert JS code that intercepts clicks on `.btn-google, .btn-facebook` elements. The interception logic is conditional on `request.session.geoip.country_code == 'RU'`.

**Tech Stack:** Django Templates, Bootstrap 4, Custom JavaScript.

---

### Task 1: Add Bootstrap Modal and JS Click Interceptor to Login Page

**Files:**
- Modify: `home/templates/account/login.html`

- [ ] **Step 1: Add the Bootstrap Modal to the login template**
Add the modal markup at the bottom of the template before `{% endblock %}` in `home/templates/account/login.html`.

- [ ] **Step 2: Add JavaScript to intercept clicks conditionally**
Add JS logic wrapped in `{% if request.session.geoip.country_code == 'RU' %}` to intercept clicks on `.btn-google` and `.btn-facebook` and display `#foreignAuthModal`.

- [ ] **Step 3: Run django check to verify template syntax**
Run: `C:\Users\anton\miniconda3\envs\le-francais\python.exe manage.py check`
Expected output: System check identified 16 issues (or similar warnings, no critical errors).

- [ ] **Step 4: Commit changes**
Run: `git add home/templates/account/login.html` and commit with message "feat: add modal to restrict foreign OAuth for RU IPs".
