# Turnkey Windows Development Environment Setup (Portable PostgreSQL + Micromamba)

## Overview
This specification details the architecture and automated scripts required to deliver a true zero-install local development environment for `le-francais` on Windows. It is specifically hardened for a non-technical assistant, eliminating external wizards, admin prompts, background service clutter, and terminal trapdoors.

---

## Hardening Decisions & Design Fixes

### 1. PostgreSQL Orphaning Resilience (The 'X' Button Trap)
* **Problem:** Windows CMD batch files cannot trap `SIGTERM` when the user clicks the "X" button, leaving `postgres.exe` orphaned in the background.
* **Resolution:** `start.bat` will never assume PostgreSQL is stopped. Before launching, it queries port `5433` (via `pg_isready`). If PostgreSQL is already running from an unclean previous exit, the script attaches to the existing instance and proceeds without error. `stop.bat` is provided for intentional termination.

### 2. Zero-Install Python Runtime via Micromamba
* **Problem:** Requiring the user to install Miniconda introduces installation wizards, PATH checkbox pitfalls, and terminal restart requirements.
* **Resolution:** `download_tools.ps1` automatically downloads a standalone `micromamba.exe` binary directly into `tools\bin\`. `setup.bat` uses Micromamba to build a self-contained Python 3.7.16 environment directly inside `tools\env\`. No installer, no admin privileges, and zero system pollution.

### 3. Micromamba Root Prefix Isolation
* **Problem:** Even when targeting `-p tools\env`, Micromamba defaults to caching packages and state in `C:\Users\<User>\micromamba`, polluting the user's home directory.
* **Resolution:** All batch scripts set `MAMBA_ROOT_PREFIX=%~dp0tools\mamba_root` prior to executing any Micromamba command, guaranteeing 100% containment within the project directory.

### 4. Execution Context & DLL Load Resilience (`micromamba run`)
* **Problem:** Invoking raw `tools\env\python.exe` directly on Windows fails to inject `tools\env\Library\bin` into `PATH`. C-extensions (`psycopg2`, `Pillow`, `lxml`, `cryptography`) will immediately crash on boot with `ImportError: DLL load failed`.
* **Resolution:** All Python invocations in `setup.bat` and `start.bat` are executed strictly through Micromamba's environment runner:
  ```cmd
  tools\bin\micromamba.exe run -p tools\env python manage.py runserver 127.0.0.1:8000
  ```
  This guarantees that all native DLL dependencies, C-runtimes, and virtual environment variables are activated cleanly without altering system-wide environment variables.

### 5. PowerShell Execution Policy Bypass
* **Problem:** Default Windows client installations enforce a `Restricted` execution policy that blocks `.ps1` execution, causing batch callers to fail immediately.
* **Resolution:** All PowerShell invocations from batch files explicitly apply `-NoProfile -ExecutionPolicy Bypass`:
  ```cmd
  powershell -NoProfile -ExecutionPolicy Bypass -File ".\tools\download_tools.ps1"
  ```

### 6. Automated GeoIP2 Database Retrieval
* **Problem:** MaxMind GeoLite2 databases are behind an authenticated login wall and cannot be fetched anonymously by an end-user.
* **Resolution:** `download_tools.ps1` downloads the pre-packaged `.mmdb` archive (`GeoLite2-City.mmdb` and `GeoLite2-Country.mmdb`) from a designated secure project URL directly into `geoip/`. If already present locally, the step is skipped.

### 7. Encrypted Secrets Management (`.env.dev.enc`)
* **Problem:** A dummy `.env.example` will break runtime features that depend on valid credentials (e.g. Yandex SpeechKit, Tinkoff Merchant, internal APIs). Distributing raw `.env` files in plain text risks leakage.
* **Resolution:** The repository includes an encrypted archive `.env.dev.enc` (AES-256 encrypted using standard PowerShell cryptography). During `setup.bat`, the user is prompted once for the decryption password provided by the project owner. The decrypted `.env` is written to the project root and remains gitignored.

### 8. Bounded Browser Poller (Anti-Zombie Protection)
* **Problem:** An unbounded `while (!(Test-NetConnection...))` loop spins indefinitely if Django fails to boot (e.g., due to code or configuration errors), accumulating zombie background PowerShell processes on repeated runs.
* **Resolution:** The browser polling process is capped at 60 retries (500ms intervals = 30 seconds total). If the server fails to bind within the window, the poller exits quietly without spawning a browser window or lingering:
  ```powershell
  $retries = 0; while (!(Test-NetConnection 127.0.0.1 -Port 8000 -WarningAction SilentlyContinue).TcpTestSucceeded -and $retries -lt 60) { Start-Sleep -Milliseconds 500; $retries++ }; if ($retries -lt 60) { Start-Process 'http://127.0.0.1:8000' }
  ```

---

## Directory Architecture

```text
le-francais/
├── tools/
│   ├── bin/
│   │   └── micromamba.exe          # Standalone package manager binary (gitignored)
│   ├── mamba_root/                 # Isolated package cache and repodata (gitignored)
│   ├── env/                        # Completely portable Python 3.7 environment (gitignored)
│   ├── pgsql/                      # Standalone PostgreSQL 12/13 binaries (gitignored)
│   ├── data/                       # PostgreSQL database cluster files (gitignored)
│   ├── download_tools.ps1          # PowerShell helper: pulls micromamba, pgsql, ffmpeg, geoip
│   ├── encrypt_env.ps1             # Developer tool: encrypts .env into .env.dev.enc
│   └── decrypt_env.ps1             # Setup tool: prompts for password & decrypts .env.dev.enc
├── ffmpeg/
│   └── bin/ffmpeg.exe              # Portable FFmpeg binary (gitignored)
├── geoip/
│   ├── GeoLite2-City.mmdb          # Downloaded MaxMind City database (gitignored)
│   └── GeoLite2-Country.mmdb       # Downloaded MaxMind Country database (gitignored)
├── tinkoff_merchant/certs/
│   └── combined_ca.pem             # Generated CA bundle (gitignored)
├── environment.yml                 # Pinned Python 3.7.16 dependency specification
├── .env.dev.enc                    # AES-256 encrypted development secrets (tracked in git)
├── setup.bat                       # Interactive one-time setup wizard
├── start.bat                       # Daily one-click launcher
└── stop.bat                        # Intentional database shutdown utility
```

---

## Component Workflows

### 1. Developer Preparation (One-Time by Project Owner)
1. Export clean `environment.yml` matching the verified Python 3.7.16 environment.
2. Run `tools\encrypt_env.ps1` to produce `.env.dev.enc` from the current working `.env` (sanitized for dev use).
3. Commit `environment.yml`, `tools/`, `.env.dev.enc`, `setup.bat`, `start.bat`, and `stop.bat`.

### 2. Assistant Initial Setup (`setup.bat`)
When run on the assistant's machine:
1. **Set Environment Root:**
   ```cmd
   set MAMBA_ROOT_PREFIX=%~dp0tools\mamba_root
   ```
2. **Tool Download (`tools\download_tools.ps1`):**
   * Invoked via:
     `powershell -NoProfile -ExecutionPolicy Bypass -File ".\tools\download_tools.ps1"`
   * Downloads `micromamba.exe` to `tools\bin\micromamba.exe`.
   * Downloads and unpacks PostgreSQL portable binaries to `tools\pgsql\`.
   * Downloads and unpacks portable `ffmpeg.exe` to `ffmpeg\`.
   * Fetches GeoIP databases to `geoip\`.
3. **Environment Decryption (`tools\decrypt_env.ps1`):**
   * Invoked via:
     `powershell -NoProfile -ExecutionPolicy Bypass -File ".\tools\decrypt_env.ps1"`
   * Prompts for the project secret password.
   * Decrypts `.env.dev.enc` into `.env`.
   * Ensures `DATABASE_URL` is set to `postgres://postgres@127.0.0.1:5433/le_francais`.
