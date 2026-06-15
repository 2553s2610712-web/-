import streamlit as st
import random

st.set_page_config(page_title="디저트 월드컵", page_icon="🎲")

st.title("🎲 오늘의 디저트 추천 배틀!")
st.write("게시판에 등록된 디저트 중 2개를 무작위로 뽑아 대결을 붙여드립니다. 마음에 드는 것을 골라보세요!")
st.write("---")

# 데이터 가져오기
desserts = st.session_state.get("dessert_list", [])

if len(desserts) < 2:
    st.info("비교할 디저트 데이터가 부족합니다. 최소 2개 이상의 디저트가 등록되어야 게임을 시작할 수 있습니다!")
else:
    # 매번 새로운 대결을 위해 세션에 대결 후보 저장
    if "matchup" not in st.session_state or st.button("🔄 새로운 대결 섞기"):
        st.session_state.matchup = random.sample(desserts, 2)
    
    candidate1 = st.session_state.matchup[0]
    candidate2 = st.session_state.matchup[1]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"### 🅰️ {candidate1['name']}")
        st.caption(f"분류: {candidate1['type']}")
        st.info(f"\"{candidate1['reason']}\"")
        if st.button(f"👍 {candidate1['name']} 선택", key="btn1"):
            st.balloons()
            st.success(f"🏅 오늘의 디저트는 **{candidate1['name']}**(으)로 결정!")
            
    with col2:
        st.markdown(f"### 🅱️ {candidate2['name']}")
        st.caption(f"분류: {candidate2['type']}")
        st.info(f"\"{candidate2['reason']}\"")
        if st.button(f"👍 {candidate2['name']} 선택", key="btn2"):
            st.balloons()
            st.success(f"🏅 오늘의 디저트는 **{candidate2['name']}**(으)로 결정!")
