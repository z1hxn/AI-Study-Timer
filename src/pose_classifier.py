import json
from pathlib import Path

import mediapipe as mp
import numpy as np
from tensorflow import keras


class PoseClassifier:
    INPUT_LENGTH = 14739

    def __init__(self, model_dir=None):
        base_dir = Path(model_dir) if model_dir else Path(__file__).resolve().parent.parent / "model"
        metadata_path = base_dir / "metadata.json"
        model_path = base_dir / "Study_AI_Model.h5"

        with metadata_path.open("r", encoding="utf-8") as f:
            metadata = json.load(f)

        self.labels = metadata["labels"]
        self.model = keras.models.load_model(model_path)
        self.pose = mp.solutions.pose.Pose()
        self.mp_drawing = mp.solutions.drawing_utils

    def analyze(self, frame_rgb):
        results = self.pose.process(frame_rgb) # Mediapipe Pose 처리

        keypoints = []
        if results and results.pose_landmarks:
            for lm in results.pose_landmarks.landmark:
                keypoints.extend([lm.x, lm.y, lm.z, lm.visibility])

        # 14739 길이로 0 패딩 (모델 입력 크기 맞추기)
        if len(keypoints) < self.INPUT_LENGTH:
            keypoints.extend([0.0] * (self.INPUT_LENGTH - len(keypoints)))
        else:
            keypoints = keypoints[:self.INPUT_LENGTH]

        input_data = np.array(keypoints, dtype=np.float32).reshape(1, 1, self.INPUT_LENGTH)
        preds = self.model.predict(input_data, verbose=0)
        preds = preds.flatten()
        pred_index = np.argmax(preds)
        pred_label = self.labels[pred_index]

        return results, preds, pred_index, pred_label

    def draw_landmarks(self, frame_rgb, pose_landmarks):
        # 뻐대 랜드마크 그리기
        if pose_landmarks:
            self.mp_drawing.draw_landmarks(
                frame_rgb,
                pose_landmarks,
                mp.solutions.pose.POSE_CONNECTIONS,
                landmark_drawing_spec=self.mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=3, circle_radius=5),
                connection_drawing_spec=self.mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=4)
            )
