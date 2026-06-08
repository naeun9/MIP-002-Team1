"""RQ1 — 서울 시민의 사회관계망은 어떻게 변해왔는가?"""
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))
from src.loaders import kgss_network_timeseries, oneperson_age_breakdown, oneperson_timeseries
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

st.markdown("---")

# ── 서울시 1인가구 연령대별 현황 (2024) ──────────────────────
st.markdown("### 서울시 1인가구 연령대별 현황 (2024)")

age_df, grp_df, total_one = oneperson_age_breakdown()

# KPI
peak_row  = age_df.loc[age_df["rate"].idxmax()]
youth_grp = grp_df[grp_df["연령대"].str.startswith("청년")].iloc[0]
c1, c2, c3 = st.columns(3)
c1.markdown(
    f'<div class="stat-card"><div class="stat-label">서울 전체 1인가구 수 (2024)</div>'
    f'<div class="stat-num">{total_one/10000:.0f}만</div></div>',
    unsafe_allow_html=True,
)
c2.markdown(
    f'<div class="stat-card"><div class="stat-label">1인가구율 최고 연령대</div>'
    f'<div class="stat-num">{peak_row["age"]}</div></div>',
    unsafe_allow_html=True,
)
c3.markdown(
    f'<div class="stat-card"><div class="stat-label">청년(20~39세) 구성비</div>'
    f'<div class="stat-num">{youth_grp["구성비"]:.1f}%</div></div>',
    unsafe_allow_html=True,
)
st.markdown("<br>", unsafe_allow_html=True)

# ── 시계열 증가 차트 ──────────────────────────────────────────
ts_df = oneperson_timeseries()
yrs = ts_df["연도"].tolist()

fig3, ax_ts = plt.subplots(figsize=(9, 4.5))
ax_ts.plot(yrs, ts_df["청년율"],   "o-",  lw=2.5, ms=8, color="#6366f1", label="청년(20~39세)")
ax_ts.plot(yrs, ts_df["중장년율"], "s--", lw=2.0, ms=7, color="#64748b", label="중장년(40~64세)")
ax_ts.plot(yrs, ts_df["노년율"],   "^--", lw=2.0, ms=7, color="#f87171", label="노년(65세+)")
for col, clr, dy in [("청년율", "#6366f1", 8), ("중장년율", "#64748b", -15), ("노년율", "#f87171", 8)]:
    for yr_v, val in zip(yrs, ts_df[col]):
        ax_ts.annotate(f"{val:.1f}%", (yr_v, val),
                       textcoords="offset points", xytext=(0, dy),
                       ha="center", fontsize=8.5, color=clr, fontweight="bold")
ax_ts.set_xticks(yrs)
ax_ts.set_ylabel("해당 연령 인구 대비 1인가구율 (%)")
ax_ts.set_title("연도별 연령 그룹별 1인가구율 (2022~2024)", fontweight="bold", pad=10)
ax_ts.legend(loc="center right", fontsize=8.5)
ax_ts.grid(alpha=0.35)

fig3.tight_layout()
st.pyplot(fig3, use_container_width=True)

