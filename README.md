# 서울 1인가구와 외로움 분석 대시보드

서울 시민의 **사회관계망 변화**와 **1인가구의 우울 취약성**을 진단하고,
외로움 영향 요인이 **연령대별로 어떻게 다른지** 분석하여,
자치구별 **연령 구성에 따른 정책 자원 배치 방향**을 제안합니다.

## 연구 질문

| RQ | 질문 | 분석 |
|----|------|------|
| RQ1 | 서울 시민의 사회관계망은 어떻게 변해왔는가? | KGSS 시계열 |
| RQ2 | 1인가구는 정말 다른 가구보다 우울한가? | 행정통계 + 외로움 회귀 |
| RQ3 | 어떤 연령층·지역에 1인가구가 분포하는가? | 자치구 SQL JOIN + Folium |
| RQ4 | 어느 지역에 자원을 우선 배치할까? | K-means 유형화 |

## 실행 방법

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 데이터 출처

- **KGSS 한국종합사회조사** (누적 2003~2025) — DOI: 10.22687/KOSSDA-A1-CUM-0074-V1

  url: https://kossda.snu.ac.kr/handle/20.500.12236/35255#files
- **서울시 가구유형별 우울감** (2022·2024·2025) : https://data.seoul.go.kr/dataList/DT201022F007017/S/2/datasetView.do
- **서울시 자치구별 우울 경험률** (2014~2023) : https://data.seoul.go.kr/dataList/DT201004E0400121/S/2/datasetView.do
- **서울복지실태조사** (2024, 가구원): https://data.si.re.kr/node/65462/
- **서울시 자치구별 인구** (2024) : https://data.seoul.go.kr/dataList/10837/S/2/datasetView.do
- **서울시 자치구별 1인가구** (2024) : https://data.seoul.go.kr/dataList/10995/S/2/datasetView.do
- 자치구 경계: [southkorea/seoul-maps](https://github.com/southkorea/seoul-maps)

모든 분석은 원본 데이터를 앱에서 직접 계산하여 재현 가능합니다.

## 폴더 구조

```
├── app.py                  # 메인 (RQ 네비게이션)
├── pages/                  # RQ별 분석 페이지
├── src/loaders.py          # 데이터 로딩·계산 (캐싱)
├── data/                   # 원본 데이터
└── assets/style.css        # 스타일
```
