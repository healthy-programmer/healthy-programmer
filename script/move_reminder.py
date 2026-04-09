#!/usr/bin/env python3

from argument_parser import parse_args
import os
import random
import sys
import time
import threading
import csv
import json

from datetime import datetime, timedelta
from exercise_log import ExerciseLogger, ExerciseLogViewer
from lib import parse_working_hours, is_within_working_hours
from config_utils import load_config_and_gifs

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

from exercise_portfolio import load_gif_descriptions, get_gif_files
from ui_utils import animate_gif
from config_utils import get_active_gif_list

# Show a GIF reminder popup, using either Tkinter or feh, and restore focus after display.
def show_gif(gif_path, description="", duration=30, position="bottom-right", general_config=None, config_changed=None, timer_reset=None):
    """
    Show a GIF as a reminder, preferring 'feh' if available to avoid stealing focus.
    After showing, restore focus to the previously active window using xdotool if available.
    The popup window will appear at the specified position.
    """
    import subprocess

    # Get the window id of the currently focused window using xdotool.
    def get_focused_window():
        """Return the window id of the currently focused window using xdotool, or None."""
        try:
            win_id = subprocess.check_output(["xdotool", "getwindowfocus"]).decode().strip()
            return win_id
        except Exception:
            return None

    # Restore focus to the given window id using xdotool.
    def restore_focus(win_id):
        """Restore focus to the given window id using xdotool."""
        if win_id:
            try:
                subprocess.Popen(["xdotool", "windowactivate", "--sync", win_id])
            except Exception:
                pass

    def _show_with_tkinter():
        nonlocal general_config
        nonlocal config_changed
        if general_config is None:
            general_config = {
                "interval": 30,
                "duration": 30,
                "position": "bottom-right",
                "working_hours": "8:00-16:30"
            }
        import textwrap
        from tkinter import Text, Scrollbar, Frame, BOTH, RIGHT, Y, Button

        # Load all gif files and descriptions for "Next exercise"
        gif_files = get_gif_files()
        gif_desc_map = load_gif_descriptions(DATA_MD)

        root = Tk()
        root.title("Move Reminder!")

        # Helper to load gif frames (must pass root as master)
        # Load all frames from a GIF for animation in the popup.
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

        # Reset the timer for the popup window auto-close.
        def reset_timer():
            # Always cancel previous timer and set a new one
            try:
                if timer_id[0]:
                    root.after_cancel(timer_id[0])
            except Exception:
                pass
            timer_id[0] = root.after(duration * 1000, root.destroy)
            minutes = general_config["interval"] if general_config and "interval" in general_config else 30
            print(f"[DEBUG] Time to next exercise: {minutes}m 0s")
            # If timer_reset is provided, set it to True to signal main loop to reset timer
            if timer_reset is not None:
                timer_reset[0] = True

        reset_timer()

        def next_exercise():
            # Use shared config/gif logic
            from config_utils import load_config_and_gifs, get_active_gif_list
            if timer_reset is not None:
                timer_reset[0] = True

            config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "personal_setup.json")
            all_gif_files, selected_gifs, general_config = load_config_and_gifs(config_path, get_gif_files)
            available = get_active_gif_list(all_gif_files, selected_gifs, current["gif_path"])
            if not available:
                print("[DEBUG] No available personalized exercises to choose from.")
                return
            new_gif = random.choice(available)
            new_name = os.path.basename(new_gif)
            gif_info = gif_desc_map.get(new_name, {})
            new_desc = gif_info.get("description", "")
            new_area = gif_info.get("area", "")
            new_action = gif_info.get("action", "")
            print(f"[DEBUG] Next exercise: {new_name}, description: '{new_desc}'")
            if not new_desc or new_desc.strip() == "!!":
                new_desc = "No description available for this exercise."
            ExerciseLogger.log_exercise(new_gif, new_desc, new_area, new_action)
            frames, delay, (width, height) = load_gif_frames(new_gif)
            if not frames:
                return
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

            min_window_width = 350
            window_width = max(display_width, min_window_width)

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

            current["gif_path"] = new_gif
            current["description"] = new_desc
            current["area"] = new_area
            current["action"] = new_action
            current["frames"] = frames
            current["delay"] = delay
            current["width"] = width
            current["height"] = height
            animate_gif(label, frames, delay, 0, anim_state)
            if subsample_factor > 1:
                resized_frames = []
                for frame in frames:
                    img = frame.subsample(subsample_factor, subsample_factor)
                    resized_frames.append(img)
                current["frames"] = resized_frames
                animate_gif(label, resized_frames, delay, 0, anim_state)
            area_label.config(text=f"Area: {new_area}", wraplength=window_width-10)
            action_label.config(text=f"Action: {new_action}", wraplength=window_width-10)
            text_widget.config(state="normal")
            text_widget.delete("1.0", "end")
            text_widget.insert("1.0", new_desc)
            text_widget.config(state="disabled")
            text_widget.config(height=int(desc_height/20))
            if len(wrapped) > desc_height // 20 or total_height > root.winfo_screenheight() or desc_height == desc_max_height:
                if not any(isinstance(w, Scrollbar) for w in desc_frame.winfo_children()):
                    scrollbar = Scrollbar(desc_frame, command=text_widget.yview)
                    text_widget.config(yscrollcommand=scrollbar.set)
                    scrollbar.pack(side=RIGHT, fill=Y)
            reset_timer()

        # Button frame at the bottom for both buttons
        button_frame = Frame(root)
        button_frame.pack(side="bottom", fill="x", pady=8)

        btn = Button(button_frame, text="Next", command=next_exercise, font=("Arial", 10), width=6, height=2)
        btn.pack(side="left", padx=(6,2), pady=4, fill="x", expand=True)

        # Close the popup and set the config_changed flag if needed.
        def close_and_debug():
            if config_changed is not None:
                config_changed[0] = True
            if timer_reset is not None:
                timer_reset[0] = True
            reset_timer()
            root.destroy()

        close_btn = Button(button_frame, text="Close", command=close_and_debug, font=("Arial", 10), width=6, height=2)
        close_btn.pack(side="right", padx=(2,6), pady=4, fill="x", expand=True)

        # Log button
        # Open the exercise log viewer window.
        def open_log_viewer():
            # Pause timer when log screen opens
            cancel_timer()
            # Pass timer callbacks to ExerciseLogViewer
            ExerciseLogViewer(root, reset_timer, cancel_timer)

        log_btn = Button(button_frame, text="Log", command=open_log_viewer, font=("Arial", 10), width=6, height=2)
        log_btn.pack(side="right", padx=(2,2), pady=4, fill="x", expand=True)

        # Gear icon button (ozubene kolecko)
        from setup_page import open_setup_page

        # Pass general_config to setup page

        # Cancel the current timer for the popup window.
        def cancel_timer():
            try:
                if timer_id[0]:
                    root.after_cancel(timer_id[0])
                    timer_id[0] = None
            except Exception:
                pass

        # Move open_setup_and_set_flag definition here so it is available for the lambda below
        # Open the setup page and set the config_changed flag if configuration is updated.
        def open_setup_and_set_flag(parent, config_changed_flag=None):
            from setup_page import open_setup_page
            def reset_timer_callback():
                if config_changed_flag is not None:
                    config_changed_flag[0] = True
                reset_timer()
            def cancel_timer_callback():
                cancel_timer()
            open_setup_page(parent, reset_timer_callback, cancel_timer_callback)

        # Defensive: ensure general_config is always defined
        config_for_setup = general_config if 'general_config' in locals() else {
            "interval": 30,
            "duration": 30,
            "position": "bottom-right",
            "working_hours": "8:00-16:30"
        }
        gear_btn = Button(
            button_frame,
            text="⚙️",
            command=lambda: open_setup_and_set_flag(root, config_changed),
            font=("Arial", 12),
            width=3,
            height=2
        )
        gear_btn.pack(side="right", padx=(2,2), pady=4)

        # Log the initial exercise when popup is shown
        ExerciseLogger.log_exercise(current["gif_path"], current["description"], current["area"], current["action"])

        root.mainloop()

    # Show the GIF using the feh image viewer (if available).
    def _show_with_feh():
        os.system(f"feh --auto-zoom --no-raise --no-focus -Y -D {duration} '{gif_path}' &")

    # Show the GIF reminder using the preferred method and restore focus after display.
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

