import tkinter as tk
from tkinter import filedialog, messagebox
import numpy as np
import tensorflow as tf

# GUI 윈도우 설정
root = tk.Tk()
root.title("TensorFlow Lite 모델 실행기")
root.geometry("400x300")

# 결과 표시용 레이블
result_label = tk.Label(root, text="결과: 아직 없음", font=("Arial", 14))
result_label.pack(pady=20)

# 모델 로딩 & 실행 함수
def run_model():
    try:
        # 모델 파일 선택
        model_path = filedialog.askopenfilename(filetypes=[("TFLite Model", "*.tflite")])
        if not model_path:
            return

        # 모델 로드
        interpreter = tf.lite.Interpreter(model_path=model_path)
        interpreter.allocate_tensors()

        # 입력/출력 정보
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()

        # 임의의 입력 데이터 생성 (224x224 RGB 기준)
        input_shape = input_details[0]['shape']
        input_data = np.random.rand(*input_shape).astype(np.float32)

        # 모델 실행
        interpreter.set_tensor(input_details[0]['index'], input_data)
        interpreter.invoke()
        output_data = interpreter.get_tensor(output_details[0]['index'])

        # 결과 출력
        result_text = f"추론 결과: {output_data}"
        result_label.config(text=result_text)

    except Exception as e:
        messagebox.showerror("오류", str(e))

# 버튼
run_button = tk.Button(root, text="모델 불러와서 실행하기", command=run_model, font=("Arial", 12))
run_button.pack(pady=10)

# GUI 루프 시작
root.mainloop()