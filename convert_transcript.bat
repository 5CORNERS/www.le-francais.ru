@echo off
setlocal
cd /d "%~dp0"
set MAMBA_ROOT_PREFIX=%~dp0tools\mamba_root

if "%1"=="" goto usage

"%~dp0tools\bin\micromamba.exe" run -p "%~dp0tools\env" python manage.py convert_transcript %*
exit /b %ERRORLEVEL%

:usage
echo.
echo =======================================================
echo  Le-Francais.ru Transcript Converter (DOCX -^> Admin)
echo =======================================================
echo.
echo  Usage:
echo    convert_transcript.bat ^<lesson_number^> [--db]
echo    convert_transcript.bat ^<path_to_docx^> [^<output_prefix^>] [--db]
echo    Options: --docx-dir ^<folder^>  --output-dir ^<folder^>
echo.
echo  Or drag and drop your .docx file onto convert_transcript.bat!
echo.
echo  Example:
echo    convert_transcript.bat 4
echo    convert_transcript.bat 4 --db
echo.
exit /b 0
