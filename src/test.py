import tkinter as tk
from tkinter import filedialog
import tensorflow as tf
import numpy as np

def run_model():
    # 모델 불러오기
    interpreter = tf.lite.Interpreter(model_path="model.tflite")
    interpreter.allocate_tensors()

    # 입력 데이터 준비
    input_details = interpreter.get_input_details()
    input_shape = input_details[0]['shape']
    input_data = np.random.rand(*input_shape).astype(np.float32)

    # 실행
    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()
    output_data = interpreter.get_tensor(interpreter.get_output_details()[0]['index'])

    # GUI에 출력
    result_label.config(text=f"결과: {output_data}")

# GUI 구성
root = tk.Tk()
result_label = tk.Label(root, text="결과 대기 중")
result_label.pack()
tk.Button(root, text="모델 실행", command=run_model).pack()
root.mainloop()