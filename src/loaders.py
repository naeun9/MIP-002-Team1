"""
데이터 로딩 + 분석 계산 모듈
모든 함수는 @st.cache로 캐싱되어 재실행 시 빠름.
원본 데이터(data/)를 읽어 앱에서 직접 계산 → 재현성 확보.
"""
import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
from pathlib import Path

DATA = Path(__file__).parent.parent / "data"

# KGSS 결측 코드
MISSING = [-8, -1, 8, 9, 88, 99, -9]
def clean(s):
    return s.where(~s.isin(MISSING))


# =====================================================
# RQ1 · RQ2도입 : KGSS
# =====================================================
@st.cache_data
def load_kgss():
    """KGSS parquet (서울만)"""
    df = pd.read_parquet(DATA / "kgss.parquet")
    return df[df["REGION"] == 1].copy()


@st.cache_data
def kgss_network_timeseries():
    """RQ1 — 비가족 접촉·이웃 관계 시계열 (2012·2016·2023)"""
    df = load_kgss()
    CONTACT_MID = {1:0, 2:1.5, 3:3.5, 4:7, 5:14.5, 6:34.5, 7:74.5, 8:100}
    NGH_MID     = {1:0, 2:1.5, 3:3.5, 4:7, 5:10}

    rows = []
    for yr in [2012, 2016, 2023]:
        sub = df[df["YEAR"] == yr]
        rec = {"year": yr}
        cb = clean(sub["CONTACTB"]).map(CONTACT_MID)
        rec["contactb"] = cb.mean()
        if yr in [2012, 2023]:
            rec["nghgrt"] = clean(sub["NGHGRT"]).map(NGH_MID).mean()
            rec["nghask"] = clean(sub["NGHASK"]).map(NGH_MID).mean()
        else:
            rec["nghgrt"] = np.nan
            rec["nghask"] = np.nan
        rows.append(rec)
    return pd.DataFrame(rows)


@st.cache_data
def kgss_loneliness_status():
    """RQ2 도입① — 외로움 현황 (2023·2025)"""
    df = load_kgss()
    sub = df[df["YEAR"].isin([2023, 2025])].copy()
    items = {"LONE4WKS": "교제 부족", "ISOL4WKS": "고립감", "LEFT4WKS": "소외감"}
    rows = []
    for var, lab in items.items():
        s = clean(sub[var])
        rows.append({
            "item": lab,
            "mean": s.mean(),
            "high_pct": (s >= 4).mean() * 100,
        })
    n = clean(sub[list(items)]).mean(axis=1).notna().sum()
    return pd.DataFrame(rows), int(n)


# =====================================================
# RQ2 : 서울시 행정통계 (우울)
# =====================================================
@st.cache_data
def depression_trend():
    """RQ2 도입② — 서울 전체 우울 경험률 추세 (2014~2023)"""
    raw = pd.read_excel(DATA / "서울시 자치구별 우울감 경험률(2014-2023).xlsx", sheet_name="데이터", header=None)
    cols = {y: c for y, c in zip(range(2014, 2024), [2,5,8,11,14,17,20,23,26,29])}
    vals = raw.iloc[2, list(cols.values())].apply(pd.to_numeric, errors="coerce")
    return pd.Series(vals.values, index=list(cols.keys()), name="우울경험률")


@st.cache_data
def depression_household():
    """RQ3 — 가구유형별 우울 (2022·2024·2025), 엑셀 직접 파싱"""
    raw = pd.read_excel(
        DATA / "서울시 가구 유형별 우울감 정도(2022, 2024, 2025).xlsx",
        header=None,
    )
    # row 14~17: 1인/부부/2세대이상/기타, col 3=2022경험, 7=2024우울, 11=2025느낀다
    rows    = [14, 15, 16, 17]
    labels  = ["1인가구", "부부가구", "2세대이상가구", "기타가구"]
    c2022, c2024, c2025 = 3, 7, 11
    return pd.DataFrame({
        "가구형태":    labels,
        "2022_경험":  [float(raw.iat[r, c2022]) for r in rows],
        "2024_우울":  [float(raw.iat[r, c2024]) for r in rows],
        "2025_느낀다": [float(raw.iat[r, c2025]) for r in rows],
    })


