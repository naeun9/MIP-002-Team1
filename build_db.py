"""
build_db.py — 원본 데이터(data/) → SQLite 데이터베이스(seoul.db) 구축 ETL

[역할]
  엑셀/parquet 원본을 읽어 '정제'한 뒤, 분석하기 좋은 형태의 테이블로
  seoul.db 에 적재한다. 엑셀 특유의 다단(多段) 헤더 파싱만 Python으로 처리하고,
  이후의 모든 집계·결합·랭킹은 src/loaders.py 에서 SQL 로 수행한다.

[실행]
  python build_db.py
  → data/seoul.db 생성 (DB Browser for SQLite 로 열어 테이블 확인 가능)

[생성 테이블]
  kgss_seoul          서울 KGSS 응답 원자료 (관계망·외로움 문항)
  pop_2024            자치구 × 연령대 인구 (2024, long)
  one_2024            자치구 × 연령대 1인가구 (2024, long)
  pop_ts              연도 × 자치구 × 연령대 인구 (2022~2024, long)
  one_ts              연도 × 자치구 × 연령대 1인가구 (2022~2024, long)
  depression_trend    서울 전체 우울 경험률 추세 (2014~2023)
  depression_household 가구유형별 우울 (2022·2024·2025)
  welfare             서울복지실태조사 회귀 입력 변수 (개인 단위, 정제 완료)
"""
import sqlite3
from pathlib import Path
import pandas as pd
import numpy as np

DATA = Path(__file__).parent / "data"
DB_PATH = DATA / "seoul.db"

# KGSS 결측 코드
MISSING = [-8, -1, 8, 9, 88, 99, -9]

# 연령대 그룹 정의 (마트 테이블 생성 SQL 에 주입)
YOUTH  = ["20~24세", "25~29세", "30~34세", "35~39세"]
MIDDLE = ["40~44세", "45~49세", "50~54세", "55~59세", "60~64세"]
SENIOR_ONE = ["65~69세", "70~74세", "75~79세", "80~84세", "85세이상"]
SENIOR_POP = ["65~69세", "70~74세", "75~79세", "80~84세",
              "85~89세", "90~94세", "95세 이상+"]


def _q(s):
    return ",".join(f"'{x}'" for x in s)


# ─────────────────────────────────────────────────────────
# 공통 정제 헬퍼 : 자치구 × 연령대 엑셀 → long DataFrame
# ─────────────────────────────────────────────────────────
def _melt_single(path: Path, n_age_cols: int) -> pd.DataFrame:
    """단일 연도 자치구×연령 엑셀 → (seq, district, age_band, value) long"""
    raw = pd.read_excel(path, sheet_name="데이터", header=None)
    age_labels = raw.iloc[2, 3:3 + n_age_cols].tolist()
    body = raw.iloc[3:].reset_index(drop=True)
    body.columns = ["gu1", "gu", "sex"] + age_labels
    body["gu1"] = body["gu1"].ffill()
    body["gu"] = body["gu"].ffill()
    body = body[body["sex"] == "계"].copy()
    body = body.reset_index(drop=True)
    body["seq"] = range(len(body))            # 원본 등장 순서 보존
    long = body.melt(
        id_vars=["seq", "gu"], value_vars=age_labels,
        var_name="age_band", value_name="value",
    ).rename(columns={"gu": "district"})
    long["value"] = pd.to_numeric(long["value"], errors="coerce")
    return long[["seq", "district", "age_band", "value"]]


def _melt_ts(path: Path, n_age_cols: int) -> pd.DataFrame:
    """3개 연도 블록 자치구×연령 엑셀 → (year, seq, district, age_band, value) long"""
    raw = pd.read_excel(path, sheet_name="데이터", header=None)
    frames = []
    for yi, yr in enumerate([2022, 2023, 2024]):
        start = 3 + yi * n_age_cols
        labels = raw.iloc[2, start:start + n_age_cols].tolist()
        gu = raw.iloc[3:, 1].ffill().reset_index(drop=True)
        sx = raw.iloc[3:, 2].reset_index(drop=True)
        block = raw.iloc[3:, start:start + n_age_cols].reset_index(drop=True)
        block.columns = labels
        block["district"] = gu
        block["sex"] = sx
        block = block[block["sex"] == "계"].reset_index(drop=True)
        block["seq"] = range(len(block))
        block["year"] = yr
        long = block.melt(
            id_vars=["year", "seq", "district"], value_vars=labels,
            var_name="age_band", value_name="value",
        )
        frames.append(long)
    out = pd.concat(frames, ignore_index=True)
    out["value"] = pd.to_numeric(out["value"], errors="coerce")
    return out[["year", "seq", "district", "age_band", "value"]]


