from tkinter import *
import time

class StudyTimer:
    def __init__(self):
        
        # 윈도우 세팅부분
        self.root = Tk()
        self.root.title("AI Study Timer")
        self.root.geometry("1000x700")
        self.root.resizable(False, False)
        self.root.configure(bg="#f0f0f0")

        # 변수들 설정부분 (타이머 상태)
        self.is_running = False  # 현재 타이머 실행 여부
        self.start_time = None   # 마지막 시작 시점의 perf_counter 값
        self.elapsed_ms = 0      # 정지 상태에서 유지되는 누적 시간(ms)
        self.tick_job = None     # after() 예약 id

        # 창 닫기 시 예약된 after 해제
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # 위젯 생성부분
        self.create_widgets()

    def create_widgets(self): # 위젯 생성부분
        self.root.grid_rowconfigure(0, weight=1)
        for col in range(3):
            self.root.grid_columnconfigure(col, weight=1)

        # 타이머 부분
        self.timer_frame = Frame(self.root, bg="#ffffff", highlightthickness=0)
        self.timer_frame.grid(row=0, column=0, columnspan=2, sticky="nsew")

        self.ai_frame = Frame(self.root, bg="#eef4ff", highlightthickness=0)
        self.ai_frame.grid(row=0, column=2, sticky="nsew")

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
        self.timer_start_button.pack(pady=(0, 20))

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
        self.timer_reset_button.pack(pady=(0, 40))

        # AI 판독 영역 부분
        self.ai_label = Label(
            self.ai_frame,
            text="AI 판독 영역 (추후 연결)",
            font=("Pretendard", 20),
            fg="#1f3b80",
            bg="#eef4ff",
        )
        self.ai_label.pack(expand=True)

    
    def toggle_timer(self): # 시작/정지 버튼 함수
        # 시작/정지 토글
        if self.is_running == False:
            # 시작
            self.is_running = True
            self.start_time = time.perf_counter()
            self.timer_start_button.config(text="Stop", bg="#f44336", activebackground="#da190b") # 버튼 Stop로 변경
            if self.tick_job is None:
                self.update_timer() # 타이머 업데이트 시작

        else:
            # 정지
            if self.start_time is not None:
                self.elapsed_ms += int((time.perf_counter() - self.start_time) * 1000)

            self.is_running = False
            self.start_time = None
            self.timer_start_button.config(text="Start", bg="#4caf50", activebackground="#45a049") # 버튼 Start로 변경

            if self.tick_job is not None:
                try:
                    self.root.after_cancel(self.tick_job)
                except Exception:
                    pass
                self.tick_job = None

            self.time_label.config(text=self.format_ms(self.elapsed_ms))

    def update_timer(self): # 타이머 업데이트 함수

        # 실행 중에만 라벨 업데이트 및 다음 틱 예약
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

    def format_ms(self, ms: int) -> str: # ms를 h:m:s 형식으로 변환
        total = ms // 1000
        h = total // 3600
        m = (total % 3600) // 60
        s = total % 60
        return f"{h}:{m:02d}:{s:02d}" # 포멧 수정

    def on_close(self): # 창 닫기 함수

         # 창 닫기 시 예약된 after 해제
        if self.tick_job is not None:
            try:
                self.root.after_cancel(self.tick_job)
            except Exception:
                pass
            self.tick_job = None
        self.root.destroy()

if __name__ == "__main__":
    app = StudyTimer()
    app.root.mainloop()
