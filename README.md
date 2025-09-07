# 📚 AI Study Timer

**2025 가천대학교 과학영재교육원 정보융합 분야 산출물**

PC 카메라 + TensorFlow 모델을 이용해 “집중 상태”를 감지하여, 집중이 감지되지 않을 때 타이머를 자동으로 정지하는 공부 타이머입니다. 현재 저장소에는 기본 타이머(시작/정지, 리셋)와 레이아웃(UI)만 포함되어 있으며, AI 연동은 이후 단계에서 연결합니다. (이전 버전의 Arduino 연동 내용은 더 이상 사용하지 않습니다.)

👉 프로젝트 관련 보고서와 발표 자료는 `report` 폴더에서 확인하세요: `report`

**상태**: 개발 진행 중

**레이아웃 개요**
- 창 크기: `1000x700`
- 가로 3등분: 좌측 2칸 = 타이머, 우측 1칸 = AI 판독 영역(플레이스홀더)
- 버튼: 시작/정지(토글), 리셋

**주요 기능(현재 구현됨)**
- 시작/정지 토글: `time.perf_counter()` 기반 정밀 타이머
- 리셋: 누적 시간 및 상태 초기화
- 안전 종료: 창 닫기 시 예약된 after 루프 해제

**향후 계획(예정)**
- TensorFlow 모델 로드(`src/module/StudyAI_TensorFlow`) 및 카메라 입력 처리
- 집중 미감지 시 타이머 자동 일시정지
- 단축키/알림/통계 등 부가 기능

**실행 환경 요구사항**
- Python 3.10 이상 권장
- Tkinter가 포함된 Python 빌드(일반 배포판에는 기본 포함)
  - macOS: `python3`가 Tk 지원을 포함해야 합니다. Homebrew Python 사용 시 기본 포함.
  - Linux: 배포판에 따라 `python3-tk` 패키지가 필요할 수 있습니다.

**실행 방법**
- 가상환경(선택)
  - 생성: `python3 -m venv venv`
  - 활성화(macOS/Linux): `source venv/bin/activate`
  - 활성화(Windows): `venv\\Scripts\\activate`
- 의존성: 타이머만 사용할 경우 추가 설치가 필요 없습니다.
- 실행: `python src/main.py`

**프로젝트 구조(요약)**
- `src/main.py`: 타이머 애플리케이션 엔트리포인트(GUI)
- `src/module/StudyAI_TensorFlow/`: 이후 연결 예정인 Teachable Machine/TensorFlow 모델 파일
- `report/`: 보고서, 발표 자료

