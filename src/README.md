# AI 스터디 타이머

AI 기반 동작 인식을 사용한 스터디 타이머입니다.

## 기능

- 실시간 카메라 화면 표시
- TensorFlow.js 모델을 사용한 동작 인식 (Studying/Distracted)
- Studying 상태일 때만 타이머 측정
- 직관적인 GUI 인터페이스

## 설치 및 실행

### 1. 필요한 패키지 설치

```bash
pip install -r requirements.txt
```

### 2. 프로그램 실행

```bash
cd src
python main.py
```

## 사용법

1. 프로그램을 실행합니다
2. "카메라 시작" 버튼을 클릭하여 카메라를 활성화합니다
3. AI가 자동으로 동작을 인식합니다:
   - **Studying**: 공부 중으로 인식되면 타이머가 작동합니다
   - **Distracted**: 산만한 상태로 인식되면 타이머가 일시정지됩니다
4. "타이머 리셋" 버튼으로 누적 시간을 초기화할 수 있습니다

## 모델 정보

- TensorFlow.js 모델 사용
- Teachable Machine으로 훈련된 포즈 인식 모델
- 2개 클래스: Studying, Distracted
- 입력 크기: 257x257 픽셀

## 주의사항

- 카메라 권한이 필요합니다
- 충분한 조명이 필요합니다
- 모델이 정확한 인식을 위해 적절한 자세를 유지해주세요
