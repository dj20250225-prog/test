import time
import streamlit as st

# -----------------------------------------------------------------------------
# 1. 페이지 기본 설정 및 스타일 정의
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="⏱️ 나만의 반응형 타이머",
    page_icon="⏱️",
    layout="centered"
)

# 커스텀 CSS (반응형 글자 크기 clamp 적용 및 카드 레이아웃 스타일)
st.markdown("""
    <style>
    /* 메인 타이머 카드 스타일 */
    .timer-card {
        background-color: #ffffff;
        border-radius: 20px;
        padding: 25px 20px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.06);
        border: 2px solid #eef2f6;
        text-align: center;
        margin-bottom: 20px;
    }
    
    /* clamp(최소크기, 권장크기, 최대크기)를 활용한 반응형 시간 글꼴 */
    .timer-text {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-size: clamp(3rem, 12vw, 5.5rem);
        font-weight: 800;
        color: #2C3E50;
        line-height: 1.1;
        margin: 15px 0;
        letter-spacing: 2px;
    }

    /* 서브 타이틀 스타일 */
    .timer-subtitle {
        color: #7F8C8D;
        font-size: clamp(0.9rem, 3vw, 1.1rem);
        margin-bottom: 10px;
    }

    /* 버튼 스타일 통일 및 모바일 터치 영역 확장 */
    .stButton > button {
        width: 100%;
        border-radius: 12px;
        height: 2.8rem;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. 세션 상태(st.session_state) 초기화
# -----------------------------------------------------------------------------
# 타이머의 상태: 'STOPPED'(정지), 'RUNNING'(실행중), 'PAUSED'(일시정지), 'FINISHED'(완료)
if "timer_state" not in st.session_state:
    st.session_state.timer_state = "STOPPED"

if "total_seconds" not in st.session_state:
    st.session_state.total_seconds = 0

if "remaining_seconds" not in st.session_state:
    st.session_state.remaining_seconds = 0.0

if "end_time" not in st.session_state:
    st.session_state.end_time = 0.0

if "input_min" not in st.session_state:
    st.session_state.input_min = 0

if "input_sec" not in st.session_state:
    st.session_state.input_sec = 0

# -----------------------------------------------------------------------------
# 3. 타이머 제어 함수 정의
# -----------------------------------------------------------------------------
def set_preset_time(minutes):
    """빠른 설정 버튼 클릭 시 분/초를 자동 입력하는 함수"""
    if st.session_state.timer_state == "STOPPED":
        st.session_state.input_min = minutes
        st.session_state.input_sec = 0

def start_timer():
    """타이머를 시작하는 함수"""
    total = (st.session_state.input_min * 60) + st.session_state.input_sec
    if total <= 0:
        st.warning("⚠️ 0분 0초 이상 시간을 설정해 주세요!")
        return
    
    st.session_state.total_seconds = total
    st.session_state.remaining_seconds = float(total)
    # time.monotonic()을 기준으로 타이머가 종료되는 시각을 정확히 저장
    st.session_state.end_time = time.monotonic() + total
    st.session_state.timer_state = "RUNNING"

def pause_timer():
    """타이머를 일시정지하는 함수"""
    if st.session_state.timer_state == "RUNNING":
        # 현재 시점 기준 남아있는 정확한 시간 계산 후 저장
        st.session_state.remaining_seconds = max(0.0, st.session_state.end_time - time.monotonic())
        st.session_state.timer_state = "PAUSED"

def resume_timer():
    """일시정지된 타이머를 다시 계속하는 함수"""
    if st.session_state.timer_state == "PAUSED":
        # 현재 시점 기준으로 남은 시간을 반영하여 종료 예정 시각 재설정
        st.session_state.end_time = time.monotonic() + st.session_state.remaining_seconds
        st.session_state.timer_state = "RUNNING"

def reset_timer():
    """타이머를 초기화하는 함수"""
    st.session_state.timer_state = "STOPPED"
    st.session_state.total_seconds = 0
    st.session_state.remaining_seconds = 0.0
    st.session_state.end_time = 0.0

# -----------------------------------------------------------------------------
# 4. 앱 화면 레이아웃 구성
# -----------------------------------------------------------------------------
st.title("⏱️ 나만의 반응형 타이머")

# 타이머 실행 중에는 입력창 수정 불가 처리 (is_disabled)
is_disabled = st.session_state.timer_state in ["RUNNING", "PAUSED"]

# [빠른 시간 설정 버튼 섹션]
st.write("⚡ **빠른 시간 설정**")
q_col1, q_col2, q_col3, q_col4 = st.columns(4)

with q_col1:
    st.button("1분", on_click=set_preset_time, args=(1,), disabled=is_disabled, use_container_width=True)
with q_col2:
    st.button("3분", on_click=set_preset_time, args=(3,), disabled=is_disabled, use_container_width=True)
with q_col3:
    st.button("5분", on_click=set_preset_time, args=(5,), disabled=is_disabled, use_container_width=True)
with q_col4:
    st.button("10분", on_click=set_preset_time, args=(10,), disabled=is_disabled, use_container_width=True)

st.write("")

# [분/초 직접 입력 섹션]
col_min, col_sec = st.columns(2)
with col_min:
    st.number_input(
        "분 (Minutes)",
        min_value=0,
        max_value=999,
        key="input_min",
        disabled=is_disabled,
        step=1
    )
with col_sec:
    st.number_input(
        "초 (Seconds)",
        min_value=0,
        max_value=59,
        key="input_sec",
        disabled=is_disabled,
        step=1
    )

st.divider()

# -----------------------------------------------------------------------------
# 5. st.fragment를 이용한 0.1초 단위 독립 화면 갱신
# -----------------------------------------------------------------------------
@st.fragment(run_every=0.1)
def render_timer():
    """전체 페이지 재실행 없이 타이머 부분만 독립적으로 업데이트하는 프래그먼트"""
    
    # 1) 실행 상태 시간 업데이트 계산
    if st.session_state.timer_state == "RUNNING":
        current = time.monotonic()
        remaining = st.session_state.end_time - current
        
        if remaining <= 0:
            st.session_state.remaining_seconds = 0.0
            st.session_state.timer_state = "FINISHED"
            st.rerun() # 완료 시 상태 갱신을 위해 rerun 호출
        else:
            st.session_state.remaining_seconds = remaining

    # 2) 시간 계산 (분:초 형식)
    rem_total_sec = int(st.session_state.remaining_seconds + 0.999) # 올림 시각화로 깔끔한 초 표시
    display_min = rem_total_sec // 60
    display_sec = rem_total_sec % 60
    time_str = f"{display_min:02d}:{display_sec:02d}"

    # 3) 진행률(Progress Bar) 계산
    progress_val = 0.0
    if st.session_state.total_seconds > 0:
        ratio = st.session_state.remaining_seconds / st.session_state.total_seconds
        progress_val = max(0.0, min(1.0, ratio))

    # 4) 타이머 UI 메인 카드 화면 출력
    st.markdown(f"""
        <div class="timer-card">
            <div class="timer-subtitle">남은 시간</div>
            <div class="timer-text">{time_str}</div>
        </div>
    """, unsafe_allow_html=True)

    # 진행률 막대
    st.progress(progress_val)

    # 5) 상태별 안내 메시지 및 효과
    if st.session_state.timer_state == "FINISHED":
        st.success("🎉 시간이 종료되었습니다!")
        st.balloons()
    elif st.session_state.timer_state == "PAUSED":
        st.info("⏸️ 타이머가 일시정지 상태입니다.")

# 프래그먼트 함수 실행
render_timer()

st.write("")

# -----------------------------------------------------------------------------
# 6. 제어 버튼 섹션 (시작 / 일시정지 / 계속 / 초기화)
# -----------------------------------------------------------------------------
btn_col1, btn_col2 = st.columns(2)

with btn_col1:
    if st.session_state.timer_state == "STOPPED":
        st.button("▶️ 시작", type="primary", use_container_width=True, on_click=start_timer)
    elif st.session_state.timer_state == "RUNNING":
        st.button("⏸️ 일시정지", type="secondary", use_container_width=True, on_click=pause_timer)
    elif st.session_state.timer_state == "PAUSED":
        st.button("▶️ 계속", type="primary", use_container_width=True, on_click=resume_timer)
    elif st.session_state.timer_state == "FINISHED":
        st.button("▶️ 시작", type="primary", use_container_width=True, on_click=start_timer, disabled=True)

with btn_col2:
    st.button("🔄 초기화", use_container_width=True, on_click=reset_timer)
