import tkinter as tk
from tkinter import ttk
import cv2
from PIL import Image, ImageTk
import time

class StudyTimerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Study Timer")

        self.start_time = None
        self.elapsed_time = 0
        self.running = False

        self.timer_label = ttk.Label(root, text="00:00:00", font=("Helvetica", 24))
        self.timer_label.pack(pady=10)

        self.start_btn = ttk.Button(root, text="Start", command=self.toggle_timer)
        self.start_btn.pack()

        self.reset_btn = ttk.Button(root, text="Reset", command=self.reset_timer)
        self.reset_btn.pack()

        self.video_label = ttk.Label(root)
        self.video_label.pack(pady=10)

        self.cap = cv2.VideoCapture(0)
        self.update_video()
        self.update_timer()

    def toggle_timer(self):
        if self.running:
            self.elapsed_time += time.time() - self.start_time
            self.running = False
            self.start_btn.config(text="Start")
        else:
            self.start_time = time.time()
            self.running = True
            self.start_btn.config(text="Pause")

    def reset_timer(self):
        self.running = False
        self.elapsed_time = 0
        self.start_btn.config(text="Start")

    def update_timer(self):
        if self.running:
            current_time = time.time() - self.start_time + self.elapsed_time
        else:
            current_time = self.elapsed_time

        mins, secs = divmod(int(current_time), 60)
        hours, mins = divmod(mins, 60)
        self.timer_label.config(text=f"{hours:02}:{mins:02}:{secs:02}")
        self.root.after(1000, self.update_timer)

    def update_video(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)
        self.root.after(30, self.update_video)

    def __del__(self):
        if self.cap.isOpened():
            self.cap.release()

if __name__ == "__main__":
    root = tk.Tk()
    app = StudyTimerApp(root)
    root.mainloop()