# =====================================================
# 외로움 회귀 : 서울복지실태조사 2024
# =====================================================
@st.cache_data
def welfare_loneliness_regression():
    """청년/노년 외로움 영향요인 회귀 (접촉·지지망·소득·건강, 표준화 계수 반환)"""
    import statsmodels.formula.api as smf

    raw = pd.read_excel(DATA / "DATA_서울시민의 생활실태 및 복지욕구 조사_가구원 데이터_SI공개용.xlsx")
    d = pd.DataFrame()

    # 종속: 외로움 (E3, 1~4)
    e3_rev = ["E3_1","E3_5","E3_6","E3_9","E3_10","E3_15","E3_16","E3_19","E3_20"]
    e3_fwd = ["E3_2","E3_3","E3_4","E3_7","E3_8","E3_11","E3_12","E3_13","E3_14","E3_18"]
    lone = raw[e3_fwd + e3_rev].apply(pd.to_numeric, errors="coerce")
    lone = lone.where((lone >= 1) & (lone <= 4))
    for c in e3_rev:
        lone[c] = 5 - lone[c]
    d["loneliness"] = lone.mean(axis=1)

    # 독립1: 접촉 빈도 (E1, 역코딩)
    e1 = raw[["E1_101","E1_102","E1_103","E1_104"]].apply(pd.to_numeric, errors="coerce")
    e1 = e1.where((e1 >= 1) & (e1 <= 5))
    d["contact"] = (6 - e1).mean(axis=1)

    # 독립2: 사회적 지지망 (E2, 있다 개수)
    e2 = raw[["E2_1","E2_2","E2_3","E2_4","E2_5"]].apply(pd.to_numeric, errors="coerce")
    d["support_net"] = (e2 == 1).sum(axis=1)

    # 통제1: 소득 (B7 합산 → log)
    b7 = raw[["B7_1","B7_2","B7_3","B7_4","B7_5","B7_6"]].apply(pd.to_numeric, errors="coerce")
    income = b7.fillna(0).sum(axis=1)
    d["income_log"] = np.log1p(income.where(income >= 0))

    # 통제2: 건강 악화 (C1_1, 1~5, 클수록 나쁨)
    health = pd.to_numeric(raw["C1_1"], errors="coerce")
    d["health_bad"] = health.where((health >= 1) & (health <= 5))

    d["female"] = (pd.to_numeric(raw["A1_4"], errors="coerce") == 2).astype(int)
    d["age"] = 2024 - pd.to_numeric(raw["A1_5_1"], errors="coerce")
    d = d.dropna(subset=["loneliness","contact","support_net","income_log","health_bad","age"])
    d = d[d["age"] >= 19]

    keymap = {"접촉 빈도": "contact_z", "사회적 지지망": "support_net_z",
              "소득(log)": "income_log_z", "건강 악화": "health_bad_z"}
    results = {}
    for grp, lo, hi in [("청년", 20, 39), ("노년", 65, 200)]:
        sub = d[(d["age"] >= lo) & (d["age"] <= hi)].copy()
        for col in ["contact","support_net","income_log","health_bad"]:
            sub[f"{col}_z"] = (sub[col]-sub[col].mean())/sub[col].std()
        m = smf.ols("loneliness ~ contact_z + support_net_z + income_log_z + health_bad_z + female",
                    data=sub).fit(cov_type="HC3")
        results[grp] = {
            "n": int(m.nobs),
            "coef": {lab: m.params[z] for lab, z in keymap.items()},
            "pval": {lab: m.pvalues[z] for lab, z in keymap.items()},
            "r2": m.rsquared,
        }
    return results


# =====================================================
# RQ3 · RQ4 : 자치구 (SQL JOIN + K-means)
# =====================================================
def _load_raw(path, n_age_cols):
    df = pd.read_excel(path, sheet_name="데이터", header=None)
    age_labels = df.iloc[2, 3:3+n_age_cols].tolist()
    df = df.iloc[3:].reset_index(drop=True)
    df.columns = ["gu1", "gu", "sex"] + age_labels
    df["gu1"] = df["gu1"].ffill()
    df["gu"]  = df["gu"].ffill()
    df = df[df["sex"] == "계"].copy()
    for c in age_labels:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


