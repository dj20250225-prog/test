# -*- coding: utf-8 -*-
"""
나만의 크리에이터 - 영상 + 이미지 합성 웹앱
- Python 표준 라이브러리 + Streamlit만 사용합니다.
- 외부 API, JavaScript, 외부 Streamlit 컴포넌트는 쓰지 않습니다.
"""

import base64          # 파일을 문자로 바꿔 HTML 안에 넣을 때 사용
import hashlib         # 파일이 같은지 확인하는 '지문(해시)' 만들 때 사용
import math            # 올림(ceil) 계산에 사용
import time            # 정확한 시간 측정에 사용
from datetime import datetime
from pathlib import Path

import streamlit as st

# 페이지 기본 설정은 반드시 Streamlit 명령 중 가장 먼저 실행해야 합니다.
APP_TITLE = "나만의 크리에이터"
APP_ICON = "🎬"
st.set_page_config(page_title=APP_TITLE, page_icon=APP_ICON, layout="centered")

# ============================================================
# 1. 학생이 바꿔 볼 수 있는 설정 구역
# ============================================================

# (1) 색상: 16진수 색상 코드(#RRGGBB)를 바꿔 보세요.
COLORS = {
    "primary": "#4F8CFF",   # 주요 색 (제목, 시계 숫자, 시작 버튼)
    "accent": "#FF8A5B",    # 포인트 색 (진행률 막대)
    "bg_start": "#EAF4FF",  # 배경 그라데이션 시작색
    "bg_end": "#FFF3EA",    # 배경 그라데이션 끝색
    "card": "#FFFFFF",      # 카드 배경색
    "text": "#22314A",      # 글자색
    "soft": "#F2F7FF",      # 시계 상자 배경색
}

# (2) 빠른 설정 시간: (버튼 이름, 분, 초) 형태로 추가/수정할 수 있어요.
QUICK_TIMES = [
    ("30초", 0, 30),
    ("1분", 1, 0),
    ("3분", 3, 0),
    ("5분", 5, 0),
]

# (3) 제한값: 비정상적인 값을 막기 위한 한계
MAX_MINUTES = 60        # 최대 설정 시간(분)
MAX_VIDEO_MB = 30       # 영상 최대 크기(MB)
MAX_IMAGE_MB = 10       # 이미지 최대 크기(MB)
UPDATE_SECONDS = 0.5    # 진행 화면을 새로 그리는 간격(초)
SAVE_FOLDER = Path("results")  # '서버에 저장'을 누르면 파일이 저장되는 폴더

# 이미지가 놓일 위치 (CSS 위치 값)
POSITIONS = {
    "왼쪽 위": "top:4%;left:4%;",
    "오른쪽 위": "top:4%;right:4%;",
    "왼쪽 아래": "bottom:4%;left:4%;",
    "오른쪽 아래": "bottom:4%;right:4%;",
    "가운데": "top:50%;left:50%;transform:translate(-50%,-50%);",
}

# 처음 값 (초기화 버튼을 누르면 이 값으로 돌아갑니다)
DEFAULTS = {
    "minutes": 0,
    "seconds": 30,
    "position": "오른쪽 아래",
    "size": 25,
    "opacity": 100,
}

# 파일 확장자별 MIME 종류 (브라우저에게 파일 종류를 알려 줍니다)
MIME_TYPES = {
    "mp4": "video/mp4", "webm": "video/webm",
    "png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg",
    "gif": "image/gif", "webp": "image/webp",
}

# 상태별로 시계 위에 보여 줄 문구
STATUS_TEXT = {
    "idle": "대기 중 · 설정한 시간",
    "running": "합성 중 · 남은 시간",
    "paused": "일시정지 · 남은 시간",
    "done": "합성 완료",
}


# ============================================================
# 2. 상태(session_state) 준비
#    Streamlit은 버튼을 누를 때마다 코드를 처음부터 다시 실행해요.
#    그래서 기억해야 할 값은 session_state에 보관합니다.
# ============================================================
def init_state():
    s = st.session_state
    s.setdefault("status", "idle")          # idle(대기) / running / paused / done
    s.setdefault("elapsed_before", 0.0)     # 일시정지 전까지 지난 시간(초)
    s.setdefault("started_at", None)        # 마지막으로 시작/계속한 시각
    s.setdefault("job", None)               # 시작 순간에 '고정'해 둔 작업 정보
    s.setdefault("saved_path", None)        # 서버에 저장된 파일 경로
    s.setdefault("result_bytes", None)      # 다운로드용 결과 파일
    s.setdefault("result_name", "")         # 다운로드 파일 이름
    s.setdefault("uploader_ver", 0)         # 업로더를 비울 때 올리는 번호
    s.setdefault("error_msg", "")           # 화면에 보여 줄 오류 문구
    for key, value in DEFAULTS.items():     # 설정값 기본 채우기
        s.setdefault(key, value)