4. **Python Environment Creation:**
   * Runs:
     `tools\bin\micromamba.exe create -p tools\env -f environment.yml -y`
5. **Post-Install Hooks & Patches:**
   * Applies Wagtail patch using `micromamba run`:
     `tools\bin\micromamba.exe run -p tools\env python -m pypatch.command apply ./bin/wagtail_nbsp.patch wagtail`
   * Generates Russian CA bundle `tinkoff_merchant\certs\combined_ca.pem` using `micromamba run`.
6. **Database Initialization & Migration:**
   * Runs `tools\pgsql\bin\initdb.exe -U postgres -A trust -E UTF-8 -D tools\data`.
   * Boots temporary Postgres instance on port 5433.
   * Creates database: `tools\pgsql\bin\createdb.exe -h 127.0.0.1 -p 5433 -U postgres le_francais`.
   * Runs migrations using `micromamba run`:
     `tools\bin\micromamba.exe run -p tools\env python manage.py migrate`
   * Cleanly stops the temporary Postgres instance:
     `tools\pgsql\bin\pg_ctl.exe -D tools\data -m fast stop`
7. Prints completion banner and instructs user to run `start.bat`.

### 3. Daily Launcher (`start.bat`)
1. **Set Environment Root:**
   ```cmd
   set MAMBA_ROOT_PREFIX=%~dp0tools\mamba_root
   ```
2. **Database Health Check:**
   * Tests port 5433 using `tools\pgsql\bin\pg_isready.exe -h 127.0.0.1 -p 5433`.
   * If not responding, starts PostgreSQL:
     `tools\pgsql\bin\pg_ctl.exe -D tools\data -l tools\postgres.log -o "-p 5433" start`
3. **Bounded Browser Poller:**
   * Spawns a background PowerShell process that polls `http://127.0.0.1:8000` with `Test-NetConnection` (max 60 attempts / 30 seconds) and launches the default browser:
     `powershell -NoProfile -ExecutionPolicy Bypass -Command "$retries = 0; while (!(Test-NetConnection 127.0.0.1 -Port 8000 -WarningAction SilentlyContinue).TcpTestSucceeded -and $retries -lt 60) { Start-Sleep -Milliseconds 500; $retries++ }; if ($retries -lt 60) { Start-Process 'http://127.0.0.1:8000' }"`
4. **Web Server:**
   * Starts Django via Micromamba to ensure complete DLL and PATH resolution:
     `tools\bin\micromamba.exe run -p tools\env python manage.py runserver 127.0.0.1:8000`

### 4. Shutdown Script (`stop.bat`)
* Explicitly shuts down PostgreSQL:
  `tools\pgsql\bin\pg_ctl.exe -D tools\data -m fast stop`