@st.cache_data
def load_districts():
    """RQ3 — 인구 ⨝ 1인가구 SQL JOIN → 비율·구성비 변수"""
    one_df = _load_raw(DATA / "1인가구 수(연령대별)(2024).xlsx", 16)
    pop_df = _load_raw(DATA / "서울시 자치구별 인구(연령대별) 2024.xlsx", 21)
    one_df = one_df[one_df["gu"] != "소계"].rename(columns={"gu":"district"}).drop(columns=["gu1","sex"])
    pop_df = pop_df[pop_df["gu"] != "소계"].rename(columns={"gu":"district"}).drop(columns=["gu1","sex"])

    one_map = {"youth":["20~24세","25~29세","30~34세","35~39세"],
               "middle":["40~44세","45~49세","50~54세","55~59세","60~64세"],
               "senior":["65~69세","70~74세","75~79세","80~84세","85세이상"]}
    pop_map = {"youth":["20~24세","25~29세","30~34세","35~39세"],
               "middle":["40~44세","45~49세","50~54세","55~59세","60~64세"],
               "senior":["65~69세","70~74세","75~79세","80~84세","85~89세","90~94세","95세 이상+"]}

    one_agg = pd.DataFrame({"district": one_df["district"].values})
    for k, cols in one_map.items():
        one_agg[f"one_{k}"] = one_df[cols].sum(axis=1).values
    one_agg["one_total"] = one_df["소계"].values

    pop_agg = pd.DataFrame({"district": pop_df["district"].values})
    for k, cols in pop_map.items():
        pop_agg[f"pop_{k}"] = pop_df[cols].sum(axis=1).values
    pop_agg["pop_total"] = pop_df["소계"].values

    conn = sqlite3.connect(":memory:")
    one_agg.to_sql("one_raw", conn, if_exists="replace", index=False)
    pop_agg.to_sql("pop_raw", conn, if_exists="replace", index=False)
    df = pd.read_sql("""
        SELECT o.district, o.one_youth, o.one_middle, o.one_senior, o.one_total,
               p.pop_total,
               ROUND(o.one_youth *100.0/p.pop_youth, 2)  AS rate_youth,
               ROUND(o.one_middle*100.0/p.pop_middle,2)  AS rate_middle,
               ROUND(o.one_senior*100.0/p.pop_senior,2)  AS rate_senior,
               ROUND(o.one_total *100.0/p.pop_total, 2)  AS rate_total,
               ROUND(o.one_youth *100.0/o.one_total, 2)  AS share_youth,
               ROUND(o.one_middle*100.0/o.one_total, 2)  AS share_middle,
               ROUND(o.one_senior*100.0/o.one_total, 2)  AS share_senior
        FROM one_raw o JOIN pop_raw p ON o.district = p.district;
    """, conn)
    conn.close()
    return df


@st.cache_data
def cluster_districts(k=3):
    """RQ4 — K-means 자치구 유형화 (연령 구성비 기반)"""
    from sklearn.preprocessing import StandardScaler
    from sklearn.cluster import KMeans

    df = load_districts().copy()
    X = df[["share_youth","share_middle","share_senior"]].values
    Xs = StandardScaler().fit_transform(X)
    km = KMeans(n_clusters=k, random_state=42, n_init=10).fit(Xs)
    df["cluster"] = km.labels_

    # 청년 구성비 평균으로 유형명 부여 (높은순: 청년밀집 / 중간: 세대균형 / 낮은: 중장년·노년)
    order = df.groupby("cluster")["share_youth"].mean().sort_values(ascending=False).index.tolist()
    names = {order[0]: "청년밀집형", order[1]: "세대혼합형", order[2]: "중장년·노년형"}
    policy = {
        "청년밀집형": "청년 사회관계망 형성·커뮤니티 공간",
        "세대혼합형": "생애주기별 복합 지원",
        "중장년·노년형": "노년 돌봄·고독사 예방·대면 접촉 확대",
    }
    df["유형"] = df["cluster"].map(names)
    df["정책방향"] = df["유형"].map(policy)
    return df

