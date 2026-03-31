#!/usr/bin/env python3

import argparse
import os
import random
import sys
import time
import threading
import csv

try:
    from tkinter import Tk, Label
except ImportError:
    print("Tkinter is required. Please run the setup script.")
    sys.exit(1)

try:
    from PIL import Image, ImageTk
except ImportError:
    print("Pillow (PIL) is required. Please run the setup script or install with: pip install pillow")
    sys.exit(1)

GIF_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../exercise/images')
DATA_CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../exercise/reminder-data.csv')

def load_gif_descriptions():
    mapping = {}
    with open(DATA_CSV, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            mapping[row['gif_filename']] = row['description']
    return mapping

def get_gif_files():
    return [
        os.path.join(GIF_DIR, f)
        for f in os.listdir(GIF_DIR)
        if f.lower().endswith('.gif')
    ]

def animate_gif(label, frames, delay, frame_idx=0):
    frame = frames[frame_idx]
    label.config(image=frame)
    label.image = frame
    next_idx = (frame_idx + 1) % len(frames)
    label.after(delay, animate_gif, label, frames, delay, next_idx)

def show_gif(gif_path, description="", duration=30, position="bottom-right"):
    """
    Show a GIF as a reminder, preferring 'feh' if available to avoid stealing focus.
    After showing, restore focus to the previously active window using xdotool if available.
    The popup window will appear at the specified position.
    """
    import subprocess

    def get_focused_window():
        """Return the window id of the currently focused window using xdotool, or None."""
        try:
            win_id = subprocess.check_output(["xdotool", "getwindowfocus"]).decode().strip()
            return win_id
        except Exception:
            return None

    def restore_focus(win_id):
        """Restore focus to the given window id using xdotool."""
        if win_id:
            try:
                subprocess.Popen(["xdotool", "windowactivate", "--sync", win_id])
            except Exception:
                pass

    def _show_with_tkinter():
        root = Tk()
        root.title("Move Reminder!")
        # Load image first to get its size
        img = Image.open(gif_path)
        width, height = img.size

        # Get screen size
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        # Calculate position
        if position == "top-left":
            x, y = 0, 0
        elif position == "top-right":
            x = screen_width - width
            y = 0
        elif position == "bottom-left":
            x = 0
            y = screen_height - height
        elif position == "center":
            x = (screen_width - width) // 2
            y = (screen_height - height) // 2
        else:  # bottom-right (default)
            x = screen_width - width
            y = screen_height - height

        # Dynamically size window for GIF and description
        from tkinter import Text, Scrollbar, Frame, BOTH, RIGHT, Y

        desc_min_height = 60
        desc_max_height = 500
        desc_width = width

        # Estimate description height based on text length
        import textwrap
        wrapped = textwrap.wrap(description, width=50)
        desc_height = max(desc_min_height, min(desc_max_height, 20 * len(wrapped))) if description else 0
        desc_height = 150

        total_height = height + desc_height
        root.geometry(f"{width}x{total_height}+{x}+{y}")
        root.resizable(False, False)
        root.attributes("-topmost", True)
        try:
            root.wm_attributes("-type", "notification")
        except Exception:
            pass

        frames = []
        try:
            while True:
                frame = ImageTk.PhotoImage(img.copy())
                frames.append(frame)
                img.seek(len(frames))
        except EOFError:
            pass

        if len(frames) == 0:
            print(f"Could not load frames from {gif_path}")
            root.destroy()
            return

        delay = img.info.get('duration', 100)
        label = Label(root)
        label.pack()
        animate_gif(label, frames, delay)

        if description:
            desc_frame = Frame(root, height=desc_height, width=desc_width)
            desc_frame.pack(fill="x", padx=5, pady=5, expand=True)
            text_widget = Text(desc_frame, wrap="word", height=int(desc_height/20), width=int(desc_width/10), font=("Arial", 12), bg="white")
            text_widget.insert("1.0", description)
            text_widget.config(state="disabled")
            text_widget.pack(side="left", fill=BOTH, expand=True)
            if desc_height == desc_max_height:
                scrollbar = Scrollbar(desc_frame, command=text_widget.yview)
                text_widget.config(yscrollcommand=scrollbar.set)
                scrollbar.pack(side=RIGHT, fill=Y)

        root.after(duration * 1000, root.destroy)
        root.mainloop()

    def _show_with_feh():
        os.system(f"feh --auto-zoom --no-raise --no-focus -Y -D {duration} '{gif_path}' &")

    def _show():
        # Save the currently focused window id
        win_id = get_focused_window()
        # Prefer feh if available
        if os.system("which feh > /dev/null 2>&1") == 0:
            _show_with_feh()
        else:
            _show_with_tkinter()
        # Give the reminder window a moment to appear, then restore focus
        time.sleep(0.5)
        restore_focus(win_id)

    t = threading.Thread(target=_show)
    t.start()

def main():
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
    args = parser.parse_args()

    gif_files = get_gif_files()
    if not gif_files:
        print(f"No GIF files found in {GIF_DIR}")
        sys.exit(1)

    gif_desc_map = load_gif_descriptions()

    print(f"Move reminder started! Every {args.interval} minutes a random exercise GIF will pop up.")
    print("Press Ctrl+C to stop.")

    try:
        while True:
            gif_path = random.choice(gif_files)
            gif_name = os.path.basename(gif_path)
            description = gif_desc_map.get(gif_name, "")
            print(f"Showing: {gif_name}")
            if description:
                print(f"Description: {description}")
            show_gif(gif_path, description=description, duration=args.duration, position=args.position)
            time.sleep(args.interval * 60)
    except KeyboardInterrupt:
        print("\nMove reminder stopped.")

if __name__ == "__main__":
    main()