# ============================================================
# 3. 도우미 함수들
# ============================================================
def get_mime(filename):
    """파일 이름 끝(확장자)으로 파일 종류를 알아냅니다."""
    ext = filename.rsplit(".", 1)[-1].lower()
    return MIME_TYPES.get(ext, "application/octet-stream")


def sha(data):
    """파일 내용의 '지문'을 만듭니다. 내용이 1비트만 달라도 지문이 달라져요."""
    return hashlib.sha256(data).hexdigest()


def get_uploaded():
    """지금 올라와 있는 영상, 이미지 파일을 돌려줍니다."""
    s = st.session_state
    video = s.get(f"video_{s.uploader_ver}")
    image = s.get(f"image_{s.uploader_ver}")
    return video, image


def current_total():
    """분 + 초를 합쳐서 전체 초로 계산합니다. 이상한 값이면 0으로 처리해요."""
    s = st.session_state
    try:
        return int(s.minutes) * 60 + int(s.seconds)
    except (TypeError, ValueError):
        return 0


def get_elapsed():
    """
    지금까지 지난 시간(초)을 계산합니다.
    - 실행 중: (이전에 쌓인 시간) + (이번 구간에서 지난 시간)
    - 일시정지/완료: 쌓아 둔 시간 그대로
    time.monotonic()은 시계를 바꿔도 흔들리지 않는 정확한 시간이에요.
    """
    s = st.session_state
    if s.job is None:
        return 0.0
    if s.status == "running" and s.started_at is not None:
        elapsed = s.elapsed_before + (time.monotonic() - s.started_at)
    else:
        elapsed = s.elapsed_before
    return min(elapsed, float(s.job["total"]))  # 전체 시간보다 커지지 않게


# ---------- 입력값 검사 (잘못된 값은 시작할 수 없게 막습니다) ----------
def check_files():
    video, image = get_uploaded()
    if video is None or image is None:
        return "영상과 이미지를 모두 올려 주세요."
    if video.size == 0 or image.size == 0:
        return "빈 파일은 사용할 수 없어요."
    if video.size > MAX_VIDEO_MB * 1024 * 1024:
        return f"영상은 {MAX_VIDEO_MB}MB 이하만 사용할 수 있어요."
    if image.size > MAX_IMAGE_MB * 1024 * 1024:
        return f"이미지는 {MAX_IMAGE_MB}MB 이하만 사용할 수 있어요."
    return ""


def check_time():
    total = current_total()
    if total <= 0:
        return "0분 0초로는 시작할 수 없어요. 1초 이상으로 정해 주세요."
    if total > MAX_MINUTES * 60:
        return f"시간은 최대 {MAX_MINUTES}분까지만 설정할 수 있어요."
    return ""


def check_options():
    s = st.session_state
    try:
        size_ok = 10 <= int(s.size) <= 60
        opacity_ok = 20 <= int(s.opacity) <= 100
    except (TypeError, ValueError):
        return "설정값이 올바르지 않아요. 초기화를 눌러 주세요."
    if s.position not in POSITIONS or not size_ok or not opacity_ok:
        return "설정값이 올바르지 않아요. 초기화를 눌러 주세요."
    return ""


# ---------- 합성 화면(HTML) 만들기 ----------
def build_overlay_html(video_bytes, video_name, image_bytes, image_name,
                       position, size, opacity):
    """
    영상 위에 이미지를 겹친 HTML 조각을 만듭니다.
    파일을 base64 문자로 바꿔 HTML 안에 직접 넣기 때문에
    하나의 파일만으로 어디서든 재생됩니다. (JavaScript는 쓰지 않아요)
    """
    video_b64 = base64.b64encode(video_bytes).decode("ascii")
    image_b64 = base64.b64encode(image_bytes).decode("ascii")
    video_src = f"data:{get_mime(video_name)};base64,{video_b64}"
    image_src = f"data:{get_mime(image_name)};base64,{image_b64}"
    pos_css = POSITIONS[position]
    return (
        '<div style="position:relative;width:100%;line-height:0;'
        'border-radius:16px;overflow:hidden;background:#000;">'
        f'<video src="{video_src}" controls autoplay muted loop playsinline '
        'style="width:100%;height:auto;display:block;"></video>'
        f'<img src="{image_src}" alt="합성 이미지" '
        f'style="position:absolute;{pos_css}width:{size}%;height:auto;'
        f'opacity:{opacity / 100};pointer-events:none;">'
        "</div>"
    )


