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
    "작은 오해가 생길 수 있으니 따뜻한 말 한마디를 건네보
