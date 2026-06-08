# 서울 1인가구와 외로움 분석 대시보드

서울 시민의 **사회관계망 변화**와 **1인가구의 우울 취약성**을 진단하고,
외로움 영향 요인이 **연령대별로 어떻게 다른지** 분석하여,
자치구별 **연령 구성에 따른 정책 자원 배치 방향**을 제안합니다.

## 연구 질문

| 페이지 | 질문 | 분석 방법 |
|--------|------|-----------|
| RQ1 | 서울 시민의 사회관계망은 어떻게 변해왔는가? | KGSS 시계열 + 1인가구 연령대별 현황 |
| RQ2 | 1인가구는 정말 다른 가구보다 우울한가? | 행정통계 + 외로움 현황 |
| RQ3 | 1인가구의 우울 취약성은 어느 정도인가? | 가구유형별 우울 비교 |
| RQ3-1 | 외로움 영향 요인이 연령대별로 다른가? | OLS 회귀분석 (청년/노년) |
| RQ4 | 어느 자치구에 1인가구가 집중되는가? | 자치구 SQL JOIN + Folium 지도 |
| RQ5 | 연령 구성에 따라 자치구를 어떻게 유형화할까? | K-means 군집화 |
| 정책 | 유형별로 어떤 정책이 필요한가? | 회귀 × 군집 결합 정책 제언 |

## 실행 방법

```bash
pip install -r requirements.txt
streamlit run HOME.py
```

## 데이터 출처

- **KGSS 한국종합사회조사** (누적 2003~2025) — DOI: 10.22687/KOSSDA-A1-CUM-0074-V1

  url: https://kossda.snu.ac.kr/handle/20.500.12236/35255#files
- **서울시 가구유형별 우울감** (2022·2024·2025) : https://data.seoul.go.kr/dataList/DT201022F007017/S/2/datasetView.do
- **서울시 자치구별 우울 경험률** (2014~2023) : https://data.seoul.go.kr/dataList/DT201004E0400121/S/2/datasetView.do
- **서울복지실태조사** (2024, 가구원): https://data.si.re.kr/node/65462/
- **서울시 자치구별 인구·1인가구** (2022·2023·2024) : https://data.seoul.go.kr/dataList/10837/S/2/datasetView.do
- **서울시 자치구별 1인가구** (2022·2023·2024) : https://data.seoul.go.kr/dataList/10995/S/2/datasetView.do
- 자치구 경계: [southkorea/seoul-maps](https://github.com/southkorea/seoul-maps)

모든 분석은 원본 데이터를 앱에서 직접 계산하여 재현 가능합니다.

## 폴더 구조

```
├── HOME.py                 # 메인 진입점 (RQ 네비게이션)
├── pages/                  # 분석 페이지 (1~7)
├── src/loaders.py          # 데이터 로딩·계산 (캐싱)
├── data/                   # 원본 데이터 (xlsx, parquet, geojson)
└── assets/style.css        # 스타일
```
