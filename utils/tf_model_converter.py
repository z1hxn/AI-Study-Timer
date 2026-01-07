import json
import numpy as np
from tensorflow import keras

# 1. JSON 파일 로드
with open("../model/model.json", "r") as f:
    model_json = json.load(f)

# 2. 모델 구조 불러오기
model = keras.Sequential.from_config(model_json["modelTopology"]["config"])

# 3. 가중치 바이너리 로드
with open("../model/weights.bin", "rb") as f:
    weights_array = np.frombuffer(f.read(), dtype=np.float32)

# 4. 가중치 매핑 정보 읽기
weights_manifest = model_json["weightsManifest"][0]["weights"]

# 레이어별 가중치 분리
tensor_slices = []
offset = 0
for w in weights_manifest:
    length = np.prod(w["shape"])
    tensor = weights_array[offset : offset + length].reshape(w["shape"])
    tensor_slices.append(tensor)
    offset += length

# 5. 모델에 가중치 주입
model.set_weights(tensor_slices)

# 6. 저장
model.save("../model/study_model.h5")
print("동작 모델 변환 완료: study_model.h5")