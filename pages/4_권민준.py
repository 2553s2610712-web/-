import streamlit as st
import pandas as pd

st.set_page_config(page_title="급식 만족도 조사")
st.title("🍱 오늘 급식 어땠나요? (익명)")

score = st.select_slider("만족도를 선택하세요", options=["😋", "🙂", "😐", "☹️"])
comment = st.text_area("건의사항 (완전 익명)")

if st.button("투표 제출"):
    st.success("익명 투표가 완료되었습니다!")
    st.balloons()
