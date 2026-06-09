"""
데이터 로딩 + 분석 모듈 (SQL 기반)

[설계]
  원본 정제는 build_db.py 가 끝내고 seoul.db 에 적재한다.
  이 모듈의 각 함수는 seoul.db 에 SQL 쿼리를 던져 집계·결합·랭킹을 수행한다.
  → 구간 중간값 매핑, 연령대 그룹핑, 비율·구성비 산출, 자치구 JOIN 까지 모두 SQL.
  → 통계 모델(OLS 회귀, K-means)만 입력을 SQL 로 뽑은 뒤 Python 으로 적합한다.

  seoul.db 가 없으면 build_db.main() 을 자동 호출해 1회 생성한다.
"""
import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
from pathlib import Path

DATA = Path(__file__).parent.parent / "data"
DB_PATH = DATA / "seoul.db"

# 연령대 그룹 정의 (SQL IN 절에 주입)
YOUTH  = ["20~24세", "25~29세", "30~34세", "35~39세"]
MIDDLE = ["40~44세", "45~49세", "50~54세", "55~59세", "60~64세"]
SENIOR_ONE = ["65~69세", "70~74세", "75~79세", "80~84세", "85세이상"]
SENIOR_POP = ["65~69세", "70~74세", "75~79세", "80~84세",
              "85~89세", "90~94세", "95세 이상+"]
# oneperson_age_breakdown 전용 — 1인가구·인구 공통 매칭 가능한 5세 구간(80~84세까지)
AGE13 = ["20~24세", "25~29세", "30~34세", "35~39세",
         "40~44세", "45~49세", "50~54세", "55~59세", "60~64세",
         "65~69세", "70~74세", "75~79세", "80~84세"]


def _q(s):
    """리스트 → SQL IN 절 문자열  ['a','b'] → "'a','b'" """
    return ",".join(f"'{x}'" for x in s)


def get_conn():
    """seoul.db 연결 (없으면 build_db 로 생성)"""
    if not DB_PATH.exists():
        import sys
        sys.path.append(str(Path(__file__).parent.parent))
        import build_db
        build_db.main()
    return sqlite3.connect(DB_PATH)


# =====================================================
# RQ1 · RQ2 도입 : KGSS  (구간 중간값 매핑 → SQL CASE WHEN)
# =====================================================
@st.cache_data
def kgss_network_timeseries():
    """RQ1 — 비가족 접촉·이웃 관계 시계열 (2012·2016·2023)
    구간형 응답을 중간값(명)으로 환산하여 연도별 평균. 매핑·집계 모두 SQL."""
    contact_case = """CASE CONTACTB
        WHEN 1 THEN 0 WHEN 2 THEN 1.5 WHEN 3 THEN 3.5 WHEN 4 THEN 7
        WHEN 5 THEN 14.5 WHEN 6 THEN 34.5 WHEN 7 THEN 74.5 WHEN 8 THEN 100 END"""
    ngh_case = lambda col: f"""CASE {col}
        WHEN 1 THEN 0 WHEN 2 THEN 1.5 WHEN 3 THEN 3.5 WHEN 4 THEN 7 WHEN 5 THEN 10 END"""
    sql = f"""
        SELECT YEAR AS year,
               AVG({contact_case}) AS contactb,
               CASE WHEN YEAR IN (2012, 2023) THEN AVG({ngh_case('NGHGRT')}) END AS nghgrt,
               CASE WHEN YEAR IN (2012, 2023) THEN AVG({ngh_case('NGHASK')}) END AS nghask
        FROM kgss_seoul
        WHERE YEAR IN (2012, 2016, 2023)
        GROUP BY YEAR
        ORDER BY YEAR;
    """
    with get_conn() as conn:
        return pd.read_sql(sql, conn)


@st.cache_data
def kgss_loneliness_status():
    """RQ2 도입① — 외로움 현황 (2023·2025)
    mean = 유효응답 평균 / high_pct = 전체 응답 중 '자주(4)+매우자주' 비율."""
    items = [("LONE4WKS", "교제 부족"), ("ISOL4WKS", "고립감"), ("LEFT4WKS", "소외감")]
    selects = []
    for var, _ in items:
        selects.append(f"AVG({var}) AS {var}_mean")
        selects.append(
            f"SUM(CASE WHEN {var} >= 4 THEN 1.0 ELSE 0 END) * 100.0 / COUNT(*) AS {var}_high"
        )
    sql = f"""
        SELECT {', '.join(selects)},
               COUNT(CASE WHEN LONE4WKS IS NOT NULL OR ISOL4WKS IS NOT NULL
                            OR LEFT4WKS IS NOT NULL THEN 1 END) AS n_valid
        FROM kgss_seoul
        WHERE YEAR IN (2023, 2025);
    """
    with get_conn() as conn:
        r = pd.read_sql(sql, conn).iloc[0]
    rows = [{"item": lab, "mean": r[f"{var}_mean"], "high_pct": r[f"{var}_high"]}
            for var, lab in items]
    return pd.DataFrame(rows), int(r["n_valid"])


