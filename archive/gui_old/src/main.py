import tkinter as tk
from tkinter import messagebox
import cv2
from PIL import Image, ImageTk
import threading
import time

class StudyTimerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Study Timer with Focus Detection")
        self.root.geometry("800x600")
        
        self.is_running = False
        self.start_time = None
        self.elapsed_time = 0

        self.label = tk.Label(root, text="00:00:00", font=("Helvetica", 48))
        self.label.pack(pady=20)

        self.start_button = tk.Button(root, text="Start", command=self.start_timer)
        self.start_button.pack(side="left", padx=10)

        self.stop_button = tk.Button(root, text="Stop", command=self.stop_timer)
        self.stop_button.pack(side="left", padx=10)

        self.reset_button = tk.Button(root, text="Reset", command=self.reset_timer)
        self.reset_button.pack(side="left", padx=10)

        self.status_label = tk.Label(root, text="Status: Unknown", font=("Helvetica", 14))
        self.status_label.pack(pady=10)

        self.camera_index = tk.IntVar(value=0)
        camera_options = [0, 1, 2, 3]  # Can be adjusted based on system
        self.camera_menu = tk.OptionMenu(root, self.camera_index, *camera_options, command=self.change_camera)
        self.camera_menu.pack(pady=10)

        self.video_label = tk.Label(root)
        self.video_label.pack(pady=10)

        self.cap = cv2.VideoCapture(0)
        self.update_video()

    def change_camera(self, value):
        try:
            index = int(value)
            self.cap.release()
            self.cap = cv2.VideoCapture(index)
        except Exception as e:
            messagebox.showerror("Camera Error", f"Unable to switch camera: {e}")

    def update_video(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img)
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)

        # You can add AI focus detection logic here and update self.status_label
        self.status_label.config(text="Status: (AI Placeholder)")

        self.root.after(30, self.update_video)

    def start_timer(self):
        if not self.is_running:
            self.is_running = True
            self.start_time = time.time() - self.elapsed_time
            self.update_timer()

    def stop_timer(self):
        if self.is_running:
            self.is_running = False
            self.elapsed_time = time.time() - self.start_time

    def reset_timer(self):
        self.is_running = False
        self.start_time = None
        self.elapsed_time = 0
        self.label.config(text="00:00:00")

    def update_timer(self):
        if self.is_running:
            self.elapsed_time = time.time() - self.start_time
            elapsed = time.strftime("%H:%M:%S", time.gmtime(self.elapsed_time))
            self.label.config(text=elapsed)
            self.root.after(1000, self.update_timer)

if __name__ == "__main__":
    root = tk.Tk()
    app = StudyTimerApp(root)
    root.mainloop()