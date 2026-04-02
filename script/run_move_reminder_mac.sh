#!/bin/bash

set -e

echo "=== Move Reminder Setup & Run Script (MacOS) ==="

# 1. Check for Homebrew
if ! command -v brew >/dev/null 2>&1; then
    echo "Homebrew not found. Please install Homebrew from https://brew.sh/"
    exit 1
fi

# 2. Check for python3
if ! command -v python3 >/dev/null 2>&1; then
    echo "python3 not found. Installing via Homebrew..."
    brew install python
fi

PYTHON="python3"

# 3. Check for Tkinter
if ! $PYTHON -c "import tkinter" >/dev/null 2>&1; then
    echo "Tkinter not found. Installing python-tk via Homebrew..."
    brew install python-tk
fi

# 4. Check for pip
if ! $PYTHON -m pip --version >/dev/null 2>&1; then
    echo "pip not found. Installing pip..."
    $PYTHON -m ensurepip --default-pip
fi

# 5. Install Pillow
if ! $PYTHON -c "from PIL import Image" >/dev/null 2>&1; then
    echo "Installing Pillow..."
    $PYTHON -m pip install --user --upgrade pillow
fi

# 6. Install tkcalendar
if ! $PYTHON -c "import tkcalendar" >/dev/null 2>&1; then
    echo "Installing tkcalendar..."
    $PYTHON -m pip install --user --upgrade tkcalendar
fi

# 7. Run the script
echo "Running move_reminder.py ..."
$PYTHON "$(dirname "$0")/move_reminder.py" "$@"