# Migration Guide: Django, Wagtail, and Python Upgrade

This document outlines the step-by-step process for upgrading the project from its current state (Django 1.11, Wagtail 2.1, Python 3.9) to the latest stable versions as of early 2026.

## 1. Current State Assessment (March 2026)

*   **Python:** 3.9.16
*   **Django:** 1.11.29 (End of Life)
*   **Wagtail:** 2.1 (End of Life)
*   **Database:** PostgreSQL (psycopg2-binary 2.8.6)
*   **Frontend:** Node 14.x (End of Life)

## 2. Target Architecture

*   **Python:** 3.14.x
*   **Package Manager:** `uv` (Replacing `pip` and `requirements.txt`)
*   **Linting/Formatting:** `ruff` (Replacing `flake8`, `isort`, `black`)
*   **Django:** 6.0.x (Latest Stable) or 5.2 (LTS)
*   **Wagtail:** 7.3.x (Latest Stable) or 7.0 (LTS)
*   **Hosting:** Render.com (Native Python Service, abandoning Heroku legacy stack)

---

## 3. Phase 1: Preparation & Tooling

### 3.1. Infrastructure & Environment Setup
Before touching code, establish a "Safe Harbor" environment to prevent local machine pollution.
*   **Version Management:** Install `uv`. It will handle Python version management (replacing `pyenv`) and virtual environments.
    ```bash
    uv python install 3.11 3.12 3.14
    ```
*   **Abandoning Heroku Stack:** The current setup uses a `Dockerfile` that mimics Heroku's "v4-heroku-20" stack. This is deprecated and bloated.
    *   **Action:** Plan to move to a native Render "Python" environment or a standard, slim `python:3.14-slim` Docker image.
    *   **Env Vars:** Migrate all `envVars` from `render.yaml` to the Render Dashboard or a modern `render.yaml` that doesn't rely on the `heroku-import` plugin.
*   **Branching Strategy:** Use a "Long-Lived Migration Branch" (`feature/major-upgrade`). Merge `master` into this branch frequently to avoid massive merge conflicts later.

### 3.2. Deep Dependency Audit & `uv` Migration
The project has several git-based and niche dependencies that are high-risk.
*   **`uv` Initialization:**
    ```bash
    uv init
    uv add $(cat requirements.txt)
    ```
*   **Audit Tools:** 
    *   `uv tree`: Visualize dependencies and conflicts.
    *   `pip-audit`: Check for known security vulnerabilities.
*   **Git-based Dependencies:** 
    *   `pybbm`, `django-recaptcha3`, `django-pure-pagination`, `bayoo-docx`. 
    *   **Action:** Check if these forks are still necessary. Django 3.x+ added many features that previously required forks.
*   **Redundant Packages:**
    *   `django-bulk-update`: Redundant as of Django 2.2 (`bulk_update()` added to ORM).
    *   `six`: Redundant once you drop Python 2 support.
    *   `django-npm`: Consider if a simple `package.json` with a build script is more maintainable.

### 3.3. Automated Migration & Quality Tools
Automate the "grunt work" to focus on architectural changes.
*   **`django-upgrade`:** This is your primary tool. Run it sequentially:
    ```bash
    uv run django-upgrade --target-version 2.0 [files...]
    uv run django-upgrade --target-version 3.0 [files...]
    ```
*   **`django-migration-linter`:** Use this to detect migrations that might break during the upgrade.
*   **`ruff`:** Your all-in-one linter and formatter.
    ```bash
    uv add --dev ruff
    uv run ruff check --fix
    uv run ruff format
    ```
    Enable Django-specific rules (`DJ`) in `pyproject.toml`.

---

## 4. Phase 2: Incremental Upgrade Path

**CRITICAL:** Do NOT skip major versions. Upgrade incrementally, run migrations, and pass all tests at each step. Each step below assumes you are running `python manage.py makemigrations` and `python manage.py migrate` upon completion.

