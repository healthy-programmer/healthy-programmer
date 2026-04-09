import os
import json
from datetime import datetime
from config_utils import load_config_and_gifs, save_config_to_file
from tkinter import (
    Toplevel, Frame, Canvas, Scrollbar, Checkbutton, IntVar, Label, Button, StringVar
)
from PIL import Image, ImageTk

def load_gif_descriptions(data_md_path):
    mapping = {}
    current_gif = None
    area = None
    action = None
    category = None
    desc_lines = []
    with open(data_md_path, encoding='utf-8') as mdfile:
        for line in mdfile:
            line = line.rstrip('\n')
            if line.startswith('## '):
                if current_gif:
                    mapping[current_gif] = {
                        "description": '\n'.join(desc_lines).strip(),
                        "area": area,
                        "action": action,
                        "category": category
                    }
                current_gif = line[3:].strip()
                area = None
                action = None
                category = None
                desc_lines = []
            elif current_gif is not None:
                if line.startswith('**Area:**'):
                    area = line.split('**Area:**', 1)[1].strip().strip()
                elif line.startswith('**Action:**'):
                    action = line.split('**Action:**', 1)[1].strip().strip()
                elif line.startswith('**Category:**'):
                    category = line.split('**Category:**', 1)[1].strip().strip()
                elif line.strip() == '':
                    continue
                else:
                    desc_lines.append(line)
        # Add last gif
        if current_gif:
            mapping[current_gif] = {
                "description": '\n'.join(desc_lines).strip(),
                "area": area,
                "action": action,
                "category": category
            }
    return mapping

from tkinter import ttk  # For tabs

