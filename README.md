# 📚 AI Study Timer

**2025 가천대학교 과학영재교육원 정보융합 분야 산출물**

AI 공부 타이머로, PC 카메라와 TensorFlow 모델을 이용해 사용자의 집중 상태를 실시간으로 감지하여, 집중이 흐트러질 경우 자동으로 타이머를 일시정지합니다. 이를 통해 효율적인 학습 시간을 관리할 수 있습니다.

👉 프로젝트 관련 보고서와 발표 자료는 [`report`](report) 폴더에서 확인하세요

**레이아웃 개요**
- 창 크기: `1000x700`
- 가로 3등분: 좌측 2칸 = 타이머, 우측 1칸 = AI 판독 영역(플레이스홀더)
- 버튼: 시작/정지(토글), 리셋

**주요 기능**
- AI 기반 집중/미집중 판별
- 미집중 시 카운트다운 후 자동 일시정지 및 경고 메시지
- 카메라 입력 실시간 표시
- 시작/정지 토글, 리셋

**추가 가능 기능(확장 아이디어)**
- 단축키
- 학습 통계 저장
- 알림 시스템 등

**실행 환경 요구사항**
- Python 3.10 이상 권장
- Tkinter가 포함된 Python 빌드(일반 배포판에는 기본 포함)
  - macOS: `python3`가 Tk 지원을 포함해야 합니다. Homebrew Python 사용 시 기본 포함.
  - Linux: 배포판에 따라 `python3-tk` 패키지가 필요할 수 있습니다.
- 추가 라이브러리: TensorFlow, mediapipe, Pillow 등

**실행 방법**
- 가상환경(선택)
  - 생성: `python3 -m venv venv`
  - 활성화(macOS/Linux): `source venv/bin/activate`
  - 활성화(Windows): `venv\\Scripts\\activate`
- 의존성: `requirements.txt` 파일을 이용해 설치 (`pip install -r requirements.txt`)
- 실행: `python src/main.py`

**프로젝트 구조(요약)**
- `src/main.py`: 타이머 애플리케이션 엔트리포인트(GUI)
- `src/module/Study_AI_Model.h5`: 학습된 TensorFlow h5 포즈 모델임
- `report/`: 보고서, 발표 자료