# ─────────────────────────────────────────────────────────
# 1. KGSS (서울 응답 원자료)
# ─────────────────────────────────────────────────────────
def build_kgss() -> pd.DataFrame:
    df = pd.read_parquet(DATA / "kgss.parquet")
    df = df[df["REGION"] == 1].copy()
    cols = ["YEAR", "CONTACTB", "NGHGRT", "NGHASK",
            "LONE4WKS", "ISOL4WKS", "LEFT4WKS"]
    out = df[cols].copy()
    for c in cols:
        out[c] = pd.to_numeric(out[c], errors="coerce")
    # 결측 코드 → NULL (이후 분석 SQL 이 결측을 신경 쓰지 않도록 ETL 단계에서 정리)
    for c in ["CONTACTB", "NGHGRT", "NGHASK", "LONE4WKS", "ISOL4WKS", "LEFT4WKS"]:
        out.loc[out[c].isin(MISSING), c] = np.nan
    return out


# ─────────────────────────────────────────────────────────
# 2. 우울 경험률 추세 (2014~2023)
# ─────────────────────────────────────────────────────────
def build_depression_trend() -> pd.DataFrame:
    raw = pd.read_excel(
        DATA / "서울시 자치구별 우울감 경험률(2014-2023).xlsx",
        sheet_name="데이터", header=None,
    )
    year_col = {y: c for y, c in zip(range(2014, 2024),
                                     [2, 5, 8, 11, 14, 17, 20, 23, 26, 29])}
    vals = raw.iloc[2, list(year_col.values())].apply(pd.to_numeric, errors="coerce")
    return pd.DataFrame({"year": list(year_col.keys()), "rate": vals.values})


# ─────────────────────────────────────────────────────────
# 3. 가구유형별 우울 (2022·2024·2025)
# ─────────────────────────────────────────────────────────
def build_depression_household() -> pd.DataFrame:
    raw = pd.read_excel(
        DATA / "서울시 가구 유형별 우울감 정도(2022, 2024, 2025).xlsx",
        header=None,
    )
    rows = [14, 15, 16, 17]
    labels = ["1인가구", "부부가구", "2세대이상가구", "기타가구"]
    c2022, c2024, c2025 = 3, 7, 11
    return pd.DataFrame({
        "household_type": labels,
        "y2022": [float(raw.iat[r, c2022]) for r in rows],
        "y2024": [float(raw.iat[r, c2024]) for r in rows],
        "y2025": [float(raw.iat[r, c2025]) for r in rows],
    })


# ─────────────────────────────────────────────────────────
# 4. 서울복지실태조사 회귀 입력 변수 (개인 단위, 정제 완료)
#    엑셀 문항(E1·E2·E3·B7·C1·A1) → 분석 변수로 정제. 표준화·회귀는 loaders 가 담당.
# ─────────────────────────────────────────────────────────
def build_welfare() -> pd.DataFrame:
    raw = pd.read_excel(
        DATA / "DATA_서울시민의 생활실태 및 복지욕구 조사_가구원 데이터_SI공개용.xlsx"
    )
    d = pd.DataFrame()

    # 종속: 외로움 (E3, 1~4) — 역/정 문항 분리 후 역코딩
    e3_rev = ["E3_1", "E3_5", "E3_6", "E3_9", "E3_10",
              "E3_15", "E3_16", "E3_19", "E3_20"]
    e3_fwd = ["E3_2", "E3_3", "E3_4", "E3_7", "E3_8",
              "E3_11", "E3_12", "E3_13", "E3_14", "E3_18"]
    lone = raw[e3_fwd + e3_rev].apply(pd.to_numeric, errors="coerce")
    lone = lone.where((lone >= 1) & (lone <= 4))
    for c in e3_rev:
        lone[c] = 5 - lone[c]
    d["loneliness"] = lone.mean(axis=1)

    # 독립1: 접촉 빈도 (E1, 역코딩 → 클수록 자주 만남)
    e1 = raw[["E1_101", "E1_102", "E1_103", "E1_104"]].apply(pd.to_numeric, errors="coerce")
    e1 = e1.where((e1 >= 1) & (e1 <= 5))
    d["contact"] = (6 - e1).mean(axis=1)

    # 독립2: 사회적 지지망 (E2, '있다(=1)' 개수)
    e2 = raw[["E2_1", "E2_2", "E2_3", "E2_4", "E2_5"]].apply(pd.to_numeric, errors="coerce")
    d["support_net"] = (e2 == 1).sum(axis=1)

    # 통제1: 소득 (B7 합산 → log1p)
    b7 = raw[["B7_1", "B7_2", "B7_3", "B7_4", "B7_5", "B7_6"]].apply(pd.to_numeric, errors="coerce")
    income = b7.fillna(0).sum(axis=1)
    d["income_log"] = np.log1p(income.where(income >= 0))

    # 통제2: 건강 악화 (C1_1, 1~5, 클수록 나쁨)
    health = pd.to_numeric(raw["C1_1"], errors="coerce")
    d["health_bad"] = health.where((health >= 1) & (health <= 5))

    d["female"] = (pd.to_numeric(raw["A1_4"], errors="coerce") == 2).astype(int)
    d["age"] = 2024 - pd.to_numeric(raw["A1_5_1"], errors="coerce")

    d = d.dropna(subset=["loneliness", "contact", "support_net",
                         "income_log", "health_bad", "age"])
    d = d[d["age"] >= 19].reset_index(drop=True)
    return d


