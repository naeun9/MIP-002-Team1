"""RQ1 — 서울 시민의 사회관계망은 어떻게 변해왔는가?"""
import streamlit as st
import matplotlib.pyplot as plt
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))
from src.loaders import kgss_network_timeseries, get_centered_df
from src.font_setup import setup as _font_setup; _font_setup()
from src.page_setup import page_header

page_header(
    "RQ1 · 서울 시민의 사회관계망 변화",
    caption="KGSS 시계열 (2012 · 2016 · 2023)",
    kpis=[
        ("↓ 축소", "비가족 접촉 추세"),
        ("↓ 약화", "이웃 관계 변화"),
        ("3개 연도", "KGSS 측정 시점"),
    ],
)

ts = kgss_network_timeseries()

st.markdown("""
서울 시민의 **비가족 접촉**과 **이웃 관계**가 어떻게 변해왔는지를 봅니다.
관계의 양적 축소는 가족 밖 관계에 의존하는 1인가구가 취약해지는 배경이 됩니다.
""")

st.markdown("---")

# ── 시계열 그래프 ────────────────────────────────────────
st.markdown("### 관계망 시계열 (2012 → 2016 → 2023)")
fig, ax = plt.subplots(figsize=(9, 5))
ax.axvline(2020, color="#f87171", ls=":", lw=1.4, zorder=1)

ax.plot(ts["year"], ts["contactb"], "o-",  lw=2.5, ms=8, label="비가족 일일 접촉",    color="#818cf8", zorder=3)
ngh = ts[ts["nghgrt"].notna()]
ax.plot(ngh["year"], ngh["nghgrt"], "s--", lw=2.0, ms=7, label="인사하는 이웃",       color="#fb923c", zorder=3)
ax.plot(ngh["year"], ngh["nghask"], "^--", lw=2.0, ms=7, label="부탁할 수 있는 이웃", color="#34d399", zorder=3)

ax.set_xticks([2012, 2016, 2020, 2023])
ax.set_xticklabels(["2012", "2016", "2020\n(코로나)", "2023"])
for tick in ax.get_xticklabels():
    if "코로나" in tick.get_text():
        tick.set_color("#f87171")
ax.set_xlabel("연도"); ax.set_ylabel("평균 인원(명)")
ax.set_title("서울 시민 사회관계망 변화", fontweight="bold", pad=12)
ax.legend(loc="upper right"); ax.grid(alpha=0.4)
fig.tight_layout()
st.pyplot(fig, use_container_width=True)

# ── 수치 표 ──────────────────────────────────────────────
st.markdown("### 변화 요약")
show = ts[["year", "contactb", "nghgrt", "nghask"]].copy()
show.columns = ["연도", "비가족 접촉", "인사하는 이웃", "부탁할 수 있는 이웃"]
styled_show = (
    show.style
    .format({"연도": "{:.0f}", "비가족 접촉": "{:.2f}",
             "인사하는 이웃": "{:.2f}", "부탁할 수 있는 이웃": "{:.2f}"}, na_rep="—")
    .set_properties(**{"text-align": "center"})
    .set_table_styles([
        {"selector": "th", "props": [("text-align", "center")]},
        {"selector": "td", "props": [("text-align", "center")]},
    ])
    .hide(axis="index")
)
st.markdown(styled_show.to_html(), unsafe_allow_html=True)

st.markdown("""
<div class="insight-box">
서울 시민의 사회관계망은 전반적으로 <b>축소</b>되었고, 특히 <b>이웃 관계의 약화</b>가 두드러집니다.
가족 외 약한 유대와 지역 유대가 동반 감소하여, 가족 밖 관계에 의존하는 1인가구가
구조적으로 취약해지는 배경이 됩니다.
</div>
""", unsafe_allow_html=True)

st.caption("※ 이웃 관계(NGHGRT·NGHASK)는 2012·2023에만 측정되어 2016은 결측입니다.")
