from tkinter import *
from tkinter import messagebox
import time
import cv2
import numpy as np
import mediapipe as mp
from PIL import Image, ImageTk
from tensorflow import keras
import json
import random

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
        self.remaining_secs = 0  # 미집중 상태 측정 시간

        # 타이머 프레임 상태 표시
        self.timer_status_var = StringVar(value="Start 버튼을 눌러 공부 측정을 시작하세요")

        # 격려 문구 관련 변수
        self.pause_message_var = StringVar()
        self.pause_message_job = None
        self.always_show_message = True  # 상시 표시 여부
        
        # 격려 문구 리스트
        self.encouragement_messages = [
            "시간은 금이다. 지금이 바로 그 순간이다.",
            "작은 습관이 큰 변화를 만든다.",
            "오늘의 노력은 내일의 성과다.",
            "포기하는 순간, 게임은 끝난다.",
            "지금 하지 않으면 영원히 후회한다.",
            "집중은 성공의 첫걸음이다.",
            "한 시간 후의 나는 지금의 나를 칭찬할까?",
            "작은 성취가 큰 자신감을 만든다.",
            "멈추지 않는 자만이 도달한다.",
            "성공은 반복된 집중에서 태어난다.",
            "시간은 당신을 기다려주지 않는다.",
            "노력 없이는 아무것도 얻을 수 없다.",
            "당신의 미래는 지금 결정된다.",
            "잠깐의 집중이 평생의 결과를 바꾼다.",
            "이 순간이 가장 중요한 순간이다."
        ]

        # 카메라 선택 관련 변수
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

        # AI 모델 불러오기
        with open("../model/TensorFlow/metadata.json", "r") as f:
            metadata = json.load(f)
        self.labels = metadata["labels"]
        self.model = keras.models.load_model("../model/Study_AI_Model.h5")
        self.pose = mp.solutions.pose.Pose()
        self.mp_drawing = mp.solutions.drawing_utils
        self.cap = cv2.VideoCapture(self.camera_index)

        self.update_ai_frame()
        
        # 상시 격려 메시지 시작
        self.start_continuous_messages()

    def create_widgets(self): # 위젯 생성
        self.root.grid_rowconfigure(0, weight=1)
        for col in range(3):
            self.root.grid_columnconfigure(col, weight=1)

        # 타이머 영역
        self.timer_frame = Frame(self.root, bg="#ffffff", highlightthickness=0)
        self.timer_frame.grid(row=0, column=0, columnspan=2, sticky="nsew")

        # 타이머 상태 표시 (맨 위, 맨 왼쪽)
        self.timer_status_label = Label(
            self.timer_frame,
            textvariable=self.timer_status_var,
            font=("Pretendard", 16),
            fg="#666666",
            bg="#ffffff",
            anchor="w"
        )
        self.timer_status_label.place(relx=0.02, rely=0.02, anchor="nw")

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

        # AI 결과 표시 라벨
        self.ai_result_label = Label(
            self.ai_frame, 
            textvariable=self.result_var,
            font=("Pretendard", 20), 
            fg="#1f3b80", 
            bg="#eef4ff"
        )
        self.ai_result_label.pack(pady=10)

        # AI 확률 표시 라벨
        self.ai_probs_label = Label(
            self.ai_frame, 
            textvariable=self.probs_var,
            font=("Pretendard", 14), 
            fg="#333333", 
            bg="#eef4ff", 
            justify="left"
        )
        self.ai_probs_label.pack(pady=5)

        # 미집중 경고 텍스트 (분리된 표시)
        self.ai_countdown_label = Label(
            self.ai_frame, 
            font=("Pretendard", 16), 
            fg="red", 
            bg="#eef4ff", 
            text=""
        )
        self.ai_countdown_label.pack(pady=5)
        
        # 미집중 타이머 숫자 (큰 폰트로 분리 표시)
        self.ai_countdown_number_label = Label(
            self.ai_frame, 
            font=("Pretendard", 32, "bold"), 
            fg="red", 
            bg="#eef4ff", 
            text=""
        )
        self.ai_countdown_number_label.pack(pady=2)
        
        # 격려 문구 표시 라벨 (카운트다운과 맨밑 사이 중간)
        self.ai_pause_message_label = Label(
            self.ai_frame, 
            textvariable=self.pause_message_var,
            font=("Pretendard", 18), 
            fg="#333333", 
            bg="#eef4ff", 
            wraplength=300, 
            justify="center"
        )
        self.ai_pause_message_label.pack(side=BOTTOM, pady=60)
    
    def toggle_timer(self): # 시작/정지 버튼 함수
        # 시작/정지 토글
        if self.is_running == False:
            # 시작
            self.is_running = True
            self.start_time = time.perf_counter()
            self.timer_start_button.config(text="Stop", bg="#f44336", activebackground="#da190b") # 버튼 Stop으로 변경
            self.timer_reset_button.place_forget()
            
            # 상태 텍스트 업데이트
            self.timer_status_var.set("현재 공부 중입니다")

            # 상시 메시지는 계속 표시되도록 유지 (중지하지 않음)
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
            
            # 상태 텍스트 업데이트
            self.timer_status_var.set("공부가 일시정지되었습니다")

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

        # 상시 메시지는 계속 표시 (리셋 시에도 격려 메시지 유지)

        # 상태 변수 초기화
        self.is_running = False
        self.start_time = None
        self.elapsed_ms = 0
        self.timer_start_button.config(text="Start", bg="#4caf50", activebackground="#45a049")
        self.time_label.config(text="0:00:00")
        self.timer_reset_button.place_forget()
        
        # 상태 텍스트 초기화
        self.timer_status_var.set("Start 버튼을 눌러 공부 측정을 시작하세요")

    def format_ms(self, ms: int) -> str: # ms를 시:분:초 형식으로 변환
        total = ms // 1000
        h = total // 3600
        m = (total % 3600) // 60
        s = total % 60
        return f"{h}:{m:02d}:{s:02d}" # 포맷 수정

    def update_ai_frame(self): # AI 판독 프레임 업데이트 함수

        # 아래 코드 TensorFlow 모델 부분 임포트 코드이므로 변경하지 말 것

        ret, frame = self.cap.read()

        # 카메라 프레임 읽기 실패 시 재시도
        if not ret:
            self.result_var.set("카메라를 사용할 수 없습니다")
            self.root.after(10, self.update_ai_frame)
            return

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # 타이머가 실행 중이지 않을경우 판독X
        if not self.is_running:
            self.result_var.set("타이머를 시작해주세요")
            self.probs_var.set("")
            self.ai_countdown_label.config(text="")
            self.ai_countdown_number_label.config(text="")
            
            # 실행 중이지 않을 때는 카운트다운 중지
            if self.countdown_job is not None:
                try:
                    self.root.after_cancel(self.countdown_job)
                except Exception:
                    pass
                self.countdown_job = None
            
            # 상시 메시지 표시는 유지 (이미 start_continuous_messages에서 자동으로 작동 중)
        else:
            # 판독 부분
            results = self.pose.process(frame_rgb)

            # 뼈대 표시
            if results.pose_landmarks:
                self.mp_drawing.draw_landmarks(
                    frame_rgb, 
                    results.pose_landmarks, 
                    mp.solutions.pose.POSE_CONNECTIONS,
                    landmark_drawing_spec=self.mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=3, circle_radius=5),
                    connection_drawing_spec=self.mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=4)
                )

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

            # 모델 라벨에 따라 결과 텍스트 바꾸기
            if pred_label == "Studying":
                status_text = "현재 상태 : 공부 중"
            elif pred_label == "Distracted":
                status_text = "현재 상태 : 미집중"
            else:
                status_text = f"현재 상태 : {pred_label}"
            self.result_var.set(status_text)

            # 미집중 감지 : 분리된 카운트다운 디스플레이 시작 (타이머 실행 중일 때만)
            if pred_label == "Distracted" and self.is_running:
                if self.countdown_job is None:
                    self.remaining_secs = 30  # 미집중 허용 시간 (초)
                    self.update_countdown()  # 텍스트 + 숫자 분리 표시 시작

            # 공부 중일 때: 미집중 카운트다운 해제
            elif pred_label == "Studying":
                # 진행 중인 카운트다운 취소
                if self.countdown_job is not None:
                    try:
                        self.root.after_cancel(self.countdown_job)
                    except Exception:
                        pass
                    self.countdown_job = None
                # 카운트다운 라벨들 초기화
                self.ai_countdown_label.config(text="")
                self.ai_countdown_number_label.config(text="")

            probs_text = " / ".join([f"{self.labels[i]}: {float(preds[i])*100:.1f}%" for i in range(len(self.labels))])
            self.probs_var.set(probs_text)

        # 카메라 비율 잘리는 것 방지
        max_width, max_height = 320, 240
        h, w = frame_rgb.shape[:2]
        scale = min(max_width / w, max_height / h)
        new_w, new_h = int(w * scale), int(h * scale)
        img = Image.fromarray(frame_rgb).resize((new_w, new_h))

        # 중앙 정렬을 위해 빈 캔버스에 붙이기
        imgtk = ImageTk.PhotoImage(image=img)
        self.ai_video_label.imgtk = imgtk
        self.ai_video_label.config(image=imgtk)

        # 10ms 간격으로 업데이트 예약
        self.root.after(10, self.update_ai_frame)

    def update_countdown(self): 
        """미집중 상태 카운트다운 처리 (텍스트와 숫자 분리 표시)"""
        
        if self.remaining_secs > 0:
            # 텍스트 라벨: 고정 메시지
            self.ai_countdown_label.config(text="집중하지 않고 있음! 타이머 정지까지")
            
            # 숫자 라벨: 카운트다운 숫자만 표시
            self.ai_countdown_number_label.config(text=f"{self.remaining_secs}")
            self.remaining_secs -= 1
            self.countdown_job = self.root.after(1000, self.update_countdown)

        else:
            # 카운트다운 종료 - 타이머 정지
            self.countdown_job = None
            if self.is_running:
                # 타이머 정지 처리
                if self.start_time is not None:
                    self.elapsed_ms += int((time.perf_counter() - self.start_time) * 1000)
                self.is_running = False
                self.start_time = None
                self.timer_start_button.config(text="Start", bg="#4caf50", activebackground="#45a049")
                
                # 타이머 업데이트 취소
                if self.tick_job is not None:
                    try:
                        self.root.after_cancel(self.tick_job)
                    except Exception:
                        pass
                    self.tick_job = None
                    
                self.time_label.config(text=self.format_ms(self.elapsed_ms))
                self.timer_reset_button.place(relx=0.5, rely=0.9, anchor="center")
                
                # 미집중으로 자동 중지 상태 텍스트
                self.timer_status_var.set("미집중으로 공부가 중단되었습니다")
            
            # 카운트다운 끝 메시지 표시
            self.ai_countdown_label.config(text="집중 실패: 30초 경과")
            self.ai_countdown_number_label.config(text="")
            messagebox.showwarning("집중 경고", "미집중 상태가 지속되어 타이머가 중지되었습니다.")

    def start_continuous_messages(self): # 메시지 표시 시작 함수
        if self.always_show_message:
            self.update_pause_message()
    
    def stop_continuous_messages(self): # 메시지 업데이트 중지 함수 (종료용)
        if self.pause_message_job is not None:
            try:
                self.root.after_cancel(self.pause_message_job)
            except Exception:
                pass
            self.pause_message_job = None
    
    def update_pause_message(self): # 메시지 30초마다 업데이트 함수
        random_message = random.choice(self.encouragement_messages) #리스트에서 메시지 랜덤으로 고르기
        self.pause_message_var.set(f'"{random_message}"') # 따옴표 붙여서 출력
        
        # 30초마다 상시 업데이트
        if self.always_show_message:
            self.pause_message_job = self.root.after(30000, self.update_pause_message)
        else:
            self.pause_message_job = None

    def select_camera(self, selection): # 카메라 선택 함수

        # 카메라 인덱스 선택 공식 코드이므로 변경하지 말 것
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
        
        # 상시 메시지 중지
        self.stop_continuous_messages()
        
        if hasattr(self, "cap") and self.cap.isOpened():
            self.cap.release()
        self.root.destroy()

if __name__ == "__main__":
    app = StudyTimer()
    app.root.mainloop()
