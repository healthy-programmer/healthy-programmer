@echo off
REM === Move Reminder Launcher (Windows) ===
REM Usage: run_move_reminder.bat [--interval MINUTES] [--duration SECONDS] [--position POS] [--working-hours START-END]

REM 1. Check for Python
where python >nul 2>nul
if %ERRORLEVEL%==0 (
    set PYTHON=python
) else (
    where python3 >nul 2>nul
    if %ERRORLEVEL%==0 (
        set PYTHON=python3
    ) else (
        echo ERROR: Python is not installed or not in PATH.
        exit /b 1
    )
)

REM 2. Run the script
echo Running move_reminder.py ...
%PYTHON% "%~dp0move_reminder.py" %*