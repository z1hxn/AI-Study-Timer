from tkinter import *
from tkinter import messagebox
import time
import cv2
import numpy as np
import mediapipe as mp
from PIL import Image, ImageTk
from tensorflow import keras
import json

class StudyTimer:
    def __init__(self):
        
        # 윈도우 설정
        self.root = Tk()
        self.root.title("AI Study Timer")
        self.root.geometry("1000x700")
        self.root.resizable(False, False)
        self.root.configure(bg="#f0f0f0")

        # 타이머 상태 관련 변수
        self.is_running = False  # 현재 타이머 실행 여부
        self.start_time = None   # 마지막 시작 시점의 perf_counter 값
        self.elapsed_ms = 0      # 정지 상태에서 유지되는 누적 시간(ms)
        self.tick_job = None     # after() 예약 ID

        self.result_var = StringVar(value="Start 버튼을 눌러 공부를 시작하세요")
        self.probs_var = StringVar()

        self.countdown_job = None
        self.remaining_secs = 0 # 미집중 상태 측정 시간
        self.countdown_var = StringVar()

        self.camera_index = 1  # 기본값: 맥북 내장 카메라

        self.camera_names = {
            0: "iPhone Camera",
            1: "MacBook Camera",
            2: "External Camera 1",
            3: "External Camera 2"
        }
        self.camera_options = [self.camera_names.get(i, f"Camera {i}") for i in range(4)]
        self.selected_camera = StringVar(value=self.camera_names[self.camera_index])

        # 창 닫기 시 예약된 after 해제
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # 위젯 생성
        self.create_widgets()

        with open("./src/module/TensorFlow/metadata.json", "r") as f:
            metadata = json.load(f)
        self.labels = metadata["labels"]
        self.model = keras.models.load_model("./src/module/Study_AI_Model.h5")
        self.pose = mp.solutions.pose.Pose()
        self.cap = cv2.VideoCapture(self.camera_index)

        self.update_ai_frame()

    def create_widgets(self): # 위젯 생성
        self.root.grid_rowconfigure(0, weight=1)
        for col in range(3):
            self.root.grid_columnconfigure(col, weight=1)

        # 타이머 영역
        self.timer_frame = Frame(self.root, bg="#ffffff", highlightthickness=0)
        self.timer_frame.grid(row=0, column=0, columnspan=2, sticky="nsew")

        # AI 판독 영역
        self.ai_frame = Frame(self.root, bg="#eef4ff", highlightthickness=0)
        self.ai_frame.grid(row=0, column=2, sticky="nsew")

        # 카메라 선택 드롭다운
        self.camera_dropdown = OptionMenu(self.ai_frame, self.selected_camera, *self.camera_options, command=self.select_camera)
        self.camera_dropdown.config(font=("Pretendard", 12))
        self.camera_dropdown.pack(pady=10)

        # 스탑워치 부분
        self.time_label = Label(
            self.timer_frame,
            text="0:00:00",
            font=("Pretendard", 96),
            fg="#111111",
            bg="#ffffff",
            width=6,
            anchor="center",
        )
        self.time_label.pack(expand=True)

        # 시작/정지 버튼
        self.timer_start_button = Button(
            self.timer_frame,
            text="Start",
            font=("Pretendard", 24),
            fg="#000000",
            bg="#4caf50",
            padx=20,
            pady=10,
            borderwidth=0,
            activebackground="#45a049",
            command=self.toggle_timer,
        )
        self.timer_start_button.place(relx=0.5, rely=0.75, anchor="center")

        # 리셋 버튼
        self.timer_reset_button = Button(
            self.timer_frame,
            text="Reset",
            font=("Pretendard", 24),
            fg="#000000",
            bg="#f44336",
            padx=20,
            pady=10,
            borderwidth=0,
            activebackground="#da190b",
            command=self.reset_timer, # 리셋 함수 연결
        )
        self.timer_reset_button.place(relx=0.5, rely=0.9, anchor="center")
        self.timer_reset_button.place_forget()  # 처음에는 숨김

        # AI 판독 영상 영역
        self.ai_video_label = Label(self.ai_frame, bg="#eef4ff")
        self.ai_video_label.pack(pady=20)

        self.ai_result_label = Label(self.ai_frame, textvariable=self.result_var,
                                     font=("Pretendard", 20), fg="#1f3b80", bg="#eef4ff")
        self.ai_result_label.pack(pady=10)

        self.ai_probs_label = Label(self.ai_frame, textvariable=self.probs_var,
                                    font=("Pretendard", 14), fg="#333333", bg="#eef4ff", justify="left")
        self.ai_probs_label.pack(pady=5)

        self.ai_countdown_label = Label(self.ai_frame, textvariable=self.countdown_var,
                                        font=("Pretendard", 16), fg="red", bg="#eef4ff")
        self.ai_countdown_label.pack(pady=5)


    
    def toggle_timer(self): # 시작/정지 버튼 함수
        # 시작/정지 토글
        if self.is_running == False:
            # 시작
            self.is_running = True
            self.start_time = time.perf_counter()
            self.timer_start_button.config(text="Stop", bg="#f44336", activebackground="#da190b") # 버튼 Stop으로 변경
            self.timer_reset_button.place_forget()
            if self.tick_job is None:
                self.update_timer() # 타이머 업데이트 시작

        else:
            # 정지
            if self.start_time is not None:
                self.elapsed_ms += int((time.perf_counter() - self.start_time) * 1000)

            self.is_running = False
            self.start_time = None
            self.timer_start_button.config(text="Start", bg="#4caf50", activebackground="#45a049") # 버튼 Start로 변경
            self.timer_reset_button.place(relx=0.5, rely=0.9, anchor="center")

            if self.tick_job is not None:
                try:
                    self.root.after_cancel(self.tick_job)
                except Exception:
                    pass
                self.tick_job = None

            self.time_label.config(text=self.format_ms(self.elapsed_ms))

    def update_timer(self): # 타이머 업데이트 함수

        # 실행 중일 때만 라벨 업데이트 및 다음 호출 예약
        if not self.is_running or self.start_time is None:
            self.tick_job = None
            return

        current_ms = self.elapsed_ms + int((time.perf_counter() - self.start_time) * 1000)
        self.time_label.config(text=self.format_ms(current_ms))
        self.tick_job = self.root.after(200, self.update_timer)

    def reset_timer(self): # 리셋 버튼 함수
        # 타이머 완전 초기화
        if self.tick_job is not None:
            try:
                self.root.after_cancel(self.tick_job)
            except Exception:
                pass
            self.tick_job = None

        # 상태 변수 초기화
        self.is_running = False
        self.start_time = None
        self.elapsed_ms = 0
        self.timer_start_button.config(text="Start", bg="#4caf50", activebackground="#45a049")
        self.time_label.config(text="0:00:00")
        self.timer_reset_button.place_forget()

    def format_ms(self, ms: int) -> str: # ms를 시:분:초 형식으로 변환
        total = ms // 1000
        h = total // 3600
        m = (total % 3600) // 60
        s = total % 60
        return f"{h}:{m:02d}:{s:02d}" # 포맷 수정

    def update_ai_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            self.result_var.set("카메라를 사용할 수 없습니다")
            self.root.after(10, self.update_ai_frame)
            return

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        if not self.is_running:
            self.result_var.set("타이머를 시작해주세요")
            self.probs_var.set("")
            self.countdown_var.set("")
        else:
            results = self.pose.process(frame_rgb)

            keypoints = []
            if results.pose_landmarks:
                for lm in results.pose_landmarks.landmark:
                    keypoints.extend([lm.x, lm.y, lm.z, lm.visibility])
            # 14739 길이로 0 패딩
            if len(keypoints) < 14739:
                keypoints.extend([0.0] * (14739 - len(keypoints)))
            else:
                keypoints = keypoints[:14739]
            input_data = np.array(keypoints, dtype=np.float32).reshape(1, 1, 14739)
      
            preds = self.model.predict(input_data, verbose=0)
            preds = preds.flatten()
            pred_index = np.argmax(preds)
            pred_label = self.labels[pred_index]
            if pred_label == "Studying":
                status_text = "현재 상태 : 공부 중"
            elif pred_label == "Distracted":
                status_text = "현재 상태 : 미집중"
            else:
                status_text = f"현재 상태 : {pred_label}"
            self.result_var.set(status_text)

            if pred_label == "Distracted":
                if self.countdown_job is None:
                    self.remaining_secs = 30  # 몇 초 동안 미집중 상태일시 정지할지 설정
                    self.update_countdown()
            elif pred_label == "Studying":
                if self.countdown_job is not None:
                    try:
                        self.root.after_cancel(self.countdown_job)
                    except Exception:
                        pass
                    self.countdown_job = None
                self.countdown_var.set("")

            probs_text = " / ".join([f"{self.labels[i]}: {float(preds[i])*100:.1f}%" for i in range(len(self.labels))])
            self.probs_var.set(probs_text)

        # 카메라 비율 잘리는 것 방지
        max_width, max_height = 320, 240
        h, w = frame_rgb.shape[:2]
        scale = min(max_width / w, max_height / h)
        new_w, new_h = int(w * scale), int(h * scale)
        img = Image.fromarray(frame_rgb).resize((new_w, new_h))

        imgtk = ImageTk.PhotoImage(image=img)
        self.ai_video_label.imgtk = imgtk
        self.ai_video_label.config(image=imgtk)

        self.root.after(10, self.update_ai_frame)

    def update_countdown(self):
        if self.remaining_secs > 0:
            self.countdown_var.set(f"집중 안함! 타이머 정지까지 {self.remaining_secs}초 남음")
            self.remaining_secs -= 1
            self.countdown_job = self.root.after(1000, self.update_countdown)
        else:
            self.countdown_job = None
            if self.is_running:
                if self.start_time is not None:
                    self.elapsed_ms += int((time.perf_counter() - self.start_time) * 1000)
                self.is_running = False
                self.start_time = None
                self.timer_start_button.config(text="Start", bg="#4caf50", activebackground="#45a049")
                if self.tick_job is not None:
                    try:
                        self.root.after_cancel(self.tick_job)
                    except Exception:
                        pass
                    self.tick_job = None
                self.time_label.config(text=self.format_ms(self.elapsed_ms))
                self.timer_reset_button.place(relx=0.5, rely=0.9, anchor="center")
            self.countdown_var.set("집중 실패: 1분 경과")
            messagebox.showwarning("집중 경고", "미집중 상태가 지속되어 타이머가 중지되었습니다.")

    def select_camera(self, selection):
        index = list(self.camera_names.values()).index(selection)
        if hasattr(self, "cap") and self.cap.isOpened():
            self.cap.release()
        self.camera_index = index
        self.cap = cv2.VideoCapture(self.camera_index)
        self.result_var.set(f"{selection}로 전환됨")

    def on_close(self): # 창 닫기 함수

         # 창 닫을 때 예약된 after 해제
        if self.tick_job is not None:
            try:
                self.root.after_cancel(self.tick_job)
            except Exception:
                pass
            self.tick_job = None
        if hasattr(self, "cap") and self.cap.isOpened():
            self.cap.release()
        self.root.destroy()

if __name__ == "__main__":
    app = StudyTimer()
    app.root.mainloop()
