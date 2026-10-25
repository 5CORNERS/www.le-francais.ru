# Windows Portable Dev Environment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Provide an automated, zero-install, hardened local development environment for `le-francais` on Windows (Python 3.7.16 via Micromamba, portable PostgreSQL 15, automated downloads, secrets decryption, pre-existing database backup restoration with catastrophic data loss prevention, and 1-click launchers).

**Architecture:** A standalone `tools/` ecosystem where `micromamba.exe` creates an isolated Python 3.7 environment in `tools/env/`, portable PostgreSQL 15 runs in user space on port 5433, `.env.dev.enc` provides encrypted credentials, database backups from PostgreSQL 15.17 are extracted into timestamped folders and restored using portable `pg_restore.exe` guarded by a `.restore_complete` lockfile with flat `goto` control flow to eliminate CMD parse-time variable expansion bugs, and batch wrappers bypass PowerShell restrictions and use `micromamba run` for complete DLL resolution.

**Tech Stack:** Windows Batch (`.bat`), PowerShell 5.1+, Windows native `tar.exe`, Micromamba, Portable PostgreSQL 15 (EnterpriseDB binaries), `pg_restore`, Python 3.7.16, Django 1.11, Wagtail 2.1, AES-256 PowerShell cryptography.

**Spec:** `docs/superpowers/specs/2026-09-26-windows-portable-dev-environment-design.md`

## Global Constraints

- Must run on standard Windows 10/11 64-bit with zero prior developer tooling.
- All batch scripts must begin with `cd /d "%~dp0"` to guarantee the correct working directory.
- All PowerShell scripts must resolve `$RepoRoot = Split-Path $PSScriptRoot -Parent`.
- All PowerShell invocations from batch files must use `-NoProfile -ExecutionPolicy Bypass`.
- Portable PostgreSQL must be version 15+ to match the Debian 15.17 dump version.
- `initdb.exe` MUST use `-A trust` (`-U postgres -A trust -E UTF-8 -D tools\data`) to avoid `scram-sha-256` authentication negotiation failures with legacy `psycopg2-binary==2.8.6`.
- `setup.bat` must guard database restore with `%~dp0tools\data\.restore_complete` using a flat `goto skip_restore` structure to completely eliminate CMD parse-time `%ERRORLEVEL%` parenthesized expansion bugs.
- All extracted archives (Micromamba `.tar.bz2`, EnterpriseDB PostgreSQL `.zip`, FFmpeg `.zip`, and DB backups `.tar.gz`) must be extracted using native `tar.exe` (or `Expand-Archive` for zip) into temporary/staging directories where necessary, flattened, and moved to their final destinations.
- Pre-create all destination directories explicitly (`New-Item -ItemType Directory -Force`) before calling `tar.exe -xf ... -C <dir>` because native `tar.exe` crashes if the target directory does not exist.
- `setup.bat` must track `%DB_ALREADY_RUNNING%` via `pg_isready`: only start Postgres if stopped, and only stop Postgres if `setup.bat` itself started it.
- PostgreSQL temporary startups must use `-w` (wait) to prevent race conditions during DB creation and restore.
- Stale PID cleanup must use `pg_isready` exit code logic.
- All Python commands must use `tools\bin\micromamba.exe run -p tools\env ...`.

## Review Focus

1. **CMD parse-time expansion trap:** Avoid parenthesized `if (...) else (...)` blocks around dynamic `%ERRORLEVEL%` and `%DB_ALREADY_RUNNING%` sets; use flat `goto skip_restore`.
2. **Catastrophic data loss prevention:** Re-running `setup.bat` on an existing installation must detect `tools\data\.restore_complete` and jump to `:skip_restore`.
3. **`tar.exe` destination directory creation:** Target folders for database archives (`tools\backups\2026-05-29T13_46Z` and `tools\backups\2026-05-29T13_45Z`) must be created with `New-Item -Force` prior to invoking `tar.exe -xf`.
4. **Authentication compatibility (`-A trust`):** PostgreSQL 15 defaults to `scram-sha-256`, which breaks `psycopg2 2.8.6`; local cluster must be initialized with `-A trust`.
5. **PostgreSQL 15 binary compatibility:** Dumps are format 15.17; portable PostgreSQL must be version 15.x so `pg_restore` does not reject the dump version.