### Step 1: Django 1.11 -> 2.2 LTS (Wagtail 2.1 -> 2.11)
*   **Python Support:** Python 3.9 is the ceiling here.
*   **Django Breaking Changes:**
    *   **`on_delete` is now mandatory:** Every `ForeignKey` and `OneToOneField` must have an explicit `on_delete` argument (e.g., `models.CASCADE`, `models.SET_NULL`). Use `grep` or `django-upgrade` to find missing ones.
    *   **URL Syntax:** `django.conf.urls.url()` is deprecated in favor of `django.urls.path()` and `re_path()`. Note: `path()` does not use regex; use `re_path()` if you need to keep regex logic.
    *   **Middlewares:** Ensure `MIDDLEWARE` is used instead of `MIDDLEWARE_CLASSES` (already implemented in this project).
    *   **`is_authenticated` / `is_anonymous`:** These are now properties, not methods. `user.is_authenticated()` will fail; use `user.is_authenticated`.
*   **Wagtail Breaking Changes:**
    *   `wagtail.wagtailcore` imports are deprecated in favor of `wagtail.core`.
    *   Update `WAGTAILSEARCH_BACKENDS` if using Elasticsearch (version compatibility).
*   **Common Pitfalls:** Third-party apps like `pybbm` and `django-allauth` must be bumped to versions supporting Django 2.2.

### Step 2: Django 2.2 -> 3.2 LTS (Wagtail 2.11 -> 2.16)
*   **Python Support:** Python 3.9 is still compatible.
*   **Django Breaking Changes:**
    *   **Translation Functions:** `ugettext`, `ugettext_lazy`, `ungettext`, etc., are removed. Replace with `gettext`, `gettext_lazy`, `ngettext`.
    *   **JSONField:** `django.contrib.postgres.fields.JSONField` is deprecated. Use the new cross-database `django.db.models.JSONField`.
    *   **Signal Arguments:** Many signals have changed their providing arguments.
*   **Wagtail Breaking Changes (The "Big Jump" to 2.16):**
    *   **Import Overhaul:** This is the last version before Wagtail 3.0's massive import flattening. Start preparing by moving from `wagtail.core` to `wagtail`.
    *   **StreamField:** New `BlockQuoteBlock` and changes to how `StreamValue` is handled in templates.
*   **Common Pitfalls:** `django-allauth` versions 0.40.0+ are required. Check `django-comments-xtd` compatibility.

### Step 3: Django 3.2 -> 4.2 LTS (Wagtail 2.16 -> 5.2)
*   **Python Support:** **UPGRADE Python to 3.11** before starting this step.
*   **Django Breaking Changes:**
    *   **Timezones:** `pytz` is deprecated. Django now uses the standard library's `zoneinfo`. Update `USE_DEPRECATED_PYTZ = False` in settings.
    *   **CSRF_TRUSTED_ORIGINS:** This setting now requires the protocol (e.g., `['https://www.le-francais.ru']`).
    *   **`request.is_ajax()`:** Removed. Check for `request.headers.get('x-requested-with') == 'XMLHttpRequest'`.
*   **Wagtail Breaking Changes (Wagtail 3.0, 4.0, 5.0):**
    *   **The Flat Import Path:** `wagtail.core.models` -> `wagtail.models`. This will break almost every file using Wagtail. Use a global search-and-replace.
    *   **New Admin UI:** The admin underwent a massive redesign. Custom admin templates or CSS will likely break.
    *   **`StreamField` Migration:** `StreamField` now requires a `use_json_field=True` argument.
*   **Common Pitfalls:** `psycopg2` should be swapped for `psycopg[c]` (psycopg 3) or ensure `psycopg2-binary` is at least 2.9+.

### Step 4: Django 4.2 -> 5.2 LTS (Wagtail 5.2 -> 7.0)
*   **Python Support:** **UPGRADE Python to 3.12 or 3.13.**
*   **Django Breaking Changes:**
    *   **GeneratedField:** You can now move logic from `save()` methods to the database level using `models.GeneratedField`.
    *   **Database Defaults:** New support for database-level default values.
    *   **Removed Features:** Final removal of many 4.x deprecations.
