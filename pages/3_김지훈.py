import streamlit as st
import google.generativeai as genai

# 1. 페이지 기본 설정 (타이틀 및 아이콘)
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
    st.error("⚠️ Streamlit Secrets에 GEMINI_API_KEY를 등록해주세요!")
    st.stop()

# 3. 데이터 저장소(세션 상태) 초기화 (추천 수 'votes' 항목 추가)
if "dessert_list" not in st.session_state:
    st.session_state.dessert_list = [
        {"name": "딸기 탕후루", "reason": "바삭하고 달콤해서 급식 먹고 매일 생각나요! 🍓", "votes": 12},
        {"name": "초코 마카롱", "reason": "시험 기간에 하나 먹으면 스트레스가 다 날아갑니다. 🍫", "votes": 8},
        {"name": "민트초코 아이스크림", "reason": "시원하고 깔끔해서 양치 안 해도 되는 기분! 🍦", "votes": 15}
    ]

# 4. AI 기반 디저트 판별 함수
def check_if_dessert(food_name):
    try:
        model = genai.GenerativeModel("gemini-2.5-flash-lite")
        prompt = (
            f"유저가 입력한 음식 이름: '{food_name}'\n"
            "이 음식을 식사 후에 먹는 디저트(후식, 간식, 과자, 아이스크림, 케이크, 빵류 등)로 볼 수 있다면 대답으로 'YES'를, "
            "디저트가 아니라 일반적인 식사 메뉴(예: 삼겹살, 김치찌개, 라면, 국밥, 떡볶이 등)라면 'NO'라고만 딱 한 단어로 답해줘."
        )
        response = model.generate_content(prompt)
        result = response.text.strip().upper()
        return "YES" in result
    except Exception as e:
        return True

# --- 화면 구현 시작 ---

# 메인 타이틀
st.title("🍰 당충전소: 학생들의 최애 디저트 게시판")
st.markdown("우리 학교 학생들이 가장 좋아하는 디저트는 무엇일까요? 여러분의 최애 디저트를 공유하고 투표해보세요!")
st.write("---")

# 사이드바: 입력 폼 및 통계
st.sidebar.header("🧁 내 최애 디저트 추천하기")

with st.sidebar.form(key="dessert_form", clear_on_submit=True):
    input_name = st.text_input("디저트 이름", placeholder="예: 초코 수플레 팬케이크")
    input_reason = st.text_area("추천하는 이유", placeholder="예: 입안에서 살살 녹고 기분이 좋아져요!")
    submit_button = st.form_submit_button(label="게시판에 등록하기")

# 등록 버튼을 눌렀을 때의 로직
if submit_button:
    if not input_name.strip() or not input_reason.strip():
        st.sidebar.warning("디저트 이름과 추천 이유를 모두 입력해주세요!")
    else:
        # AI 필터링 진행
        with st.sidebar.spinner("디저트가 맞는지 AI가 검사 중... 🔍"):
            is_dessert = check_if_dessert(input_name)
        
        if is_dessert:
            # 새로운 의견을 리스트에 추가 (초기 추천 수는 0)
            new_dessert = {"name": input_name, "reason": input_reason, "votes": 0}
            st.session_state.dessert_list.append(new_dessert)
            st.sidebar.success(f"🎉 '{input_name}' 등록 완료!")
            st.rerun() 
        else:
            st.sidebar.error(f"❌ '{input_name}'은(는) 디저트가 아닌 것 같아요! 식사류 대신 달콤한 후식 메뉴를 적어주세요. 🙅‍♂️")

# 사이드바 하단 통계 표시
st.sidebar.write("---")
st.sidebar.write(f"📊 현재까지 모인 디저트 의견: **{len(st.session_state.dessert_list)}개**")


# --- 메인 화면: 실시간 정렬 및 목록 출력 ---

# 1. 정렬 기준 선택 토글 (라디오 버튼)
sort_option = st.radio(
    "정렬 기준 선택",
    ["🔥 추천 많은 순 (종합 높은 순)", "⏱️ 최신 등록 순"],
    horizontal=True
)

st.write("---")

# 2. 선택한 기준에 따라 데이터 정렬 정렬
if sort_option == "🔥 추천 많은 순 (종합 높은 순)":
    # votes(추천수) 기준으로 내림차순 정렬
    display_list = sorted(st.session_state.dessert_list, key=lambda x: x["votes"], reverse=True)
else:
    # 원래 리스트를 역순(최신순)으로 뒤집어서 표현
    display_list = list(reversed(st.session_state.dessert_list))

# 3. 디저트 카드 목록 출력
if not display_list:
    st.info("아직 등록된 디저트가 없습니다. 첫 번째 주인공이 되어보세요!")
else:
    for idx, item in enumerate(display_list):
        # 고유한 인덱스를 찾기 위해 원본 리스트에서의 인덱스 계산
        original_idx = st.session_state.dessert_list.index(item)
        
        # 2열 레이아웃 구성 (왼쪽: 디저트 내용 카드, 오른쪽: 투표 버튼)
        col1, col2 = st.columns([5, 1])
        
        with col1:
            st.markdown(
                f"""
                <div style="background-color: #f9f9f9; padding: 15px; border-radius: 10px; border-left: 5px solid #ff4b4b; shadow: 1px 1px 3px rgba(0,0,0,0.1);">
                    <h4 style="margin: 0; color: #ff4b4b;">✨ {item['name']}</h4>
                    <p style="margin: 6px 0 0 0; color: #333333; font-size: 15px; line-height: 1.5;">"{item['reason']}"</p>
