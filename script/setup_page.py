import os
import json
from tkinter import (
    Toplevel, Frame, Canvas, Scrollbar, Checkbutton, IntVar, Label, Button
)
from PIL import Image, ImageTk

def load_gif_descriptions(data_md_path):
    mapping = {}
    current_gif = None
    area = None
    action = None
    desc_lines = []
    with open(data_md_path, encoding='utf-8') as mdfile:
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

def open_setup_page(parent, reset_timer_callback, cancel_timer_callback):
    setup_win = Toplevel(parent)
    setup_win.title("Personalize Exercises")
    setup_win.geometry("600x600")
    setup_win.resizable(False, False)
    # Cancel the reminder window timer immediately
    if cancel_timer_callback:
        cancel_timer_callback()

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

    selected_count_label = Label(button_row, text="", font=("Arial", 11), background="#f0f0f0")
    selected_count_label.pack(side="left", padx=(8,4))

    canvas = Canvas(setup_win, borderwidth=0, background="#f0f0f0")
    frame = Frame(canvas, background="#f0f0f0")
    scrollbar = Scrollbar(setup_win, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="top", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    canvas.create_window((0,0), window=frame, anchor="nw")

    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
    frame.bind("<Configure>", on_frame_configure)

    def _on_mousewheel(event):
        delta = event.delta if event.delta else (-120 if event.num == 5 else 120)
        canvas.yview_scroll(int(-1*(delta/120)), "units")
    canvas.bind_all("<MouseWheel>", _on_mousewheel)
    canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
    canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))

    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "personalized_exercises.json")
    selected_gifs = set()
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                selected_gifs = set(json.load(f))
        except Exception:
            selected_gifs = set()

    gif_desc_map = load_gif_descriptions(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../exercise/reminder-data.md'))
    gif_files = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), '../exercise/images/resized', f)
        for f in os.listdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../exercise/images/resized'))
        if f.lower().endswith('.gif') and f in gif_desc_map.keys()
    ]

    checkbox_vars = {}
    anim_states = {}

    def update_selected_count():
        count = sum(var.get() for var in checkbox_vars.values())
        selected_count_label.config(text=f"Selected: {count}")


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

    for idx, gif_path in enumerate(gif_files):
        gif_name = os.path.basename(gif_path)
        gif_info = gif_desc_map.get(gif_name, {})
        desc = gif_info.get("description", "")
        area = gif_info.get("area", "")
        action = gif_info.get("action", "")

        row_frame = Frame(frame, background="#f0f0f0", relief="groove", borderwidth=1)
        row_frame.pack(fill="x", padx=4, pady=4)

        content_row = Frame(row_frame, background="#f0f0f0")
        content_row.pack(fill="x", padx=4, pady=4)

        var = IntVar(value=1 if gif_name in selected_gifs else 0)
        checkbox = Checkbutton(content_row, text="Include", variable=var, background="#f0f0f0", font=("Arial", 10))
        checkbox.pack(side="left", anchor="n", padx=(0, 8), pady=4)
        checkbox_vars[gif_name] = var

        def on_checkbox_toggle(*args):
            update_selected_count()
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

        desc_text = f"{desc}\nArea: {area}\nAction: {action}"
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

    def save_config():
        selected = [name for name, var in checkbox_vars.items() if var.get() == 1]
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(selected, f, indent=2)
            save_label.config(text="Saved!", fg="green")
            setup_win.after(300, setup_win.destroy)
        except Exception as e:
            save_label.config(text=f"Error: {e}", fg="red")

    def select_all():
        for var in checkbox_vars.values():
            var.set(1)
        update_selected_count()

    def deselect_all():
        for var in checkbox_vars.values():
            var.set(0)
        update_selected_count()

    select_all_btn.config(command=select_all)
    deselect_all_btn.config(command=deselect_all)
    save_btn.config(command=save_config)
    def on_setup_close():
        setup_win.destroy()
        reset_timer_callback()
    close_btn.config(command=on_setup_close)

    setup_win.protocol("WM_DELETE_WINDOW", on_setup_close)
    update_selected_count()