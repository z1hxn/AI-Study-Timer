# 🧠 AI Study Timer

> **2025 가천대학교 과학영재교육원 정보융합 분야 산출물**  
> 실시간 포즈 인식을 통한 지능형 학습 집중도 모니터링 시스템

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.16.1-orange.svg)](https://tensorflow.org)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10.21-green.svg)](https://mediapipe.dev)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.12.0-red.svg)](https://opencv.org)

## 📋 프로젝트 개요

본 프로젝트는 AI를 활용해 사용자의 집중 상태만을 자동 기록하는 스마트 공부 타이머를 개발하는 데 목적이 있습니다. 컴퓨터의 카메라로 사용자의 공부 모습을 촬영하고, MediaPipe가 추출한 자세 랜드마크를 TensorFlow 모델에 입력하여 실시간으로 집중/미집중을 판별합니다. 사용자가 집중하지 않는 것으로 판단되면 타이머가 자동으로 정지하며, 경고와 함께 집중을 유도하는 멘트를 제공합니다. 이를 통해 기존 공부 타이머가 가지던 “실제 집중 여부를 반영하지 못하는 한계”를 보완하고, 사용자가 자신의 공부 습관을 더 정확히 점검·개선할 수 있도록 돕습니다.

## ✨ 주요 기능

### 🎯 핵심 기능
- **AI 기반 실시간 집중도 판별**: MediaPipe로 추출한 랜드마크를 TensorFlow 모델이 분석해 실시간으로 집중 여부를 판별하고 화면에 표시
- **자동 타이머 제어**: 집중 상태일 때만 타이머가 작동하며, 미집중 상태가 30초 지속되면 자동 일시정지(카운트다운 포함)
- **시각화 및 피드백 제공**: 영상 위에 포즈 랜드마크(뼈대)를 시각적으로 표시하고, 미집중 시 경고 팝업과 상시 동기부여 메시지 제공
- **사용자 친화적 UI**: Start/Stop/Reset로 직관적인 제어, 상태에 따라 색상·문구 변화로 즉각적 피드백 제공

### 🎨 사용자 인터페이스
- **좌측**: 타이머 표시와 제어 버튼(Start/Stop/Reset)
- **우측**: 실시간 카메라 피드, AI 판별 결과, 카운트다운 및 격려 문구

### 🔧 기술적 특징
- **실시간 처리**: 10ms 주기의 프레임 갱신과 즉시 판별
- **직관적 피드백**: 상태별 색상/문구 및 카운트다운 제공
- **크로스 플랫폼**: macOS, Windows, Linux 지원
- **확장 가능성**: 모듈화된 구조로 기능 확장 용이

## 🏗️ 시스템 아키텍처

### 기술 스택
```
Frontend: Tkinter (Python GUI)
Computer Vision: OpenCV + MediaPipe
Machine Learning: TensorFlow + Keras
Data Processing: NumPy + PIL
```

### 스택별 역할
- **Tkinter**: 메인 화면(UI), 타이머·상태 표시, 팝업/카운트다운·격려 메시지 제공
- **TensorFlow(Keras)**: 집중 여부를 판별하는 AI 모델 학습·실행 (Teachable Machine 학습 모델을 .h5로 변환하여 사용)
- **MediaPipe**: 얼굴·눈·손·자세 등의 랜드마크를 정확한 좌표 데이터로 추출
- **OpenCV**: 카메라에서 실시간 영상 캡처, 프레임 전달 및 GUI 표시용 이미지 변환

### 모델 구조
- **입력**: MediaPipe 포즈 랜드마크 (33개 관절점 × 4차원 = 132차원)
- **전처리**: 모델 호환을 위해 14,739차원으로 패딩
- **모델**: Teachable Machine에서 학습 후 TensorFlow(.h5)로 변환해 사용
- **출력**: 2클래스 분류 (Studying, Distracted)

### 집중 판별 플로우
1. **카메라 촬영(OpenCV)**: 실시간 프레임 캡처 → MediaPipe 전달
2. **전처리(MediaPipe)**: 랜드마크 추출 → 구조화된 좌표 데이터로 변환
3. **AI 판별(TensorFlow)**: 랜드마크 입력 → 집중/미집중 판별
4. **시각화(OpenCV)**: 프레임에 뼈대(랜드마크) 그리기 및 피드백 제공
5. **GUI 제어(Tkinter)**: 판별 결과에 따라 타이머 동작·경고 팝업·카운트다운

## 📦 설치 및 실행

### 시스템 요구사항
- **Python**: 3.10 이상
- **운영체제**: macOS, Windows, Linux
- **카메라**: 웹캠 또는 내장 카메라
- **메모리**: 최소 4GB RAM 권장

### 설치 과정

1. **저장소 클론**
```bash
git clone https://github.com/z1hxn/AI-Study-Timer.git
cd AI-Study-Timer
```

2. **가상환경 생성 및 활성화**
```bash
# 가상환경 생성
python3 -m venv venv

# 활성화 (macOS/Linux)
source venv/bin/activate

# 활성화 (Windows)
venv\Scripts\activate
```

3. **의존성 설치**
```bash
pip install -r requirements.txt
```

4. **애플리케이션 실행**
```bash
cd src  # 상대경로 모델파일 참조를 위해 src 폴더에서 실행 필요
python main.py
```

### 의존성 패키지
주요 패키지 목록:
- `tensorflow==2.16.1`: 딥러닝 모델 실행
- `mediapipe==0.10.21`: 포즈 인식 및 랜드마크 추출
- `opencv-python==4.12.0.88`: 컴퓨터 비전 처리
- `pillow==11.3.0`: 이미지 처리
- `numpy==1.26.4`: 수치 연산

## 📁 프로젝트 구조

```
AI-Study-Timer/
├── src/
│   └── main.py                 # 메인 애플리케이션 (GUI + AI 로직)
├── model/
│   ├── Study_AI_Model.h5       # 훈련된 TensorFlow 모델
│   └── TensorFlow/
│       ├── metadata.json       # 모델 메타데이터
│       ├── model.json          # 모델 구조 정의
│       └── weights.bin         # 모델 가중치
├── tests/
│   ├── check_tf.py            # TensorFlow 설치 확인
│   ├── tf_model_converter.py  # 모델 변환 유틸리티
│   └── tf_model_test.py       # 모델 테스트
├── docs/
│   ├── diagram/               # 시스템 다이어그램
│   └── source/               # 프로젝트 자료
├── requirements.txt           # Python 의존성
└── README.md                 # 프로젝트 문서
```

## 🎮 사용법

### 기본 사용법
1. **애플리케이션 실행**: `cd src && python main.py`
2. **카메라 설정**: 우측 상단 드롭다운에서 카메라 선택
3. **학습 시작**: "Start" 버튼 클릭하여 타이머 시작
4. **상태 모니터링**: 실시간으로 집중 상태 확인
5. **자동 제어**: 미집중 상태 30초 지속 시 자동 일시정지

### 인터페이스 구성
- **좌측 영역**: 타이머 표시 및 제어 버튼
- **우측 영역**: 실시간 카메라 피드 및 AI 분석 결과
- **상태 표시**: 현재 집중 상태 및 확률 정보
- **경고 시스템**: 미집중 시 카운트다운 및 알림


## 📈 성능 및 검증 결과

- 10분 × 3회 작동 테스트에서 정상 동작 확인
- 동일 모델을 Teachable Machine(웹)에서 구동했을 때 대비, 본 프로그램(.h5 변환 모델)에서는 인식 정확도가 낮게 나타남
- 원인 추정: TensorFlow.js(웹) → TensorFlow/Keras(.h5) 변환 과정에서의 성능 저하 가능성
- 후속 조치: 변환 파이프라인 점검 및 재학습/튜닝 등 추가 탐구 필요

## 🔍 한계와 고찰

- 본 모델은 ‘동작 인식 기반’이므로 인지적 집중(예: 졸음 등)을 직접 감지하지 못함
- 사용자가 ‘집중 자세’를 유지한 채 인지적으로 이탈한 경우 오인식 가능
- 개선 방향: 동작 인식에 더해 시선/눈 개방 정도/손의 물체 보유 여부 등 추가 시각 신호 결합 필요

## 🚀 향후 개발 방향

- 멀티 모델 융합: 동작 인식 + 이미지 감지(눈 개방, 손 물체 등) 모델 결합
- 장기 학습 패턴 분석: 누적 데이터를 기반으로 리포트/습관 개선 가이드 제공
- IoT 연동: 집중 저하 시 조명/알람 등 환경 피드백 제공, 최적 학습 환경 자동 조성
- 다양한 집중도 모델 지원 및 웹 기반 버전 확장

## 🤝 기여하기

버그 리포트나 기능 제안은 GitHub Issues를 통해 해주세요.

1. 저장소를 Fork 합니다
2. 새 브랜치를 생성합니다 (`git checkout -b feature/새기능`)
3. 변경사항을 커밋합니다 (`git commit -m '새 기능 추가'`)
4. 브랜치에 푸시합니다 (`git push origin feature/새기능`)
5. Pull Request를 생성합니다

## 📄 프로젝트 자료

프로젝트의 상세한 발표 자료와 문서는 [docs](./docs) 폴더를 참조하세요.
- 중간발표회 및 최종발표회 PPT 및 보고서
- 프로젝트 다이어그램 및 플로우차트
- 시연 영상 및 관련 자료

---

**⭐ 프로젝트가 도움이 되었다면 스타를 눌러주세요!**