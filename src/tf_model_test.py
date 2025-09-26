import cv2
import numpy as np
import mediapipe as mp
import tkinter as tk
from PIL import Image, ImageTk
from tensorflow import keras
import json
with open("./src/model/TensorFlow/metadata.json", "r") as f:
    metadata = json.load(f)
labels = metadata["labels"]

# 1. 모델 불러오기
model = keras.models.load_model("./src/model/Study_AI_Model.h5")

# 2. Mediapipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

# 3. Tkinter 윈도우
window = tk.Tk()
window.title("Pose Recognition")
label = tk.Label(window)
label.pack(side="top")

result_var = tk.StringVar()
result_label = tk.Label(window, textvariable=result_var, font=("Arial", 20))
result_label.pack(side="bottom")

cap = cv2.VideoCapture(0)

def update_frame():
    ret, frame = cap.read()
    if not ret:
        return

    # BGR → RGB 변환
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(image)

    # 포즈 keypoints 추출
    keypoints = []
    if results.pose_landmarks:
        for lm in results.pose_landmarks.landmark:
            keypoints.extend([lm.x, lm.y, lm.z, lm.visibility])
    # 부족하면 zero padding
    while len(keypoints) < 14739:
        keypoints.append(0.0)

    keypoints = np.array(keypoints[:14739], dtype=np.float32).reshape(1,1,14739)

    # 모델 예측
    pred = model.predict(keypoints, verbose=0)
    pred_class = np.argmax(pred)
    pred_label = labels[pred_class] if pred_class < len(labels) else str(pred_class)
    result_var.set(f"예측: {pred_label}")

    # Tkinter에 표시
    img = Image.fromarray(image).resize((640, 480))
    imgtk = ImageTk.PhotoImage(image=img)
    label.imgtk = imgtk
    label.configure(image=imgtk)

    window.after(10, update_frame)

update_frame()
window.mainloop()
cap.release()