# =====================================================
# RQ2 : 서울시 행정통계 (우울)
# =====================================================
@st.cache_data
def depression_trend():
    """RQ2 도입② — 서울 전체 우울 경험률 추세 (2014~2023)"""
    with get_conn() as conn:
        df = pd.read_sql("SELECT year, rate FROM depression_trend ORDER BY year;", conn)
    return pd.Series(df["rate"].values, index=df["year"].astype(int).values, name="우울경험률")


@st.cache_data
def depression_household():
    """RQ3 — 가구유형별 우울 (2022·2024·2025)"""
    with get_conn() as conn:
        df = pd.read_sql(
            "SELECT household_type, y2022, y2024, y2025 FROM depression_household;", conn
        )
    return df.rename(columns={
        "household_type": "가구형태",
        "y2022": "2022_경험", "y2024": "2024_우울", "y2025": "2025_느낀다",
    })


# =====================================================
# 외로움 회귀 : 서울복지실태조사 2024
#   변수 정제는 DB(welfare 테이블)에서 완료 → 표준화·OLS만 Python
# =====================================================
@st.cache_data
def welfare_loneliness_regression():
    """청년/노년 외로움 영향요인 회귀 (표준화 계수). 입력은 welfare 테이블에서 SQL 조회."""
    import statsmodels.formula.api as smf

    keymap = {"접촉 빈도": "contact_z", "사회적 지지망": "support_net_z",
              "소득(log)": "income_log_z", "건강 악화": "health_bad_z"}
    results = {}
    for grp, lo, hi in [("청년", 20, 39), ("노년", 65, 200)]:
        with get_conn() as conn:
            sub = pd.read_sql(
                "SELECT loneliness, contact, support_net, income_log, health_bad, female "
                "FROM welfare WHERE age >= ? AND age <= ?;",
                conn, params=(lo, hi),
            )
        for col in ["contact", "support_net", "income_log", "health_bad"]:
            sub[f"{col}_z"] = (sub[col] - sub[col].mean()) / sub[col].std()
        m = smf.ols(
            "loneliness ~ contact_z + support_net_z + income_log_z + health_bad_z + female",
            data=sub,
        ).fit(cov_type="HC3")
        results[grp] = {
            "n": int(m.nobs),
            "coef": {lab: m.params[z] for lab, z in keymap.items()},
            "pval": {lab: m.pvalues[z] for lab, z in keymap.items()},
            "r2": m.rsquared,
        }
    return results


# =====================================================
# RQ4 · RQ5 : 자치구 (SQL JOIN + K-means)
# =====================================================
@st.cache_data
def load_districts():
    """RQ4 — 자치구 분석 마트(district_metrics) 조회. 인구⨝1인가구 JOIN·비율/구성비는
    build_db.py 가 마트 테이블로 미리 적재한다."""
    with get_conn() as conn:
        return pd.read_sql(
            "SELECT district, one_youth, one_middle, one_senior, one_total, pop_total, "
            "rate_youth, rate_middle, rate_senior, rate_total, "
            "share_youth, share_middle, share_senior "
            "FROM district_metrics ORDER BY seq;",
            conn,
        )


# =====================================================
# 핵심 SQL 분석 : 정제된 마트로 '질문에 답하는' 쿼리
# =====================================================
@st.cache_data
def rank_districts(metric="rate_total", n=5, ascending=False):
    """자치구 랭킹 (밀집도·절대수 등). ORDER BY … LIMIT 로 Top/Bottom N 추출."""
    assert metric in {"rate_total", "rate_youth", "rate_middle", "rate_senior",
                       "one_total", "share_youth", "share_senior"}
    order = "ASC" if ascending else "DESC"
    with get_conn() as conn:
        return pd.read_sql(
            f"SELECT district, {metric} FROM district_metrics "
            f"ORDER BY {metric} {order} LIMIT {n};",
            conn,
        )


@st.cache_data
def scale_vs_density():
    """규모 vs 밀집 괴리 — 절대수 1위와 밀집도 1위가 다름을 한 쿼리로 대비.
    각 지표의 순위를 윈도우 함수로 매겨 상위 5개를 나란히 본다."""
    sql = """
        WITH ranked AS (
            SELECT district, one_total, rate_total,
                   RANK() OVER (ORDER BY one_total  DESC) AS rank_scale,
                   RANK() OVER (ORDER BY rate_total DESC) AS rank_density
            FROM district_metrics
        )
        SELECT district, one_total, rank_scale, rate_total, rank_density
        FROM ranked
        WHERE rank_scale <= 5 OR rank_density <= 5
        ORDER BY rank_density;
    """
    with get_conn() as conn:
        return pd.read_sql(sql, conn)


@st.cache_data
def youth_senior_contrast(n=5):
    """청년 밀집 상위 구 vs 노년 밀집 상위 구 — '밀집=청년 동네' 공간 구조 확인."""
    with get_conn() as conn:
        youth = pd.read_sql(
            f"SELECT district, rate_youth FROM district_metrics "
            f"ORDER BY rate_youth DESC LIMIT {n};", conn)
        senior = pd.read_sql(
            f"SELECT district, rate_senior FROM district_metrics "
            f"ORDER BY rate_senior DESC LIMIT {n};", conn)
    return youth, senior


