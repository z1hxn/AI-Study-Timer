# 🧠 AI Study Timer

> **2025 가천대학교 과학영재교육원 정보융합 분야 산출물**  
> 실시간 포즈 인식을 통한 지능형 학습 집중도 모니터링 시스템

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.16.1-orange.svg)](https://tensorflow.org)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10.21-green.svg)](https://mediapipe.dev)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.12.0-red.svg)](https://opencv.org)

## 📋 프로젝트 개요

AI Study Timer는 컴퓨터 비전과 머신러닝을 활용하여 사용자의 학습 집중도를 실시간으로 모니터링하는 지능형 타이머 애플리케이션입니다. MediaPipe 포즈 인식과 TensorFlow 딥러닝 모델을 통해 사용자의 자세와 행동을 분석하여 집중/미집중 상태를 판별하고, 미집중 상태가 지속될 경우 자동으로 타이머를 일시정지하여 효율적인 학습 시간 관리를 지원합니다.

## ✨ 주요 기능

### 🎯 핵심 기능
- **실시간 포즈 인식**: MediaPipe를 활용한 사용자 자세 실시간 추적
- **AI 기반 집중도 판별**: TensorFlow 모델을 통한 학습/미집중 상태 자동 분류
- **지능형 타이머 제어**: 미집중 상태 지속 시 자동 타이머 일시정지
- **시각적 피드백**: 실시간 카메라 피드와 포즈 랜드마크 시각화
- **다중 카메라 지원**: 다양한 카메라 소스 선택 가능

### 🎨 사용자 인터페이스
- **직관적 GUI**: Tkinter 기반의 깔끔하고 사용하기 쉬운 인터페이스
- **실시간 상태 표시**: 현재 집중 상태와 확률 정보 실시간 표시
- **카운트다운 알림**: 미집중 상태 지속 시 시각적 경고 시스템
- **격려 메시지**: 학습 동기 부여를 위한 랜덤 격려 문구 표시

### 🔧 기술적 특징
- **고성능 처리**: 10ms 간격의 실시간 프레임 처리
- **메모리 효율성**: 효율적인 리소스 관리 및 메모리 최적화
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


### 모델 구조
- **입력**: MediaPipe 포즈 랜드마크 (33개 관절점 × 4차원 = 132차원)
- **전처리**: 14,739차원으로 패딩 (모델 호환성)
- **모델**: Teachable Machine으로 훈련된 포즈 분류 모델
- **출력**: 2클래스 분류 (Studying, Distracted)

### 각 기술 스택별 집중 상태 판별 과정

#### 1. 웹캠 촬영 (OpenCV)
- 웹캠에서 영상 프레임을 실시간으로 받아옴
- 받아 온 프레임을 MediaPipe로 전달

#### 2. 전처리 단계 (MediaPipe)
- OpenCV에서 프레임을 받아옴
- 사람의 얼굴, 눈, 손, 자세 등 주요 특징점을 추출
- 단순 픽셀 단위 이미지 → 구조화된 좌표 데이터로 변환

#### 3. 집중 상태 AI 판별 단계 (TensorFlow)
- MediaPipe가 추출한 특징점 데이터를 입력값으로 받음
- 학습된 모델을 통해 현재 사용자의 집중 상태를 분류
- 이 결과값이 타이머 작동에 사용됨

#### 4. 후처리 및 시각화 (OpenCV)
- 원본 프레임에 결과 표시용 그래픽 (얼굴, 손 특징점)을 그려줌
- 영상 스트리밍과 시각적 피드백을 담당

#### 5. GUI 및 타이머 제어 (Tkinter)
- 프로그램의 메인 UI를 담당
- 타이머 기능을 구현하고, 사용자가 조작할 수 있도록 제공
- TensorFlow 분류 결과에 따라 타이머를 일시정지하고 경고 메시지를 띄움

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


## 🚀 향후 계획

- 학습 통계 및 리포트 기능
- 사용자 프로필 및 설정 저장
- 다양한 집중도 모델 지원
- 웹 기반 버전 개발

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