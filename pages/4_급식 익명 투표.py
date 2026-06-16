import streamlit as st
import google.generativeai as genai

# 페이지 설정 및 효과음 소스
st.set_page_config(page_title="급식 만족도 조사", page_icon="🍱")
SOUND_URL = "https://www.soundjay.com/misc/sounds/bell-ringing-05.mp3"

# 사이드바 Secrets 설정
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except:
    st.error("Secrets에 GEMINI_API_KEY를 설정해주세요.")

st.title("🍱 오늘 급식 어땠나요? (익명)")
st.caption("여러분의 의견은 완전 익명으로 처리되니 안심하고 투표해주세요!")

# 투표 영역
score = st.radio("오늘의 만족도는?", ["😋 정말 맛있어요", "🙂 먹을만해요", "😐 평범해요", "☹️ 아쉬워요"], horizontal=True)
comment = st.text_input("영양사 선생님께 한마디! (선택)")

if st.button("투표 완료! 🚀"):
    st.balloons()
    st.audio(SOUND_URL, format="audio/mp3", autoplay=True)
    st.success("투표가 성공적으로 기록되었습니다!")
    
    if comment:
        model = genai.GenerativeModel('gemini-2.5-flash-lite')
        response = model.generate_content(f"학생의 급식 피드백 '{comment}'을 읽고 영양사님께 힘이 되는 짧은 요약글을 작성해줘.")
        st.info(f"🤖 AI의 한줄평: {response.text}")

st.divider()
st.info("💡 투표 데이터는 데이터베이스 연결 시 실시간 통계로 표시될 수 있습니다.")
