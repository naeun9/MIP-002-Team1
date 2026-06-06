"""RQ2 — 서울 시민의 외로움과 우울은 어떤 양상을 보이는가?"""
import streamlit as st
import matplotlib.pyplot as plt
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))
from src.loaders import kgss_loneliness_status, depression_trend, get_centered_df
from src.font_setup import setup as _font_setup; _font_setup()
from src.page_setup import page_header

page_header(
    "RQ2 · 서울 시민의 외로움과 우울 양상",
    caption="외로움 현황(KGSS 2023·2025) → 우울 경험률 추세(행정통계 2014~2023)",
    kpis=[
        ("4.8%",  "교제부족 '자주 이상' 비율"),
        ("8.4%",  "우울 경험률 최고치 (2023)"),
        ("5.1%",  "우울 경험률 최저치 (2018)"),
    ],
)

# ── ① 외로움 현황 ─────────────────────────────────────────
st.markdown("### ① 서울 시민의 외로움 현황 (KGSS 2023·2025)")
lone, n = kgss_loneliness_status()

fig, ax = plt.subplots(figsize=(8, 4))
bars = ax.bar(lone["item"], lone["high_pct"],
              color=["#f87171", "#fb923c", "#fb923c"], width=0.5)
ax.bar_label(bars, fmt="%.1f%%", padding=4,
             color="#e2e8f0", fontsize=10, fontweight="bold")
ax.set_ylabel("자주+매우 자주 (%)"); ax.set_ylim(0, 7)
ax.set_title(f"외로움을 자주 이상 느낀 비율 (n={n})", fontweight="bold", pad=10)
ax.grid(axis="y", alpha=0.4)
fig.tight_layout()
st.pyplot(fig, use_container_width=True)
st.caption("교제 부족이 가장 높음 — 관계의 양적 부족이 질적 단절보다 먼저 나타남")

lone_disp = lone.rename(columns={
    "item":     "외로움 항목",
    "mean":     "평균 점수",
    "high_pct": "자주 이상 비율(%)",
})
styled_lone = (
    lone_disp.style
    .format({"평균 점수": "{:.2f}", "자주 이상 비율(%)": "{:.2f}"})
    .set_properties(**{"text-align": "center"})
    .set_table_styles([
        {"selector": "th", "props": [("text-align", "center")]},
        {"selector": "td", "props": [("text-align", "center")]},
    ])
    .hide(axis="index")
)
st.markdown(styled_lone.to_html(), unsafe_allow_html=True)

st.markdown("""
<div class="insight-box">
서울 시민이 가장 빈번하게 느끼는 외로움은 <b>교제·동반자 부족</b>입니다.
관계의 질적 단절보다 <b>양적 부족</b>이 앞서 나타나는 점이 특징입니다.
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ── ② 우울 추세 ──────────────────────────────────────────
st.markdown("### ② 서울 전체 우울 경험률 추세 (행정통계 2014~2023)")
trend = depression_trend()
fig, ax = plt.subplots(figsize=(9, 4.5))
ax.axvline(2020, color="#f87171", ls=":", lw=1.2)
ax.text(2020.12,
        trend.values.min() + (trend.values.max() - trend.values.min()) * 0.82,
        "코로나(2020)", color="#f87171", fontsize=9)
ax.plot(trend.index, trend.values, "o-", lw=2.5, ms=7, color="#818cf8")
ax.plot(2023, trend.loc[2023], "o", ms=11, color="#f87171", zorder=5,
        label=f"2023년 최고치 {trend.loc[2023]:.1f}%")
ax.set_xticks(list(trend.index)); ax.set_ylabel("우울 경험률 (%)")
ax.set_title("서울 우울 경험률 — 코로나 후 최고치", fontweight="bold", pad=10)
ax.legend(); ax.grid(alpha=0.4)
fig.tight_layout()
st.pyplot(fig, use_container_width=True)

st.markdown("""
<div class="insight-box">
서울 우울 경험률은 2018년 최저(5.1%)에서 2023년 <b>최고(8.4%)</b>로 상승했습니다.
코로나 이후 사회관계망 축소와 맞물려 우울 수준이 구조적으로 높아진 양상입니다.
</div>
""", unsafe_allow_html=True)
st.caption("외로움 현황과는 출처·주기가 달라 겹쳐 해석하지 않음. → 가구유형별 차이는 RQ3에서 심층 분석")
