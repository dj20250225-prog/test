import hashlib
import random
from datetime import date
import streamlit as st

# 페이지 기본 설정 (타이틀, 레이아웃)
st.set_page_config(
    page_title="오늘의 운세", page_icon="🔮", layout="centered"
)

# 커스텀 CSS 적용 (밝고 깔끔한 카드 디자인 및 반응형 스타일ing)
st.markdown(
    """
    <style>
    /* 배경색 및 기본 폰트 설정 */
    .stApp {
        background-color: #f7f9fc;
    }
    
    /* 중앙 카드 스타일 */
    .fortune-card {
        background-color: #ffffff;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
        margin-bottom: 1.5rem;
        text-align: center;
    }
    
    /* 제목 스타일 */
    .main-title {
        color: #4a4e69;
        font-size: 2.2rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    /* 부제목/날짜 스타일 */
    .sub-title {
        color: #6c757d;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }
    
    /* 운세 결과 항목 카드 */
    .result-item {
        background-color: #f8f9fa;
        border-left: 5px solid #70a1ff;
        padding: 1rem;
        margin-bottom: 1rem;
        border-radius: 5px;
        text-align: left;
    }
    
    /* 운세 카테고리 이름 */
    .category-name {
        font-weight: bold;
        color: #2f3542;
        font-size: 1.1rem;
    }
    
    /* 행운의 아이템 박스 */
    .lucky-box {
        background-color: #eccc68;
        color: #ffffff;
        padding: 0.8rem;
        border-radius: 10px;
        font-weight: bold;
        margin-top: 1rem;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# 데이터 정의 (운세 메시지 목록)
WEALTH_MESSAGES = [
    "뜻밖의 용돈을 받거나 작은 이득을 얻을 수 있는 날입니다! 💰",
    "지출을 조금 줄이면 나중에 큰 도움이 됩니다. 💳",
    "사고 싶었던 물건을 할인된 가격에 찾을 지도 몰라요! 🛍️",
    "친구와의 거래나 금전 거래는 신중하게 하세요. ⚠️",
]

FRIEND_MESSAGES = [
    "오래된 친구에게서 반가운 연락이 올 수 있어요! 📱",
    "새로운 친구를 만나 즐거운 대화를 나눌 기회가 생깁니다. 🤝",
    "친구의 고민을 들어주면 우정이 더욱 깊어집니다. 👂",
    "작은 오해가 생길 수 있으니 따뜻한 말 한마디를 건네보세요. 💬",
]

LOVE_MESSAGES = [
    "마음이 설레는 기분 좋은 일이 일어날 것 같아요! 💕",
    "주변 사람들에게 당신의 매력이 충분히 발산되는 날입니다. ✨",
    "좋아하는 사람에게 먼저 밝게 인사를 건네보세요! 😊",
    "혼자만의 시간을 가지며 자신을 사랑하는 하루를 보내세요. 🌿",
]

STUDY_MESSAGES = [
    "집중력이 최고조에 달해 공부나 일이 잘 풀리는 날입니다! 📖",
    "새로운 것을 배우기 아주 좋은 날이에요. 도전해보세요! 💡",
    "잠시 휴식을 취해야 효율이 더 올라갑니다. ☕",
    "포기하지 않고 끝까지 완수하면 좋은 결과를 얻습니다. 🎯",
]

LUCKY_ITEMS = ["파란색 학용품 ✏️", "달콤한 초콜릿 🍫", "따뜻한 차 한 잔 🍵", "좋아하는 노래 🎶", "노란색 소품 💛"]


# 시드 생성 함수 (이름 + 오늘 날짜 기반)
def get_daily_seed(name: str) -> int:
    today_str = str(date.today())
    # 이름과 오늘 날짜를 조합하여 문자열 생성
    combined = f"{name}_{today_str}"
    # SHA-256 해시를 사용하여 언제 입력해도 오늘 하루 동안은 같은 숫자가 나오도록 설정
    hash_val = hashlib.sha256(combined.encode()).hexdigest()
    return int(hash_val, 16)


# UI 구성 (중앙 카드 레이아웃)
st.markdown(
    """
    <div class="fortune-card">
        <div class="main-title">🔮 오늘의 운세</div>
        <div class="sub-title">오늘 당신을 기다리는 운세는 무엇일까요?</div>
    </div>
""",
    unsafe_allow_html=True,
)

# 사용자 입력 받는 영역
user_name = st.text_input("이름을 입력해주세요:", placeholder="예: 홍길동")

# 운세 보기 버튼
if st.button("🔮 운세보기", use_container_width=True):
    if not user_name.strip():
        st.warning("이름을 입력해 주세요!")
    else:
        # 오늘 날짜와 이름 기반으로 난수 시드 고정
        seed = get_daily_seed(user_name.strip())
        random.seed(seed)

        # 운세 결과 뽑기
        wealth = random.choice(WEALTH_MESSAGES)
        friend = random.choice(FRIEND_MESSAGES)
        love = random.choice(LOVE_MESSAGES)
        study = random.choice(STUDY_MESSAGES)
        lucky = random.choice(LUCKY_ITEMS)

        # 결과 화면 출력
        st.markdown(
            f"### 📜 **{user_name}**님의 {date.today().strftime('%Y년 %m월 %d일')} 운세"
        )

        # 모바일 대응을 위해 2열 레이아웃 사용 (화면 크기에 따라 자동 정렬)
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(
                f"""
                <div class="result-item">
                    <div class="category-name">💰 재물운</div>
                    <div>{wealth}</div>
                </div>
                <div class="result-item">
                    <div class="category-name">🤝 친구운</div>
                    <div>{friend}</div>
                </div>
            """,
                unsafe_allow_html=True,
            )

        with col2:
            st.markdown(
                f"""
                <div class="result-item">
                    <div class="category-name">❤️ 사랑운</div>
                    <div>{love}</div>
                </div>
                <div class="result-item">
                    <div class="category-name">📚 학업/성공운</div>
                    <div>{study}</div>
                </div>
            """,
                unsafe_allow_html=True,
            )

        # 행운의 아이템 출력
        st.markdown(
            f"""
            <div class="lucky-box" style="text-align: center;">
                🍀 오늘의 행운의 아이템: {lucky}
            </div>
        """,
            unsafe_allow_html=True,
        )
