"""RQ5 — 어느 지역에 자원을 우선 배치해야 하는가?"""
import streamlit as st
import json
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))
from src.loaders import cluster_districts, get_centered_df
from src.page_setup import page_header

df   = cluster_districts()
DATA = Path(__file__).parent.parent / "data"

TYPE_COLOR = {"청년밀집형": "#6366f1", "세대혼합형": "#64748b", "중장년·노년형": "#f87171"}
TYPE_CLASS = {"청년밀집형": "card-a", "세대혼합형": "card-b", "중장년·노년형": "card-c"}

page_header(
    "RQ5 · 어느 지역에 자원을 우선 배치해야 하는가?",
    caption="K-means 연령 구성 군집화",
    kpis=[
        ("3유형", "K-means 군집 수"),
        ("25개구", "분류 대상"),
    ],
)

# ── 유형 요약 카드 ─────────────────────────────────────────
st.markdown("### 자치구 3유형")
cards_html = '<div style="display:flex; flex-direction:row; gap:1rem;">'
for tname, color in TYPE_COLOR.items():
    sub = df[df["유형"] == tname]
    districts = " · ".join(sub["district"].tolist())
    y_pct  = sub["share_youth"].mean()
    m_pct  = sub["share_middle"].mean()
    s_pct  = sub["share_senior"].mean()
    cards_html += (
        f'<div class="rq-card {TYPE_CLASS[tname]}" style="flex:1; height:auto; border-top:3px solid {color}; display:flex; flex-direction:column; padding:0.75rem 0.85rem;">'
        f'<div style="font-weight:900; color:{color}; font-size:0.95rem; margin-bottom:0.05rem;">{tname}</div>'
        f'<div style="font-size:0.75rem; color:#94a3b8; margin-bottom:0.55rem;">{len(sub)}개 구</div>'
        f'<div style="font-size:0.68rem; color:#64748b; font-weight:600; text-transform:uppercase; letter-spacing:0.04em; margin-bottom:0.25rem;">연령 구성</div>'
        f'<div style="display:flex; gap:0.3rem; margin-bottom:0.55rem;">'
        f'  <div style="flex:1; text-align:center; background:rgba(148,163,184,0.08); border-radius:5px; padding:0.2rem 0;">'
        f'    <div style="font-size:0.65rem; color:#64748b;">청년</div>'
        f'    <div style="font-size:0.82rem; font-weight:800; color:#cbd5e1;">{y_pct:.0f}%</div>'
        f'  </div>'
        f'  <div style="flex:1; text-align:center; background:rgba(148,163,184,0.08); border-radius:5px; padding:0.2rem 0;">'
        f'    <div style="font-size:0.65rem; color:#64748b;">중장년</div>'
        f'    <div style="font-size:0.82rem; font-weight:800; color:#cbd5e1;">{m_pct:.0f}%</div>'
        f'  </div>'
        f'  <div style="flex:1; text-align:center; background:rgba(148,163,184,0.08); border-radius:5px; padding:0.2rem 0;">'
        f'    <div style="font-size:0.65rem; color:#64748b;">노년</div>'
        f'    <div style="font-size:0.82rem; font-weight:800; color:#cbd5e1;">{s_pct:.0f}%</div>'
        f'  </div>'
        f'</div>'
        f'<div style="font-size:0.72rem; color:#64748b; line-height:1.6; margin-bottom:0.4rem;">{districts}</div>'
        f'</div>'
    )
cards_html += '</div>'
st.markdown(cards_html, unsafe_allow_html=True)

st.markdown("---")

# ── 유형 지도 ─────────────────────────────────────────────
st.markdown("<h3 style='text-align:center;'>자치구 유형 지도</h3>", unsafe_allow_html=True)
try:
    import folium
    from streamlit_folium import st_folium

    geo       = json.loads((DATA / "seoul_municipalities.geojson").read_text(encoding="utf-8"))
    dist_type = dict(zip(df["district"], df["유형"]))
    m         = folium.Map(location=[37.5665, 126.978], zoom_start=11, tiles="cartodbdarkmatter")

    def style_fn(feat):
        t = dist_type.get(feat["properties"]["name"])
        return {"fillColor": TYPE_COLOR.get(t, "#475569"),
                "color": "#0f172a", "weight": 1.5, "fillOpacity": 0.72}

    folium.GeoJson(
        geo,
        style_function=style_fn,
        tooltip=folium.GeoJsonTooltip(fields=["name"], aliases=[""]),
    ).add_to(m)
    for feat in geo["features"]:
        name   = feat["properties"]["name"]
        coords = feat["geometry"]["coordinates"]
        if feat["geometry"]["type"] == "MultiPolygon":
            coords = max(coords, key=lambda p: len(p[0]))
        ring = coords[0]
        lat  = sum(p[1] for p in ring) / len(ring)
        lon  = sum(p[0] for p in ring) / len(ring)
        folium.map.Marker(
            [lat, lon],
            icon=folium.features.DivIcon(
                icon_size=(62, 22), icon_anchor=(31, 11),
                html=f'<div style="font-size:8px;font-weight:700;text-align:center;'
                     f'color:#fff;text-shadow:0 0 3px #000;">{name}</div>',
            ),
        ).add_to(m)
    _, map_col, _ = st.columns([0.5, 9, 0.5])
    with map_col:
        st_folium(m, width=None, height=520, returned_objects=[], use_container_width=True)
except ImportError:
    st.warning("지도 라이브러리(folium)가 없습니다.")

# ── 자치구 상세 표 ────────────────────────────────────────
st.markdown("---")
st.markdown("### 자치구별 상세")

TYPE_ORDER = ["전체", "청년밀집형", "세대혼합형", "중장년·노년형"]
sort_by = st.radio("정렬 기준", TYPE_ORDER, horizontal=True)

base = (
    df[["district", "유형", "rate_total", "share_youth", "share_senior"]]
    .rename(columns={
        "district":     "자치구",
        "rate_total":   "1인가구율(%)",
        "share_youth":  "청년구성비(%)",
        "share_senior": "노년구성비(%)",
    })
    .round(2)
)
if sort_by == "전체":
    base = base.sort_values("자치구")
else:
    base = base[base["유형"] == sort_by].sort_values("자치구")

NUM_COLS = ["1인가구율(%)", "청년구성비(%)", "노년구성비(%)"]
styled = (
    base.style
    .format({c: "{:.2f}" for c in NUM_COLS})
    .set_properties(**{"text-align": "center"})
    .set_table_styles([
        {"selector": "th", "props": [("text-align", "center")]},
        {"selector": "td", "props": [("text-align", "center")]},
    ])
    .hide(axis="index")
)
st.markdown(styled.to_html(), unsafe_allow_html=True)

st.markdown("""
<div class="insight-box">
회귀(RQ3-1)에서 밝힌 <b>연령별 외로움 원인 차이</b>를 군집(RQ5)의 <b>연령별 지역 분포</b>와 결합하면:
<br>• <b>청년밀집형</b> → 관계의 질 중심, 커뮤니티·관계망 형성 사업
<br>• <b>세대혼합형</b> → 생애주기별 복합 지원, 맞춤형 프로그램
<br>• <b>중장년·노년형</b> → 대면 접촉이 효과적, 돌봄·고독사 예방 집중
</div>
""", unsafe_allow_html=True)
st.caption("※ K-means는 25개 구를 3유형으로 요약하는 정리 도구이며, 분석적 발견은 회귀가 담당합니다.")
