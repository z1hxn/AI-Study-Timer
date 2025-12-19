"""
AI Study Timer에서 사용자가 조정할 수 있는 설정들입니다.
사용 시 주석에 따라 아래 값들을 수정해주세요
"""

# ===== 타이머 표시 관련 =====
TIMER_TICK_INTERVAL_MS = 200  # 타이머 라벨을 갱신하는 간격(ms)

# ===== 미집중 감지 관련 =====
FOCUS_COUNTDOWN_SECONDS = 30  # 미집중으로 판단되기까지 허용 시간(초)
FOCUS_COUNTDOWN_INTERVAL_MS = 1000  # 카운트다운 숫자 감소 주기(ms)
FOCUS_APPLY_PENALTY = True  # 미집중으로 정지 시 공부 시간 차감 여부
FOCUS_PENALTY_MS = 30000  # 차감할 공부 시간(ms)
FOCUS_COUNTDOWN_LABEL = "타이머 정지까지"  # 카운트다운 안내 문구
FOCUS_FINISHED_LABEL = "집중 실패: {seconds}초 경과"  # 카운트다운 완료 문구
FOCUS_WARNING_TITLE = "집중 경고"  # 경고 팝업 제목
FOCUS_WARNING_MESSAGE = (
    "미집중 상태가 지속되어 타이머가 중지되었습니다. "
    "공부하지 않은 시간은 타이머에서 제외됩니다."
)  # 경고 팝업 본문

# ===== 격려 문구 관련 =====
ENCOURAGEMENT_ALWAYS_SHOW = True  # 격려 문구 상시 표시 여부
ENCOURAGEMENT_ROTATION_INTERVAL_MS = 30000  # 격려 문구 교체 주기(ms)
ENCOURAGEMENT_MESSAGES = [
    "시간은 금이다.",
    "작은 습관이 큰 변화를 만든다.",
    "오늘의 노력은 내일의 성과다.",
    "포기하는 순간, 게임은 끝난다.",
    "지금 하지 않으면 후회한다.",
    "집중은 성공의 시작이다.",
    "한 시간 후, 나는 나를 칭찬할까?",
    "작은 성취가 큰 자신감을 만든다.",
    "멈추지 않는 자만이 도달한다.",
    "성공은 반복된 집중에서 태어난다.",
    "시간은 기다려주지 않는다.",
    "노력 없이는 얻을 수 없다.",
    "미래는 지금 결정된다.",
    "잠깐의 집중이 평생을 바꾼다.",
    "지금 이 순간이 가장 소중하다.",
]  # 격려 문구 리스트 (사용자 수정 가능)

# ===== 카메라 미리보기 관련 =====
CAMERA_MAX_WIDTH = 320  # 프리뷰 최대 너비(px)
CAMERA_MAX_HEIGHT = 240  # 프리뷰 최대 높이(px)
CAMERA_REFRESH_INTERVAL_MS = 10  # 카메라 프레임 재생 간격(ms)
