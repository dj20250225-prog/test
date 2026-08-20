import random
import time
import streamlit as st

# -----------------------------------------------------------------------------
# 1. 페이지 기본 설정 및 스타일 정의
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="자리 배치 테스트 버전",
    page_icon="🏫",
    layout="centered"
)

# 커스텀 CSS (교실 칠판, 책상 카드, 반응형 레이아웃 스타일)
st.markdown("""
    <style>
    /* 칠판 스타일 */
    .blackboard {
        background-color: #2e5a44;
        color: #ffffff;
        border: 8px solid #8d5b4c;
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        font-size: clamp(1.2rem, 4vw, 1.8rem);
        font-weight: bold;
        margin-bottom: 25px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.15);
        letter-spacing: 2px;
    }

    /* 교탁 표시 스타일 */
    .teacher-desk {
        width: 120px;
        margin: -15px auto 20px auto;
        background-color: #d7ccc8;
        border: 2px solid #8d6e63;
        border-radius: 6px;
        text-align: center;
        font-size: 0.85rem;
        color: #4e342e;
        padding: 4px;
        font-weight: bold;
    }

    /* 책상 카드 스타일 */
    .seat-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 12px 5px;
        text-align: center;
        border: 2px solid #e0e0e0;
        box-shadow: 0 3px 6px rgba(0,0,0,0.05);
        margin-bottom: 12px;
        transition: all 0.3s ease;
    }

    /* 배정 완료된 책상 스타일 */
    .seat-card-assigned {
        background-color: #e8f5e9;
        border-color: #66bb6a;
        box-shadow: 0 4px 8px rgba(76, 175, 80, 0.15);
    }

    /* 책상 번호 (자리 라벨) */
    .seat-label {
        font-size: clamp(0.7rem, 2vw, 0.85rem);
        color: #78909c;
        font-weight: 600;
        margin-bottom: 4px;
    }

    /* 학생 번호 표시 */
    .student-number {
        font-size: clamp(1.1rem, 3.5vw, 1.5rem);
        font-weight: 800;
        color: #1b5e20;
    }

    /* 미배정 빈 상태 표시 */
    .empty-number {
        font-size: clamp(1.1rem, 3.5vw, 1.5rem);
        font-weight: bold;
        color: #cfd8dc;
    }

    /* 버튼 스타일 조정 */
    .stButton > button {
        width: 100%;
        border-radius: 10px;
        height: 2.8rem;
        font-weight: bold;
        font-size: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. 세션 상태(st.session_state) 초기화
# -----------------------------------------------------------------------------
# seats: 25개 자리에 배정된 학생 번호 리스트 (None이면 미배정)
if "seats" not in st.session_state:
    st.session_state.seats = [None] * 25

# status: 'IDLE' (시작 전), 'ASSIGNING' (배정 진행 중), 'FINISHED' (배정 완료)
if "status" not in st.session_state:
    st.session_state.status = "IDLE"

# -----------------------------------------------------------------------------
# 3. 자리 배정 함수 정의
# -----------------------------------------------------------------------------
def assign_seats():
    """1~25번 학생을 무작위로 25개 자리에 배치하는 함수"""
    # 진행 중 중복 클릭 방지
    if st.session_state.status == "ASSIGNING":
        return

    st.session_state.status = "ASSIGNING"
    
    # 1부터 25까지 번호 생성 후 무작위 섞기
    students = list(range(1, 26))
    random.shuffle(students)
    
    # 배치 애니메이션 효과 (시간차를 두고 한 명씩 배치)
    for i in range(25):
        st.session_state.seats[i] = students[i]
        time.sleep(0.05)  # 0.05초 간격으로 한 자리씩 배정 연출

    st.session_state.status = "FINISHED"

def reset_seats():
    """자리 배정 상태를 초기화하고 무작위로 다시 배치하는 함수"""
    # 진행 중 중복 클릭 방지
    if st.session_state.status == "ASSIGNING":
        return

    # 모든 자리 초기화 후 즉시 재배정 실행
    st.session_state.seats = [None] * 25
    st.session_state.status = "IDLE"
    assign_seats()

# -----------------------------------------------------------------------------
# 4. 앱 화면 헤더 및 제어 버튼 구성
# -----------------------------------------------------------------------------
st.title("🏫 자리 배치 테스트 버전")

# [시작 / 다시 배치 버튼 영역]
btn_col1, btn_col2 = st.columns(2)

is_running = st.session_state.status == "ASSIGNING"

with btn_col1:
    if st.session_state.status == "IDLE":
        st.button("▶️ 시작", type="primary", use_container_width=True, on_click=assign_seats, disabled=is_running)
    else:
        st.button("▶️ 시작", type="primary", use_container_width=True, disabled=True)

with btn_col2:
    st.button("🔄 다시", use_container_width=True, on_click=reset_seats, disabled=is_running)

st.write("")

# -----------------------------------------------------------------------------
# 5. 교실 배치 화면 (칠판 + 25개 자리)
# -----------------------------------------------------------------------------
# [칠판 디자인]
st.markdown('<div class="blackboard">📋 칠 판 (Front)</div>', unsafe_allow_html=True)
st.markdown('<div class="teacher-desk">교 탁</div>', unsafe_allow_html=True)

# [25개 자리 5x5 교실 형태 배치]
# 5행 5열 구조 생성
TOTAL_SEATS = 25
COLS_PER_ROW = 5

for row in range(5):
    cols = st.columns(COLS_PER_ROW)
    for col in range(COLS_PER_ROW):
        seat_index = row * COLS_PER_ROW + col
        student_num = st.session_state.seats[seat_index]
        
        with cols[col]:
            # 자리 배정 여부에 따른 카드의 CSS 클래스 및 텍스트 선택
            if student_num is not None:
                card_html = f"""
                <div class="seat-card seat-card-assigned">
                    <div class="seat-label">자리 {seat_index + 1}</div>
                    <div class="student-number">{student_num}번</div>
                </div>
                """
            else:
                card_html = f"""
                <div class="seat-card">
                    <div class="seat-label">자리 {seat_index + 1}</div>
                    <div class="empty-number">-</div>
                </div>
                """
            st.markdown(card_html, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 6. 완료 상태 및 알림 메시지 표시
# -----------------------------------------------------------------------------
if st.session_state.status == "FINISHED":
    st.success("🎉 자리 배정이 성공적으로 완료되었습니다!")
    st.balloons()
