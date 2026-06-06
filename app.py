"""
서울 1인가구와 외로움 분석 대시보드
KOSSDA 2026 / 경영정보처리론
"""
import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="서울 1인가구 외로움 지도",
    page_icon="🏙️",
    layout="wide",
)

css = Path(__file__).parent / "assets" / "style.css"
if css.exists():
    st.markdown(f"<style>{css.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

# ===== 히어로 =====
st.markdown('<div class="accent-bar"></div>', unsafe_allow_html=True)
st.markdown('<div class="main-title">🏙️ 서울 1인가구와 외로움 분석</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">데이터로 읽는 한국 사회 — 변화와 미래 &nbsp;|&nbsp; '
    'KGSS · 서울시 행정통계 · 서울복지실태조사</div>',
    unsafe_allow_html=True,
)

st.markdown("""
서울 시민의 **사회관계망 변화**와 **외로움·우울 양상**을 진단하고,
**1인가구의 우울 취약성**과 **외로움 영향요인의 연령대별 차이**를 분석하여,
자치구별 **연령 구성에 따른 정책 자원 배치 방향**을 제안합니다.
""")

# ===== KPI 카드 =====
k1, k2, k3, k4 = st.columns(4)
kpis = [
    ("19.4%", "1인가구 우울 비율 (2025)"),
    ("8.4%",  "서울 우울 경험률 최고치 (2023)"),
    ("25개구", "서울 자치구 분석 대상"),
    ("3유형",  "K-means 정책 군집"),
]
for col, (num, label) in zip([k1, k2, k3, k4], kpis):
    col.markdown(
        f'<div class="stat-card"><div class="stat-num">{num}</div>'
        f'<div class="stat-label">{label}</div></div>',
        unsafe_allow_html=True,
    )

st.markdown("---")

# ===== Part 1 =====
st.markdown("#### Part 1 · 사회관계망, 외로움, 우울")
cols1 = st.columns(4)
rqs_part1 = [
    ("RQ1",   "사회관계망은 어떻게 변했는가?",                    "KGSS 시계열"),
    ("RQ2",   "서울 시민의 외로움과 우울은 어떤 양상을 보이는가?", "KGSS + 행정통계"),
    ("RQ3",   "1인가구는 다른 가구보다 우울에 더 취약한가?",        "가구유형별 비교"),
    ("RQ3-1", "외로움 영향요인은 연령대별로 어떻게 다른가?",        "복지실태조사 회귀"),
]
for col, (tag, q, method) in zip(cols1, rqs_part1):
    col.markdown(
        f'<div class="rq-card">'
        f'<span class="rq-tag">{tag}</span>'
        f'<div class="rq-q">{q}</div>'
        f'<div style="color:#475569;font-size:0.78rem;margin-top:0.55rem;">{method}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

st.markdown("---")

# ===== Part 2 =====
st.markdown("#### Part 2 · 분포와 자원 배치")
cols2 = st.columns(2)
rqs_part2 = [
    ("RQ4", "어떤 연령층, 어느 지역에 1인가구가 많이 분포하는가?", "자치구 SQL + 지도"),
    ("RQ5", "어느 지역에 자원을 우선 배치해야 하는가?",            "K-means 유형화"),
]
for col, (tag, q, method) in zip(cols2, rqs_part2):
    col.markdown(
        f'<div class="rq-card">'
        f'<span class="rq-tag">{tag}</span>'
        f'<div class="rq-q">{q}</div>'
        f'<div style="color:#475569;font-size:0.78rem;margin-top:0.55rem;">{method}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

st.markdown("---")
st.info("👈 왼쪽 사이드바에서 각 분석 페이지(RQ1 ~ RQ5)를 확인하세요.")

with st.expander("📊 데이터 출처 및 방법"):
    st.markdown("""
    - **KGSS 한국종합사회조사** (누적, 2003~2025) — 사회관계망·외로움 *(DOI: 10.22687/KOSSDA-A1-CUM-0074-V1)*
    - **서울시 가구유형별 우울감** (2022·2024·2025)
    - **서울시 자치구별 우울 경험률** (2014~2023)
    - **서울복지실태조사** (2024, 가구원) — UCLA 외로움 척도 회귀
    - **서울시 자치구별 인구·1인가구** (2024)

    모든 분석은 원본 데이터를 앱에서 직접 계산하여 재현 가능합니다.
    """)