def open_setup_page(parent, reset_timer_callback, cancel_timer_callback):
    setup_win = Toplevel(parent)
    setup_win.title("Personalize Exercises")
    setup_win.geometry("600x600")
    setup_win.resizable(False, False)
    # Cancel the reminder window timer immediately
    if cancel_timer_callback:
        cancel_timer_callback()
    # Always load config from file
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "personal_setup.json")

    # Use config_utils.load_config_and_gifs for config loading
    def get_gif_files():
        # Load all GIFs from the resized images directory, filtered by those present in the descriptions
        images_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../exercise/images/resized')
        data_md_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../exercise/reminder-data.md')
        gif_desc_map = load_gif_descriptions(data_md_path)
        return [
            os.path.join(images_dir, f)
            for f in os.listdir(images_dir)
            if f.lower().endswith('.gif') and f in gif_desc_map.keys()
        ]

    # DEBUG: Print config_path before loading
    print(f"[DEBUG] Using config_path: {config_path}")
    gif_files, selected_gifs, general_config = load_config_and_gifs(config_path, get_gif_files)
    # Always update UI variables from general_config to reflect latest file values
    interval_var_value = general_config.get("interval", 30)
    duration_var_value = general_config.get("duration", 30)
    position_var_value = general_config.get("position", "bottom-right")
    working_hours_var_value = general_config.get("working_hours", "8:00-16:30")

    # Create notebook for tabs
    notebook = ttk.Notebook(setup_win)
    notebook.pack(fill="both", expand=True)

    # General setup tab
    general_tab = Frame(notebook, background="#f0f0f0")
    notebook.add(general_tab, text="General Setup")

    # Selected exercises tab
    exercises_tab = Frame(notebook, background="#f0f0f0")
    notebook.add(exercises_tab, text="Selected Exercises")

    # General setup UI
    Label(general_tab, text="Interval (minutes):", font=("Arial", 11), background="#f0f0f0").pack(anchor="w", padx=8, pady=4)
    interval_var = IntVar(value=interval_var_value)
    interval_entry = ttk.Entry(general_tab, textvariable=interval_var, font=("Arial", 11))
    interval_entry.pack(anchor="w", padx=8, pady=4)

    Label(general_tab, text="Duration (seconds):", font=("Arial", 11), background="#f0f0f0").pack(anchor="w", padx=8, pady=4)
    duration_var = IntVar(value=duration_var_value)
    duration_entry = ttk.Entry(general_tab, textvariable=duration_var, font=("Arial", 11))
    duration_entry.pack(anchor="w", padx=8, pady=4)

    Label(general_tab, text="Position:", font=("Arial", 11), background="#f0f0f0").pack(anchor="w", padx=8, pady=4)
    position_var = StringVar(value=position_var_value)
    position_menu = ttk.Combobox(general_tab, textvariable=position_var, values=["top-left", "top-right", "bottom-left", "bottom-right", "center"], font=("Arial", 11))
    position_menu.pack(anchor="w", padx=8, pady=4)

    Label(general_tab, text="Working Hours:", font=("Arial", 11), background="#f0f0f0").pack(anchor="w", padx=8, pady=4)
    working_hours_var = StringVar(value=working_hours_var_value)
    working_hours_entry = ttk.Entry(general_tab, textvariable=working_hours_var, font=("Arial", 11))
    working_hours_entry.pack(anchor="w", padx=8, pady=4)

    # --- Move the exercise selection UI to the exercises_tab ---

    # Button row for exercises tab
    # Move button row outside the tab container
    button_row = Frame(setup_win, background="#f0f0f0")
    button_row.pack(side="top", fill="x", pady=(8,2))

    select_all_btn = Button(button_row, text="Select all", font=("Arial", 11), width=10, height=1)
    select_all_btn.pack(side="left", padx=(8,4))
    deselect_all_btn = Button(button_row, text="Deselect all", font=("Arial", 11), width=12, height=1)
    deselect_all_btn.pack(side="left", padx=(4,8))
    save_btn = Button(button_row, text="Save", font=("Arial", 11), bg="#4caf50", fg="white", width=10, height=1)
    save_btn.pack(side="left", padx=(8,4))
    close_btn = Button(button_row, text="Close", font=("Arial", 11), bg="#f44336", fg="white", width=10, height=1)
    close_btn.pack(side="left", padx=(4,8))
    save_label = Label(button_row, text="", font=("Arial", 11), background="#f0f0f0")
    save_label.pack(side="left", padx=(8,4))

    selected_count_label = Label(button_row, text="", font=("Arial", 11), background="#d8f5d3")
    selected_count_label.pack(side="left", padx=(8,4))

    # Move exercise selection UI to exercises_tab
    canvas = Canvas(exercises_tab, borderwidth=0, background="#f0f0f0")
    frame = Frame(canvas, background="#f0f0f0")
    scrollbar = Scrollbar(exercises_tab, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="top", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    canvas.create_window((0,0), window=frame, anchor="nw")

    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
    frame.bind("<Configure>", on_frame_configure)

    # Mouse wheel binding helper (unified with log screen)
    def _bind_mousewheel_to_widget(widget):
        widget.bind("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        widget.bind("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
        widget.bind("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))
    # Also bind to the main window for global scroll
    setup_win.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

    # Updated config path and structure
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "personal_setup.json")
    # Always reload selected_gifs from file, but do NOT overwrite general_config here
    # Use config_utils.load_config_and_gifs to get selected_gifs (as gif_files)
    # Already loaded above: gif_files_for_selection, selected_gifs

    gif_desc_map = load_gif_descriptions(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../exercise/reminder-data.md'))

    # Extract unique categories
    categories = set()
    for gif_info in gif_desc_map.values():
        cat = gif_info.get("category")
        if cat:
            categories.add(cat)
    categories = sorted(categories)

    # Category filter state
    category_vars = {cat: IntVar(value=1) for cat in categories}

    # Category filter UI
    category_row = Frame(exercises_tab, background="#e0e0e0")
    category_row.pack(side="top", fill="x", pady=(2,2))
    Label(category_row, text="Filter by category:", font=("Arial", 11), background="#e0e0e0").pack(side="left", padx=(8,4))
    for cat in categories:
        cb = Checkbutton(category_row, text=cat, variable=category_vars[cat], background="#e0e0e0", font=("Arial", 10))
        cb.pack(side="left", padx=(2,2))
    def select_all_categories():
        for var in category_vars.values():
            var.set(1)
        update_gif_rows()
    def deselect_all_categories():
        for var in category_vars.values():
            var.set(0)
        update_gif_rows()
    Button(category_row, text="Select all", command=select_all_categories, font=("Arial", 10), width=8).pack(side="left", padx=(8,2))
    Button(category_row, text="Deselect all", command=deselect_all_categories, font=("Arial", 10), width=10).pack(side="left", padx=(2,8))

    gif_files = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), '../exercise/images/resized', f)
        for f in os.listdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../exercise/images/resized'))
        if f.lower().endswith('.gif') and f in gif_desc_map.keys()
    ]

    checkbox_vars = {}
    anim_states = {}
    row_frames = {}

    def update_selected_count():
        count = sum(var.get() for var in checkbox_vars.values())
        selected_count_label.config(text=f"Selected: {count}")

    def update_row_backgrounds():
        for gif_name, var in checkbox_vars.items():
            bg = "#d8f5d3" if var.get() == 1 else "#f0f0f0"
            row_frame = row_frames.get(gif_name)
            if row_frame:
                row_frame.config(background=bg)
                # Also update content_row background for consistency
                for child in row_frame.winfo_children():
                    child.config(background=bg)


    def load_gif_frames_for_thumb(gif_path):
        img = Image.open(gif_path)
        frames = []
        thumb_height = 74
        orig_width, orig_height = img.size
        thumb_width = int(orig_width * (thumb_height / orig_height))
        thumb_size = (thumb_width, thumb_height)
        try:
            while True:
                thumb_img = img.copy().resize(thumb_size, Image.LANCZOS)
                frame = ImageTk.PhotoImage(thumb_img, master=setup_win)
                frames.append(frame)
                img.seek(len(frames))
        except EOFError:
            pass
        return frames, img.info.get('duration', 100)

    # Store GIF row widgets for filtering
    gif_row_data = []

    def create_gif_row(gif_path, selected_gifs):
        gif_name = os.path.basename(gif_path)
        gif_info = gif_desc_map.get(gif_name, {})
        desc = gif_info.get("description", "")
        area = gif_info.get("area", "")
        action = gif_info.get("action", "")
        category = gif_info.get("category", "")

        row_frame = Frame(frame, background="#f0f0f0", relief="groove", borderwidth=1)
        row_frames[gif_name] = row_frame

        content_row = Frame(row_frame, background="#f0f0f0")
        content_row.pack(fill="x", padx=4, pady=4)

        var = IntVar(value=1 if gif_name in selected_gifs else 0)
        checkbox = Checkbutton(content_row, text="Include", variable=var, background="#f0f0f0", font=("Arial", 10))
        checkbox.pack(side="left", anchor="n", padx=(0, 8), pady=4)
        checkbox_vars[gif_name] = var

        def on_checkbox_toggle(*args):
            update_selected_count()
            update_row_backgrounds()
        var.trace_add("write", on_checkbox_toggle)

        try:
            thumb_frames, thumb_delay = load_gif_frames_for_thumb(gif_path)
        except Exception:
            thumb_frames, thumb_delay = [], 100

        thumb_label = Label(content_row, background="#f0f0f0")
        thumb_label.pack(side="left", anchor="n", padx=(0, 8), pady=4)

        anim_states[gif_name] = {"timer_id": None}

        def animate_thumb(label, frames, delay, frame_idx=0, anim_state=None):
            if not frames:
                label.config(text="[GIF]")
                return
            frame = frames[frame_idx]
            label.config(image=frame)
            label.image = frame
            next_idx = (frame_idx + 1) % len(frames)
            if anim_state is not None:
                if anim_state["timer_id"]:
                    label.after_cancel(anim_state["timer_id"])
                anim_state["timer_id"] = label.after(delay, animate_thumb, label, frames, delay, next_idx, anim_state)
            else:
                label.after(delay, animate_thumb, label, frames, delay, next_idx)

        animate_thumb(thumb_label, thumb_frames, thumb_delay, 0, anim_states[gif_name])

        desc_text = f"{desc}\nArea: {area}\nAction: {action}\nCategory: {category}"
        desc_label = Label(
            content_row,
            text=desc_text,
            justify="left",
            wraplength=340,
            background="#f0f0f0",
            font=("Arial", 11)
        )
        desc_label.pack(side="left", anchor="n", fill="y", padx=(0, 4), pady=4)
        content_row.config(width=580)

        # Bind mouse wheel events to all widgets for unified scroll
        _bind_mousewheel_to_widget(row_frame)
        _bind_mousewheel_to_widget(content_row)
        _bind_mousewheel_to_widget(checkbox)
        _bind_mousewheel_to_widget(thumb_label)
        _bind_mousewheel_to_widget(desc_label)

        gif_row_data.append({
            "gif_name": gif_name,
            "category": category,
            "row_frame": row_frame,
        })

        return row_frame

    def update_gif_rows():
        # Remove all rows
        for data in gif_row_data:
            data["row_frame"].pack_forget()
        # Show only rows matching selected categories
        selected_cats = {cat for cat, var in category_vars.items() if var.get() == 1}
        for data in gif_row_data:
            if data["category"] in selected_cats:
                data["row_frame"].pack(fill="x", padx=4, pady=4)
        # Force scroll to top and update scrollregion
        canvas.update_idletasks()
        canvas.yview_moveto(0)
        canvas.configure(scrollregion=canvas.bbox("all"))

    # Create GIF rows
    for idx, gif_path in enumerate(gif_files):
        create_gif_row(gif_path, selected_gifs)

    # Initial filter
    update_gif_rows()


    def save_config():
        selected = [name for name, var in checkbox_vars.items() if var.get() == 1]
        try:
            # Update general config from UI
            general_config["interval"] = interval_var.get()
            general_config["duration"] = duration_var.get()
            general_config["position"] = position_var.get()
            general_config["working_hours"] = working_hours_var.get()
    
            # Save using the utility function
            save_config_to_file(config_path, general_config, selected)
            print(f"[DEBUG] Setup updated: {json.dumps({**general_config, 'selected_gifs': selected}, indent=2)}")
    
            # Notify main loop to reload config
            if reset_timer_callback:
                reset_timer_callback()
    
            save_label.config(text="Saved!", fg="green")
            setup_win.after(300, setup_win.destroy)
        except Exception as e:
            save_label.config(text=f"Error: {e}", fg="red")

    def select_all():
        for var in checkbox_vars.values():
            var.set(1)
        update_selected_count()
        update_row_backgrounds()

    def deselect_all():
        for var in checkbox_vars.values():
            var.set(0)
        update_selected_count()
        update_row_backgrounds()

    select_all_btn.config(command=select_all)
    deselect_all_btn.config(command=deselect_all)
    save_btn.config(command=save_config)
    def on_setup_close():
        # Reload config from file before resetting timer
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "personal_setup.json")
        try:
            _, general_config = load_config_and_gifs(config_path, lambda: [])
            print("[DEBUG] Config reloaded in on_setup_close.")
        except Exception as e:
            print(f"[DEBUG] Failed to reload config in on_setup_close: {e}")
        setup_win.destroy()
        reset_timer_callback()
    close_btn.config(command=on_setup_close)

    setup_win.protocol("WM_DELETE_WINDOW", on_setup_close)
    update_selected_count()
    update_row_backgrounds()

    # Update GIF rows when category filter changes
    for var in category_vars.values():
        var.trace_add("write", lambda *args: update_gif_rows())