# ─────────────────────────────────────────────────────────
# 메인 : 모든 테이블 적재
# ─────────────────────────────────────────────────────────
def main():
    if DB_PATH.exists():
        DB_PATH.unlink()
    conn = sqlite3.connect(DB_PATH)

    tables = {
        "kgss_seoul":           build_kgss(),
        "pop_2024":             _melt_single(DATA / "서울시 자치구별 인구(연령대별) 2024.xlsx", 21),
        "one_2024":             _melt_single(DATA / "1인가구 수(연령대별)(2024).xlsx", 16),
        "pop_ts":               _melt_ts(DATA / "서울시 자치구별 인구(연령대별)(2022-2024).xlsx", 21),
        "one_ts":               _melt_ts(DATA / "1인가구 수(연령대별)(2022-2024).xlsx", 16),
        "depression_trend":     build_depression_trend(),
        "depression_household": build_depression_household(),
        "welfare":              build_welfare(),
    }
    for name, df in tables.items():
        df.to_sql(name, conn, if_exists="replace", index=False)
        print(f"  ✔ {name:22s} {len(df):>7,} rows  ({len(df.columns)} cols)")

    # 인덱스 (JOIN·필터 가속)
    cur = conn.cursor()
    cur.execute("CREATE INDEX idx_pop24  ON pop_2024(district, age_band);")
    cur.execute("CREATE INDEX idx_one24  ON one_2024(district, age_band);")
    cur.execute("CREATE INDEX idx_popts  ON pop_ts(year, district, age_band);")
    cur.execute("CREATE INDEX idx_onets  ON one_ts(year, district, age_band);")
    cur.execute("CREATE INDEX idx_kgss   ON kgss_seoul(YEAR);")
    conn.commit()

    # ── 자치구 분석 마트 (정제 → 마트) ──────────────────────
    # 인구 ⨝ 1인가구 JOIN 결과를 테이블로 저장. 이후 모든 자치구 분석 쿼리(랭킹·비교)는
    # 이 마트 위에서 수행한다.
    conn.executescript(f"""
    DROP TABLE IF EXISTS district_metrics;
    CREATE TABLE district_metrics AS
    WITH one_g AS (
        SELECT district, MIN(seq) AS seq,
            SUM(CASE WHEN age_band IN ({_q(YOUTH)})      THEN value END) AS one_youth,
            SUM(CASE WHEN age_band IN ({_q(MIDDLE)})     THEN value END) AS one_middle,
            SUM(CASE WHEN age_band IN ({_q(SENIOR_ONE)}) THEN value END) AS one_senior,
            SUM(CASE WHEN age_band = '소계'              THEN value END) AS one_total
        FROM one_2024 WHERE district != '소계' GROUP BY district
    ),
    pop_g AS (
        SELECT district,
            SUM(CASE WHEN age_band IN ({_q(YOUTH)})      THEN value END) AS pop_youth,
            SUM(CASE WHEN age_band IN ({_q(MIDDLE)})     THEN value END) AS pop_middle,
            SUM(CASE WHEN age_band IN ({_q(SENIOR_POP)}) THEN value END) AS pop_senior,
            SUM(CASE WHEN age_band = '소계'              THEN value END) AS pop_total
        FROM pop_2024 WHERE district != '소계' GROUP BY district
    )
    SELECT o.district, o.seq, o.one_youth, o.one_middle, o.one_senior, o.one_total,
           p.pop_total,
           ROUND(o.one_youth  * 100.0 / p.pop_youth,  2) AS rate_youth,
           ROUND(o.one_middle * 100.0 / p.pop_middle, 2) AS rate_middle,
           ROUND(o.one_senior * 100.0 / p.pop_senior, 2) AS rate_senior,
           ROUND(o.one_total  * 100.0 / p.pop_total,  2) AS rate_total,
           ROUND(o.one_youth  * 100.0 / o.one_total,  2) AS share_youth,
           ROUND(o.one_middle * 100.0 / o.one_total,  2) AS share_middle,
           ROUND(o.one_senior * 100.0 / o.one_total,  2) AS share_senior
    FROM one_g o JOIN pop_g p ON o.district = p.district;
    """)
    conn.commit()
    print(f"  ✔ {'district_metrics':22s} {'25':>7} rows  (분석 마트)")

    conn.close()
    print(f"\n[완료] {DB_PATH}  ({DB_PATH.stat().st_size/1024:.0f} KB)")


if __name__ == "__main__":
    print("seoul.db 구축 시작...")
    main()