# Main entry point for the move reminder application.
def main():
    # Main entry point for the move reminder application.
    # Add a flag to signal timer reset from popup actions
    timer_reset = [False]

    # Parses command-line arguments, loads configuration and exercise portfolio,
    # and starts the reminder loop that periodically shows exercise GIFs during working hours.
    # Parse command-line arguments (e.g., --interval, --duration, etc.)
    args = parse_args()

    # Build the path to the personal configuration file
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "personal_setup.json")
    # Mutable flag to detect if config was changed in the UI
    config_changed = [False]
    # Load all available GIFs, selected GIFs, and general config from the config file
    gif_files, selected_gifs, general_config = load_config_and_gifs(config_path, get_gif_files)
    # Exit if no GIFs are found (cannot run reminders)
    if not gif_files:
        print(f"No GIF files found in {GIF_DIR} or personalized config.")
        sys.exit(1)
    # Load the mapping of GIF filenames to their descriptions, areas, and actions
    gif_desc_map = load_gif_descriptions(DATA_MD)

    # Extract reminder parameters from config
    interval = general_config["interval"]        # Minutes between reminders
    duration = general_config["duration"]        # How long the popup stays visible
    position = general_config["position"]        # Where to display the popup
    working_hours = general_config["working_hours"]  # Time range for reminders

    # Filter GIFs to only those selected in the config (if any)
    # Is a list of full file paths from all available GIFs, filtered to only those whose basenames
    # are in selected_gifs. If selected_gifs is empty, it falls back to all GIFs.
    gif_files = get_active_gif_list(gif_files, selected_gifs)

    # Print startup info
    print(f"Move reminder started! Every {interval} minutes a random exercise GIF will pop up.")
    print("Press Ctrl+C to stop.")

    try:
        # Parse working hours into start/end hour and minute
        (start_h, start_m), (end_h, end_m) = parse_working_hours(working_hours)

        while True:
            # Get the current time
            now = datetime.now()
            # Check if we are within working hours
            if is_within_working_hours(now, start_h, start_m, end_h, end_m):
                # Pick a random GIF from the available list
                gif_path = random.choice(gif_files)
                gif_name = os.path.basename(gif_path)
                # Get description, area, and action for the selected GIF
                gif_info = gif_desc_map.get(gif_name, {})
                description = gif_info.get("description", "")
                area = gif_info.get("area", "")
                action = gif_info.get("action", "")
                # Print info about the selected exercise
                print(f"[{now:%Y-%m-%d %H:%M:%S}] Showing: {gif_name}")
                if description:
                    print(f"Description: {description}")
                if area:
                    print(f"Area: {area}")
                if action:
                    print(f"Action: {action}")
                # Show the GIF popup reminder
                show_gif(
                    gif_path,
                    description=description,
                    duration=duration,
                    position=position,
                    general_config=general_config,
                    config_changed=config_changed,
                    timer_reset=timer_reset
                )
            else:
                # If outside working hours, skip showing a reminder
                print(f"[{now:%Y-%m-%d %H:%M:%S}] Outside working hours ({working_hours}), skipping reminder.")

            # Calculate when the next reminder should occur
            next_reminder_time = datetime.now() + timedelta(minutes=interval)
            seconds_remaining = interval * 60

            # Wait until it's time for the next reminder, handling config reloads and working hours
            while seconds_remaining > 0:
                now = datetime.now()
                if config_changed[0]:
                    # If config was changed in the UI, reload all config and update variables
                    gif_files, selected_gifs, general_config = load_config_and_gifs(config_path, get_gif_files)
                    interval = general_config["interval"]
                    duration = general_config["duration"]
                    position = general_config["position"]
                    working_hours = general_config["working_hours"]
                    (start_h, start_m), (end_h, end_m) = parse_working_hours(working_hours)
                    print(f"[INFO] Config reloaded: interval={interval}, duration={duration}, position={position}, working_hours={working_hours}")
                    config_changed[0] = False
                    # Restart timer for next reminder
                    next_reminder_time = datetime.now() + timedelta(minutes=interval)
                    print(f"[DEBUG] Time to next exercise: {interval}m 0s")
                    seconds_remaining = interval * 60
                    break
                if timer_reset[0]:
                    # If timer reset was requested from popup, reset timer and clear flag
                    timer_reset[0] = False
                    next_reminder_time = datetime.now() + timedelta(minutes=interval)
                    print(f"[DEBUG] Timer reset from popup. Time to next exercise: {interval}m 0s")
                    seconds_remaining = interval * 60
                    break
                if not is_within_working_hours(now, start_h, start_m, end_h, end_m):
                    # If outside working hours, calculate how long to sleep until working hours resume
                    today_start = now.replace(hour=start_h, minute=start_m, second=0, microsecond=0)
                    if now < today_start:
                        wait_seconds = (today_start - now).total_seconds()
                    else:
                        tomorrow = now + timedelta(days=1)
                        next_start = tomorrow.replace(hour=start_h, minute=start_m, second=0, microsecond=0)
                        wait_seconds = (next_start - now).total_seconds()
                    print(f"[DEBUG] Sleeping until working hours resume in {int(wait_seconds//60)}m {int(wait_seconds%60)}s")
                    time.sleep(min(wait_seconds, seconds_remaining))
                    seconds_remaining -= min(wait_seconds, seconds_remaining)
                else:
                    # If within working hours, sleep in 1-minute increments until next reminder
                    time_left = next_reminder_time - now
                    minutes_left = int(time_left.total_seconds() // 60)
                    seconds_left = int(time_left.total_seconds() % 60)
                    print(f"[DEBUG] Time to next exercise: {minutes_left}m {seconds_left}s")
                    sleep_time = min(60, seconds_remaining)
                    time.sleep(sleep_time)
                    seconds_remaining -= sleep_time
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        print("\nMove reminder stopped.")
if __name__ == "__main__":
    main()