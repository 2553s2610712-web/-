import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="디저트 등록하기", page_icon="✏️")

# Gemini API 설정 및 예외 처리
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("⚠️ Secrets 설정에서 GEMINI_API_KEY를 입력해주세요!")
    st.stop()

# AI 기반 디저트 판별 함수
def check_if_dessert(food_name):
    try:
        model = genai.GenerativeModel("gemini-2.5-flash-lite")
        prompt = (
            f"유저가 입력한 음식 이름: '{food_name}'\n"
            "이 음식을 식사 후 먹는 디저트(후식, 간식, 과자, 아이스크림, 케이크, 빵 등)로 볼 수 있다면 'YES', "
            "디저트가 아니라 일반적인 식사 메뉴(예: 삼겹살, 김치찌개, 라면, 국밥, 떡볶이, 짜장면 등)라면 'NO'라고만 답해줘."
        )
        response = model.generate_content(prompt)
        return "YES" in response.text.strip().upper()
    except Exception:
        return True # 오류 시 안전하게 통과

st.title("🧁 내 최애 디저트 등록하기")
st.write("Gemini AI가 디저트 여부를 판별하여 게시판에 등록해 줍니다!")

with st.form(key="add_form", clear_on_submit=True):
    input_name = st.text_input("디저트 이름", placeholder="예: 망고 빙수")
    input_type = st.selectbox("디저트 종류", ["베이커리", "아이스크림", "과일/젤리", "음료/차", "기타 간식"])
    input_reason = st.text_area("추천하는 이유", placeholder="예: 여름에 먹으면 뼛속까지 시원해요!")
    submit_btn = st.form_submit_button("게시판에 올리기")

if submit_btn:
    if not input_name.strip() or not input_reason.strip():
        st.warning("내용을 모두 입력해주세요!")
    else:
        with st.spinner("AI가 디저트인지 검사 중... 🔍"):
            is_dessert = check_if_dessert(input_name)
        
        if is_dessert:
            # 새로운 데이터를 전역 세션의 맨 앞에 추가
            new_item = {"name": input_name, "type": input_type, "reason": input_reason}
            if "dessert_list" not in st.session_state:
                st.session_state.dessert_list = []
            st.session_state.dessert_list.insert(0, new_item)
            st.success(f"🎉 '{input_name}'이(가) 성공적으로 등록되었습니다! 메인 화면에서 확인하세요.")
        else:
            st.error(f"❌ '{input_name}'은(는) 디저트가 아닌 것 같아요! 식사류가 아닌 달콤한 후식을 적어주세요.")
