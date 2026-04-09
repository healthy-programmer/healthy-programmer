import argparse

# Parse command-line arguments for the move reminder application.
def parse_args():
    parser = argparse.ArgumentParser(
        description="Remind yourself to move every N minutes by popping up a random exercise GIF."
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=30,
        help="Interval in minutes between reminders (default: 30)"
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=30,
        help="How long (seconds) to show the GIF window (default: 30)"
    )
    parser.add_argument(
        "--position",
        type=str,
        choices=["top-left", "top-right", "bottom-left", "bottom-right", "center"],
        default="bottom-right",
        help="Popup window position: top-left, top-right, bottom-left, bottom-right, center (default: bottom-right)"
    )
    parser.add_argument(
        "--working-hours",
        type=str,
        default="8:00-16:30",
        help="Only show reminders between these hours (24h format, e.g. 8:00-16:30). Default: 8:00-16:30"
    )
    return parser.parse_args()