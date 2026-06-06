"""각 RQ 페이지 공통 초기화 — CSS 주입 + 헤더 렌더링"""
import streamlit as st
from pathlib import Path

_CSS_PATH = Path(__file__).parent.parent / "assets" / "style.css"


def inject_css():
    if _CSS_PATH.exists():
        st.markdown(
            f"<style>{_CSS_PATH.read_text(encoding='utf-8')}</style>",
            unsafe_allow_html=True,
        )


def page_header(title: str, caption: str = "", kpis: list = None, highlight_idx: int = None):
    """
    accent-bar + 그라데이션 타이틀 + 선택적 KPI 카드 행을 렌더링한다.
    kpis = [("값", "레이블"), ...]  /  highlight_idx: 강조할 카드 인덱스
    """
    inject_css()
    st.markdown('<div class="accent-bar"></div>', unsafe_allow_html=True)
    st.title(title)
    if caption:
        st.caption(caption)
    if kpis:
        cols = st.columns(len(kpis))
        for i, (col, (num, label)) in enumerate(zip(cols, kpis)):
            if i == highlight_idx:
                col.markdown(
                    f'<div class="stat-card" style="border-color:rgba(248,113,113,0.5);background:rgba(248,113,113,0.07);">'
                    f'<div class="stat-label">{label}</div>'
                    f'<div class="stat-num" style="background:linear-gradient(135deg,#f87171,#fb923c);'
                    f'-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">{num}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            else:
                col.markdown(
                    f'<div class="stat-card">'
                    f'<div class="stat-label">{label}</div>'
                    f'<div class="stat-num">{num}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
        st.markdown("<br>", unsafe_allow_html=True)
