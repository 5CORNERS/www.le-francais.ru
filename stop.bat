@echo off
setlocal
cd /d "%~dp0"

echo Stopping PostgreSQL on port 5433...
"%~dp0tools\pgsql\bin\pg_ctl.exe" -D "%~dp0tools\data" -m fast stop
pause