---

### Task 1: Python 3.7 Conda Specification (`environment.yml`)

**Files:**
- Create: `environment.yml`
- Test: Parse and validate package consistency against working environment export

**Interfaces:**
- Produces: `environment.yml` containing Python 3.7.16 and exact pinned pip dependencies (`django==1.11.29`, `wagtail==2.1`, `psycopg2-binary==2.8.6`, `Pillow==5.4.1`, `pypatch==1.0.2`, etc.).

- [ ] **Step 1: Create `environment.yml`**
Extract dependencies from the verified local `le-francais` conda environment into a clean, reproducible `environment.yml` format with `channels: [defaults, conda-forge]` and pip section. Include `pypatch==1.0.2` and all required forks (`pybbm`, `bayoo-docx`, `django-recaptcha3`, `django-pure-pagination`, `py3-validate-email`, `django-bootstrap4`).

- [ ] **Step 2: Validate `environment.yml` syntax**
Run PowerShell script to verify YAML syntax and validate that core packages (`python=3.7.16`, `django==1.11.29`, `wagtail==2.1`, `psycopg2-binary==2.8.6`) are properly defined:
```powershell
powershell -Command "if ((Get-Content environment.yml) -match 'python=3.7.16' -and (Get-Content environment.yml) -match 'psycopg2-binary==2.8.6') { Write-Host 'VALID' } else { throw 'INVALID' }"
```
Expected: `VALID`

- [ ] **Step 3: Commit**
```bash
git add environment.yml
git commit -m "chore: add locked environment.yml for Python 3.7 Windows dev"
```

---

### Task 2: Encrypted Secrets Tooling (`tools/encrypt_env.ps1` & `tools/decrypt_env.ps1`)

**Files:**
- Create: `tools/encrypt_env.ps1`
- Create: `tools/decrypt_env.ps1`
- Create: `tools/tests/test_crypto.ps1`

**Interfaces:**
- Produces: `tools/encrypt_env.ps1` (takes `.env`, outputs `.env.dev.enc`).
- Produces: `tools/decrypt_env.ps1` (takes password, outputs `.env` with `DATABASE_URL` configured for port 5433).
- Uses `$RepoRoot = Split-Path $PSScriptRoot -Parent` for all file resolution.

- [ ] **Step 1: Write test for encryption/decryption roundtrip**
Create `tools/tests/test_crypto.ps1` that creates a dummy `.env.test`, encrypts it using `tools/encrypt_env.ps1`, decrypts it using `tools/decrypt_env.ps1`, and asserts content equivalence.

- [ ] **Step 2: Run test to verify it fails**
Run: `powershell -NoProfile -ExecutionPolicy Bypass -File tools/tests/test_crypto.ps1`
Expected: FAIL (scripts not found).

- [ ] **Step 3: Implement AES-256 encryption in `tools/encrypt_env.ps1`**
Use `System.Security.Cryptography.AesManaged` and `System.Security.Cryptography.Rfc2898DeriveBytes` (PBKDF2 with SHA-256 and 100,000 iterations, random salt). Resolve paths via `$RepoRoot`. Output to `$RepoRoot\.env.dev.enc`.

- [ ] **Step 4: Implement AES-256 decryption in `tools/decrypt_env.ps1`**
Read `$RepoRoot\.env.dev.enc`, prompt for password (masked input), derive key using salt from file, decrypt, and ensure `DATABASE_URL=postgres://postgres@127.0.0.1:5433/le_francais` is set in the output `$RepoRoot\.env`.

- [ ] **Step 5: Run roundtrip test to verify it passes**
Run: `powershell -NoProfile -ExecutionPolicy Bypass -File tools/tests/test_crypto.ps1`
Expected: PASS

- [ ] **Step 6: Encrypt the current development `.env` into `.env.dev.enc`**
Run `tools/encrypt_env.ps1` with the project password to create `.env.dev.enc`.

- [ ] **Step 7: Commit**
```bash
git add tools/encrypt_env.ps1 tools/decrypt_env.ps1 tools/tests/test_crypto.ps1 .env.dev.enc
git commit -m "feat: add encrypted secrets management for Windows dev"
```

