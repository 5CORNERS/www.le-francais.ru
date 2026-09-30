# Project Context & Agent Directives: Le-Francais.ru

This document serves as the primary system context for **Antigravity CLI (`agy`)** and other autonomous developer agents working in the `le-francais` repository. Read this file completely before inspecting files or making changes.

---

## 1. Core Metadata & Production Architecture

* **Project**: Le-Francais.ru (Educational French language learning and certification platform).
* **Production Hosting**: Render.com (`render.yaml`, `Dockerfile`).
* **Production Git Branch**: **`render`** (⚠️ **CRITICAL:** The primary production branch is **`render`**, NOT `master` or `main`. All feature branches, diffs, and production pull requests must be based on and targeted to `render`).
* **Default Encoding**: UTF-8 with CRLF line endings on Windows.

---

## 2. Technology Stack & Exact Version Matrix

| Layer | Technology | Exact Version | Notes / Constraints |
|---|---|---|---|
| **Language** | Python | **3.7.16** | **Strict version floor & ceiling.** Python 3.8+ breaks Django 1.11 / Wagtail 2.1 (`collections.abc` changes, C-extension build failures). All code must use Python 3.7 compatible syntax (no `:=` walrus, no `match/case`). |
| **Web Framework** | Django | **1.11.29** | Legacy LTS release (`django >= 1.11.29, < 2.0.0`). |
| **CMS** | Wagtail | **2.1** | Uses `wagtail.core`, `wagtail.admin`. Requires rich-text patch `bin/wagtail_nbsp.patch` applied via `pypatch`. |
| **Primary Database** | PostgreSQL | **16.x** | Database engine: `django.db.backends.postgresql_psycopg2`. Adapter: `psycopg2-binary==2.8.6`. Port: **5433** in local dev. Local cluster uses `-A trust` authentication on `127.0.0.1` to eliminate `scram-sha-256` password negotiation issues with older `psycopg2`. |
| **Secondary Database** | PostgreSQL (`courses`) | **16.x** | Secondary database routing via `COURSES_DATABASE_URL` (`DATABASES['courses']`). |
| **Runtime Manager** | Micromamba | **2.9.x** | Portable conda runner (`tools\bin\micromamba.exe`). Keeps all caches isolated to `tools\mamba_root` via `MAMBA_ROOT_PREFIX`. |
| **Frontend Assets** | Vanilla CSS / JS | Pre-compiled | Compiled static assets are tracked in Git in `static_compiled/`. **No Node.js or Gulp installation is needed for backend Python/template development.** |
| **GeoIP Location** | MaxMind GeoIP2 | `geoip2==3.0.0` | Uses databases `geoip/GeoLite2-City.mmdb` and `geoip/GeoLite2-Country.mmdb`. `le_francais.middleware.GeoIpSessionMiddleware` runs on every request. |
| **Payment Gateway** | Tinkoff Merchant | Custom app | Located in `tinkoff_merchant/`. Requires combined Russian root CA certificates bundle `tinkoff_merchant/certs/combined_ca.pem`. |
| **Audio & TTS** | FFmpeg & Yandex / AWS | Custom apps | `ffmpeg/ffmpeg.exe` appended to PATH by `yandex_speechkit/models.py`. Polly integration in `polly/`. |

---

## 3. Directory Structure & App Responsibilities

```text
le-francais/
├── le_francais/                   # Core Django project configuration
│   ├── settings/
│   │   ├── base.py                # Base project settings, installed apps, middleware, DB definitions
│   │   ├── dev.py                 # Local development settings (DEBUG=True, local caches)
│   │   ├── production.py          # Render production settings
│   │   └── local.py               # Machine-specific developer overrides (gitignored)
│   ├── middleware.py              # GeoIpSessionMiddleware, CourseMiddleware, UserSessionMiddleware
│   ├── urls.py                    # Root URL router
│   └── wsgi.py                    # WSGI entrypoint (gunicorn)
├── home/                          # Main Wagtail CMS models (HomePage, LessonPage, ArticlePage, Blocks)
├── custom_user/                   # Custom User model (custom_user.User), auth pipeline, user profiles
├── conjugation/                   # French verb conjugation engine, tables, formulas, verb search
├── le_francais_dictionary/        # Vocabulary database, flashcard packets, pronunciation audio
├── tinkoff_merchant/              # Tinkoff payment notifications, webhooks, receipts, CA certs
├── forum/ & forum_messages/       # PyBBM-based discussion forum and notifications
├── mass_mailer/                   # Email newsletters and automated student reminder campaigns
├── yandex_speechkit/              # Text-to-speech audio generation via Yandex SpeechKit
├── polly/                         # Text-to-speech audio generation via AWS Polly
├── static_compiled/               # Pre-compiled CSS, JS, and webfonts (served by Whitenoise in dev)
├── geoip/                         # MaxMind GeoLite2-City and Country databases (gitignored)
├── ffmpeg/                        # Portable FFmpeg binary directory (gitignored)
├── tools/                         # Portable Windows development ecosystem (gitignored)
│   ├── bin/micromamba.exe         # Standalone package manager
│   ├── env/                       # Isolated Python 3.7.16 virtual environment
│   ├── pgsql/                     # Standalone PostgreSQL 16 portable binaries
│   ├── data/                      # Local PostgreSQL database cluster (port 5433)
│   ├── mamba_root/                # Isolated micromamba package caches
│   ├── backups/                   # .dir.tar.gz database archives (courses & le_francais)
│   ├── download_tools.ps1         # Downloads & extracts runtime tools
│   ├── encrypt_env.ps1            # AES-256 secrets encryptor
│   ├── decrypt_env.ps1            # AES-256 secrets decryptor (maps DATABASE_URL to 5433)
│   └── generate_certs.py          # Assembles tinkoff_merchant/certs/combined_ca.pem
├── environment.yml                # Locked Python 3.7.16 Conda specification
├── .env.dev.enc                   # AES-256 encrypted development secrets (password: le-francais-dev)
├── setup.bat                      # One-time automated setup wizard
├── start.bat                      # Daily launcher (starts Postgres 5433, starts Django, opens browser)
├── stop.bat                       # Clean database shutdown utility
└── README_WINDOWS_DEV.md          # 3-step assistant quickstart guide
```

