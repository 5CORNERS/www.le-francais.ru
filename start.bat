@echo off
setlocal
cd /d "%~dp0"
set MAMBA_ROOT_PREFIX=%~dp0tools\mamba_root

rem Check if PostgreSQL is already responding on port 5433
"%~dp0tools\pgsql\bin\pg_isready.exe" -h 127.0.0.1 -p 5433 >nul 2>&1
if %ERRORLEVEL% neq 0 (
    rem If not responding, clean any stale postmaster.pid
    if exist "%~dp0tools\data\postmaster.pid" del /f /q "%~dp0tools\data\postmaster.pid"
    echo Starting PostgreSQL on port 5433...
    "%~dp0tools\pgsql\bin\pg_ctl.exe" -D "%~dp0tools\data" -l "%~dp0tools\postgres.log" -o "-p 5433" -w start
) else (
    echo PostgreSQL is already running on port 5433.
)

rem Launch bounded background browser poller with hidden window (30s timeout)
start "" powershell -WindowStyle Hidden -NoProfile -ExecutionPolicy Bypass -Command "$r = 0; while (!(Test-NetConnection 127.0.0.1 -Port 8000 -WarningAction SilentlyContinue).TcpTestSucceeded -and $r -lt 60) { Start-Sleep -Milliseconds 500; $r++ }; if ($r -lt 60) { Start-Process 'http://127.0.0.1:8000' }"

echo Starting le-francais development server...
"%~dp0tools\bin\micromamba.exe" run -p "%~dp0tools\env" python manage.py runserver 127.0.0.1:8000
