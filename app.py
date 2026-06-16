import streamlit as st
import google.generativeai as genai
import json
from collections import Counter

# 1. 페이지 설정 및 디자인
st.set_page_config(
    page_title="🥢 나의 먹킷리스트",
    page_icon="🥢",
    layout="centered"
)

# 기본 스타일 커스텀 (중앙 정렬 및 카드 스타일)
st.markdown("""
    <style>
    .rank-box {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        border-left: 5px solid #ff4b4b;
    }
    .dessert-warning {
        background-color: #fff3cd;
        color: #856404;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #ffeeba;
    }
    </style>
""", unsafe_allow_html=True)

# 2. API 키 검증 및 AI 모델 설정
if "GEMINI_API_KEY" not in st.secrets:
    st.error("🔑 Streamlit Secrets에 'GEMINI_API_KEY'가 설정되지 않았습니다. 관리자 설정을 확인해주세요.")
    st.stop()

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# 3. 세션 상태(Session State) 초기화 (데이터 휘발 방지)
if "food_history" not in st.session_state:
    st.session_state.food_history = []
if "ai_feedback" not in st.session_state:
    st.session_state.ai_feedback = None
if "warning_msg" not in st.session_state:
    st.session_state.warning_msg = None

# 4. AI 분석 함수 정의 (gemini-2.5-flash-lite 활용)
def analyze_food_with_ai(user_input):
    model = genai.GenerativeModel('gemini-2.5-flash-lite')
    
    prompt = f"""
    당신은 학생들이 입력한 음식을 분석하는 스마트한 AI 영양사입니다.
    사용자가 입력한 문장: "{user_input}"
    
    다음 규칙에 따라 엄격하게 판별하고 오직 JSON 형식으로만 응답하세요. 다른 설명이나 마크다운 기호는 생략하세요.
    
    [규칙]
    1. 'is_dessert': 입력된 음식을 판단하여 디저트/간식류(케이크, 마카롱, 탕후루, 아이스크림, 카페 음료, 초콜릿, 쿠키 등)라면 true, 주식/식사류(떡볶이, 치킨, 피자, 마라탕, 삼겹살, 국밥 등)라면 false로 판단하십시오.
    2. 'standard_name': 사용자가 입력한 표현을 대표하는 단일 명사 단어(예: "치킨먹고파" -> "치킨", "엽떡" -> "떡볶이", "마라탕탕탕" -> "마라탕")로 표준화하십시오. 식사류가 아니거나 알 수 없다면 빈 문자열("")로 보냅니다.
    3. 'comment': 학생에게 건넬 친근하고 재치 있는 한마디 답변을 한국어로 작성하십시오. 
    
    [반환 JSON 포맷]
    {{
        "is_dessert": true 또는 false,
        "standard_name": "표준화된 음식명",
        "comment": "리액션 한마디"
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        # JSON 문자열 추출 및 정제
        clean_text = response.text.strip().replace("```json", "").replace("```", "")
        result = json.loads(clean_text)
        return result
    except Exception as e:
        # 에러 발생 시 예외 처리 (안정적인 기본값 반환)
        return {
            "is_dessert": False,
            "standard_name": user_input[:10].strip(),
            "comment": "와! 정말 맛있겠네요. 먹킷리스트에 추가할게요! 😋"
        }

# 5. 메인 화면 레이아웃 구성
st.title("🥢 나의 먹킷리스트")
st.subheader("내가 먹고 싶은 음식은..")
st.write("친구들이 가장 먹고 싶어 하는 주식(식사) 메뉴를 실시간으로 집계합니다!")

st.write("---")

# [화면 중앙] 실시간 1~5등 분류 및 시각화
st.markdown("### 🏆 실시간 먹킷리스트 TOP 5")

if st.session_state.food_history:
    # 빈도수 계산
    counts = Counter(st.session_state.food_history)
    top_5 = counts.most_common(5)
    
    # 순위별 아이콘 정의
    rank_icons = ["🥇 1등", "🥈 2등", "🥉 3등", "🏅 4등", "🏅 5등"]
    
    # 랭킹 출력
    for idx, (food, count) in enumerate(top_5):
        st.markdown(f"""
        <div class="rank-box">
            <span style='font-size:1.2rem; font-weight:bold;'>{rank_icons[idx]}: {food}</span> 
            <span style='float:right; color:#666;'>{count}표 🗳️</span>
        </div>
        """, unsafe_allow_html=True)
        
    # 5등까지 다 안 채워졌을 때 가이드
    if len(top_5) < 5:
        st.caption(f"Tip: 현재 {len(top_5)}개의 메뉴가 등록되었습니다. 더 많은 음식을 등록해 5등까지 채워보세요!")
else:
    st.info("💡 아직 등록된 주식 메뉴가 없습니다. 아래 입력창에서 먹고 싶은 음식을 추가해 주세요!")

st.write("---")

# 6. 입력 및 기능 제어 영역
with st.form(key="food_form", clear_on_submit=True):
    user_food = st.text_input("먹고 싶은 음식을 자유롭게 적어보세요! (예: 치킨, 엽떡, 뜨끈한 국밥 등)", placeholder="여기에 입력...")
    # 이 부분의 함수명을 올바르게 수정했습니다!
    submit_button = st.form_submit_button("먹킷리스트에 등록 🚀")

if submit_button:
    if not user_food.strip():
        st.warning("음식 이름을 입력한 후 등록 버튼을 눌러주세요!")
    else:
        with st.spinner("AI가 메뉴를 분석하고 분류하는 중..."):
            ai_res = analyze_food_with_ai(user_food)
            
            # 디저트 유무에 따른 분기 로직
            if ai_res.get("is_dessert", False):
                st.session_state.warning_msg = f"⚠️ '{user_food}'은(는) 디저트네요! 디저트는 '🍰 디저트 전용 먹킷리스트' 페이지에서 작성해 주세요! 여기는 든든한 주식만 받습니다."
                st.session_state.ai_feedback = None
            else:
                standard_name = ai_res.get("standard_name", "").strip()
                if standard_name:
                    st.session_state.food_history.append(standard_name)
                    st.session_state.ai_feedback = f"🤖 AI 분석 결과: '{standard_name}' 추가 완료!\n\n💬 {ai_res.get('comment', '')}"
                    st.session_state.warning_msg = None
                else:
                    st.session_state.warning_msg = "🤔 식사류 음식을 인식하지 못했습니다. 다시 정확한 음식명으로 입력해 주세요."
                    st.session_state.ai_feedback = None
        
        # 최신 결과를 즉시 반영하기 위해 리런(Rerun)
        st.rerun()

# 7. AI 피드백 및 결과 메시지 출력
if st.session_state.warning_msg:
    st.markdown(f'<div class="dessert-warning">{st.session_state.warning_msg}</div>', unsafe_allow_html=True)

if st.session_state.ai_feedback:
    st.success(st.session_state.ai_feedback)

# 8. 유틸리티 및 데이터 관리 기능 (차별화 요소: 샘플 데이터 및 초기화)
st.write(" ")
st.write(" ")
with st.expander("⚙️ 앱 테스트 및 관리자 도구"):
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📊 테스트용 샘플 데이터 채우기"):
            sample_data = ["치킨", "치킨", "치킨", "떡볶이", "떡볶이", "마라탕", "마라탕", "마라탕", "마라탕", "피자", "피자", "짜장면"]
            st.session_state.food_history.extend(sample_data)
            st.success("샘플 데이터가 추가되었습니다! 중앙의 랭킹 보드를 확인하세요.")
            st.rerun()
    with col2:
        if st.button("🗑️ 모든 데이터 리셋"):
            st.session_state.food_history = []
            st.session_state.ai_feedback = None
            st.session_state.warning_msg = None
            st.success("데이터가 초기화되었습니다.")
            st.rerun()
