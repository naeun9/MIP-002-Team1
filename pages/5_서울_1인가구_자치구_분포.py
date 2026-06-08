"""RQ4 — 어떤 연령층, 어느 지역에 1인가구가 많이 분포하는가?"""
import streamlit as st
import json
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))
from src.loaders import load_districts, get_centered_df
from src.page_setup import page_header

df   = load_districts()
DATA = Path(__file__).parent.parent / "data"

page_header(
    "RQ4 · 어떤 연령층·어느 지역에 1인가구가 분포하는가?",
    caption="인구 ⨝ 1인가구 SQL JOIN → 비율·구성비 + Folium 지도",
    kpis=[
        ("25개구", "서울 자치구 전체"),
        (f"{df['rate_total'].max():.1f}%",  "최고 1인가구율"),
        (f"{df['one_total'].max():,.0f}명", "최대 1인가구 절대수"),
    ],
)

# ── 랭킹 ─────────────────────────────────────────────────
st.markdown("### 규모 vs 밀집")
c1, c2 = st.columns(2)
with c1:
    st.markdown("""
    <div style="font-weight:700; color:#a5b4fc; margin-bottom:0.5rem;">
    🏆 1인가구 절대수 Top 5</div>
    """, unsafe_allow_html=True)
    top_n = df.nlargest(5, "one_total")[["district", "one_total"]].copy()
    top_n.columns = ["자치구", "1인가구 수"]
    styled_n = (
        top_n.style
        .format({"1인가구 수": "{:,.0f}"})
        .set_properties(**{"text-align": "center"})
        .set_table_styles([
            {"selector": "th", "props": [("text-align", "center")]},
            {"selector": "td", "props": [("text-align", "center")]},
        ])
        .hide(axis="index")
    )
    st.markdown(styled_n.to_html(), unsafe_allow_html=True)
with c2:
    st.markdown("""
    <div style="font-weight:700; color:#a5b4fc; margin-bottom:0.5rem;">
    🏆 인구 대비 비율 Top 5 (%)</div>
    """, unsafe_allow_html=True)
    top_r = df.nlargest(5, "rate_total")[["district", "rate_total"]].copy()
    top_r.columns = ["자치구", "1인가구율"]
    styled_r = (
        top_r.style
        .format({"1인가구율": "{:.2f}"})
        .set_properties(**{"text-align": "center"})
        .set_table_styles([
            {"selector": "th", "props": [("text-align", "center")]},
            {"selector": "td", "props": [("text-align", "center")]},
        ])
        .hide(axis="index")
    )
    st.markdown(styled_r.to_html(), unsafe_allow_html=True)

st.markdown("---")

# ── 지도 ─────────────────────────────────────────────────
st.markdown("<h3 style='text-align:center;'>연령대별 1인가구 분포 지도</h3>", unsafe_allow_html=True)
_, _radio_col, _ = st.columns([0.5, 9, 0.5])
with _radio_col:
    metric = st.radio("표시 지표", ["전체 1인가구율", "청년 1인가구율", "노년 1인가구율"], horizontal=True)
col_map = {"전체 1인가구율": "rate_total", "청년 1인가구율": "rate_youth", "노년 1인가구율": "rate_senior"}
col     = col_map[metric]

try:
    import folium
    from streamlit_folium import st_folium

    geo = json.loads((DATA / "seoul_municipalities.geojson").read_text(encoding="utf-8"))
    m   = folium.Map(location=[37.5665, 126.978], zoom_start=11, tiles="cartodbdarkmatter")
    folium.Choropleth(
        geo_data=geo, data=df, columns=["district", col],
        key_on="feature.properties.name", fill_color="YlOrRd",
        fill_opacity=0.75, line_opacity=0.3, legend_name=f"{metric} (%)",
    ).add_to(m)
    val_map = dict(zip(df["district"], df[col]))
    for feat in geo["features"]:
        name   = feat["properties"]["name"]
        coords = feat["geometry"]["coordinates"]
        if feat["geometry"]["type"] == "MultiPolygon":
            coords = max(coords, key=lambda p: len(p[0]))
        ring = coords[0]
        lat  = sum(p[1] for p in ring) / len(ring)
        lon  = sum(p[0] for p in ring) / len(ring)
        v    = val_map.get(name)
        folium.map.Marker(
            [lat, lon],
            icon=folium.features.DivIcon(
                icon_size=(72, 30), icon_anchor=(36, 15),
                html=f'<div style="font-size:8px;font-weight:700;text-align:center;'
                     f'color:#fff;text-shadow:0 0 3px #000;">{name}<br>{v}%</div>',
            ),
        ).add_to(m)
    _, map_col, _ = st.columns([0.5, 9, 0.5])
    with map_col:
        st_folium(m, width=None, height=520, returned_objects=[], use_container_width=True)
except ImportError:
    st.warning("지도 라이브러리(folium)가 설치되지 않았습니다.")
    st.dataframe(
        get_centered_df(df[["district", col]].set_index("district")),
        use_container_width=True,
    )

st.markdown("""
<div class="insight-box">
1인가구율이 높은 구(관악·광진·마포 등)는 대부분 <b>청년</b>이 밀어올린 것이며,
노년 1인가구는 오히려 1인가구율이 낮은 <b>외곽</b>에 분산됩니다.
"1인가구 밀집 = 청년 동네"라는 공간 구조가 확인됩니다.
</div>
""", unsafe_allow_html=True)
