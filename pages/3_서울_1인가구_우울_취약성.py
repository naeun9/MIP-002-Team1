"""RQ3 — 1인가구는 다른 가구보다 우울에 더 취약한가?"""
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))
from src.loaders import depression_household, get_centered_df
from src.font_setup import setup as _font_setup; _font_setup()
from src.page_setup import page_header

df = depression_household()
# 기타가구는 2022값이 측정방식 이질로 크게 튀므로 주요 비교에서 제외
main = df[df["가구형태"] != "기타가구"].copy()

page_header(
    "RQ3 · 1인가구는 다른 가구보다 우울에 더 취약한가?",
    caption="가구유형별 우울감 비교 (행정통계 2022·2024·2025)",
    kpis=[
        ("19.4%", "1인가구 우울 (2025)"),
        ("9.6%",  "부부가구 우울 (2025)"),
        ("7.8%",  "2세대이상 우울 (2025)"),
        ("×2.0",  "1인/부부 배율"),
    ],
    highlight_idx=0,
)

st.markdown("""
RQ2에서 확인한 서울 전체 우울 상승이 **가구 유형에 따라 다르게 나타나는지** 검토합니다.\n
엑셀 원본에는 **1인가구·부부가구·2세대이상가구·기타가구** 4개 유형이 있습니다.
""")

st.markdown("---")

# ── 그룹 막대 : 3개 연도 × 3가구 ────────────────────────────
st.markdown("### 연도·가구유형별 우울감 비교 (2022·2024·2025)")

labels  = main["가구형태"].tolist()
y2022   = main["2022_경험"].tolist()
y2024   = main["2024_우울"].tolist()
y2025   = main["2025_느낀다"].tolist()
x       = np.arange(len(labels))
w       = 0.26
COLORS  = ["#94a3b8", "#818cf8", "#f87171"]

fig, ax = plt.subplots(figsize=(10, 5))
b0 = ax.bar(x - w,   y2022, w, label="2022 우울감 경험 여부(%)",   color=COLORS[0])
b1 = ax.bar(x,       y2024, w, label="2024 우울감 정도(%)",   color=COLORS[1])
b2 = ax.bar(x + w,   y2025, w, label="2025 우울감을 느낀다(%)", color=COLORS[2])
for bars in [b0, b1, b2]:
    ax.bar_label(bars, fmt="%.1f", padding=3,
                 color="#cbd5e1", fontsize=9, fontweight="bold")
ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=11)
ax.set_ylabel("우울 응답 비율 (%)"); ax.set_ylim(0, 26)
ax.set_title("가구유형별 우울감 — 1인가구가 모든 연도에서 최고", fontweight="bold", pad=12)
ax.legend(); ax.grid(axis="y", alpha=0.4)
fig.tight_layout()
st.pyplot(fig, use_container_width=True)

st.caption("2022는 '우울 경험 여부'(이분), 2024·2025는 '우울하다/느낀다 (%)' — 척도 차이로 직접 비교 시 주의")

st.markdown("---")

# ── 연도별 꺾은선 추이 : 가구유형별 3선 ─────────────────────
st.markdown("### 연도별 1인가구 vs 다른 가구 추이")
years = [2022, 2024, 2025]
STYLES = [
    ("1인가구",      "#f87171", "o", "-",  2.8, 9),
    ("부부가구",     "#818cf8", "s", "--", 2.2, 8),
    ("2세대이상가구","#34d399", "^", "-.", 2.2, 8),
]
fig2, ax2 = plt.subplots(figsize=(9, 5))
for name, color, marker, ls, lw, ms in STYLES:
    row = main[main["가구형태"] == name].iloc[0]
    vals = [row["2022_경험"], row["2024_우울"], row["2025_느낀다"]]
    ax2.plot(years, vals, marker=marker, ls=ls, lw=lw, ms=ms,
             color=color, label=name)
    for yr, v in zip(years, vals):
        ax2.annotate(f"{v:.1f}%", (yr, v),
                     textcoords="offset points", xytext=(0, 9),
                     ha="center", fontsize=9, color=color, fontweight="bold")
ax2.set_xticks(years)
ax2.set_xlim(2021, 2026)
ax2.set_ylabel("우울 응답 비율 (%)")
ax2.set_ylim(0, 25)
ax2.set_title("가구유형별 우울 추이 — 1인가구 일관 최고", fontweight="bold", pad=12)
ax2.legend(loc="upper left"); ax2.grid(axis="y", alpha=0.4)
fig2.tight_layout()
st.pyplot(fig2, use_container_width=True)

# ── 수치 표 ──────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 원본 수치 (기타가구 포함)")
disp = df.rename(columns={
    "가구형태":    "가구형태",
    "2022_경험":  "2022 우울감 경험 여부(%)",
    "2024_우울":  "2024 우울감 정도(%)",
    "2025_느낀다": "2025 우울감을 느낀다(%)",
})
_num_cols_rq3 = ["2022 우울감 경험 여부(%)", "2024 우울감 정도(%)", "2025 우울감을 느낀다(%)"]

styled_rq3 = (
    disp.style
    .format({c: "{:g}" for c in _num_cols_rq3})
    .set_properties(**{"text-align": "center"})
    .set_table_styles([
        {"selector": "th", "props": [("text-align", "center")]},
        {"selector": "td", "props": [("text-align", "center")]},
    ])
    .hide(axis="index")
)
st.markdown(styled_rq3.to_html(), unsafe_allow_html=True)
st.caption("※ 기타가구 2022(14.4%)는 측정 대상이 달라 2024·2025(0.7%·1.6%)와 단순 비교 불가")

st.markdown("""
<div class="insight-box">
<b>1인가구</b>는 2022·2024·2025 세 연도 모두에서 우울 비율이 가장 높습니다(최대 19.4%).
<b>2세대 이상 가구</b>(7.4→7.7→7.8%)는 연도 간 변화가 작고 부부가구(6.8→5.7→9.6%)와
비슷한 수준을 유지합니다. 결국 가구 규모가 클수록 우울 방어 효과가 나타나며,
혼자 거주한다는 사실 자체가 우울의 <b>구조적·지속적 위험 요인</b>임을 확인합니다.
</div>
""", unsafe_allow_html=True)