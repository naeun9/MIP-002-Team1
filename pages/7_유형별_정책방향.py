"""유형별 정책 방향 — 군집 유형별 맞춤 정책 제언"""
import streamlit as st
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))
from src.page_setup import page_header

TYPE_COLOR = {"청년밀집형": "#6366f1", "세대혼합형": "#64748b", "중장년·노년형": "#f87171"}

CARD_STYLE_A = 'class="rq-card card-a" style="height:170px; overflow-y:auto; box-sizing:border-box;"'
CARD_STYLE_B = 'class="rq-card card-b" style="height:170px; overflow-y:auto; box-sizing:border-box;"'
CARD_STYLE_C = 'class="rq-card card-c" style="height:195px; overflow-y:auto; box-sizing:border-box;"'

page_header(
    "유형별 정책 방향",
    caption="군집 유형 × 회귀 분석 결합 정책 제언",
)

st.markdown(
    "회귀분석(RQ3)에서 도출한 **연령별 외로움 원인**과 K-means 군집(RQ5)의 "
    "**연령별 지역 분포**를 결합하여 각 유형에 최적화된 정책 방향을 제시합니다."
)
st.markdown("---")

# ═══════════════════════════════════════════════════════════
# TYPE A : 청년밀집형
# ═══════════════════════════════════════════════════════════
color_a = TYPE_COLOR["청년밀집형"]
st.markdown(
    f'<div style="border-left:5px solid {color_a}; padding:0.4rem 1rem; margin-bottom:0.6rem;">'
    f'<span style="font-size:1.3rem; font-weight:900; color:{color_a};">TYPE A · 청년밀집형</span>'
    f'</div>',
    unsafe_allow_html=True,
)

with st.expander("인사이트 & 근거", expanded=True):
    st.markdown(
        "**인사이트** : 잦은 대면 접촉(+0.054)이 오히려 외로움을 가중시키는 "
        "**'네트워킹의 역설'** 상태."
    )
    st.markdown(
        "**의견** : 대면 접촉의 양적 증가가 오히려 피로감을 유발하는 '네트워킹의 역설' 구간. "
        "단순한 양적 교류가 아닌 **관계의 질(−0.091)** 을 높이는 전략이 필요하다."
    )

st.markdown("#### 구체적 정책")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        f"""<div {CARD_STYLE_A}>
<div style="font-weight:800; color:{color_a}; font-size:0.88rem; margin-bottom:0.35rem;">
  데이터 맵핑 기반 '목적형' 매칭 플랫폼
</div>
<ul style="font-size:0.82rem; color:#cbd5e1; line-height:1.65; padding-left:1rem; margin:0;">
  <li>불특정 다수와의 가벼운 네트워킹 지양</li>
  <li>특정 직무 스터디·취향·목표가 확실한 소그룹을 정교하게 연결하는 서비스</li>
</ul>
</div>""",
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        f"""<div {CARD_STYLE_A}>
<div style="font-weight:800; color:{color_a}; font-size:0.88rem; margin-bottom:0.35rem;">
  '목적 달성형' 커뮤니티 공간 및 활동비 지원
</div>
<ul style="font-size:0.82rem; color:#cbd5e1; line-height:1.65; padding-left:1rem; margin:0;">
  <li>명확한 기한·목표가 있는 소그룹 활동 지원
    <br><span style="color:#94a3b8; font-size:0.82rem;">예: 4주 완성 스터디, 취향 기반 독서 모임</span>
  </li>
  <li>공통의 목표를 함께 달성할 때 가장 자연스럽게 깊은 유대감 형성</li>
</ul>
</div>""",
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        f"""<div {CARD_STYLE_A}>
<div style="font-weight:800; color:{color_a}; font-size:0.88rem; margin-bottom:0.35rem;">
  지역 기반 '호스트' 육성 정책
</div>
<ul style="font-size:0.82rem; color:#cbd5e1; line-height:1.65; padding-left:1rem; margin:0;">
  <li>공간 대여를 넘어 특정 관심사 중심의 모임을 이끌 청년 호스트를 지자체에서 발굴·활동비 지원</li>
  <li>양질의 커뮤니티가 지역 내 자생적으로 활성화</li>
</ul>
</div>""",
        unsafe_allow_html=True,
    )

st.markdown("---")

# ═══════════════════════════════════════════════════════════
# TYPE B : 세대혼합형
# ═══════════════════════════════════════════════════════════
color_b = TYPE_COLOR["세대혼합형"]
st.markdown(
    f'<div style="border-left:5px solid {color_b}; padding:0.4rem 1rem; margin-bottom:0.6rem;">'
    f'<span style="font-size:1.3rem; font-weight:900; color:{color_b};">TYPE B · 세대혼합형</span>'
    f'</div>',
    unsafe_allow_html=True,
)

with st.expander("인사이트 & 근거", expanded=True):
    st.markdown(
        "**인사이트** : 전 연령대가 혼재되어 있어 단일 연령 타겟 정책으로는 예산 효율이 떨어짐."
    )
    st.markdown(
        "**의견** : 청년(48%)·중장년(30%)·노년(21%)이 고르게 분포. "
        "단일 연령층 타겟 정책보다는 한정된 자원을 다층적으로 활용하는 "
        "**'생애주기별 복합 지원'** 이 요구됨."
    )