def wrap_standalone_page(body_html):
    """합성 화면을 '혼자서도 열리는 HTML 파일' 형태로 감쌉니다."""
    return (
        '<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        f"<title>{APP_TITLE}</title>"
        f'<style>body{{margin:0;padding:16px;background:{COLORS["bg_start"]};'
        'font-family:sans-serif;}.wrap{max-width:900px;margin:0 auto;}</style>'
        f'</head><body><div class="wrap">{body_html}</div></body></html>'
    )


# ============================================================
# 4. 버튼을 눌렀을 때 실행되는 함수들 (콜백)
# ============================================================
def set_quick(minutes, seconds):
    """빠른 설정 시간 버튼: 분/초 칸에 값을 채워 넣습니다."""
    st.session_state.minutes = minutes
    st.session_state.seconds = seconds


def on_start():
    """시작: 입력을 검사하고, 그 순간의 파일·설정을 '고정'합니다."""
    s = st.session_state
    msg = check_files() or check_time() or check_options()
    if msg:
        s.error_msg = msg
        return
    video, image = get_uploaded()
    video_bytes = video.getvalue()
    image_bytes = image.getvalue()
    size = max(10, min(60, int(s.size)))
    opacity = max(20, min(100, int(s.opacity)))

    # 이 job에 담긴 값만 실행 중에 사용합니다.
    # → 실행 중에 영상·이미지·설정이 달라질 수 없어요.
    s.job = {
        "total": current_total(),
        "video_name": video.name,
        "image_name": image.name,
        "video_hash": sha(video_bytes),
        "image_hash": sha(image_bytes),
        "position": s.position,
        "size": size,
        "opacity": opacity,
        "html": build_overlay_html(video_bytes, video.name, image_bytes,
                                   image.name, s.position, size, opacity),
        "matched": None,
    }
    s.status = "running"
    s.elapsed_before = 0.0
    s.started_at = time.monotonic()
    s.saved_path = None
    s.result_bytes = None
    s.error_msg = ""


def on_pause():
    """일시정지: 지금까지 지난 시간을 저장해 둡니다."""
    s = st.session_state
    if s.status == "running":
        s.elapsed_before = get_elapsed()   # 지난 시간 저장
        s.started_at = None                # 시계 멈춤
        s.status = "paused"


def on_resume():
    """계속: 저장해 둔 시간 뒤부터 다시 셉니다. (그래서 시간이 정확해요)"""
    s = st.session_state
    if s.status == "paused":
        s.started_at = time.monotonic()
        s.status = "running"


def on_reset():
    """초기화: 모든 값을 처음 상태로 되돌립니다."""
    s = st.session_state
    s.status = "idle"
    s.elapsed_before = 0.0
    s.started_at = None
    s.job = None
    s.saved_path = None
    s.result_bytes = None
    s.result_name = ""
    s.error_msg = ""
    s.uploader_ver += 1                  # 번호를 바꾸면 업로더가 비워집니다
    for key, value in DEFAULTS.items():  # 설정값도 처음으로
        s[key] = value


def finish_job():
    """시간이 다 되면 호출: 결과 파일을 만들고, 파일이 일치하는지 확인합니다."""
    s = st.session_state
    job = s.job
    video, image = get_uploaded()
    # 실행 전에 고정해 둔 지문과 지금 파일의 지문이 같은지 비교합니다.
    job["matched"] = (
        video is not None and image is not None
        and sha(video.getvalue()) == job["video_hash"]
        and sha(image.getvalue()) == job["image_hash"]
    )
    s.elapsed_before = float(job["total"])
    s.started_at = None
    s.status = "done"
    s.result_bytes = wrap_standalone_page(job["html"]).encode("utf-8")
    s.result_name = datetime.now().strftime("creator_%Y%m%d_%H%M%S.html")


