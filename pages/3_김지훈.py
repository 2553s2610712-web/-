import streamlit as st

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="최애 디저트 종합 게시판", 
    page_icon="🍰", 
    layout="centered"
)

# 2. 전역 데이터(세션 상태) 초기화 (모든 조원 페이지가 이 데이터를 공유하고 실시간 반영함)
if "dessert_list" not in st.session_state:
    st.session_state.dessert_list = [
        {"name": "딸기 탕후루", "type": "과일/젤리", "reason": "바삭하고 달콤해서 급식 먹고 매일 생각나요! 🍓"},
        {"name": "초코 마카롱", "type": "베이커리", "reason": "시험 기간에 하나 먹으면 스트레스 다 날아감 🍫"},
        {"name": "민트초코 아이스크림", "type": "아이스크림", "reason": "치약 맛 아니에요! 시원하고 깔끔한 최고의 후식 🍦"}
    ]

# 데이터 편리하게 쓰기 위해 변수 지정
desserts = st.session_state.dessert_list

# 3. 상단 메인 타이틀
st.title("🍰 당충전소: 우리 학교 최애 디저트 대시보드")
st.markdown("조원들이 등록한 데이터와 통계가 **실시간으로 종합**되어 표시되는 메인 화면입니다.")
st.write("---")


# 4. 실시간 종합 통계 섹션 (상단에 배치하여 시인성 확보)
st.subheader("📊 실시간 종합 현황 현황")

if not desserts:
    st.info("아직 등록된 디저트 데이터가 없습니다. 왼쪽 사이드바 메뉴를 통해 등록해 주세요!")
else:
    # 상단 요약 미니 카드 (총 개수 및 가장 인기 있는 카테고리 계산)
    type_counts = {}
    for item in desserts:
        t = item["type"]
        type_counts[t] = type_counts.get(t, 0) + 1
    
    # 가장 많이 등록된 카테고리 찾기
    most_popular_type = max(type_counts, key=type_counts.get)
    
    # 2열 구조로 요약 수치 보여주기
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="🎈 누적 추천 디저트 수", value=f"{len(desserts)} 개")
    with col2:
        st.metric(label="👑 가장 인기 있는 종류", value=f"{most_popular_type} ({type_counts[most_popular_type]}개)")

    # 카테고리별 실시간 지분율 (프로그래스 바로 깔끔하게 시각화)
    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
    with st.expander("🔍 디저트 종류별 실시간 지분 상세 보기", expanded=True):
        all_types = ["베이커리", "아이스크림", "과일/젤리", "음료/차", "기타 간식"]
        for t_name in all_types:
            count = type_counts.get(t_name, 0)
            percentage = (count / len(desserts)) * 100
            
            # 텍스트 정렬용 2열 배치
            t_col1, t_col2 = st.columns([3, 1])
            t_col1.caption(f"**{t_name}**")
            t_col2.caption(f"{count}개 ({int(percentage)}%)")
            st.progress(int(percentage))

st.write("---")


# 5. 실시간 게시판 목록 섹션 (하단에 배치)
st.subheader("📢 학생들이 추천한 최애 디저트 (최신순)")

if not desserts:
    st.info("현재 게시판에 보여줄 내용이 없습니다.")
else:
    for item in desserts:
        st.markdown(
            f"""
            <div style="background-color: #f9f9f9; padding: 15px; border-radius: 10px; margin-bottom: 12px; border-left: 5px solid #ff4b4b; box-shadow: 1px 1px 5px rgba(0,0,0,0.05);">
                <span style="background-color: #ffe3e3; color: #ff4b4b; padding: 3px 8px; border-radius: 5px; font-size: 11px; font-weight: bold;">{item['type']}</span>
                <h4 style="margin: 5px 0 0 0; color: #ff4b4b;">✨ {item['name']}</h4>
                <p style="margin: 6px 0 0 0; color: #333333; font-size: 15px;">"{item['reason']}"</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
