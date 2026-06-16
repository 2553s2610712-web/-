import streamlit as st
import google.generativeai as genai
import json
from collections import Counter
import datetime

# 1. 페이지 설정 및 디자인
st.set_page_config(
    page_title="🥢 나의 먹킷리스트",
    page_icon="🥢",
    layout="centered"
)

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
    .other-box {
        background-color: #e9ecef;
        padding: 12px;
        border-radius: 10px;
        text-align: center;
        color: #495057;
        font-weight: 500;
        margin-top: 15px;
    }
    .chance-text {
        font-size: 0.9rem;
        color: #666;
        margin-bottom: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# 2. API 키 검증 및 AI 모델 설정
if "GEMINI_API_KEY" not in st.secrets:
    st.error("🔑 Streamlit Secrets에 'GEMINI_API_KEY'가 설정되지 않았습니다. 관리자 설정을 확인해주세요.")
    st.stop()

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# 3. 모든 학생이 공유하는 공용 데이터베이스
@st.cache_resource
def get_shared_database():
    return {
        "food_history": [],
        "last_date": str(datetime.date.today())
    }

db = get_shared_database()

# 실제 시간 기준 하루마다 자동 초기화 로직
current_date_str = str(datetime.date.today())
if db["last_date"] != current_date_str:
    db["food_history"] = []          
    db["last_date"] = current_date_str 
    if "ai_feedback" in st.session_state: st.session_state.ai_feedback = None
    if "warning_msg" in st.session_state: st.session_state.warning_msg = None

# 4. 개인 세션 상태 초기화 (★ 하루 3회 추천 제한 기능 추가)
if "ai_feedback" not in st.session_state:
    st.session_state.ai_feedback = None
if "warning_msg" not in st.session_state:
    st.session_state.warning_msg = None
if "submit_count" not in st.session_state:
    st.session_state.submit_count = 0
if "today_tracked" not in st.session_state:
    st.session_state.today_tracked = current_date_str

# 날짜가 바뀌면 개인의 하루 제출 횟수도 0으로 리셋
if st.session_state.today_tracked != current_date_str:
    st.session_state.submit_count = 0
    st.session_state.today_tracked = current_date_str

# 5. AI 분석 함수
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
        clean_text = response.text.strip().replace("```json", "").replace("```", "")
        return json.loads(clean_text)
    except Exception as e:
        return {
            "is_dessert": False,
            "standard_name": user_input[:10].strip(),
            "comment": "와! 정말 맛있겠네요. 먹킷리스트에 추가할게요! 😋"
        }

# 6. 메인 화면 레이아웃
st.title("🥢 나의 먹킷리스트")
st.subheader("내가 먹고 싶은 음식은..")
st.caption(f"📅 오늘 날짜: {current_date_str} (매일 자정에 랭킹이 리셋됩니다)")

st.write("---")

# [화면 중앙] 실시간 1~5등 분류 및 시각화
st.markdown("### 🏆 오늘의 먹킷리스트 TOP 5")

if db["food_history"]:
    counts = Counter(db["food_history"])
    top_5 = counts.most_common(5)
    
    rank_icons = ["🥇 1등", "🥈 2등", "🥉 3등", "🏅 4등", "🏅 5등"]
    
    for idx, (food, count) in enumerate(top_5):
        st.markdown(f"""
        <div class="rank-box">
            <span style='font-size:1.2rem; font-weight:bold;'>{rank_icons[idx]}: {food}</span> 
            <span style='float:right; color:#666;'>{count}표 🗳️</span>
        </div>
        """, unsafe_allow_html=True)
        
    total_unique_menu = len(counts)
    if total_unique_menu > 5:
        other_menu_count = total_unique_menu - 5
        other_votes_count = sum(count for food, count in counts.most_common()[5:])
        st.markdown(f"""
        <div class="other-box">
            🔹 1~5등 외에도 <b>{other_menu_count}개</b>의 다양한 메뉴가 더 적혔어요! (그 외 메뉴 총 {other_votes_count}표 입력됨)
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("💡 오늘 처음으로 먹고 싶은 주식 메뉴를 등록해 보세요!")

st.write("---")

# 7. 입력 및 기능 제어 영역 (★ 하루 3회 제한 UI 및 텍스트 창 안내 추가)
remaining_chances = 3 - st.session_state.submit_count

with st.form(key="food_form", clear_on_submit=True):
    # 상단에 기회 실시간 안내
    st.markdown(f"✍️ **음식 추천하기** (오늘 남은 추천 기회: **{remaining_chances} / 3**회)")
    
    # 텍스트 창 레이블에 하루 3개 제한 안내 명시
    user_food = st.text_input(
        "먹고 싶은 음식을 적어주세요! (🚨 하루에 딱 3개의 메뉴만 추천 가능합니다)", 
        placeholder="예: 치킨, 엽떡, 마라탕, 삼겹살 등",
        disabled=(remaining_chances <= 0) # 기회를 다 쓰면 텍스트창 비활성화
    )
    
    submit_button = st.form_submit_button("먹킷리스트에 등록 🚀", disabled=(remaining_chances <= 0))

if submit_button:
    # 3회 초과 검증 (보안용 크로스체크)
    if st.session_state.submit_count >= 3:
        st.error("🚫 오늘은 이미 3번의 추천을 모두 완료했습니다! 내일 새로운 메뉴를 추천해 주세요.")
    elif not user_food.strip():
        st.warning("음식 이름을 입력한 후 등록 버튼을 눌러주세요!")
    else:
        with st.spinner("AI가 메뉴를 분석하고 분류하는 중..."):
            ai_res = analyze_food_with_ai(user_food)
            
            if ai_res.get("is_dessert", False):
                st.session_state.warning_msg = f"⚠️ '{user_food}'은(는) 디저트네요! 디저트는 '🍰 디저트 전용 먹킷리스트' 페이지에서 작성해 주세요! 여기는 든든한 주식만 받습니다."
                st.session_state.ai_feedback = None
            else:
                standard_name = ai_res.get("standard_name", "").strip()
                if standard_name:
                    db["food_history"].append(standard_name) 
                    # 등록 성공 시에만 개인 제출 횟수 +1 증가!
                    st.session_state.submit_count += 1
                    st.session_state.ai_feedback = f"🤖 AI 분석 결과: '{standard_name}' 추가 완료! (남은 추천 기회: {3 - st.session_state.submit_count}회)\n\n💬 {ai_res.get('comment', '')}"
                    st.session_state.warning_msg = None
                else:
                    st.session_state.warning_msg = "🤔 식사류 음식을 인식하지 못했습니다. 다시 정확한 음식명으로 입력해 주세요."
                    st.session_state.ai_feedback = None
        st.rerun()

# 피드백 메시지 출력
if st.session_state.warning_msg:
    st.markdown(f'<div class="dessert-warning">{st.session_state.warning_msg}</div>', unsafe_allow_html=True)

if st.session_state.ai_feedback:
    st.success(st.session_state.ai_feedback)

# 8. 관리자 도구 (테스트용 내 기회 리셋 기능 추가)
st.write(" ")
st.write(" ")
with st.expander("⚙️ 앱 테스트 및 관리자 도구"):
    admin_password = st.text_input("관리자 비밀번호를 입력하세요", type="password")
    
    if admin_password == "1234":
        st.success("🔓 관리자 인증 성공!")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📊 대량 샘플 채우기"):
                sample_data = ["치킨", "치킨", "치킨", "떡볶이", "떡볶이", "마라탕", "마라탕", "피자", "짜장면", "국밥"]
                db["food_history"].extend(sample_data)
                st.success("샘플 주입 완료!")
                st.rerun()
        with col2:
            if st.button("🔄 내 추천 기회 리셋"):
                st.session_state.submit_count = 0
                st.success("내 추천 기회가 3회로 충전되었습니다! (테스트용)")
                st.rerun()
        with col3:
            if st.button("🗑️ 전체 데이터 리셋"):
                db["food_history"] = []
                st.session_state.ai_feedback = None
                st.session_state.warning_msg = None
                st.success("전체 초기화 완료!")
                st.rerun()
    elif admin_password != "":
        st.error("🔒 비밀번호가 틀렸습니다.")
