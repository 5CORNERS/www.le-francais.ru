# Design Document: Exercise Text Editor (Редактор текстов упражнений)

**Date**: 2026-11-04  
**Author**: Antigravity & User  
**Status**: Draft (Under Review)  
**Target Branch**: `render`

---

## 1. Intent & Problem Statement

### 1.1 The Why
Across the Le-Francais platform, over 1,300 interactive LearningApps exercises are embedded across lessons. Historically, exercise text fields (assignments, hints, compliments) were proofread and tracked ad-hoc (often using green background colors as visual checkboxes). 

To ensure high educational quality, punctuation and grammar correctness, a dedicated, efficient internal administration tool is required to audit and edit exercise text fields across all lessons. The tool must allow rapid side-by-side editing and previewing on large desktop displays (2560x1440), and immediately propagate verified edits to the production static server `files.le-francais.ru`.

### 1.2 User Journey
1. The administrator navigates to `/accounts/admin_commands/exercise-texts/` (protected by `@staff_member_required`).
2. Selects the target field to audit via top tabs: **«Задание (tasktext)»** (default), **«Подсказка (helptext)»**, or **«Комплимент (feedback)»**.
3. Selects a lesson from the dropdown (e.g. Lesson 29).
4. All exercises for that lesson are displayed in a vertical scrollable list.
5. In each exercise card:
   - Left side: HTML source editor with quick formatting buttons (bold, italic, underline, superscript, subscript, and 5 theme-resilient Bootstrap color classes: orange, red, green, blue, sky-blue) and hotkeys (`Ctrl+B`, `Ctrl+I`, `Ctrl+U`, `Ctrl+S`).
   - Right side: Live preview rendering the exact modal dialog used on the live site.
6. When modifications are made, the status badge turns to *«Есть несохранённые правки»* and the **«Сохранить»** button becomes enabled.
7. Pressing `Ctrl+S` (or clicking «Сохранить») sends an asynchronous request to update `index.html` locally and immediately upload it via SFTP to `files.le-francais.ru`. The button reverts to disabled and displays *«Сохранено и отправлено на files ✓»*.

---

## 2. Architecture & Components

### 2.1 Backend Routing & Views
* **Location**: `custom_user` app (alongside `AdminCommands`).
* **Route**: `/accounts/admin_commands/exercise-texts/` in `custom_user/urls.py`.
* **API Route**: `/accounts/admin_commands/exercise-texts/save/` (POST) to handle individual exercise saves.
* **Access Control**: `@staff_member_required` / `user.is_staff`.

### 2.2 Data Source & File Storage
* **Registry**: `home/data/all_learning_apps_table.txt` maps `(lesson, number, app_id)` for all 1,305 exercises. (Tracked in Git to ensure portability across developer environments).
* **Local Exercise Storage**: `home/data/learning_apps_cache/apps/<app_id>/index.html`.
  * Within `index.html`, exercise configuration is serialized as `var AppClientAppData = { ... };`.
  * **Field Mapping**:
    * `tasktext`: read/written directly as `AppClientAppData.tasktext`.
    * `helptext`: read/written directly as `AppClientAppData.helptext`.
    * `feedback`: read from the URL-encoded query string inside `AppClientAppData.initparameters` (`feedback=...`) with fallback to top-level `feedback`. On save, updated in BOTH `initparameters` (URL-encoded) and top-level `AppClientAppData.feedback`, ensuring full compatibility with `AppClientServer.js`.
* **Remote Deployment (SFTP)**:
  * Host: `SFTP_FILES_LE_FRANCAIS_HOSTNAME`
  * Username: `SFTP_FILES_LE_FRANCAIS_USERNAME`
  * Password: `SFTP_FILES_LE_FRANCAIS_PASSWORD`
  * Remote base: `/var/www/www-root/data/www/files.le-francais.ru/learning-apps/<app_id>/index.html`.
  * Remote assets: `/var/www/www-root/data/www/files.le-francais.ru/learning-apps/assets/`.

