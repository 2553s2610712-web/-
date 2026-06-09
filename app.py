import streamlit as st
import google.generativeai as genai

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="최애 디저트 게시판",
    page_icon="🍰",
    layout="centered"
)

# 2. Gemini API 설정 및 예외 처리
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
else:
    st.error("⚠️ Secrets 설정에서 GEMINI_API_KEY를 입력해주세요!")
    st.stop()

# 3. 세션 상태(데이터 저장소) 초기화
if "dessert_list" not in st.session_state:
    st.session_state.dessert_list = [
        {"name": "딸기 탕후루", "reason": "바삭하고 달콤해서 급식 먹고 매일 생각나요! 🍓"},
        {"name": "초코 마카롱", "reason": "시험 기간에 하나 먹으면 스트레스 다 날아감 🍫"}
    ]

# 4. AI 기반 디저트 판별 함수
def check_if_dessert(food_name):
    try:
        model = genai.GenerativeModel("gemini-2.5-flash-lite")
        prompt = (
            f"유저가 입력한 음식 이름: '{food_name}'\n"
            "이 음식을 식사 후 먹는 디저트(후식, 간식, 과자, 아이스크림, 케이크 등)로 볼 수 있다면 'YES', "
            "디저트가 아니라 일반적인 식사 메뉴(예: 삼겹살, 김치찌개, 라면, 국밥 등)라면 'NO'라고만 답해줘."
        )
        response = model.generate_content(prompt)
        result = response.text.strip().upper()
        return "YES" in result
    except Exception as e:
        # API 오류 발생 시 안전을 위해 일단 통과시키도록 예외 처리
        return True

# --- 화면 구현 ---

# 메인 타이틀
st.title("🍰 당충전소: 학생들의 최애 디저트 게시판")
st.markdown("우리 학교 학생들이 가장 좋아하는 디저트는 무엇일까요? 여러분의 최애 디저트를 공유해주세요!")
st.write("---")

# 사이드바: 입력 폼 및 통계
st.sidebar.header("🧁 내 최애 디저트 등록하기")

with st.sidebar.form(key="dessert_form", clear_on_submit=True):
    input_name = st.text_input("디저트 이름", placeholder="예: 초코 수플레 팬케이크")
    input_reason = st.text_area("추천하는 이유", placeholder="예: 입안에서 살살 녹아요...")
    submit_button = st.form_submit_button(label="게시판에 올리기")

if submit_button:
    if not input_name.strip() or not input_reason.strip():
        st.sidebar.warning("디저트 이름과 이유를 모두 입력해주세요!")
    else:
        # AI 필터링 진행
        with st.sidebar.spinner("디저트 검사 중... 🔍"):
            is_dessert = check_if_dessert(input_name)
        
        if is_dessert:
            # 새로운 의견을 리스트 맨 앞에 추가 (최신순 정렬을 위해)
            new_dessert = {"name": input_name, "reason": input_reason}
            st.sidebar.success(f"🎉 '{input_name}' 등록 완료!")
            st.session_state.dessert_list.insert(0, new_dessert)
            st.rerun()
        else:
            st.sidebar.error(f"❌ '{input_name}'은(는) 디저트가 아닌 것 같아요! 후식 메뉴만 입력해주세요. 🙅‍♂️")

# 사이드바 하단 통계
st.sidebar.write("---")
st.sidebar.write(f"📊 지금까지 모인 디저트 의견: **{len(st.session_state.dessert_list)}개**")


# 메인 화면: 등록된 디저트 목록 보여주기
st.subheader("📢 학생들이 추천한 디저트 목록 (최신순)")

if not st.session_state.dessert_list:
    st.info("아직 등록된 디저트가 없습니다. 첫 번째 주인공이 되어보세요!")
else:
    for idx, item in enumerate(st.session_state.dessert_list):
        # 귀여운 카드 형태로 출력
        with st.container():
            st.markdown(
                f"""
                <div style="background-color: #f9f9f9; padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 5px solid #ff4b4b;">
                    <h4 style="margin: 0; color: #ff4b4b;">✨ {item['name']}</h4>
                    <p style="margin: 5px 0 0 0; color: #333333; font-size: 15px;">"{item['reason']}"</p>
                </div>
                """, 
                unsafe_allow_html=True
            )            
