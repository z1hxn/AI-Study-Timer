from tkinter import *
from tkinter import messagebox
from tkinter import ttk
import time
import cv2
import numpy as np
import mediapipe as mp
from PIL import Image, ImageTk
import random

from camera_utils import (
    detect_cameras as detect_cameras_util,
    get_system_camera_names as get_system_camera_names_util,
    get_camera_display_name as get_camera_display_name_util,
)
from encouragement import ENCOURAGEMENT_MESSAGES
from pose_classifier import PoseClassifier


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
        self.remaining_secs = 0  # 미집중 카운트다운 시간

        # 타이머 프레임 상태 표시
        self.timer_status_var = StringVar(value="Start 버튼을 눌러 공부 측정을 시작하세요")

        # 격려 문구 관련 변수
        self.pause_message_var = StringVar()
        self.pause_message_job = None
        self.always_show_message = True  # 상시 표시 여부
        
        # 격려 문구 리스트
        self.encouragement_messages = ENCOURAGEMENT_MESSAGES[:]

        # 카메라 선택 관련 변수
        self.available_cameras = self.detect_cameras()
        if self.available_cameras:
            self.camera_index, default_camera_name = self.available_cameras[0]
        else:
            self.camera_index = 0
            default_camera_name = "기본 카메라"
            self.available_cameras = [(self.camera_index, default_camera_name)]
        
        self.selected_camera = StringVar(value=default_camera_name)

        # 창 닫기 시 예약된 after 해제
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # 테마 구성 및 위젯 생성
        self.configure_styles()
        self.create_widgets()

        # AI 모델 불러오기
        pose_resources = PoseClassifier()
        self.labels = pose_resources.labels
        self.model = pose_resources.model
        self.pose = pose_resources.pose
        self.mp_drawing = pose_resources.mp_drawing
        self.cap = cv2.VideoCapture(self.camera_index)

        # AI 프레임 업데이트 시작
        self.update_ai_frame()
        
        # 상시 격려 메시지 시작
        self.start_continuous_messages()

    def detect_cameras(self, max_devices=8): # 사용 가능한 카메라 감지
        return detect_cameras_util(max_devices)

    def get_system_camera_names(self): # 운영체제별 카메라 이름 조회
        return get_system_camera_names_util()

    def get_camera_display_name(self, index): # 인덱스로 표시 이름 찾기
        return get_camera_display_name_util(self.available_cameras, index)

    def configure_styles(self): # 테마 구성
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except Exception:
            pass

        style.configure(
            "Camera.TCombobox",
            fieldbackground="#ffffff",
            background="#dbe6ff",
            foreground="#1f3b80",
            bordercolor="#b4c6f0",
            arrowsize=18,
            arrowcolor="#1f3b80"
        )
        style.map(
            "Camera.TCombobox",
            fieldbackground=[("readonly", "#eef4ff"), ("active", "#eef4ff")],
            background=[("readonly", "#dbe6ff"), ("active", "#c7d8ff")],
            foreground=[("readonly", "#1f3b80")]
        )

    def create_widgets(self): # 위젯 생성
        self.root.grid_rowconfigure(0, weight=1)
        for col in range(2):
            self.root.grid_columnconfigure(col, weight=1)

        # 타이머 영역
        self.timer_frame = Frame(self.root, bg="#ffffff", highlightthickness=0)
        self.timer_frame.grid(row=0, column=0, sticky="nsew")

        # 프로그램 상태 표시
        self.timer_status_label = Label(
            self.timer_frame,
            textvariable=self.timer_status_var,
            font=("Pretendard", 22, "bold"),
            fg="#666666",
            bg="#ffffff",
            anchor="w"
        )
        self.timer_status_label.place(relx=0.02, rely=0.02, anchor="nw")

        # 경과 시간 라벨
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

        # Start/Stop 버튼
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

        # Reset 버튼
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
            command=self.reset_timer,
        )
        self.timer_reset_button.place(relx=0.5, rely=0.9, anchor="center")
        self.timer_reset_button.place_forget()

        # AI 판독 영역
        self.ai_frame = Frame(self.root, bg="#eef4ff", highlightthickness=0)
        self.ai_frame.grid(row=0, column=1, sticky="nsew")

        # 카메라 선택 콤보박스
        self.camera_selector = ttk.Combobox(
            self.ai_frame,
            textvariable=self.selected_camera,
            values=[name for _, name in self.available_cameras],
            state="readonly",
            font=("Pretendard", 12),
            style="Camera.TCombobox"
        )
        self.camera_selector.pack(pady=10)
        self.camera_selector.bind("<<ComboboxSelected>>", self.select_camera)

        # 카메라 프레임 표시 공간
        self.ai_video_label = Label(self.ai_frame, bg="#eef4ff")
        self.ai_video_label.pack(pady=20)

        # AI 결과 텍스트
        self.ai_result_label = Label(
            self.ai_frame,
            textvariable=self.result_var,
            font=("Pretendard", 60, "bold"),
            fg="#1f3b80",
            bg="#eef4ff"
        )
        self.ai_result_label.pack(pady=10)

        # 확률 표시
        self.ai_probs_label = Label(
            self.ai_frame,
            textvariable=self.probs_var,
            font=("Pretendard", 30),
            fg="#333333",
            bg="#eef4ff",
            justify="left"
        )
        self.ai_probs_label.pack(pady=6)

        # 미집중 경고 텍스트 설명 라벨 (카운트다운 위)
        self.ai_countdown_label = Label(
            self.ai_frame, 
            font=("Pretendard", 22), 
            fg="#ff3700", 
            bg="#eef4ff",
            text=""
        )
        self.ai_countdown_label.pack(pady=(50, 6))

        # 미집중 카운트다운 숫자
        self.ai_countdown_number_label = Label(
            self.ai_frame, 
            font=("Pretendard", 55, "bold"), 
            fg="#ff3700", 
            bg="#eef4ff", 
            text=""
        )
        self.ai_countdown_number_label.pack(pady=2)

        # 격려 문구 표시 라벨
        self.ai_pause_message_label = Label(
            self.ai_frame, 
            textvariable=self.pause_message_var,
            font=("Pretendard", 22, "italic"), 
            fg="#333333", 
            bg="#eef4ff", 
            wraplength=350, 
            justify="center"
        )
        self.ai_pause_message_label.pack(side=BOTTOM, pady=40)
    
    def toggle_timer(self): # 시작/정지 버튼 함수

        # 눌렀을 때 상태에 따라 시작/정지 토글
        if self.is_running == False: # 정지상태일시 시작

            self.is_running = True
            self.start_time = time.perf_counter() # 측정시작
            self.timer_start_button.config(text="Stop", bg="#f44336", activebackground="#da190b") # 버튼 Stop으로 변경
            self.timer_reset_button.place_forget() #리셋버튼 없애기
            
            # 상태 텍스트 업데이트
            self.timer_status_var.set("현재 공부 중입니다")

            # 상시 메시지는 계속 표시되도록 유지 (중지하지 않음)
            if self.tick_job is None:
                self.update_timer() # 타이머 업데이트 시작

        else:  # 실행상태일시 중지
            if self.start_time is not None:
                self.elapsed_ms += int((time.perf_counter() - self.start_time) * 1000) # 누적 시간에 더하기

            self.is_running = False
            self.start_time = None
            self.timer_start_button.config(text="Start", bg="#4caf50", activebackground="#45a049") # 버튼 Start로 변경
            self.timer_reset_button.place(relx=0.5, rely=0.9, anchor="center") # 리셋버튼 보이기
            
            # 상태 텍스트 업데이트
            self.timer_status_var.set("공부가 일시정지되었습니다")

            # 타이머 업데이트 취소
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

        current_ms = self.elapsed_ms + int((time.perf_counter() - self.start_time) * 1000) # 현재 시간 계산
        self.time_label.config(text=self.format_ms(current_ms)) # 라벨 업데이트
        self.tick_job = self.root.after(200, self.update_timer) # 200ms (업데이트 간격) 후에 다시 호출

    def reset_timer(self): # 리셋 버튼 함수

        # 타이머 완전 초기화
        if self.tick_job is not None:
            try:
                self.root.after_cancel(self.tick_job) # 예약된 타이머 업데이트 취소
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
        
        # 상태 텍스트 초기화
        self.timer_status_var.set("Start 버튼을 눌러 공부 측정을 시작하세요")

    def format_ms(self, ms: int) -> str: # ms를 시:분:초 형식으로 변환
        total = ms // 1000
        h = total // 3600
        m = (total % 3600) // 60
        s = total % 60
        return f"{h}:{m:02d}:{s:02d}" # 포맷 수정

    def update_ai_frame(self): # AI 판독 프레임 업데이트 함수

        ret, frame = self.cap.read() # OpenCV로 카메라 프레임 읽기

        # 카메라 프레임 읽기 실패 시 재시도
        if not ret:
            self.result_var.set("카메라를 사용할 수 없습니다")
            self.root.after(10, self.update_ai_frame)
            return

        # BGR을 RGB로 변환 (Mediapipe는 RGB 사용)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)


        if not self.is_running: # 타이머가 실행 중일 경우에만 판독 X
            self.result_var.set("대기 중") # 텍스트 색상 변경
            self.ai_result_label.config(fg="#1f3b80")
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

        else: # 실행 중일 경우 판독
            results = self.pose.process(frame_rgb) # Mediapipe Pose 처리

            # 뻐대 랜드마크 그리기
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

            # 14739 길이로 0 패딩 (모델 입력 크기 맞추기)
            if len(keypoints) < 14739:
                keypoints.extend([0.0] * (14739 - len(keypoints)))
            else:
                keypoints = keypoints[:14739]
            input_data = np.array(keypoints, dtype=np.float32).reshape(1, 1, 14739)
            
            # 모델 예측
            preds = self.model.predict(input_data, verbose=0)
            preds = preds.flatten()
            pred_index = np.argmax(preds)
            pred_label = self.labels[pred_index]

            # 모델 라벨에 따라 결과 텍스트 및 색상 변경
            if pred_label == "Studying":
                status_text = "공부 중"
                self.ai_result_label.config(fg="#1f3b80")  # green
            elif pred_label == "Distracted":
                status_text = "미집중"
                self.ai_result_label.config(fg="#ff3700")  # orange
            else:  # 예외 처리 및 대기(etc)
                status_text = f"{pred_label}"
                self.ai_result_label.config(fg="#1f3b80")  # default blue
            self.result_var.set(status_text)

            # 타이머 실행 중 미집중 감지 : 카운트다운 시작
            if pred_label == "Distracted" and self.is_running:
                if self.countdown_job is None:
                    self.remaining_secs = 30  # 미집중 카운트다운 시작 초기화
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

            # 확률 표시 업데이트
            # Display only the probability for the predicted label (concentration level)
            self.probs_var.set(f"집중도: {preds[pred_index]*100:.1f}%")

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

    def update_countdown(self): # 미집중 카운트다운 업데이트 함수
        
        if self.remaining_secs > 0: # 카운트다운이 진행중이라면

            # 텍스트 라벨: 고정 메시지
            self.ai_countdown_label.config(text="타이머 정지까지")
            
            # 숫자 라벨: 카운트다운 숫자만 표시
            self.ai_countdown_number_label.config(text=f"{self.remaining_secs}")
            self.remaining_secs -= 1
            self.countdown_job = self.root.after(1000, self.update_countdown)

        else: # 카운트다운 종료 (미집중 시간 초과) : 타이머 정지

            # 카운트다운 예약 해제
            self.countdown_job = None
            if self.is_running: # 타이머 실행중이면 취소

                if self.start_time is not None:
                    self.elapsed_ms += int((time.perf_counter() - self.start_time) * 1000) # 누적 시간에 더하기
                self.elapsed_ms = max(0, self.elapsed_ms - 30000)  # 미집중으로 정지 시 30초 패널티 적용

                # 상태 변수 초기화
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
                
                # 리셋 버튼 보이기
                self.time_label.config(text=self.format_ms(self.elapsed_ms))
                self.timer_reset_button.place(relx=0.5, rely=0.9, anchor="center")
                
                # 상태 텍스트 변경
                self.timer_status_var.set("미집중으로 공부가 중단되었습니다")
            
            # 카운트다운 끝 메시지 표시
            self.ai_countdown_label.config(text="집중 실패: 30초 경과")
            self.ai_countdown_number_label.config(text="")
            messagebox.showwarning("집중 경고", "미집중 상태가 지속되어 타이머가 중지되었습니다. 공부하지 않은 시간은 타이머에서 제외됩니다.")

    def start_continuous_messages(self): # 메시지 표시 시작 함수
        if self.always_show_message:
            self.update_pause_message()
    
    def update_pause_message(self): # 메시지 30초마다 업데이트 함수
            random_message = random.choice(self.encouragement_messages) #리스트에서 메시지 랜덤으로 고르기
            self.pause_message_var.set(f'"{random_message}"') # 따옴표 붙여서 출력
            
            # 30초마다 상시 업데이트
            if self.always_show_message:
                self.pause_message_job = self.root.after(30000, self.update_pause_message)
            else:
                self.pause_message_job = None

    def select_camera(self, event=None): # 카메라 선택 함수
        selection = self.selected_camera.get()
        for index, name in self.available_cameras:
            if name == selection:
                self.switch_camera(index, name)
                break

    def switch_camera(self, index, display_name): # 카메라 전환 처리
        if index == self.camera_index and hasattr(self, "cap") and self.cap.isOpened():
            return

        new_cap = cv2.VideoCapture(index)
        if not new_cap or not new_cap.isOpened():
            if new_cap:
                new_cap.release()
            messagebox.showerror("카메라 오류", f"선택한 카메라({display_name})를 열 수 없습니다.")
            self.selected_camera.set(self.get_camera_display_name(self.camera_index))
            return

        if hasattr(self, "cap") and self.cap.isOpened():
            self.cap.release()

        self.camera_index = index
        self.cap = new_cap
        messagebox.showinfo("카메라 전환 알림", f"카메라가 {display_name}(으)로 전환되었습니다")

    def on_close(self): # 창 닫기 함수
        
        # 창 닫을 때 예약된 after 해제
        if self.tick_job is not None:
            try:
                self.root.after_cancel(self.tick_job)
            except Exception:
                pass
            self.tick_job = None
        
        # 상시 메시지 중지
        if self.pause_message_job is not None:
            try:
                self.root.after_cancel(self.pause_message_job)
            except Exception:
                pass
            self.pause_message_job = None
        
        if hasattr(self, "cap") and self.cap.isOpened():
            self.cap.release()
        self.root.destroy()