def on_save():
    """서버(실행 중인 컴퓨터)의 results 폴더에 결과를 저장합니다."""
    s = st.session_state
    if s.status != "done" or s.result_bytes is None:
        return
    try:
        SAVE_FOLDER.mkdir(exist_ok=True)
        path = SAVE_FOLDER / s.result_name
        path.write_bytes(s.result_bytes)
        s.saved_path = str(path)
        s.error_msg = ""
    except OSError:
        s.error_msg = "파일을 저장하지 못했어요. 다운로드 버튼을 이용해 주세요."


# ============================================================
# 5. 화면 꾸미기 (CSS)
# ============================================================
def inject_css():
    css = """
    <style>
    .stApp { background: linear-gradient(135deg, __BG_START__, __BG_END__);
             color: __TEXT__; }
    /* 가운데 카드 */
    .block-container, [data-testid="stMainBlockContainer"] {
        max-width: 760px !important; background: __CARD__;
        border-radius: 24px; padding: 2rem 1.5rem !important;
        margin: 1.5rem auto; box-shadow: 0 10px 40px rgba(79,140,255,0.18);
    }
    .app-title { text-align:center; font-size:2.1rem; font-weight:800;
                 color: __PRIMARY__; margin:0; padding:0; }
    .app-sub { text-align:center; color:#6B7A90; margin:0 0 1rem 0; }
    .step-title { font-weight:700; font-size:1.05rem; margin:1.1rem 0 .3rem; }
    .timer-box { background: __SOFT__; border-radius:18px; padding:1rem;
                 text-align:center; margin:.5rem 0; }
    .timer-label { font-size:.95rem; color:#6B7A90; }
    .timer-num { font-size:2.8rem; font-weight:800; color: __PRIMARY__;
                 font-variant-numeric: tabular-nums; }
    /* 버튼 */
    .stButton > button, .stDownloadButton > button {
        width:100%; min-height:3rem; border-radius:14px; font-weight:700; }
    .stButton > button[kind="primary"] {
        background: __PRIMARY__; border-color: __PRIMARY__; color:#fff; }
    /* 진행률 막대 색 */
    .stProgress div[role="progressbar"] > div { background-color: __ACCENT__; }
    /* 스마트폰: 버튼을 2열로 정렬 */
    @media (max-width: 640px) {
        .block-container, [data-testid="stMainBlockContainer"] {
            padding: 1.2rem .9rem !important; margin: .5rem auto;
            border-radius: 18px; }
        div[data-testid="stColumn"], div[data-testid="column"] {
            min-width: calc(50% - 1rem) !important;
            flex: 1 1 calc(50% - 1rem) !important; }
        .app-title { font-size:1.7rem; }
        .timer-num { font-size:2.3rem; }
    }
    </style>
    """
    for name, value in COLORS.items():
        css = css.replace(f"__{name.upper()}__", value)
    st.markdown(css, unsafe_allow_html=True)


# ============================================================
# 6. 진행 패널 (0.5초마다 자동으로 새로 그려지는 부분)
# ============================================================
def render_timer_panel():
    s = st.session_state
    job = s.job
    total = job["total"] if job else current_total()
    elapsed = get_elapsed()

    # 실행 중에 시간이 다 되면 완료 처리 후 전체 화면을 새로 그립니다.
    if s.status == "running" and elapsed >= total:
        finish_job()
        st.rerun()

    remaining = max(0, math.ceil(total - elapsed))
    minutes, seconds = divmod(remaining, 60)
    if s.status == "done":
        minutes, seconds = 0, 0
    if s.status == "idle":
        minutes, seconds = divmod(total, 60)

    ratio = 0.0 if total <= 0 else min(1.0, elapsed / total)
    st.markdown(
        f'<div class="timer-box"><div class="timer-label">'
        f'{STATUS_TEXT[s.status]}</div>'
        f'<div class="timer-num">{minutes:02d}:{seconds:02d}</div></div>',
        unsafe_allow_html=True,
    )
    st.progress(ratio, text=f"{int(ratio * 100)}% 진행")


