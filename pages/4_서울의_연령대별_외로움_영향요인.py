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
        ("양보다 질", "청년 — 접촉 잦아도 외로움 안 줄어"),
        ("대면접촉", "노년 — 만날수록 외로움 감소"),
        ("사회적 지지망", "청년·노년 공통 보호요인"),
    ],
)

st.markdown("""
1인가구의 우울 취약성(RQ3)을 배경으로, **외로움을 낮추는 요인이 연령대에 따라 어떻게 달라지는지**를 분석합니다.
\n소득·건강을 통제한 뒤에도 나타나는 차이를 통해, 정책 대응의 타깃을 연령별로 달리해야 하는 근거를 제공합니다.
""")

st.markdown("---")

# ── 변수 설명 (4개) ───────────────────────────────────────
labels = ["접촉 빈도", "사회적 지지망", "소득(log)", "건강 악화"]
descs = [
    ("접촉 빈도", "가족 외 지인·이웃을 <b>실제로 만나는 빈도</b>. 관계의 <b>양적</b> 지표."),
    ("사회적 지지망", "힘들 때 <b>도움받을 수 있는 사람</b>이 있는가. 관계의 <b>질적</b> 지표."),
    ("소득(log)", "가구원 연간 총소득(로그 변환). <b>경제적 자원</b> 통제변수."),
    ("건강 악화", "주관적 건강상태(나쁠수록 ↑). <b>신체·정신 건강</b> 통제변수."),
]
cols = st.columns(4)
for col, (name, desc) in zip(cols, descs):
    with col:
        st.markdown(f"""
        <div class="rq-card" style="border-top:3px solid #818cf8;">
        <div style="font-weight:700; color:#818cf8; margin-bottom:0.4rem;">{name}</div>
        <div style="font-size:0.82rem; color:#94a3b8; line-height:1.6;">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── 회귀 결과 그래프 (4변수) ──────────────────────────────
st.markdown("### 표준화 회귀계수 비교 (청년 vs 노년)")
reg    = welfare_loneliness_regression()
youth  = [reg["청년"]["coef"][l] for l in labels]
senior = [reg["노년"]["coef"][l] for l in labels]
y_sig  = [reg["청년"]["pval"][l] < 0.05 for l in labels]
s_sig  = [reg["노년"]["pval"][l] < 0.05 for l in labels]

x = np.arange(len(labels)); w = 0.35
fig, ax = plt.subplots(figsize=(9.5, 5))
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
ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=10.5)
ax.set_ylabel("표준화 회귀계수 (외로움 ↑)")
ax.set_title("외로움 영향 요인 — 청년 vs 노년 (소득·건강 통제)", fontweight="bold", pad=12)
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

    - 접촉 빈도: 양(+) — 잦은 접촉이 외로움 해소로 이어지지 않음
    - 사회적 지지망(**유의**) : 보호요인
    - 건강 악화(**유의**) : 건강이 나쁠수록 외로움 ↑ (효과 큼)
    - 소득: n.s. — 외로움과 무관
    </div>
    """, unsafe_allow_html=True)
with c2:
    st.markdown("""
    <div class="rq-card" style="border-top: 3px solid #f87171;">
    <div style="font-weight:800; color:#f87171; font-size:1rem; margin-bottom:0.5rem;">노년 (만 65세 이상)</div>

    - 접촉 빈도: 음(−) — 대면 접촉의 직접 완화 효과
    - 사회적 지지망(**유의**) : 보호요인
    - 건강 악화(**유의**) : 외로움 ↑
    - 소득(**유의**) : 소득 낮을수록 외로움 ↑ (경제적 취약)
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div class="insight-box">
<b>사회적 지지망</b>은 연령과 무관하게 외로움을 낮추는 일관된 보호요인이며,
소득·건강을 통제한 뒤에도 <b>접촉 빈도의 효과는 청년과 노년에서 정반대</b>로 나타납니다 —
노년은 자주 만날수록 덜 외로웠으나(대면 접촉의 직접 효과),
청년은 잦은 접촉에도 외로움이 줄지 않았습니다(양보다 질).
또한 <b>건강 악화</b>는 두 연령 모두에서 유의하게 외로움과 연관되었고, <b>소득</b>은 노년에서만 외로움과 연관되었습니다.
<br><br>
→ <b>노년</b>: 대면 접촉 기회 확대 + 경제·건강 지원<br>
→ <b>청년</b>: 의미 있는 관계망 형성 + 건강(정신건강 포함) 지원
</div>
""", unsafe_allow_html=True)
st.caption("R²는 청년 0.08 / 노년 0.10으로 사회과학 횡단면의 통상 범위. 인과가 아닌 연관으로 해석.")