# 서울 1인가구와 외로움 분석 대시보드

서울 시민의 **사회관계망 변화**와 **1인가구의 우울 취약성**을 진단하고,
외로움 영향 요인이 **연령대별로 어떻게 다른지** 분석하여,
자치구별 **연령 구성에 따른 정책 자원 배치 방향**을 제안합니다.

## 연구 질문

| 페이지 | 질문 | 분석 방법 |
|--------|------|-----------|
| RQ1 | 서울 시민의 사회관계망은 어떻게 변해왔는가? | KGSS 시계열 + 1인가구 연령대별 현황 |
| RQ2 | 서울 시민의 외로움과 우울은 어떤 양상을 보이는가? | 행정통계 + 외로움 현황 |
| RQ3 | 1인가구는 다른 가구보다 우울에 더 취약한가? | 가구유형별 우울 비교 |
| RQ3-1 | 외로움 영향 요인이 연령대별로 다른가? | OLS 회귀분석 (청년/노년) |
| RQ4 | 어느 자치구에 1인가구가 집중되는가? | 자치구 SQL JOIN + Folium 지도 |
| RQ5 | 연령 구성에 따라 자치구를 어떻게 유형화할까? | K-means 군집화 |
| 정책 | 유형별로 어떤 정책이 필요한가? | 회귀 × 군집 결합 정책 제언 |

## 데이터 처리 구조 (ETL → DB → 분석)

```
원본 데이터(data/*.xlsx, *.parquet)
        │  build_db.py  ── 엑셀 다단 헤더 정제 + long 변환
        ▼
   seoul.db (SQLite)   ── kgss_seoul / pop·one_2024 / pop·one_ts /
        │                  depression_trend / depression_household / welfare
        │  src/loaders.py ── SQL 집계·JOIN·랭킹·구간 매핑
        ▼
   Streamlit 대시보드 (HOME.py + pages/)
```

- **정제(ETL)** : `build_db.py` 가 원본을 읽어 분석용 테이블 8종으로 `seoul.db` 에 적재
- **분석** : 연령대 그룹핑·비율/구성비 산출·자치구 인구⨝1인가구 JOIN·KGSS 구간 중간값 매핑을 모두 **SQL** 로 수행
- **모델** : OLS 회귀·K-means 만 입력을 SQL 로 추출한 뒤 Python(statsmodels/scikit-learn)으로 적합

## 실행 방법

```bash
pip install -r requirements.txt

# 1) 데이터베이스 구축 (data/seoul.db 생성)
python build_db.py

# 2) 대시보드 실행
streamlit run HOME.py
```

> `seoul.db` 가 없으면 앱 첫 실행 시 자동으로 `build_db.main()` 이 호출되어 생성됩니다.
> 빌드된 `seoul.db` 는 DB Browser for SQLite 로 열어 테이블·스키마를 직접 확인할 수 있습니다.

## 데이터베이스 테이블

| 테이블 | 내용 | 형식 |
|--------|------|------|
| `kgss_seoul` | 서울 KGSS 응답 (관계망·외로움 문항) | 응답 단위 |
| `pop_2024` / `one_2024` | 자치구 × 연령대 인구 / 1인가구 (2024) | long |
| `pop_ts` / `one_ts` | 연도 × 자치구 × 연령대 (2022~2024) | long |
| `depression_trend` | 서울 우울 경험률 추세 (2014~2023) | 연도별 |
| `depression_household` | 가구유형별 우울 (2022·2024·2025) | 유형별 |
| `welfare` | 복지실태조사 회귀 입력 변수 (정제 완료) | 개인 단위 |

## 데이터 출처

- **KGSS 한국종합사회조사** (누적 2003~2025) — DOI: 10.22687/KOSSDA-A1-CUM-0074-V1

  url: https://kossda.snu.ac.kr/handle/20.500.12236/35255#files
- **서울시 가구유형별 우울감** (2022·2024·2025) : https://data.seoul.go.kr/dataList/DT201022F007017/S/2/datasetView.do
- **서울시 자치구별 우울 경험률** (2014~2023) : https://data.seoul.go.kr/dataList/DT201004E0400121/S/2/datasetView.do
- **서울복지실태조사** (2024, 가구원): https://data.si.re.kr/node/65462/
- **서울시 자치구별 인구·1인가구** (2022·2023·2024) : https://data.seoul.go.kr/dataList/10837/S/2/datasetView.do
- **서울시 자치구별 1인가구** (2022·2023·2024) : https://data.seoul.go.kr/dataList/10995/S/2/datasetView.do
- 자치구 경계: [southkorea/seoul-maps](https://github.com/southkorea/seoul-maps)

모든 분석은 원본 데이터를 정제해 SQLite DB로 적재한 뒤 SQL로 계산하여 재현 가능합니다.

## 폴더 구조

```
├── build_db.py             # ETL: 원본 → seoul.db 구축
├── HOME.py                 # 메인 진입점 (RQ 네비게이션)
├── pages/                  # 분석 페이지 (1~7)
├── src/loaders.py          # SQL 기반 데이터 로딩·분석 (캐싱)
├── data/                   # 원본(xlsx·parquet·geojson) + seoul.db
└── assets/style.css        # 스타일
```