@st.cache_data
def oneperson_age_breakdown():
    """1인가구 + 인구 데이터 → 서울 전체 연령대별 1인가구 현황 (2024)"""
    one = _load_raw(DATA / "1인가구 수(연령대별)(2024).xlsx", 16)
    pop = _load_raw(DATA / "서울시 자치구별 인구(연령대별) 2024.xlsx", 21)

    one_s = one[one["gu"] == "소계"].iloc[0]
    pop_s = pop[pop["gu"] == "소계"].iloc[0]

    # 1인가구·인구 파일 공통 5세 단위 구간 (80~84세까지 매칭 가능)
    age_bands = [
        "20~24세", "25~29세", "30~34세", "35~39세",
        "40~44세", "45~49세", "50~54세", "55~59세", "60~64세",
        "65~69세", "70~74세", "75~79세", "80~84세",
    ]
    rows = []
    for ab in age_bands:
        ov = pd.to_numeric(one_s[ab], errors="coerce")
        pv = pd.to_numeric(pop_s[ab], errors="coerce")
        rows.append({"age": ab, "one": ov, "pop": pv,
                     "rate": ov / pv * 100 if pv else np.nan})
    df = pd.DataFrame(rows)

    total_one = pd.to_numeric(one_s["소계"], errors="coerce")
    df["share"] = df["one"] / total_one * 100

    # 3그룹 집계
    group_map = {
        "청년\n(20~39세)":   ["20~24세", "25~29세", "30~34세", "35~39세"],
        "중장년\n(40~64세)": ["40~44세", "45~49세", "50~54세", "55~59세", "60~64세"],
        "노년\n(65세+)":     ["65~69세", "70~74세", "75~79세", "80~84세"],
    }
    grp_rows = []
    for label, cols in group_map.items():
        sub = df[df["age"].isin(cols)]
        grp_rows.append({
            "연령대":    label,
            "1인가구수": sub["one"].sum(),
            "평균율":    sub["rate"].mean(),
            "구성비":    sub["share"].sum(),
        })
    grp_df = pd.DataFrame(grp_rows)

    return df, grp_df, int(total_one)


@st.cache_data
def oneperson_timeseries():
    """연도별(2022~2024) 서울 전체 1인가구 증가 추이 (연령 그룹별 인원·비율)"""
    one_raw = pd.read_excel(DATA / "1인가구 수(연령대별)(2022-2024).xlsx",          sheet_name="데이터", header=None)
    pop_raw = pd.read_excel(DATA / "서울시 자치구별 인구(연령대별)(2022-2024).xlsx", sheet_name="데이터", header=None)

    ONE_N, POP_N = 16, 21  # 연도당 age 열 수

    def _soegye(raw, year_idx, n_cols):
        start   = 3 + year_idx * n_cols
        labels  = raw.iloc[2, start:start + n_cols].tolist()
        gu_vals = raw.iloc[3:, 1].ffill().values
        sx_vals = raw.iloc[3:, 2].values
        block   = raw.iloc[3:, start:start + n_cols].reset_index(drop=True)
        block.columns = labels
        mask = (pd.Series(gu_vals) == "소계") & (pd.Series(sx_vals) == "계")
        row  = block.loc[mask.values].iloc[0]
        return {c: pd.to_numeric(row[c], errors="coerce") for c in labels}

    youth_bands  = ["20~24세", "25~29세", "30~34세", "35~39세"]
    middle_bands = ["40~44세", "45~49세", "50~54세", "55~59세", "60~64세"]

    rows = []
    for yi, yr in enumerate([2022, 2023, 2024]):
        one_d = _soegye(one_raw, yi, ONE_N)
        pop_d = _soegye(pop_raw, yi, POP_N)

        total_one = one_d["소계"]
        total_pop = pop_d["소계"]

        youth_one  = sum(one_d.get(b, 0) or 0 for b in youth_bands)
        middle_one = sum(one_d.get(b, 0) or 0 for b in middle_bands)
        sr_bands_o = [k for k in one_d if any(k.startswith(p) for p in ["65", "70", "75", "80", "85"])]
        senior_one = sum(one_d.get(b, 0) or 0 for b in sr_bands_o)

        youth_pop  = sum(pop_d.get(b, 0) or 0 for b in youth_bands)
        middle_pop = sum(pop_d.get(b, 0) or 0 for b in middle_bands)
        sr_bands_p = [k for k in pop_d if any(k.startswith(p) for p in ["65", "70", "75", "80", "85", "90", "95"])]
        senior_pop = sum(pop_d.get(b, 0) or 0 for b in sr_bands_p)

        rows.append({
            "연도":     yr,
            "총1인가구": int(total_one),
            "청년":      int(youth_one),
            "중장년":    int(middle_one),
            "노년":      int(senior_one),
            "1인가구율": total_one / total_pop * 100 if total_pop else np.nan,
            "청년율":    youth_one  / youth_pop  * 100 if youth_pop  else np.nan,
            "중장년율":  middle_one / middle_pop * 100 if middle_pop else np.nan,
            "노년율":    senior_one / senior_pop * 100 if senior_pop else np.nan,
        })

    return pd.DataFrame(rows)


def get_centered_df(df):
    return (
        df.style
        .set_properties(**{"text-align": "center"})
        .set_table_styles([
            {"selector": "th", "props": [("text-align", "center"), ("font-weight", "700")]},
            {"selector": "td", "props": [("text-align", "center")]},
        ])
    )
