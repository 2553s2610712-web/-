import streamlit as st

# 페이지 기본 설정
st.set_page_config(page_title="최애 디저트 게시판", page_icon="🍰", layout="centered")

# 전역 데이터(세션 상태) 초기화 (모든 조원 페이지가 공유함)
if "dessert_list" not in st.session_state:
    st.session_state.dessert_list = [
        {"name": "딸기 탕후루", "type": "과일/젤리", "reason": "바삭하고 달콤해서 급식 먹고 매일 생각나요! 🍓"},
        {"name": "초코 마카롱", "type": "베이커리", "reason": "시험 기간에 하나 먹으면 스트레스 다 날아감 🍫"},
        {"name": "민트초코 아이스크림", "type": "아이스크림", "reason": "치약 맛 아니에요! 시원하고 깔끔한 최고의 후식 🍦"}
    ]

# 메인 타이틀 및 소개
st.title("🍰 당충전소: 학생들의 최애 디저트 게시판")
st.markdown("### 우리 학교 학생들이 가장 좋아하는 디저트를 한눈에 확인해보세요!")
st.write("왼쪽 사이드바의 메뉴를 이용해 새로운 디저트를 등록하거나 미니게임을 즐길 수 있습니다.")
st.write("---")

# 등록된 디저트 목록 출력 (최신순)
st.subheader("📢 학생들이 추천한 디저트 목록")

if not st.session_state.dessert_list:
    st.info("아직 등록된 디저트가 없습니다. 2번 페이지에서 첫 번째 디저트를 등록해보세요!")
else:
    for item in st.session_state.dessert_list:
        st.markdown(
            f"""
            <div style="background-color: #f9f9f9; padding: 15px; border-radius: 10px; margin-bottom: 12px; border-left: 5px solid #ff4b4b;">
                <span style="background-color: #ffe3e3; color: #ff4b4b; padding: 3px 8px; border-radius: 5px; font-size: 12px; font-weight: bold;">{item['type']}</span>
                <h4 style="margin: 5px 0 0 0; color: #ff4b4b;">✨ {item['name']}</h4>
                <p style="margin: 6px 0 0 0; color: #333333; font-size: 15px;">"{item['reason']}"</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
