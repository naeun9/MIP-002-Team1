"""RQ3-1 — 외로움 영향요인은 연령대별로 어떻게 다른가?"""
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))
from src.loaders import welfare_loneliness_regression
from src.font_setup import setup as _font_setup; _font_setup()
from src.page_setup import page_header

page_header(
    "RQ3-1 · 외로움 영향요인의 연령대별 차이",
    caption="서울복지실태조사 2024 — UCLA 외로움 척도 회귀 (청년 vs 노년)",
    kpis=[
        ("양보다 질", "청년 — 접촉 빈도 효과 없음(n.s.)"),
        ("대면접촉 ★", "노년 — 만날수록 외로움 감소"),
        ("지지망 ★★", "청년·노년 공통 보호요인"),
    ],
)

st.markdown("""
1인가구의 우울 취약성(RQ3)을 배경으로, **외로움을 낮추는 요인이 연령대에 따라 어떻게 달라지는지**를 분석합니다.
정책 대응의 타깃을 연령별로 달리해야 하는 근거를 제공합니다.
""")

st.markdown("---")

# ── 변수 설명 ─────────────────────────────────────────────
col_v1, col_v2, col_v3 = st.columns(3)
with col_v1:
    st.markdown("""
    <div class="rq-card" style="border-top:3px solid #818cf8;">
    <div style="font-weight:700; color:#818cf8; margin-bottom:0.4rem;">접촉 빈도</div>
    <div style="font-size:0.85rem; color:#94a3b8; line-height:1.6;">일주일간 가족 외 지인·이웃을 <b>실제로 만난 횟수</b>. 관계의 <b>양적</b> 지표.</div>
    </div>
    """, unsafe_allow_html=True)
with col_v2:
    st.markdown("""
    <div class="rq-card" style="border-top:3px solid #818cf8;">
    <div style="font-weight:700; color:#818cf8; margin-bottom:0.4rem;">사회적 지지망</div>
    <div style="font-size:0.85rem; color:#94a3b8; line-height:1.6;">힘들 때 <b>도움받을 수 있는 사람</b>이 있는가. 관계의 <b>질적</b> 지표.</div>
    </div>
    """, unsafe_allow_html=True)
with col_v3:
    st.markdown("""
    <div class="rq-card" style="border-top:3px solid #818cf8;">
    <div style="font-weight:700; color:#818cf8; margin-bottom:0.4rem;">주관적 지위</div>
    <div style="font-size:0.85rem; color:#94a3b8; line-height:1.6;">사회경제적 계층에서 <b>본인이 어느 위치</b>라고 느끼는지. 1(하)~10(상) 자기 평가.</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── 회귀 결과 그래프 ──────────────────────────────────────
st.markdown("### 표준화 회귀계수 비교 (청년 vs 노년)")
reg    = welfare_loneliness_regression()
labels = ["접촉 빈도", "사회적 지지망", "주관적 지위"]
youth  = [reg["청년"]["coef"][l] for l in labels]
senior = [reg["노년"]["coef"][l] for l in labels]
y_sig  = [reg["청년"]["pval"][l] < 0.05 for l in labels]
s_sig  = [reg["노년"]["pval"][l] < 0.05 for l in labels]

x = np.arange(len(labels)); w = 0.35
fig, ax = plt.subplots(figsize=(9, 5))
b1 = ax.bar(x - w/2, youth,  w, label=f"청년 (n={reg['청년']['n']})", color="#818cf8")
b2 = ax.bar(x + w/2, senior, w, label=f"노년 (n={reg['노년']['n']})", color="#f87171")
for bars, sig in [(b1, y_sig), (b2, s_sig)]:
    for bar, s in zip(bars, sig):
        h = bar.get_height()
        ax.annotate(
            "★" if s else "n.s.",
            (bar.get_x() + bar.get_width() / 2, h),
            textcoords="offset points",
            xytext=(0, 4 if h >= 0 else -15),
            ha="center", fontsize=10, fontweight="bold",
            color="#fbbf24" if s else "#475569",
        )
ax.axhline(0, color="#475569", lw=0.9)
ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=11)
ax.set_ylabel("표준화 회귀계수 (외로움 ↑)")
ax.set_title("외로움 영향 요인 — 청년 vs 노년", fontweight="bold", pad=12)
ax.legend(); ax.grid(axis="y", alpha=0.4)
fig.tight_layout()
st.pyplot(fig, use_container_width=True)

# ── 결과 카드 ─────────────────────────────────────────────
st.markdown("### 연령대별 주요 결과 요약")
c1, c2 = st.columns(2)
with c1:
    st.markdown("""
    <div class="rq-card" style="border-top: 3px solid #818cf8;">
    <div style="font-weight:800; color:#818cf8; font-size:1rem; margin-bottom:0.5rem;">청년 (만 19~39세)</div>

    - 접촉 빈도: **n.s.** — 양보다 질이 중요
    - 사회적 지지망: **★** — 보호요인
    - 주관적 지위: **★** — 사회적 위치감 중요
    </div>
    """, unsafe_allow_html=True)
with c2:
    st.markdown("""
    <div class="rq-card" style="border-top: 3px solid #f87171;">
    <div style="font-weight:800; color:#f87171; font-size:1rem; margin-bottom:0.5rem;">노년 (만 65세 이상)</div>

    - 접촉 빈도: **★** — 대면 접촉 직접 효과
    - 사회적 지지망: **★** — 보호요인
    - 주관적 지위: **n.s.**
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div class="insight-box">
<b>사회적 지지망</b>은 연령과 무관하게 외로움을 낮추는 일관된 보호요인입니다.
반면 <b>접촉 빈도의 효과는 반대</b>로 나타납니다 —
노년은 자주 만날수록 덜 외로웠으나(대면 접촉의 직접 효과),
청년은 잦은 접촉에도 외로움이 줄지 않았습니다(양보다 질).
<br><br>
→ <b>노년</b>: 대면 접촉 기회 확대 정책이 효과적<br>
→ <b>청년</b>: 의미 있는 관계망 형성 지원이 필요
</div>
""", unsafe_allow_html=True)
st.caption("R²는 0.05~0.08로 사회과학 횡단면의 통상 범위. 인과가 아닌 연관으로 해석.")
st.caption("→ 이 연령별 차이를 지역에 적용한 자원 배치는 RQ5(유형화·정책)에서 확인하세요.")
