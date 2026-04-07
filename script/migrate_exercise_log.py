import os
import csv
from datetime import datetime

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "log"))
OLD_LOG = os.path.join(SCRIPT_DIR, "exercise_log.log")

def ensure_log_dir():
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR, exist_ok=True)

def migrate():
    if not os.path.exists(OLD_LOG):
        print(f"No old log file found at {OLD_LOG}")
        return

    ensure_log_dir()
    moved = 0
    with open(OLD_LOG, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row or len(row) < 2:
                continue
            # First column is datetime: 'YYYY-MM-DD HH:MM:SS'
            dt_str = row[0]
            try:
                date_str = dt_str.split(" ")[0]
                daily_log = os.path.join(LOG_DIR, f"{date_str}.log")
                with open(daily_log, "a", encoding="utf-8", newline='') as out:
                    writer = csv.writer(out)
                    writer.writerow(row)
                moved += 1
            except Exception as e:
                print(f"Failed to process row: {row} ({e})")
    print(f"Moved {moved} log entries to daily log files in {LOG_DIR}")

    # Optionally, rename the old log file to prevent re-migration
    backup = OLD_LOG + ".bak"
    os.rename(OLD_LOG, backup)
    print(f"Renamed old log file to {backup}")

if __name__ == "__main__":
    migrate()