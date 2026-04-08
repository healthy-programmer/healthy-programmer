#!/usr/bin/env bash

set -e

echo "=== Move Reminder Launcher (Linux) ==="
echo "Usage: $0 [--interval MINUTES] [--duration SECONDS] [--position POS] [--working-hours START-END]"

command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Allow override via PYTHON_BIN environment variable
if [ -n "$PYTHON_BIN" ]; then
    PYTHON="$PYTHON_BIN"
else
    PYTHON=""
    if command_exists python3; then
        PYTHON="python3"
    elif command_exists python; then
        PYTHON="python"
    fi
fi

if [ -z "$PYTHON" ]; then
    echo "ERROR: Python 3 is not installed or not in PATH."
    exit 1
fi

# Print the full path of the Python interpreter
PYTHON_PATH=$(command -v "$PYTHON" 2>/dev/null)
echo "Using Python interpreter: $PYTHON_PATH"

# Warn if Homebrew Python is detected
if [[ "$PYTHON_PATH" == *"linuxbrew"* ]]; then
    echo "WARNING: You are using Homebrew Python ($PYTHON_PATH)."
    echo "This version often does NOT support Tkinter on Linux."
    echo "If you see errors about missing '_tkinter', try using your system Python:"
    echo "  /usr/bin/python3 ./script/run_move_reminder.sh ..."
    echo "Or set PYTHON_BIN=/usr/bin/python3"
fi

# Check for Tkinter support
if ! $PYTHON -c "import tkinter" >/dev/null 2>&1; then
    echo "ERROR: The selected Python interpreter does not have Tkinter support."
    echo "This is common with Homebrew Python on Linux."
    echo "Try using your system Python (e.g., /usr/bin/python3) or install python3-tk:"
    echo "  sudo apt install python3-tk"
    echo "  or use: sudo dnf install python3-tkinter"
    echo "  or use: sudo yum install python3-tkinter"
    echo "  or use: sudo pacman -Sy tk"
    exit 1
fi

echo "Running move_reminder.py ..."
"$PYTHON" "$(dirname "$0")/move_reminder.py" "$@"