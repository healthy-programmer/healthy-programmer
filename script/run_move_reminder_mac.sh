#!/bin/bash

set -e

echo "=== Move Reminder Launcher (MacOS) ==="
echo "Usage: $0 [--interval MINUTES] [--duration SECONDS] [--position POS] [--working-hours START-END]"

if ! command -v python3 >/dev/null 2>&1; then
    echo "ERROR: python3 is not installed or not in PATH."
    exit 1
fi

echo "Running move_reminder.py ..."
python3 "$(dirname "$0")/move_reminder.py" "$@"