st.markdown("#### 구체적 정책")
col1, col2 = st.columns(2)

with col1:
    st.markdown(
        f"""<div {CARD_STYLE_B}>
<div style="font-weight:800; color:{color_b}; font-size:0.88rem; margin-bottom:0.35rem;">
  세대 간 교류형 '로컬 멘토링' 인프라 조성
</div>
<ul style="font-size:0.82rem; color:#cbd5e1; line-height:1.65; padding-left:1rem; margin:0;">
  <li>직무·생활 노하우를 공유할 수 있는 중장년·시니어와 청년 1인가구를 연결하는 멘토-멘티 매칭 프로그램 운영</li>
  <li>세대 통합형 사회적 지지망 확보</li>
</ul>
</div>""",
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        f"""<div {CARD_STYLE_B}>
<div style="font-weight:800; color:{color_b}; font-size:0.88rem; margin-bottom:0.35rem;">
  시간 분할형 세대 교류 거점 공간
</div>
<ul style="font-size:0.82rem; color:#cbd5e1; line-height:1.65; padding-left:1rem; margin:0;">
  <li>역 내 공공시설·커뮤니티 거점을 시간대별로 분할 운영</li>
  <li><span style="color:#94a3b8; font-size:0.82rem;">주간 → 시니어 건강·디지털 교육 거점<br>야간 → 청년층 코워킹·스터디 스페이스</span></li>
</ul>
</div>""",
        unsafe_allow_html=True,
    )

st.markdown("---")

# ═══════════════════════════════════════════════════════════
# TYPE C : 중장년·노년형
# ═══════════════════════════════════════════════════════════
color_c = TYPE_COLOR["중장년·노년형"]
st.markdown(
    f'<div style="border-left:5px solid {color_c}; padding:0.4rem 1rem; margin-bottom:0.6rem;">'
    f'<span style="font-size:1.3rem; font-weight:900; color:{color_c};">TYPE C · 중장년·노년형</span>'
    f'</div>',
    unsafe_allow_html=True,
)

with st.expander("인사이트 & 근거", expanded=True):
    st.markdown(
        "**인사이트** : 접촉 빈도(−0.044) 확보가 중요하나, "
        "낮은 소득(−0.049)과 건강 악화(+0.046)로 인해 자발적 외출이 불가능한 **'물리적 고립'** 상태."
    )
    st.markdown(
        "**의견** : 대면 만남(양) 자체가 고립을 막는 가장 강력한 방어기제. "
        "거동 불편 및 건강 악화로 인한 **'물리적 단절'** 을 최우선으로 해소해야 함."
    )

st.markdown("#### 구체적 정책")
col1, col2 = st.columns(2)

with col1:
    st.markdown(
        f"""<div {CARD_STYLE_C}>
<div style="font-weight:800; color:{color_c}; font-size:0.88rem; margin-bottom:0.35rem;">
  생활 밀착형 '마이크로 컨택(Micro-contact)' 스팟 조성
</div>
<ul style="font-size:0.82rem; color:#cbd5e1; line-height:1.65; padding-left:1rem; margin:0;">
  <li>복지관처럼 특정 장소로 찾아오게 만드는 '수동적 복지' 방식 탈피</li>
  <li>노년층의 실제 생활 반경
    <span style="color:#94a3b8; font-size:0.82rem;">(단지 내 산책로, 동네 약국, 슈퍼마켓 앞 등)</span>에
    자연스러운 대면 교류가 가능한 소규모 쉼터(스마트 벤치 등) 거점화
  </li>
</ul>
</div>""",
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        f"""<div {CARD_STYLE_C}>
<div style="font-weight:800; color:{color_c}; font-size:0.88rem; margin-bottom:0.35rem;">
  데이터 기반 '사회적 활력도' 모니터링 및 찾아가는 복지
</div>
<ul style="font-size:0.82rem; color:#cbd5e1; line-height:1.65; padding-left:1rem; margin:0;">
  <li>대중교통 주말 승하차량·공공시설 이용률 등 익명화된 거시적 지역 데이터를 활력도 지표화</li>
  <li>향후 공공 데이터(교통·시설 등) 연계를 통한 분석 확장성 확보 기대</li>
  <li>사회적 활력이 급감하는 구역에 방문 간호·이동 지원 서비스를 선제적으로 집중 배치</li>
</ul>
</div>""",
        unsafe_allow_html=True,
    )

st.markdown("---")

st.markdown("""
<div class="insight-box">
<b>종합</b> : 회귀(RQ3)에서 밝힌 <b>연령별 외로움 원인 차이</b>를 군집(RQ5)의 <b>연령별 지역 분포</b>와 결합하면
각 유형마다 전혀 다른 개입 전략이 도출됩니다.
<br>• <b>청년밀집형(A)</b> → 양이 아닌 <b>관계의 질</b> 중심 목적형 커뮤니티 설계
<br>• <b>세대혼합형(B)</b> → 한정 자원의 <b>생애주기별 복합 활용</b>, 세대 간 연결 인프라
<br>• <b>중장년·노년형(C)</b> → <b>물리적 고립 해소</b>가 최우선, 찾아가는 접촉·데이터 기반 선제 대응
</div>
""", unsafe_allow_html=True)