### 2.3 Environment & Production Guards
* The tool is primarily a local developer workflow tool run on `127.0.0.1:8000` to interactively audit and push live updates directly to `files.le-francais.ru`.
* If accessed in production where `home/data/learning_apps_cache/` is not provisioned, the view safely displays a clear warning banner rather than raising an unhandled 500 error.

### 2.4 CSS & Theme Compatibility
* All exercises in iframe load `../assets/bootstrap.css` and `../assets/LearningApps.css`.
* Colors are applied using Bootstrap contextual text classes rather than inline `color: ...` styles:
  * Оранжевый: `<span class="text-warning">`
  * Красный: `<span class="text-danger">`
  * Зеленый: `<span class="text-success">`
  * Синий: `<span class="text-primary">`
  * Голубой: `<span class="text-info">`
* `home/data/learning_apps_cache/assets/LearningApps.css` is updated with explicit definitions for these 5 classes and synced to the remote server, ensuring vibrant and consistent rendering in both light and dark themes.

### 2.4 Frontend & UI Specifications
* **Screen Estate**: Optimized for 2560x1440 desktop workstation.
* **Top Navigation Bar**:
  * Tab group: `tasktext` / `helptext` / `feedback`. Switching tabs retains unsaved changes in memory and switches all displayed cards to that field.
  * Lesson Selector: Dropdown containing all lessons with count of exercises.
  * Global status & hotkey reminder bar.
* **Exercise Cards (Vertical Scroll)**:
  * Header: Exercise number (e.g. `29.4`), app ID (`pmbcn1vs519`), exercise type, dirty status badge, and individual Save button.
  * Split Grid (1fr 1fr):
    * **Editor Column**:
      * Contextual toolbar:
        * Text formatting: `<b>`, `<i>`, `<u>`, `<sup>`, `<sub>`.
        * Color swatches: 5 compact button squares (warning, danger, success, primary, info) with tooltips.
      * Textarea: Captures input, updates live preview on every keystroke, and listens for hotkeys.
    * **Preview Column**:
      * Canvas wrapper mimicking LearningApps background.
      * White modal card (`.la-modal`) with title corresponding to the active field, rendered HTML content, and standard "OK" button.

---

## 3. Implementation Details

### 3.1 Save Endpoint (`POST /accounts/admin_commands/exercise-texts/save/`)
1. Validates staff credentials.
2. Accepts JSON payload:
   ```json
   {
     "app_id": "pmbcn1vs519",
     "field": "tasktext",
     "value": "Updated HTML string..."
   }
   ```
3. Reads local `home/data/learning_apps_cache/apps/<app_id>/index.html`.
4. Parses `AppClientAppData` JSON using regex `r'var AppClientAppData\s*=\s*(\{.*?\});'`.
5. Updates `AppClientAppData[field] = value`.
6. Writes updated file locally.
7. Connects to SFTP (using cached connection or single-file put) and uploads to `/var/www/www-root/data/www/files.le-francais.ru/learning-apps/<app_id>/index.html`.
8. Returns `{"status": "ok", "app_id": "pmbcn1vs519"}`.

### 3.2 Error Handling & Fallbacks
* If SFTP upload encounters a transient network timeout, the local file remains updated, and the response informs the UI (`"status": "partial_saved", "warning": "Saved locally, SFTP sync failed"`), allowing retry without data loss.

---

## 4. Scope, Constraints & Non-Goals

* **Python Version**: Strictly Python 3.7.16 compatible (no walrus operator, no positional-only arguments).
* **Django/Wagtail**: Django 1.11.29 / Wagtail 2.1 LTS.
* **No Database Migrations Required**: The exercise texts are stored directly in static HTML/JSON files on `files.le-francais.ru` and local cache.
* **Non-Goals**:
  * No bulk auto-translation or spellcheck bot.
  * No modification of non-text exercise logic (e.g. crossword coordinate matrices, ranking pairs).
