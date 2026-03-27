#!/usr/bin/env python3

import argparse
import os
import random
import sys
import time
import threading

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

def show_gif(gif_path, duration=30):
    def _show():
        root = Tk()
        root.title("Move Reminder!")
        root.geometry("+500+300")
        root.resizable(False, False)

        img = Image.open(gif_path)
        frames = []
        try:
            while True:
                frame = ImageTk.PhotoImage(img.copy())
                frames.append(frame)
                img.seek(len(frames))  # Move to next frame
        except EOFError:
            pass  # End of sequence

        if len(frames) == 0:
            print(f"Could not load frames from {gif_path}")
            root.destroy()
            return

        delay = img.info.get('duration', 100)  # Duration in ms per frame
        label = Label(root)
        label.pack()
        animate_gif(label, frames, delay)

        # Close window after duration seconds
        root.after(duration * 1000, root.destroy)
        root.mainloop()
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
    args = parser.parse_args()

    gif_files = get_gif_files()
    if not gif_files:
        print(f"No GIF files found in {GIF_DIR}")
        sys.exit(1)

    print(f"Move reminder started! Every {args.interval} minutes a random exercise GIF will pop up.")
    print("Press Ctrl+C to stop.")

    try:
        while True:
            gif_path = random.choice(gif_files)
            print(f"Showing: {os.path.basename(gif_path)}")
            show_gif(gif_path, duration=args.duration)
            time.sleep(args.interval * 60)
    except KeyboardInterrupt:
        print("\nMove reminder stopped.")

if __name__ == "__main__":
    main()