@echo off
REM === Move Reminder Setup & Run Script (Windows) ===
REM Usage: run_move_reminder.bat [--interval MINUTES] [--duration SECONDS] [--position POS] [--working-hours START-END]
REM   --working-hours: Only show reminders between these hours (24h format, e.g. 8:00-16:30). Default: 8:00-16:30

REM 1. Check for Python
where python >nul 2>nul
if %ERRORLEVEL%==0 (
    set PYTHON=python
) else (
    where python3 >nul 2>nul
    if %ERRORLEVEL%==0 (
        set PYTHON=python3
    ) else (
        echo ERROR: Python is not installed. Please install Python 3 from https://www.python.org/downloads/
        exit /b 1
    )
)

REM 2. Check for pip
%PYTHON% -m pip --version >nul 2>nul
if %ERRORLEVEL%==0 (
    REM pip exists
) else (
    echo pip not found, attempting to install pip...
    %PYTHON% -m ensurepip --default-pip >nul 2>nul
    if %ERRORLEVEL%==0 (
        echo pip installed successfully.
    ) else (
        echo ERROR: Could not install pip automatically. Please install pip manually.
        exit /b 1
    )
)

REM 3. Install Pillow
%PYTHON% -c "from PIL import Image" >nul 2>nul
if %ERRORLEVEL%==0 (
    REM Pillow exists
) else (
    echo Installing Pillow...
    %PYTHON% -m pip install --user --upgrade pillow
)

REM 4. Install tkcalendar
%PYTHON% -c "import tkcalendar" >nul 2>nul
if %ERRORLEVEL%==0 (
    REM tkcalendar exists
) else (
    echo Installing tkcalendar...
    %PYTHON% -m pip install --user --upgrade tkcalendar
)

REM 5. Run the script
echo Running move_reminder.py ...
%PYTHON% "%~dp0move_reminder.py" %*