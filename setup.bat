@echo off
setlocal
cd /d "%~dp0"
set MAMBA_ROOT_PREFIX=%~dp0tools\mamba_root

echo ========================================================
echo  Le-Francais Windows Development Setup Wizard
echo ========================================================
echo.

rem Verify directory is writable
echo test > "%~dp0.write_test" 2>nul
if exist "%~dp0.write_test" goto dir_writable
echo [ERROR] Current folder is read-only or in a write-protected location!
echo Please copy the project folder to a writable directory before running setup.bat.
pause
exit /b 1

:dir_writable
del /f /q "%~dp0.write_test" 2>nul

echo [1/6] Downloading runtime tools and backups...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\download_tools.ps1"
if %ERRORLEVEL% neq 0 goto step_failed

echo [2/6] Configuring environment secrets...
set PASS_ARG=
if "%~1" neq "" set PASS_ARG=-Password "%~1"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\decrypt_env.ps1" %PASS_ARG%
if %ERRORLEVEL% neq 0 goto step_failed

echo [3/6] Building Python 3.7 runtime environment...
if exist "%~dp0tools\env\python.exe" goto env_ready
"%~dp0tools\bin\micromamba.exe" create -p "%~dp0tools\env" -f "%~dp0environment.yml" -y
if %ERRORLEVEL% neq 0 goto step_failed
"%~dp0tools\bin\micromamba.exe" run -p "%~dp0tools\env" pip install django-session-header==1.0 --no-deps
if %ERRORLEVEL% neq 0 goto step_failed
:env_ready

echo [4/6] Applying Wagtail rich-text patch and security certificates...
"%~dp0tools\bin\micromamba.exe" run -p "%~dp0tools\env" python -m pypatch.command apply "%~dp0bin\wagtail_nbsp.patch" wagtail
"%~dp0tools\bin\micromamba.exe" run -p "%~dp0tools\env" python "%~dp0tools\generate_certs.py"

echo [5/6] Initializing local PostgreSQL cluster...
if exist "%~dp0tools\data\PG_VERSION" goto cluster_ready
"%~dp0tools\pgsql\bin\initdb.exe" -U postgres -A trust -E UTF-8 -D "%~dp0tools\data"
if %ERRORLEVEL% neq 0 goto step_failed
echo listen_addresses = '127.0.0.1' >> "%~dp0tools\data\postgresql.conf"
:cluster_ready

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

rem Locate extracted backup directories
set COURSES_DUMP=
set LE_FRANCAIS_DUMP=
for /f "delims=" %%D in ('dir "%~dp0tools\backups\*courses_database_*" /s /b /ad 2^>nul ^| findstr /v /i "test_"') do set "COURSES_DUMP=%%D"
for /f "delims=" %%D in ('dir "%~dp0tools\backups\*le_francais_database*" /s /b /ad 2^>nul ^| findstr /v /i "test_"') do set "LE_FRANCAIS_DUMP=%%D"

rem Create databases
"%~dp0tools\pgsql\bin\createdb.exe" -h 127.0.0.1 -p 5433 -U postgres courses 2>nul
"%~dp0tools\pgsql\bin\createdb.exe" -h 127.0.0.1 -p 5433 -U postgres le_francais 2>nul

rem Restore courses
if defined COURSES_DUMP (
    echo Restoring courses database...
    "%~dp0tools\pgsql\bin\pg_restore.exe" -h 127.0.0.1 -p 5433 -U postgres -d courses --clean --if-exists --no-owner --jobs=4 -Fd "%COURSES_DUMP%"
) else (
    echo Warning: courses database backup not found.
)

rem Restore le_francais
if defined LE_FRANCAIS_DUMP (
    echo Restoring le_francais database...
    "%~dp0tools\pgsql\bin\pg_restore.exe" -h 127.0.0.1 -p 5433 -U postgres -d le_francais --clean --if-exists --no-owner --jobs=4 -Fd "%LE_FRANCAIS_DUMP%"
) else (
    echo Warning: le_francais database backup not found.
)

if %ERRORLEVEL% gtr 1 goto restore_failed
echo Database restore finished. Creating lockfile...
echo 1 > "%~dp0tools\data\.restore_complete"
goto restore_cleanup

:restore_failed
echo Warning: Database restore encountered fatal errors. Lockfile not created.

:restore_cleanup
if defined COURSES_DUMP for %%P in ("%COURSES_DUMP%\..") do rd /s /q "%%~fP" 2>nul
if defined LE_FRANCAIS_DUMP for %%P in ("%LE_FRANCAIS_DUMP%\..") do rd /s /q "%%~fP" 2>nul

if %DB_ALREADY_RUNNING% neq 0 (
    "%~dp0tools\pgsql\bin\pg_ctl.exe" -D "%~dp0tools\data" -m fast stop
)

:skip_restore

echo =======================================================
echo Setup complete! You can now double-click start.bat to run.
echo =======================================================
pause
exit /b 0

:step_failed
echo.
echo [ERROR] Setup encountered an error.
pause
exit /b 1
