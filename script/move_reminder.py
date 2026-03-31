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

def animate_gif(label, frames, delay, frame_idx=0, anim_state=None):
    frame = frames[frame_idx]
    label.config(image=frame)
    label.image = frame
    next_idx = (frame_idx + 1) % len(frames)
    # Cancel previous animation if anim_state is provided
    if anim_state is not None:
        if anim_state["timer_id"]:
            label.after_cancel(anim_state["timer_id"])
        anim_state["timer_id"] = label.after(delay, animate_gif, label, frames, delay, next_idx, anim_state)
    else:
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
        import textwrap
        from tkinter import Text, Scrollbar, Frame, BOTH, RIGHT, Y, Button

        # Load all gif files and descriptions for "Next exercise"
        gif_files = get_gif_files()
        gif_desc_map = load_gif_descriptions()

        root = Tk()
        root.title("Move Reminder!")

        # Helper to load gif frames (must pass root as master)
        def load_gif_frames(gif_path):
            img = Image.open(gif_path)
            frames = []
            try:
                while True:
                    frame = ImageTk.PhotoImage(img.copy(), master=root)
                    frames.append(frame)
                    img.seek(len(frames))
            except EOFError:
                pass
            return frames, img.info.get('duration', 100), img.size

        # State for current gif/desc
        current = {
            "gif_path": gif_path,
            "description": description,
            "frames": [],
            "delay": 100,
            "width": 0,
            "height": 0,
        }

        # Load initial gif
        frames, delay, (width, height) = load_gif_frames(current["gif_path"])
        current["frames"] = frames
        current["delay"] = delay
        current["width"] = width
        current["height"] = height

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

        desc_min_height = 60
        desc_max_height = 500
        desc_width = width

        wrapped = textwrap.wrap(current["description"], width=50)
        desc_height = max(desc_min_height, min(desc_max_height, 20 * len(wrapped))) if current["description"] else 0
        desc_height = 150

        total_height = height + desc_height + 40  # Add space for button
        root.geometry(f"{width}x{total_height}+{x}+{y}")
        root.resizable(False, False)
        root.attributes("-topmost", True)
        try:
            root.wm_attributes("-type", "notification")
        except Exception:
            pass

        label = Label(root)
        label.pack()

        # Animation state for GIF
        anim_state = {"timer_id": None}

        animate_gif(label, current["frames"], current["delay"], 0, anim_state)

        desc_frame = Frame(root, height=desc_height, width=desc_width)
        desc_frame.pack(fill="x", padx=5, pady=5, expand=True)
        text_widget = Text(desc_frame, wrap="word", height=int(desc_height/20), width=int(desc_width/10), font=("Arial", 12), bg="white")
        text_widget.insert("1.0", current["description"])
        text_widget.config(state="disabled")
        text_widget.pack(side="left", fill=BOTH, expand=True)
        if desc_height == desc_max_height:
            scrollbar = Scrollbar(desc_frame, command=text_widget.yview)
            text_widget.config(yscrollcommand=scrollbar.set)
            scrollbar.pack(side=RIGHT, fill=Y)

        # Timer logic
        timer_id = [None]

        def reset_timer():
            if timer_id[0]:
                root.after_cancel(timer_id[0])
            timer_id[0] = root.after(duration * 1000, root.destroy)

        reset_timer()

        def next_exercise():
            # Pick a new random gif (not the current one)
            available = [f for f in gif_files if f != current["gif_path"]]
            if not available:
                return
            new_gif = random.choice(available)
            new_name = os.path.basename(new_gif)
            new_desc = gif_desc_map.get(new_name, "")
            # Load new frames
            frames, delay, (width, height) = load_gif_frames(new_gif)
            if not frames:
                return
            # Update state
            current["gif_path"] = new_gif
            current["description"] = new_desc
            current["frames"] = frames
            current["delay"] = delay
            current["width"] = width
            current["height"] = height
            # Cancel previous animation and start new one
            animate_gif(label, frames, delay, 0, anim_state)
            # Update description
            text_widget.config(state="normal")
            text_widget.delete("1.0", "end")
            text_widget.insert("1.0", new_desc)
            text_widget.config(state="disabled")
            # Reset timer
            reset_timer()

        btn = Button(root, text="Next exercise", command=next_exercise, font=("Arial", 12))
        btn.pack(pady=5)

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