# ============================================================
# 7. 메인 화면
# ============================================================
def main():
    init_state()
    inject_css()
    s = st.session_state
    locked = s.status != "idle"   # 실행 중·일시정지·완료 상태에서는 설정 잠금

    st.markdown(f'<h1 class="app-title">{APP_ICON} {APP_TITLE}</h1>',
                unsafe_allow_html=True)
    st.markdown('<p class="app-sub">영상 위에 내 이미지를 올려 합성해 보세요</p>',
                unsafe_allow_html=True)

    # ----- 1단계: 파일 올리기 -----
    st.markdown('<div class="step-title">1️⃣ 영상과 이미지 고르기</div>',
                unsafe_allow_html=True)
    st.file_uploader("영상 (mp4, webm)", type=["mp4", "webm"],
                     key=f"video_{s.uploader_ver}", disabled=locked)
    st.file_uploader("이미지 (png, jpg, gif, webp)",
                     type=["png", "jpg", "jpeg", "gif", "webp"],
                     key=f"image_{s.uploader_ver}", disabled=locked)

    # ----- 2단계: 설정 -----
    st.markdown('<div class="step-title">2️⃣ 합성 설정하기</div>',
                unsafe_allow_html=True)
    st.selectbox("이미지 위치", list(POSITIONS.keys()),
                 key="position", disabled=locked)
    col1, col2 = st.columns(2)
    col1.slider("이미지 크기 (%)", 10, 60, step=5, key="size", disabled=locked)
    col2.slider("이미지 진하기 (%)", 20, 100, step=5, key="opacity",
                disabled=locked)

    st.caption("⏱️ 합성 시간")
    col1, col2 = st.columns(2)
    col1.number_input("분", min_value=0, max_value=MAX_MINUTES, step=1,
                      key="minutes", disabled=locked)
    col2.number_input("초", min_value=0, max_value=59, step=1,
                      key="seconds", disabled=locked)

    # 빠른 설정 시간 버튼
    quick_cols = st.columns(len(QUICK_TIMES))
    for i, (label, m, sec) in enumerate(QUICK_TIMES):
        quick_cols[i].button(label, key=f"quick_{i}", on_click=set_quick,
                             args=(m, sec), disabled=locked)

    # 입력값 오류 안내 (잘못된 값이면 시작 버튼이 꺼집니다)
    problems = [m for m in (check_files(), check_time(), check_options()) if m]
    if not locked:
        for message in problems:
            st.warning(message)
    if s.error_msg:
        st.error(s.error_msg)

    # ----- 버튼 (모바일에서는 2열) -----
    st.markdown('<div class="step-title">3️⃣ 실행하기</div>',
                unsafe_allow_html=True)
    b1, b2, b3, b4 = st.columns(4)
    b1.button("▶️ 시작", key="btn_start", type="primary", on_click=on_start,
              disabled=(s.status != "idle" or bool(problems)))
    b2.button("⏸️ 일시정지", key="btn_pause", on_click=on_pause,
              disabled=(s.status != "running"))
    b3.button("⏯️ 계속", key="btn_resume", on_click=on_resume,
              disabled=(s.status != "paused"))
    b4.button("🔄 초기화", key="btn_reset", on_click=on_reset)

    # ----- 진행 패널: 실행 중일 때만 0.5초마다 자동 갱신 -----
    run_every = UPDATE_SECONDS if s.status == "running" else None
    st.fragment(run_every=run_every)(render_timer_panel)()

    # ----- 합성 화면 -----
    st.markdown('<div class="step-title">4️⃣ 합성 화면</div>',
                unsafe_allow_html=True)
    job = s.job
    if job is not None:
        # 실행 중에는 '고정해 둔 작업(job)'만 보여 줍니다.
        st.html(job["html"])
        st.caption(f"🎞️ {job['video_name']} ({job['video_hash'][:8]}) · "
                   f"🖼️ {job['image_name']} ({job['image_hash'][:8]})  "
                   "— 실행 중에는 이 파일로 고정돼요.")
    elif not check_files() and not check_options():
        # 대기 중에는 미리보기를 보여 줍니다.
        video, image = get_uploaded()
        st.html(build_overlay_html(video.getvalue(), video.name,
                                   image.getvalue(), image.name,
                                   s.position, int(s.size), int(s.opacity)))
    else:
        st.info("영상과 이미지를 올리면 여기에 미리보기가 나타나요.")

    # ----- 결과 저장 / 다운로드 -----
    if s.status == "done" and job is not None:
        st.success("🎉 합성이 끝났어요!")
        if job["matched"]:
            st.success("✅ 실행 중 사용한 영상·이미지가 처음 선택한 파일과 정확히 일치해요.")
        else:
            st.error("⚠️ 파일이 처음 선택한 것과 달라요. 초기화 후 다시 시도해 주세요.")
        c1, c2 = st.columns(2)
        c1.download_button("⬇️ 다운로드", data=s.result_bytes,
                           file_name=s.result_name, mime="text/html")
        c2.button("💾 서버에 저장", key="btn_save", on_click=on_save)
        if s.saved_path:
            st.info(f"저장 위치: {s.saved_path}")


main()