---

### Task 3: Tooling, Binaries & Database Backup Downloader (`tools/download_tools.ps1`)

**Files:**
- Create: `tools/download_tools.ps1`
- Test: Verify standalone execution, staging folders, component extraction, and database backup extraction using native `tar.exe`

**Interfaces:**
- Consumes: HTTP endpoints for Micromamba, PostgreSQL 15 portable zip, FFmpeg zip, GeoIP databases, and local/bundled `.tar.gz` backup archives.
- Uses: `$RepoRoot = Split-Path $PSScriptRoot -Parent` for all file resolution.
- Uses: `New-Item -ItemType Directory -Force` before running extraction.
- Staging and flattening:
  - Micromamba: Extract `.tar.bz2` to `$RepoRoot\tools\temp_mamba`, move `micromamba.exe` to `$RepoRoot\tools\bin\micromamba.exe`, delete staging.
  - PostgreSQL 15: Extract `.zip` to `$RepoRoot\tools\temp_pg`, move contents of nested `pgsql\*` directly into `$RepoRoot\tools\pgsql\`, delete staging.
  - FFmpeg: Extract `.zip` to `$RepoRoot\tools\temp_ff`, find `ffmpeg.exe` within nested folders and move directly to `$RepoRoot\ffmpeg\ffmpeg.exe`, delete staging.
  - GeoIP: Fetch/verify `GeoLite2-City.mmdb` and `GeoLite2-Country.mmdb` in `$RepoRoot\geoip\`.
  - Database Backups:
    - Pre-create `$RepoRoot\tools\backups\2026-05-29T13_46Z` and `$RepoRoot\tools\backups\2026-05-29T13_45Z`.
    - If bundled backups exist in `$RepoRoot\backups\` (or `C:\Users\anton\workspace\postgres-setup\backups\`), copy or extract `courses_database_2026-05-29T13_46Z.dir.tar.gz` and `le-francais-database_2026-05-29T13_45Z.dir.tar.gz` into `$RepoRoot\tools\backups\`.
- Produces:
  - `tools/bin/micromamba.exe`
  - `tools/pgsql/bin/initdb.exe`, `tools/pgsql/bin/pg_ctl.exe`, `tools/pgsql/bin/pg_restore.exe` (PostgreSQL 15)
  - `ffmpeg/ffmpeg.exe`
  - `geoip/GeoLite2-City.mmdb` and `geoip/GeoLite2-Country.mmdb`
  - `tools/backups/2026-05-29T13_46Z/courses_database_yyqi`
  - `tools/backups/2026-05-29T13_45Z/le_francais_database`

- [ ] **Step 1: Write `tools/download_tools.ps1`**
Implement download, staging, and extraction logic:
- Resolve `$RepoRoot = Split-Path $PSScriptRoot -Parent`.
- Ensure `$RepoRoot\tools\bin` exists via `New-Item -ItemType Directory -Force -Path "$RepoRoot\tools\bin"`.
- If `$RepoRoot\tools\bin\micromamba.exe` is absent:
  - Download `micromamba.tar.bz2` from `https://micro.mamba.pm/api/micromamba/win-64/latest`.
  - Run `New-Item -ItemType Directory -Force -Path "$RepoRoot\tools\temp_mamba"`.
  - Extract via `tar.exe -xf micromamba.tar.bz2 -C "$RepoRoot\tools\temp_mamba"`.
  - Locate `micromamba.exe` inside `$RepoRoot\tools\temp_mamba` (under `Library\bin\` or root) and move to `$RepoRoot\tools\bin\micromamba.exe`.
  - Remove `$RepoRoot\tools\temp_mamba` and the downloaded archive.
- Ensure `$RepoRoot\tools\pgsql\bin\postgres.exe` exists. If absent:
  - Download EnterpriseDB PostgreSQL 15 Windows x64 zip binaries (`https://get.enterprisedb.com/postgresql/postgresql-15.8-1-windows-x64-binaries.zip`) to `$RepoRoot\tools\postgres.zip`.
  - Run `New-Item -ItemType Directory -Force -Path "$RepoRoot\tools\temp_pg"`.
  - Expand to staging: `Expand-Archive -Path "$RepoRoot\tools\postgres.zip" -DestinationPath "$RepoRoot\tools\temp_pg" -Force`.
  - Move inner `pgsql\*` contents directly into `$RepoRoot\tools\pgsql\`.
  - Remove staging folder and zip archive.
- Ensure `$RepoRoot\ffmpeg\ffmpeg.exe` exists. If absent:
  - Download lightweight FFmpeg Windows x64 zip to `$RepoRoot\tools\ffmpeg.zip`.
  - Run `New-Item -ItemType Directory -Force -Path "$RepoRoot\tools\temp_ff"`.
  - Expand to staging: `Expand-Archive -Path "$RepoRoot\tools\ffmpeg.zip" -DestinationPath "$RepoRoot\tools\temp_ff" -Force`.
  - Locate `ffmpeg.exe` inside staging and move to `$RepoRoot\ffmpeg\ffmpeg.exe`.
  - Remove staging folder and zip archive.
- Ensure `$RepoRoot\geoip` exists. Check for `GeoLite2-City.mmdb` and `GeoLite2-Country.mmdb`; copy from current local directory or download from designated hosted backup URL.
- Ensure `$RepoRoot\tools\backups` exists:
  - Check if `$RepoRoot\tools\backups\2026-05-29T13_46Z\courses_database_yyqi` exists. If not:
    - Run `New-Item -ItemType Directory -Force -Path "$RepoRoot\tools\backups\2026-05-29T13_46Z"`.
    - If `C:\Users\anton\workspace\postgres-setup\backups\2026-05-29T13_46Z` exists, copy directly.
    - Else if `$RepoRoot\backups\courses_database_2026-05-29T13_46Z.dir.tar.gz` exists, extract using `tar.exe -xf "$RepoRoot\backups\courses_database_2026-05-29T13_46Z.dir.tar.gz" -C "$RepoRoot\tools\backups\2026-05-29T13_46Z"`.
  - Check if `$RepoRoot\tools\backups\2026-05-29T13_45Z\le_francais_database` exists. If not:
    - Run `New-Item -ItemType Directory -Force -Path "$RepoRoot\tools\backups\2026-05-29T13_45Z"`.
    - If `C:\Users\anton\workspace\postgres-setup\backups\2026-05-29T13_45Z` exists, copy directly.
    - Else if `$RepoRoot\backups\le-francais-database_2026-05-29T13_45Z.dir.tar.gz` exists, extract using `tar.exe -xf "$RepoRoot\backups\le-francais-database_2026-05-29T13_45Z.dir.tar.gz" -C "$RepoRoot\tools\backups\2026-05-29T13_45Z"`.

- [ ] **Step 2: Test script execution on local machine**
Run: `powershell -NoProfile -ExecutionPolicy Bypass -File "tools\download_tools.ps1"`
Verify:
```powershell
powershell -Command "$r = (Get-Item .).FullName; Test-Path $r\tools\bin\micromamba.exe; Test-Path $r\tools\pgsql\bin\pg_ctl.exe; Test-Path $r\ffmpeg\ffmpeg.exe; Test-Path $r\tools\backups\2026-05-29T13_45Z\le_francais_database"
```
Expected: All return `True`.

- [ ] **Step 3: Commit**
```bash
git add tools/download_tools.ps1
git commit -m "feat: add automated Windows binaries and database backup extractor"
```

---

### Task 4: Automated Setup Script (`setup.bat`)

**Files:**
- Create: `setup.bat`
- Test: Full end-to-end setup verification with `-w` synchronous Postgres boot, active DB detection, flat `goto` data loss guard, and `pg_restore`

**Interfaces:**
- Consumes: `tools/download_tools.ps1`, `tools/decrypt_env.ps1`, `environment.yml`, `bin/wagtail_nbsp.patch`, extracted database backup directories.
- Anchors working directory via `cd /d "%~dp0"`.
- Uses flat `goto skip_restore` control flow to eliminate CMD parse-time expansion bugs.
- Tracks `%DB_ALREADY_RUNNING%` using `pg_isready`: skips startup/shutdown if port 5433 is already active.
- Uses synchronous wait flag `-w` for Postgres start.
- Uses `initdb.exe -U postgres -A trust -E UTF-8 -D "%~dp0tools\data"`.
- Uses `pg_restore.exe` with `-Fd`, `--clean`, `--if-exists`, `--no-owner`, `--jobs=4`.
- Guards database restore with `tools\data\.restore_complete` lockfile.
- Produces: Initialized DB cluster in `tools/data`, restored `courses` and `le_francais` databases, patched Wagtail, generated `combined_ca.pem`.

- [ ] **Step 1: Implement `setup.bat`**
```cmd
@echo off
setlocal
cd /d "%~dp0"
set MAMBA_ROOT_PREFIX=%~dp0tools\mamba_root

echo [1/6] Downloading runtime tools and backups...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\download_tools.ps1"
if %ERRORLEVEL% neq 0 ( echo Error downloading tools. & pause & exit /b 1 )

echo [2/6] Configuring environment secrets...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\decrypt_env.ps1"
if %ERRORLEVEL% neq 0 ( echo Error decrypting environment. & pause & exit /b 1 )

echo [3/6] Building Python 3.7 runtime environment...
"%~dp0tools\bin\micromamba.exe" create -p "%~dp0tools\env" -f "%~dp0environment.yml" -y
if %ERRORLEVEL% neq 0 ( echo Error creating Python environment. & pause & exit /b 1 )

echo [4/6] Applying Wagtail rich-text patch and security certificates...
"%~dp0tools\bin\micromamba.exe" run -p "%~dp0tools\env" python -m pypatch.command apply "%~dp0bin\wagtail_nbsp.patch" wagtail
"%~dp0tools\bin\micromamba.exe" run -p "%~dp0tools\env" python -c "import certifi, os; d = os.path.abspath('tinkoff_merchant/certs'); default_certs = open(certifi.where(), 'r', encoding='utf-8').read(); custom_certs = [open(os.path.join(d, f), 'r', encoding='utf-8', errors='ignore').read().strip() for f in os.listdir(d) if (f.endswith('.pem') or f.endswith('.crt')) and f != 'combined_ca.pem']; open(os.path.join(d, 'combined_ca.pem'), 'w', encoding='utf-8').write(default_certs + '\n\n' + '\n\n'.join(custom_certs))"

echo [5/6] Initializing local PostgreSQL cluster...
if not exist "%~dp0tools\data\PG_VERSION" (
    "%~dp0tools\pgsql\bin\initdb.exe" -U postgres -A trust -E UTF-8 -D "%~dp0tools\data"
)

echo [6/6] Restoring databases from backup...
if exist "%~dp0tools\data\.restore_complete" (
    echo Databases already restored. Skipping baseline import...
    goto skip_restore
)

"%~dp0tools\pgsql\bin\pg_isready.exe" -h 127.0.0.1 -p 5433 >nul 2>&1
set DB_ALREADY_RUNNING=%ERRORLEVEL%
if %DB_ALREADY_RUNNING% neq 0 (
    "%~dp0tools\pgsql\bin\pg_ctl.exe" -D "%~dp0tools\data" -l "%~dp0tools\postgres.log" -o "-p 5433" -w start
)

rem Create databases
"%~dp0tools\pgsql\bin\createdb.exe" -h 127.0.0.1 -p 5433 -U postgres courses 2>nul
"%~dp0tools\pgsql\bin\createdb.exe" -h 127.0.0.1 -p 5433 -U postgres le_francais 2>nul

rem Restore courses
echo Restoring courses database...
"%~dp0tools\pgsql\bin\pg_restore.exe" -h 127.0.0.1 -p 5433 -U postgres -d courses --clean --if-exists --no-owner --jobs=4 -Fd "%~dp0tools\backups\2026-05-29T13_46Z\courses_database_yyqi"

rem Restore le_francais
echo Restoring le_francais database...
"%~dp0tools\pgsql\bin\pg_restore.exe" -h 127.0.0.1 -p 5433 -U postgres -d le_francais --clean --if-exists --no-owner --jobs=4 -Fd "%~dp0tools\backups\2026-05-29T13_45Z\le_francais_database"

echo Database restore finished. Creating lockfile...
echo 1 > "%~dp0tools\data\.restore_complete"

if %DB_ALREADY_RUNNING% neq 0 (
    "%~dp0tools\pgsql\bin\pg_ctl.exe" -D "%~dp0tools\data" -m fast stop
)

:skip_restore

echo =======================================================
echo Setup complete! You can now double-click start.bat to run.
echo =======================================================
pause
```

- [ ] **Step 2: Test setup execution steps**
Verify that all post-install hooks, lockfile logic, and database initialization execute without errors:
```powershell
powershell -Command "Test-Path tools\data\PG_VERSION; Test-Path tinkoff_merchant\certs\combined_ca.pem"
```
Expected: Returns `True`.

- [ ] **Step 3: Commit**
```bash
git add setup.bat
git commit -m "feat: add turnkey Windows setup.bat wizard with database backup restoration and data loss guard"
```

---

### Task 5: Daily Launcher & Shutdown Scripts (`start.bat` & `stop.bat`)

**Files:**
- Create: `start.bat`
- Create: `stop.bat`
- Test: Process start, stale PID cleanup, hidden browser polling, and graceful shutdown

**Interfaces:**
- `start.bat`: Anchors working directory via `cd /d "%~dp0"`; cleans stale PID only if `pg_isready` fails; launches PostgreSQL on port 5433; polls port 8000 in background with `-WindowStyle Hidden` (max 30s) to launch browser; executes `python manage.py runserver` via `micromamba run`.
- `stop.bat`: Shuts down PostgreSQL on port 5433 cleanly.

- [ ] **Step 1: Implement `start.bat`**
```cmd
@echo off
setlocal
cd /d "%~dp0"
set MAMBA_ROOT_PREFIX=%~dp0tools\mamba_root

rem Check if PostgreSQL is already responding on port 5433
"%~dp0tools\pgsql\bin\pg_isready.exe" -h 127.0.0.1 -p 5433 >nul 2>&1
if %ERRORLEVEL% neq 0 (
    rem If not responding, clean any stale postmaster.pid
    if exist "%~dp0tools\data\postmaster.pid" del /f /q "%~dp0tools\data\postmaster.pid"
    echo Starting PostgreSQL...
    "%~dp0tools\pgsql\bin\pg_ctl.exe" -D "%~dp0tools\data" -l "%~dp0tools\postgres.log" -o "-p 5433" -w start
)

rem Launch bounded background browser poller with hidden window (30s timeout)
start "" powershell -WindowStyle Hidden -NoProfile -ExecutionPolicy Bypass -Command "$r = 0; while (!(Test-NetConnection 127.0.0.1 -Port 8000 -WarningAction SilentlyContinue).TcpTestSucceeded -and $r -lt 60) { Start-Sleep -Milliseconds 500; $r++ }; if ($r -lt 60) { Start-Process 'http://127.0.0.1:8000' }"

echo Starting le-francais development server...
"%~dp0tools\bin\micromamba.exe" run -p "%~dp0tools\env" python manage.py runserver 127.0.0.1:8000
```

- [ ] **Step 2: Implement `stop.bat`**
```cmd
@echo off
setlocal
cd /d "%~dp0"
echo Stopping PostgreSQL...
"%~dp0tools\pgsql\bin\pg_ctl.exe" -D "%~dp0tools\data" -m fast stop
```

- [ ] **Step 3: Test launch and shutdown behavior**
Test running `start.bat` and `stop.bat` components, verify port 5433 responds and releases.

- [ ] **Step 4: Commit**
```bash
git add start.bat stop.bat
git commit -m "feat: add start.bat and stop.bat with hidden browser poller and orphan resilience"
```

---

### Task 6: Documentation & Instructions (`README_WINDOWS_DEV.md`)

**Files:**
- Create: `README_WINDOWS_DEV.md`

- [ ] **Step 1: Write `README_WINDOWS_DEV.md`**
Provide a concise, 3-step visual instruction sheet for the assistant:
1. Double-click `setup.bat` (first time only) and enter the project password when prompted.
2. Double-click `start.bat` to work (the browser will open automatically).
3. Double-click `stop.bat` (or close the window) when finished.

- [ ] **Step 2: Commit**
```bash
git add README_WINDOWS_DEV.md
git commit -m "docs: add Windows assistant quickstart guide"
```