---

## 4. How to Execute Commands (Agent Workflow)

### The Golden Rule of Execution
⚠️ **NEVER run `python` or `python.exe` directly.** Unactivated environments on Windows fail to resolve C-extension DLLs located in `tools\env\Library\bin` (causing `ImportError: DLL load failed` for `psycopg2`, `Pillow`, `cryptography`).

**Always run commands through Micromamba:**
```cmd
set MAMBA_ROOT_PREFIX=%~dp0tools\mamba_root
tools\bin\micromamba.exe run -p tools\env python <command>
```
*(In PowerShell: `$env:MAMBA_ROOT_PREFIX = "$pwd\tools\mamba_root"; tools\bin\micromamba.exe run -p tools\env python <command>`)*

### Common Commands

#### 1. Running Django Management Commands
```powershell
$env:MAMBA_ROOT_PREFIX = "$pwd\tools\mamba_root"
tools\bin\micromamba.exe run -p tools\env python manage.py check
tools\bin\micromamba.exe run -p tools\env python manage.py showmigrations
```

#### 2. Running Automated Tests
```powershell
$env:MAMBA_ROOT_PREFIX = "$pwd\tools\mamba_root"
# Test a specific Django app:
tools\bin\micromamba.exe run -p tools\env python manage.py test home
tools\bin\micromamba.exe run -p tools\env python manage.py test custom_user
```

#### 3. Running Django Development Server
```powershell
$env:MAMBA_ROOT_PREFIX = "$pwd\tools\mamba_root"
tools\bin\micromamba.exe run -p tools\env python manage.py runserver 127.0.0.1:8000
```

#### 4. Managing Local PostgreSQL (Port 5433)
```powershell
# Check if PostgreSQL is accepting connections:
tools\pgsql\bin\pg_isready.exe -h 127.0.0.1 -p 5433

# Start PostgreSQL manually:
tools\pgsql\bin\pg_ctl.exe -D tools\data -l tools\postgres.log -o "-p 5433" -w start

# Stop PostgreSQL cleanly:
tools\pgsql\bin\pg_ctl.exe -D tools\data -m fast stop

# Execute SQL query:
tools\pgsql\bin\psql.exe -h 127.0.0.1 -p 5433 -U postgres -d le_francais --pset=pager=off -c "SELECT COUNT(*) FROM auth_user;"
```

---

## 5. Critical Code Conventions & Development Guardrails

1. **Python 3.7 Compatibility:**
   * No `walrus operator` (`:=`).
   * No positional-only parameters (`def func(a, /, b):`).
   * No standard library `importlib.metadata` (use `import importlib_metadata`).
   * No `match/case` statements.
   * Dictionary order cannot be relied upon in older serialization.

2. **Django 1.11 & Wagtail 2.1 Patterns:**
   * **Foreign Keys:** Always provide explicit `on_delete` parameters (`models.CASCADE`, `models.SET_NULL`, `models.PROTECT`).
   * **Wagtail Page Panels:** Wagtail 2.x panel definitions live in `wagtail.admin.edit_handlers` (`StreamFieldPanel`, `FieldPanel`, `MultiFieldPanel`).
   * **Reverse URLs:** Many apps use namespaces (e.g. `reverse('tinkoff:payment_result_page_success')`, `reverse('pybb:forum_topic_list')`).

3. **Database Baseline & Migrations:**
   * **Do NOT run `manage.py migrate` on clean installs.** The development databases are restored from verified PostgreSQL directory dumps in `tools\backups\` using `pg_restore.exe`.
   * Only create new migrations (`makemigrations <app_name>`) when modifying models as part of a task.

4. **Secrets & Environment:**
   * `.env` is loaded automatically by `settings/base.py` via `python-dotenv`.
   * In local development, `DATABASE_URL` must point to `postgres://postgres@127.0.0.1:5433/le_francais`.
   * Never commit `.env` or plaintext API secrets to Git.

5. **Source Control & Git Mandates:**
   * **Target branch is `render`.**
   * Never stage or commit changes without explicit instructions from the user.
   * Never use `git add .` or `git add -A`. Only stage the specific modified or created files.
