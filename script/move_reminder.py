#!/usr/bin/env python3

import argparse
import os
import random
import sys
import time
import threading
import csv
import json

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
DATA_MD = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../exercise/reminder-data.md')

def load_gif_descriptions():
    mapping = {}
    current_gif = None
    area = None
    action = None
    desc_lines = []
    with open(DATA_MD, encoding='utf-8') as mdfile:
        for line in mdfile:
            line = line.rstrip('\n')
            if line.startswith('## '):
                if current_gif:
                    mapping[current_gif] = {
                        "description": '\n'.join(desc_lines).strip(),
                        "area": area,
                        "action": action
                    }
                current_gif = line[3:].strip()
                area = None
                action = None
                desc_lines = []
            elif current_gif is not None:
                if line.startswith('**Area:**'):
                    area = line.split('**Area:**', 1)[1].strip().strip()
                elif line.startswith('**Action:**'):
                    action = line.split('**Action:**', 1)[1].strip().strip()
                elif line.strip() == '':
                    continue
                else:
                    desc_lines.append(line)
        # Add last gif
        if current_gif:
            mapping[current_gif] = {
                "description": '\n'.join(desc_lines).strip(),
                "area": area,
                "action": action
            }
    return mapping

def get_gif_files():
    # Only GIFs referenced in reminder-data.csv
    gif_desc_map = load_gif_descriptions()
    csv_gifs = set(gif_desc_map.keys())
    return [
        os.path.join(GIF_DIR, f)
        for f in os.listdir(GIF_DIR)
        if f.lower().endswith('.gif') and f in csv_gifs
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
            "area": gif_desc_map.get(os.path.basename(gif_path), {}).get("area", ""),
            "action": gif_desc_map.get(os.path.basename(gif_path), {}).get("action", ""),
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

        area_action_height = 80  # Increased estimate for area/action labels
        button_height = 70  # Slightly increased for two buttons
        desc_min_height = 60
        desc_max_height = 500
        desc_width = width

        wrapped = textwrap.wrap(current["description"], width=50)
        desc_height = max(desc_min_height, min(desc_max_height, 20 * len(wrapped))) if current["description"] else 0

        # Calculate available height for GIF after reserving space for area/action, description, and buttons
        reserved_height = area_action_height + desc_height + button_height
        max_gif_height = screen_height - reserved_height
        display_height = min(height, max_gif_height)
        total_height = area_action_height + display_height + desc_height + button_height

        # If GIF is too tall, scale it down
        if height > max_gif_height:
            scale = max_gif_height / height
            display_width = int(width * scale)
            subsample_factor = int(height / max_gif_height)
        else:
            display_width = width
            subsample_factor = 1

        # Enforce minimum window width for buttons
        min_window_width = 350
        window_width = max(display_width, min_window_width)

        # Adjust x position for centered GIF if window is wider than GIF
        if window_width > display_width:
            x = x - ((window_width - display_width) // 2)

        # Resize window to fit everything
        root.geometry(f"{window_width}x{total_height}+{x}+{y}")
        root.resizable(False, False)
        root.attributes("-topmost", True)
        try:
            root.wm_attributes("-type", "notification")
        except Exception:
            pass

        # Area and Action labels
        area_label = Label(
            root,
            text=f"Area: {current['area']}",
            font=("Arial", 14, "bold"),
            bg="white",
            anchor="w",
            justify="left",
            wraplength=window_width-10
        )
        area_label.pack(fill="x", padx=5, pady=(5,0))
        action_label = Label(
            root,
            text=f"Action: {current['action']}",
            font=("Arial", 13),
            bg="white",
            anchor="w",
            justify="left",
            wraplength=window_width-10
        )
        action_label.pack(fill="x", padx=5, pady=(0,5))

        label = Label(root)
        label.pack()
        # If GIF is scaled, resize frames
        if subsample_factor > 1:
            resized_frames = []
            for frame in current["frames"]:
                img = frame.subsample(subsample_factor, subsample_factor)
                resized_frames.append(img)
            current["frames"] = resized_frames

        # Animation state for GIF
        anim_state = {"timer_id": None}

        animate_gif(label, current["frames"], current["delay"], 0, anim_state)

        desc_frame = Frame(root, height=desc_height, width=desc_width)
        desc_frame.pack(fill="x", padx=5, pady=5, expand=True)
        text_widget = Text(
            desc_frame,
            wrap="word",
            height=int(desc_height/20),
            width=int(desc_width/10),
            font=("Arial", 12),
            bg="white"
        )
        text_widget.insert("1.0", current["description"])
        text_widget.config(state="disabled")
        text_widget.pack(side="left", fill=BOTH, expand=True)
        # Always add scrollbar if text is long or window is shrunk
        scrollbar = Scrollbar(desc_frame, command=text_widget.yview)
        text_widget.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=RIGHT, fill=Y)

        # Timer logic
        timer_id = [None]

        def reset_timer():
            # Always cancel previous timer and set a new one
            try:
                if timer_id[0]:
                    root.after_cancel(timer_id[0])
            except Exception:
                pass
            timer_id[0] = root.after(duration * 1000, root.destroy)

        reset_timer()

        def next_exercise():
            # Filter exercises based on personalized configuration
            personalized_gifs = []
            config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "personalized_exercises.json")
            if os.path.exists(config_path):
                try:
                    with open(config_path, "r", encoding="utf-8") as f:
                        personalized_gifs = json.load(f)
                except json.JSONDecodeError:
                    print("[DEBUG] Error: Malformed JSON in personalized configuration. Falling back to all exercises.")
                    personalized_gifs = []
                except Exception as e:
                    print(f"[DEBUG] Error loading personalized configuration: {e}. Falling back to all exercises.")
                    personalized_gifs = []
            else:
                print("[DEBUG] Personalized configuration file not found. Falling back to all exercises.")

            # Fallback to all exercises if personalized config is empty
            if not personalized_gifs:
                print("[DEBUG] Personalized configuration is empty. Using all exercises.")
                personalized_gifs = [os.path.basename(f) for f in gif_files]

            # Pick a new random gif (not the current one) ONLY from checked (included) exercises
            available = [f for f in gif_files if f != current["gif_path"] and os.path.basename(f) in personalized_gifs]
            # Only show exercises in personalized_gifs; if only one is available, do nothing
            if not available:
                print("[DEBUG] No available personalized exercises to choose from.")
                return
            new_gif = random.choice(available)
            new_name = os.path.basename(new_gif)
            gif_info = gif_desc_map.get(new_name, {})
            new_desc = gif_info.get("description", "")
            new_area = gif_info.get("area", "")
            new_action = gif_info.get("action", "")
            # Log the description for debugging
            print(f"[DEBUG] Next exercise: {new_name}, description: '{new_desc}'")
            # If description is empty or suspicious, set a default
            if not new_desc or new_desc.strip() == "!!":
                new_desc = "No description available for this exercise."
            # Load new frames
            frames, delay, (width, height) = load_gif_frames(new_gif)
            if not frames:
                return
            # Estimate new description height
            area_action_height = 80
            button_height = 70
            desc_min_height = 60
            desc_max_height = 500
            desc_width = width
            wrapped = textwrap.wrap(new_desc, width=50)
            desc_height = max(desc_min_height, min(desc_max_height, 20 * len(wrapped))) if new_desc else desc_min_height

            reserved_height = area_action_height + desc_height + button_height
            max_gif_height = root.winfo_screenheight() - reserved_height
            display_height = min(height, max_gif_height)
            total_height = area_action_height + display_height + desc_height + button_height

            if height > max_gif_height:
                scale = max_gif_height / height
                display_width = int(width * scale)
            else:
                display_width = width

            # Enforce minimum window width for buttons
            min_window_width = 350
            window_width = max(display_width, min_window_width)

            # Calculate position (recompute x, y)
            screen_width = root.winfo_screenwidth()
            screen_height = root.winfo_screenheight()
            if position == "top-left":
                x, y = 0, 0
            elif position == "top-right":
                x = screen_width - window_width
                y = 0
            elif position == "bottom-left":
                x = 0
                y = screen_height - total_height
            elif position == "center":
                x = (screen_width - window_width) // 2
                y = (screen_height - total_height) // 2
            else:  # bottom-right (default)
                x = screen_width - window_width
                y = screen_height - total_height

            root.geometry(f"{window_width}x{total_height}+{x}+{y}")

            # Update state
            current["gif_path"] = new_gif
            current["description"] = new_desc
            current["area"] = new_area
            current["action"] = new_action
            current["frames"] = frames
            current["delay"] = delay
            current["width"] = width
            current["height"] = height
            # Cancel previous animation and start new one
            animate_gif(label, frames, delay, 0, anim_state)
            # If GIF is scaled, resize frames
            if subsample_factor > 1:
                resized_frames = []
                for frame in frames:
                    img = frame.subsample(subsample_factor, subsample_factor)
                    resized_frames.append(img)
                current["frames"] = resized_frames
                animate_gif(label, resized_frames, delay, 0, anim_state)
            # Update area and action labels
            area_label.config(text=f"Area: {new_area}", wraplength=window_width-10)
            action_label.config(text=f"Action: {new_action}", wraplength=window_width-10)
            # Update description
            text_widget.config(state="normal")
            text_widget.delete("1.0", "end")
            text_widget.insert("1.0", new_desc)
            text_widget.config(state="disabled")
            # Update text widget height
            text_widget.config(height=int(desc_height/20))
            # Add scrollbar if needed
            if len(wrapped) > desc_height // 20 or total_height > root.winfo_screenheight() or desc_height == desc_max_height:
                if not any(isinstance(w, Scrollbar) for w in desc_frame.winfo_children()):
                    scrollbar = Scrollbar(desc_frame, command=text_widget.yview)
                    text_widget.config(yscrollcommand=scrollbar.set)
                    scrollbar.pack(side=RIGHT, fill=Y)
            # Reset timer
            reset_timer()

        # Button frame at the bottom for both buttons
        button_frame = Frame(root)
        button_frame.pack(side="bottom", fill="x", pady=8)

        btn = Button(button_frame, text="Next", command=next_exercise, font=("Arial", 10), width=6, height=2)
        btn.pack(side="left", padx=(6,2), pady=4, fill="x", expand=True)

        close_btn = Button(button_frame, text="Close", command=root.destroy, font=("Arial", 10), width=6, height=2)
        close_btn.pack(side="right", padx=(2,6), pady=4, fill="x", expand=True)

        # Gear icon button (ozubene kolecko)
        from setup_page import open_setup_page


        def cancel_timer():
            try:
                if timer_id[0]:
                    root.after_cancel(timer_id[0])
                    timer_id[0] = None
            except Exception:
                pass

        gear_btn = Button(
            button_frame,
            text="⚙️",
            command=lambda: open_setup_page(root, reset_timer, cancel_timer),
            font=("Arial", 12),
            width=3,
            height=2
        )
        gear_btn.pack(side="right", padx=(2,2), pady=4)

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
    # Personalized config logic
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "personalized_exercises.json")
    personalized_gifs = []
    if os.path.exists(config_path):
        try:
            import json
            with open(config_path, "r", encoding="utf-8") as f:
                personalized_gifs = json.load(f)
            # Only use personalized list if it contains at least one valid gif
            if personalized_gifs:
                gif_files = [f for f in gif_files if os.path.basename(f) in personalized_gifs]
        except Exception:
            pass
    if not gif_files:
        print(f"No GIF files found in {GIF_DIR} or personalized config.")
        sys.exit(1)

    gif_desc_map = load_gif_descriptions()

    print(f"Move reminder started! Every {args.interval} minutes a random exercise GIF will pop up.")
    print("Press Ctrl+C to stop.")

    try:
        while True:
            gif_path = random.choice(gif_files)
            gif_name = os.path.basename(gif_path)
            gif_info = gif_desc_map.get(gif_name, {})
            description = gif_info.get("description", "")
            area = gif_info.get("area", "")
            action = gif_info.get("action", "")
            print(f"Showing: {gif_name}")
            if description:
                print(f"Description: {description}")
            if area:
                print(f"Area: {area}")
            if action:
                print(f"Action: {action}")
            show_gif(
                gif_path,
                description=description,
                duration=args.duration,
                position=args.position
            )
            time.sleep(args.interval * 60)
    except KeyboardInterrupt:
        print("\nMove reminder stopped.")

if __name__ == "__main__":
    main()