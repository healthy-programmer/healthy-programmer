import os
import csv
from datetime import datetime
from tkinter import Toplevel, Frame, Label, Button, Canvas, Scrollbar, Listbox, PhotoImage, filedialog
from tkinter import simpledialog
from tkinter import messagebox
from tkinter import Tk
from PIL import Image, ImageTk

LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "exercise_log.log")

class ExerciseLogger:
    @staticmethod
    def log_exercise(image_path, description, area, action):
        dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Log all image files (gif, jpg, png, etc.)
        try:
            print(f"[ExerciseLogger] Logging exercise: {dt}, {image_path}, {description}, {area}, {action}")
            with open(LOG_FILE, "a", encoding="utf-8", newline='') as f:
                writer = csv.writer(f)
                writer.writerow([dt, os.path.basename(image_path), description, area, action])
            print(f"[ExerciseLogger] Log entry written to {LOG_FILE}")
        except Exception as e:
            print(f"[ExerciseLogger] Failed to log exercise: {e}")

    @staticmethod
    def read_logs():
        logs = []
        if not os.path.exists(LOG_FILE):
            return logs
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 5:
                    dt, image, description, area, action = row[:5]
                    logs.append({
                        "datetime": dt,
                        "date": dt.split(" ")[0],
                        "image": image,
                        "description": description,
                        "area": area,
                        "action": action
                    })
        return logs

    @staticmethod
    def logs_by_date():
        logs = ExerciseLogger.read_logs()
        by_date = {}
        for log in logs:
            date = log["date"]
            by_date.setdefault(date, []).append(log)
        return by_date

class ExerciseLogViewer:
    def __init__(self, parent):
        self.parent = parent
        self.top = Toplevel(parent)
        self.top.title("Exercise Log Viewer")
        self.top.geometry("700x600")
        self.top.resizable(False, False)

        self.logs_by_date = ExerciseLogger.logs_by_date()
        self.dates = sorted(self.logs_by_date.keys(), reverse=True)

        self.create_calendar()
        self.create_log_list()
        self.selected_date = None

    def create_calendar(self):
        cal_frame = Frame(self.top)
        cal_frame.pack(side="top", fill="x", padx=10, pady=10)

        Label(cal_frame, text="Select a day:", font=("Arial", 13, "bold")).pack(side="left", padx=5)
        self.date_listbox = Listbox(cal_frame, height=10, width=15, font=("Arial", 12))
        for date in self.dates:
            self.date_listbox.insert("end", date)
        self.date_listbox.pack(side="left", padx=5)
        self.date_listbox.bind("<<ListboxSelect>>", self.on_date_select)

    def create_log_list(self):
        self.log_frame = Frame(self.top)
        self.log_frame.pack(side="top", fill="both", expand=True, padx=10, pady=10)
        self.log_canvas = Canvas(self.log_frame, borderwidth=0, background="#f0f0f0")
        self.log_scrollbar = Scrollbar(self.log_frame, orient="vertical", command=self.log_canvas.yview)
        self.log_canvas.configure(yscrollcommand=self.log_scrollbar.set)
        self.log_canvas.pack(side="left", fill="both", expand=True)
        self.log_scrollbar.pack(side="right", fill="y")
        self.log_inner = Frame(self.log_canvas, background="#f0f0f0")
        self.log_canvas.create_window((0,0), window=self.log_inner, anchor="nw")
        self.log_inner.bind("<Configure>", lambda e: self.log_canvas.configure(scrollregion=self.log_canvas.bbox("all")))

    def on_date_select(self, event):
        selection = self.date_listbox.curselection()
        if not selection:
            return
        idx = selection[0]
        date = self.dates[idx]
        self.selected_date = date
        self.show_logs_for_date(date)

    def show_logs_for_date(self, date):
        # Clear previous widgets
        for widget in self.log_inner.winfo_children():
            widget.destroy()
        logs = self.logs_by_date.get(date, [])
        if not logs:
            Label(self.log_inner, text="No exercises logged for this day.", font=("Arial", 12)).pack(pady=10)
            return
        for log in logs:
            row = Frame(self.log_inner, background="#e8f5e9", relief="groove", borderwidth=1)
            row.pack(fill="x", padx=4, pady=6)
            # Thumbnail
            img_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../exercise/images", log["image"])
            thumb = None
            if os.path.exists(img_path):
                try:
                    img = Image.open(img_path)
                    img.thumbnail((80, 80))
                    thumb = ImageTk.PhotoImage(img, master=self.top)
                except Exception:
                    thumb = None
            if thumb:
                img_label = Label(row, image=thumb, background="#e8f5e9")
                img_label.image = thumb
                img_label.pack(side="left", padx=8, pady=8)
            else:
                img_label = Label(row, text="[Image]", background="#e8f5e9")
                img_label.pack(side="left", padx=8, pady=8)
            # Description
            desc_text = f"{log['description']}\nArea: {log['area']}\nAction: {log['action']}"
            desc_label = Label(row, text=desc_text, justify="left", wraplength=400, background="#e8f5e9", font=("Arial", 11))
            desc_label.pack(side="left", padx=8, pady=8)

# Example usage:
# ExerciseLogger.log_exercise("/path/to/exercise.jpg", "Description", "Area", "Action")
# viewer = ExerciseLogViewer(parent_window)