@st.cache_data
def household_depression_gap():
    """가구유형별 우울 격차 (2025) — 1인가구가 타 가구의 몇 배인지 SQL 로 산출.
    측정방식이 이질적인 기타가구는 제외."""
    sql = """
        SELECT household_type, y2025,
               ROUND(y2025 / (SELECT y2025 FROM depression_household
                              WHERE household_type = '부부가구'), 2) AS ratio_vs_couple
        FROM depression_household
        WHERE household_type != '기타가구'
        ORDER BY y2025 DESC;
    """
    with get_conn() as conn:
        return pd.read_sql(sql, conn)


@st.cache_data
def cluster_districts(k=3):
    """RQ5 — K-means 자치구 유형화 (연령 구성비 기반). 입력은 SQL, 군집만 Python."""
    from sklearn.preprocessing import StandardScaler
    from sklearn.cluster import KMeans

    df = load_districts().copy()
    X = df[["share_youth", "share_middle", "share_senior"]].values
    Xs = StandardScaler().fit_transform(X)
    km = KMeans(n_clusters=k, random_state=42, n_init=10).fit(Xs)
    df["cluster"] = km.labels_

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
    """서울 전체 연령대별 1인가구 현황 (2024). 소계 행 기준 SQL JOIN 집계."""
    sql = f"""
        SELECT o.age_band AS age, o.value AS one, p.value AS pop,
               o.value * 100.0 / p.value AS rate
        FROM one_2024 o JOIN pop_2024 p ON o.age_band = p.age_band
        WHERE o.district = '소계' AND p.district = '소계'
          AND o.age_band IN ({_q(AGE13)});
    """
    with get_conn() as conn:
        df = pd.read_sql(sql, conn)
        total_one = pd.read_sql(
            "SELECT value FROM one_2024 WHERE district='소계' AND age_band='소계';", conn
        ).iat[0, 0]
    # AGE13 순서 보장
    df["age"] = pd.Categorical(df["age"], categories=AGE13, ordered=True)
    df = df.sort_values("age").reset_index(drop=True)
    df["age"] = df["age"].astype(str)
    df["share"] = df["one"] / total_one * 100

    group_map = {
        "청년\n(20~39세)":   YOUTH,
        "중장년\n(40~64세)": MIDDLE,
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
    return df, pd.DataFrame(grp_rows), int(total_one)


@st.cache_data
def oneperson_timeseries():
    """연도별(2022~2024) 서울 전체 1인가구 추이 (연령 그룹별 인원·비율). 소계 행 SQL 집계."""
    one_sql = f"""
        SELECT year,
            SUM(CASE WHEN age_band = '소계'              THEN value END) AS total_one,
            SUM(CASE WHEN age_band IN ({_q(YOUTH)})      THEN value END) AS youth_one,
            SUM(CASE WHEN age_band IN ({_q(MIDDLE)})     THEN value END) AS middle_one,
            SUM(CASE WHEN age_band IN ({_q(SENIOR_ONE)}) THEN value END) AS senior_one
        FROM one_ts WHERE district = '소계' GROUP BY year ORDER BY year;
    """
    pop_sql = f"""
        SELECT year,
            SUM(CASE WHEN age_band = '소계'              THEN value END) AS total_pop,
            SUM(CASE WHEN age_band IN ({_q(YOUTH)})      THEN value END) AS youth_pop,
            SUM(CASE WHEN age_band IN ({_q(MIDDLE)})     THEN value END) AS middle_pop,
            SUM(CASE WHEN age_band IN ({_q(SENIOR_POP)}) THEN value END) AS senior_pop
        FROM pop_ts WHERE district = '소계' GROUP BY year ORDER BY year;
    """
    with get_conn() as conn:
        o = pd.read_sql(one_sql, conn)
        p = pd.read_sql(pop_sql, conn)
    m = o.merge(p, on="year")
    return pd.DataFrame({
        "연도":     m["year"].astype(int),
        "총1인가구": m["total_one"].astype(int),
        "청년":      m["youth_one"].astype(int),
        "중장년":    m["middle_one"].astype(int),
        "노년":      m["senior_one"].astype(int),
        "1인가구율": m["total_one"]  / m["total_pop"]  * 100,
        "청년율":    m["youth_one"]  / m["youth_pop"]  * 100,
        "중장년율":  m["middle_one"] / m["middle_pop"] * 100,
        "노년율":    m["senior_one"] / m["senior_pop"] * 100,
    })


def get_centered_df(df):
    return (
        df.style
        .set_properties(**{"text-align": "center"})
        .set_table_styles([
            {"selector": "th", "props": [("text-align", "center"), ("font-weight", "700")]},
            {"selector": "td", "props": [("text-align", "center")]},
        ])
    )
