import hashlib
import random
import time
from datetime import datetime, date
import streamlit as st

# ==========================================
# 1. 페이지 기본 설정 (밝고 깔끔한 레이아웃)
# ==========================================
st.set_page_config(
    page_title="오늘의 운세",
    page_icon="🔮",
    layout="centered"  # 중앙 정렬 방식으로 모바일/PC 모니터 모두 대응
)

# ==========================================
# 2. 운세 데이터 정의 (파이썬 리스트 활용)
# ==========================================
MONEY_LUCK = [
    "뜻밖의 용돈이나 소소한 재물이 들어올 수 있는 매우 운 좋은 날입니다!",
    "불필요한 지출을 줄이면 저녁쯤 작은 기쁨이 찾아옵니다.",
    "충동구입을 주의하세요. 꼭 필요한 것만 구매하는 지혜가 필요합니다.",
    "투자나 통장 정리를 하기에 아주 적절한 날입니다.",
    "주변 사람에게 작은 선물을 베풀면 더 큰 재물운으로 돌아옵니다."
]

LOVE_LUCK = [
    "마음속에 두고 있던 사람에게 따뜻한 안부 인사를 건네보기 좋은 날입니다.",
    "솔직하고 진심 어린 대화가 상대방의 마음을 움직입니다.",
    "새로운 인연을 만나거나 친구와의 우정이 더욱 깊어지는 하루입니다.",
    "작은 오해가 생길 수 있으니 상대방의 말을 끝까지 들어주세요.",
    "스스로를 사랑하는 시간을 가져보세요. 당신의 매력이 돋보이는 날입니다."
]

LUCKY_ITEMS = ["파란색 연필", "따뜻한 아메리카노", "노란색 포스트잇", "무선 이어폰", "푹신한 쿠션", "초록색 텀블러"]
LUCKY_COLORS = ["파스텔 핑크", "스카이 블루", "레몬 옐로우", "민트 그린", "라벤더"]

# ==========================================
# 3. 고정된 운세 생성 함수 (결과값 유지를 위함)
# ==========================================
def generate_fortune(birth_date: date) -> dict:
    """
    사용자의 생년월일과 '오늘 날짜'를 조합하여 매일 변경되지만,
    같은 날 안에서는 아무리 새로고침해도 동일한 결과가 나오도록 시드(Seed)를 설정합니다.
    """
    today_str = datetime.now().strftime("%Y-%m-%d")
    seed_string = f"{birth_date}_{today_str}"
    
    # 해시 함수(MD5)를 사용하여 숫자로 변환 후 랜덤 시드로 설정
    seed_number = int(hashlib.md5(seed_string.encode()).hexdigest(), 16)
    rng = random.Random(seed_number)
    
    return {
        "score": rng.randint(60, 100),  # 60~100점 사이의 종합 점수
        "money": rng.choice(MONEY_LUCK),
        "love": rng.choice(LOVE_LUCK),
        "item": rng.choice(LUCKY_ITEMS),
        "color": rng.choice(LUCKY_COLORS),
        "number": rng.randint(1, 99)
    }

# ==========================================
# 4. st.fragment를 활용한 실시간 상태 업데이트
# ==========================================
@st.fragment(run_every="5s")
def render_live_header():
    """
    5초마다 앱 전체를 다시 그리지 않고 이 부분만 실시간으로 업데이트합니다.
    앱 실행 중 운세 결과가 무작위로 변경되는 것을 방지하면서 실시간성을 유지합니다.
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.caption(f"⏱️ 실시간 서버 시간: {now} (5초마다 자동 갱신)")

# ==========================================
# 5. 세션 상태(Session State) 초기화
# ==========================================
if "is_loading" not in st.session_state:
    st.session_state.is_loading = False

if "fortune_data" not in st.session_state:
    st.session_state.fortune_data = None

# ==========================================