*   **Wagtail Breaking Changes (Wagtail 6.0, 7.0):**
    *   **LTS Stability:** Wagtail 7.0 is an LTS version. It focuses on stability and accessibility.
    *   **Python 3.10+:** Support for older Python versions is dropped.
*   **Common Pitfalls:** Ensure `django-storages` and `boto3` are updated to support new AWS signature versions.

### Step 5: Django 5.2 -> 6.0 (Wagtail 7.0 -> 7.3)
*   **Python Support:** **UPGRADE Python to 3.14.** This is the latest stable target.
*   **Django Breaking Changes:**
    *   Django 6.0 is the "bleeding edge." Check the official release notes for the removal of features deprecated in 5.1/5.2.
*   **Wagtail Breaking Changes:**
    *   Wagtail 7.3 provides the best compatibility for Django 6.0 and Python 3.14 features like improved typing support.
*   **Common Pitfalls:** Many niche third-party apps may not yet officially support Django 6.0. This is the stage to contribute fixes or find alternatives.

---

## 5. Phase 3: Code Refactoring & Best Practices

### 5.1. Authentication & Social Auth
*   Upgrade `django-allauth` and `social-auth-app-django` to their latest versions.
*   The `SOCIAL_AUTH_PIPELINE` may need adjustments for newer `social-core` versions.

### 5.2. Wagtail Modernization
*   Update `StreamField` definitions to the new block-based syntax.
*   Review `wagtail_hooks.py` for API changes in the admin interface.
*   Check template tags: `{% load wagtailcore_tags %}` becomes `{% load wagtail_tags %}`.

### 5.3. Frontend & Static Files
*   Upgrade Node.js to 20.x+ and npm.
*   Evaluate replacing `django-npm` with a modern build tool (Vite or Webpack) if needed, although `whitenoise` handles serving well.

---

## 6. Phase 4: Testing & Deployment

### 6.1. Migration Validation
*   Run `python manage.py makemigrations` and `python manage.py migrate` at every step.
*   **Data Integrity:** Pay special attention to migrations involving `JSONField` and `StreamField`.

### 6.2. CI/CD Integration
*   Update `.render-buildpacks.json`, `Dockerfile`, and `render.yaml` to reflect new Python/Node versions.
*   Update `runtime.txt` and `requirements.txt`.

### 6.3. Rollback Plan
*   Always take a full database backup before each major version bump.
*   Keep the old environment available for comparison.

---

## 7. Immediate Actions
1.  **Bump Python to 3.11** as a baseline (supported by both Django 1.11 and 4.2).
2.  **Run `django-upgrade --target-version 2.2`** to handle the first wave of syntax changes.
3.  **Audit the `custom_user` app** as it is the core of the authentication system and most sensitive to Django upgrades.

---

## 8. Critical Path Test Plan
... (rest of Section 8) ...

---

## 9. Modernizing the `bin/` Folder

The current `bin/` scripts are tailored for Heroku's build lifecycle. They must be modernized:

### 9.1. `bin/post_compile`
*   **Current Role:** Installs niche packages manually, deletes `static_src`, and patches Wagtail.
*   **New Role:** This logic should be moved to a `build.sh` script for Render or a clean `Dockerfile`.
*   **UV Migration:** Any `pip install` commands here (like `django-session-header`) must be added to `pyproject.toml` via `uv add`.

### 9.2. `bin/send_auto_messages.sh`
*   **Current Role:** Likely a wrapper for a cron job.
*   **Action:** Update to use `uv run python manage.py ...` and ensure compatibility with Render's "Cron Jobs" service type.

### 9.3. `bin/wagtail_nbsp.patch`
*   **Action:** Investigate the source of this patch. Modern Wagtail (5.0+) has significantly improved rich text handling. The goal is to **remove this patch** by implementing the logic via Wagtail's `register_rich_text_features` hook if still necessary.
