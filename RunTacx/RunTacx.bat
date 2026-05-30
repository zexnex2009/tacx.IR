@echo off
setlocal
set "SCRIPT_DIR=%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (
    py -3 "%SCRIPT_DIR%main.py" %*
) else (
    python "%SCRIPT_DIR%main.py" %*
)

if errorlevel 1 (
    echo RunTacx exited with an error.
    pause
)

