#!/usr/bin/env bash

set -e

echo "=== Move Reminder Setup & Run Script ==="

command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 1. Find best python3 (prefer system python with tkinter)
PYTHON_CANDIDATES=()
if command_exists python3; then
    PYTHON_CANDIDATES+=("python3")
fi
if command_exists python; then
    PYTHON_CANDIDATES+=("python")
fi
if command_exists /usr/bin/python3; then
    PYTHON_CANDIDATES+=("/usr/bin/python3")
fi
if command_exists /usr/local/bin/python3; then
    PYTHON_CANDIDATES+=("/usr/local/bin/python3")
fi
if command_exists /home/linuxbrew/.linuxbrew/bin/python3; then
    PYTHON_CANDIDATES+=("/home/linuxbrew/.linuxbrew/bin/python3")
fi

PYTHON=""
for candidate in "${PYTHON_CANDIDATES[@]}"; do
    if "$candidate" -c "import tkinter" >/dev/null 2>&1; then
        PYTHON="$candidate"
        break
    fi
done

if [ -z "$PYTHON" ]; then
    # Try to install Tkinter for all candidates
    for candidate in "${PYTHON_CANDIDATES[@]}"; do
        if [[ "$candidate" == *"linuxbrew"* ]]; then
            echo "WARNING: Homebrew Python detected at $candidate."
            echo "Homebrew Python on Linux often does NOT support Tkinter."
            echo "It is recommended to use your system Python (e.g., /usr/bin/python3) for GUI scripts."
            echo "If you want to try anyway, run: brew reinstall python-tk"
        fi
    done
    # Try to install Tkinter for system Python
    if command_exists apt; then
        sudo apt update
        sudo apt install -y python3-tk
    elif command_exists dnf; then
        sudo dnf install -y python3-tkinter
    elif command_exists yum; then
        sudo yum install -y python3-tkinter
    elif command_exists pacman; then
        sudo pacman -Sy --noconfirm tk
    elif command_exists brew; then
        brew install python-tk
    fi
    # Try again to find a working python
    for candidate in "${PYTHON_CANDIDATES[@]}"; do
        if "$candidate" -c "import tkinter" >/dev/null 2>&1; then
            PYTHON="$candidate"
            break
        fi
    done
fi

if [ -z "$PYTHON" ]; then
    echo "ERROR: No Python interpreter with Tkinter support found."
    echo "Try installing system Python (e.g., sudo apt install python3 python3-tk) and rerun this script."
    exit 1
fi

echo "Using Python interpreter: $PYTHON"

# 2. Check pip
if ! $PYTHON -m pip --version >/dev/null 2>&1; then
    echo "pip not found, attempting to install pip..."
    if command_exists apt; then
        sudo apt update
        sudo apt install -y python3-pip
    elif command_exists dnf; then
        sudo dnf install -y python3-pip
    elif command_exists yum; then
        sudo yum install -y python3-pip
    elif command_exists pacman; then
        sudo pacman -Sy --noconfirm python-pip
    elif command_exists brew; then
        brew install pipx
        pipx ensurepath
    else
        echo "No supported package manager found for pip installation."
        exit 1
    fi
fi

# 3. Ensure Pillow is installed for this Python
if ! $PYTHON -c "from PIL import Image" >/dev/null 2>&1; then
    echo "Pillow (PIL) not found, installing with pip..."
    $PYTHON -m pip install --user --upgrade pillow
fi

# 4. Ensure tkcalendar is installed for this Python
if ! $PYTHON -c "import tkcalendar" >/dev/null 2>&1; then
    echo "tkcalendar not found, installing with pip..."
    $PYTHON -m pip install --user --upgrade tkcalendar
fi

# 5. Run the script
echo "Running move_reminder.py ..."
"$PYTHON" "$(dirname "$0")/move_reminder.py" "$@"