st.markdown("""
<div class="insight-box">
2022→2024년 3개 연령 그룹의 1인가구율이 <b>모두 상승</b>했습니다.
<b>청년(20~39세)</b>의 증가 폭이 가장 커(26.6% → 28.2%), 1인가구 확산을 주도하고 있으며,
<b>노년(65세+)</b>도 완만하게 증가(19.2% → 20.1%)해 고립 위험 인구가 꾸준히 늘고 있습니다.
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── 차트 A: 연령대별 1인가구율 (수평 막대) ───────────────────
DECADE_MAP = [
    ("20대",  ["20~24세", "25~29세"],            "#6366f1"),
    ("30대",  ["30~34세", "35~39세"],            "#6366f1"),
    ("40대",  ["40~44세", "45~49세"],            "#64748b"),
    ("50대",  ["50~54세", "55~59세"],            "#64748b"),
    ("60대",  ["60~64세", "65~69세"],            "#f87171"),
    ("70대+", ["70~74세", "75~79세", "80~84세"], "#f87171"),
]
dec_rows = []
for label, bands, clr in DECADE_MAP:
    sub = age_df[age_df["age"].isin(bands)]
    tot_one = sub["one"].sum()
    tot_pop = sub["pop"].sum()
    dec_rows.append({"age": label, "rate": tot_one / tot_pop * 100 if tot_pop else 0, "color": clr})
dec_df = pd.DataFrame(dec_rows)

fig_a, ax1 = plt.subplots(figsize=(9, 4))
bars_l = ax1.barh(dec_df["age"], dec_df["rate"], color=dec_df["color"], alpha=0.75, height=0.6)
for bar, val in zip(bars_l, dec_df["rate"]):
    ax1.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2,
             f"{val:.1f}%", va="center", fontsize=9, color="#cbd5e1")
ax1.set_xlabel("해당 연령 인구 대비 1인가구 비율 (%)")
ax1.set_title("연령대별 1인가구율 (2024)", fontweight="bold", pad=10)
ax1.set_xlim(0, 42)
ax1.axvline(dec_df["rate"].mean(), color="#fbbf24", ls="--", lw=1.2,
            label=f"평균 {dec_df['rate'].mean():.1f}%")
ax1.legend(fontsize=8.5)
ax1.grid(axis="x", alpha=0.35)
fig_a.tight_layout()
st.pyplot(fig_a, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── 차트 B: 연령 그룹별 구성비 & 1인가구율 ───────────────────
grp_colors = ["#6366f1", "#64748b", "#f87171"]
x = range(len(grp_df))

fig_b, ax2 = plt.subplots(figsize=(9, 4))
ax2.bar(x, grp_df["구성비"], color=grp_colors, alpha=0.7, width=0.5)
ax2b = ax2.twinx()
ax2b.plot(x, grp_df["평균율"], "D--", lw=2.0, ms=8, color="#fbbf24",
          label="평균 1인가구율 (%)", zorder=3)
for i, (share, rate) in enumerate(zip(grp_df["구성비"], grp_df["평균율"])):
    ax2.text(i, share + 0.5, f"{share:.1f}%", ha="center", fontsize=9.5,
             color="#cbd5e1", fontweight="bold")
    ax2b.annotate(f"{rate:.1f}%", (i, rate), textcoords="offset points",
                  xytext=(0, 8), ha="center", fontsize=9, color="#fbbf24", fontweight="bold")
ax2.set_xticks(list(x))
ax2.set_xticklabels(grp_df["연령대"], fontsize=10)
ax2.set_ylabel("1인가구 중 연령 구성비 (%)")
ax2b.set_ylabel("해당 연령 인구 대비 1인가구율 (%)")
ax2b.set_ylim(0, 40)
ax2.set_ylim(0, 60)
ax2.set_title("연령 그룹별 구성비 & 1인가구율 (2024)", fontweight="bold", pad=10)
h, l = ax2b.get_legend_handles_labels()
ax2b.legend(h, l, loc="upper right", fontsize=8.5)
ax2.grid(axis="y", alpha=0.35)
fig_b.tight_layout()
st.pyplot(fig_b, use_container_width=True)

st.markdown("""
<div class="insight-box">
2024년 서울 1인가구 <b>166만 명</b> 중 청년(20~39세)이 <b>48.4%</b>로 절반에 가깝습니다.
연령대별 1인가구율은 <b>25~29세(34.5%)</b>에서 정점을 찍고, 30대 후반~50대에 낮아졌다가
노년층에서 다시 상승하는 <b>U자형</b> 구조를 보입니다.
청년은 자발적 독립, 노년은 사별·이별에 의한 비자발적 고립이 주된 원인으로,
두 연령대 모두 관계망 축소에 취약합니다.
</div>
""", unsafe_allow_html=True)