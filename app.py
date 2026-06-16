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
    .dessert-warning {
        background-color: #fff3cd;
        color: #856404;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #ffeeba;
        margin-bottom: 15px;
    }
    .other-box {
        background-color: #e9ecef;
        padding: 12px;
        border-radius: 10px;
        text-align: center;
        color: #495057;
        font-weight: 500;
        margin-top: 15px;
        margin-bottom: 30px;
    }
    </style>
""", unsafe_allow_html=True)

# 2. API 키 검증 및 모델 설정
if "GEMINI_API_KEY" not in st.secrets:
    st.error("🔑 Streamlit Secrets에 'GEMINI_API_KEY'가 설정되지 않았습니다.")
    st.stop()

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# 3. [공용 DB] 모든 학생이 공유하는 데이터베이스
@st.cache_resource
def get_shared_database():
    return {
        "food_history": [],  # 적힌 음식들 (순서 기록)
        "likes": {},         # 음식별 좋아요 수 {"치킨": 5, "마라탕": 2}
        "last_date": str(datetime.date.today())
    }

db = get_shared_database()

# 하루마다 자동 초기화 로직
current_date_str = str(datetime.date.today())
if db["last_date"] != current_date_str:
    db["food_history"] = []          
    db["likes"] = {}
    db["last_date"] = current_date_str 
    if "ai_feedback" in st.session_state: st.session_state.ai_feedback = None
    if "warning_msg" in st.session_state: st.session_state.warning_msg = None

# 4. [개인 세션] 사용자별 상태 초기화
if "ai_feedback" not in st.session_state: st.session_state.ai_feedback = None
if "warning_msg" not in st.session_state: st.session_state.warning_msg = None
if "submit_count" not in st.session_state: st.session_state.submit_count = 0
if "today_tracked" not in st.session_state: st.session_state.today_tracked = current_date_str
if "admin_fail_count" not in st.session_state: st.session_state.admin_fail_count = 0
if "admin_lock_date" not in st.session_state: st.session_state.admin_lock_date = ""

# ★ 개인이 누른 '좋아요' 기록 (음식당 1개 제한용)
if "liked_foods" not in st.session_state:
    st.session_state.liked_foods = set()

# 날짜가 바뀌면 개인 기록 모두 리셋
if st.session_state.today_tracked != current_date_str:
    st.session_state.submit_count = 0
    st.session_state.admin_fail_count = 0
    st.session_state.admin_lock_date = ""
    st.session_state.liked_foods = set()
    st.session_state.today_tracked = current_date_str

# 5. 음식 카드 UI + 좋아요 버튼 렌더링 함수
def draw_food_card(food, rank_or_icon, key_prefix):
    sub_count = db["food_history"].count(food)
    like_count = db["likes"].get(food, 0)
    total_score = sub_count + like_count
    
    with st.container(border=True):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"#### {rank_or_icon} {food}")
            st.caption(f"🔥 총 **{total_score}**점 (추천 {sub_count}회 + 좋아요 {like_count}개)")
        with col2:
            st.write("") # 버튼 수직 중앙 정렬용 간격
            if food in st.session_state.liked_foods:
                st.button("❤️ 완료", key=f"{key_prefix}_{food}_done", disabled=True, use_container_width=True)
            else:
                if st.button("🤍 좋아요", key=f"{key_prefix}_{food}", use_container_width=True):
                    db["likes"][food] = like_count + 1
                    st.session_state.liked_foods.add(food)
                    st.rerun()

# 6. AI 분석 함수
def analyze_food_with_ai(user_input):
    model = genai.GenerativeModel('gemini-2.5-flash-lite')
    prompt = f"""
    당신은 학생들이 입력한 음식을 분석하는 영양사입니다. 사용자 입력: "{user_input}"
    [규칙]
    1. 'is_dessert': 디저트/간식류면 true, 주식/식사류면 false.
    2. 'standard_name': 단일 명사 단어로 표준화.
    3. 'comment': 학생에게 건넬 재치 있는 한마디. 
    [반환 JSON 포맷] {{"is_dessert": true/false, "standard_name": "음식명", "comment": "코멘트"}}
    """
    try:
        response = model.generate_content(prompt)
        return json.loads(response.text.strip().replace("```json", "").replace("```", ""))
    except Exception as e:
        return {"is_dessert": False, "standard_name": user_input[:10].strip(), "comment": "맛있겠네요! 추가할게요 😋"}

# 7. 메인 화면 레이아웃
st.title("🥢 나의 먹킷리스트")
st.subheader("내가 먹고 싶은 음식은..")
st.caption(f"📅 오늘 날짜: {current_date_str} (매일 자정에 랭킹이 리셋됩니다)")
st.write("---")

# [화면 중앙 1] 실시간 1~5등 분류 및 시각화 (총점 기준)
st.markdown("### 🏆 오늘의 먹킷리스트 TOP 5")

if db["food_history"]:
    # 총점 계산 (추천 횟수 + 좋아요 수)
    unique_foods = set(db["food_history"])
    scores = {}
    for f in unique_foods:
        scores[f] = db["food_history"].count(f) + db["likes"].get(f, 0)
    
    # 점수 기준으로 내림차순 정렬
    sorted_foods = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_5 = sorted_foods[:5]
    
    rank_icons = ["🥇 1등", "🥈 2등", "🥉 3등", "🏅 4등", "🏅 5등"]
    
    # TOP 5 출력
    for idx, (food, score) in enumerate(top_5):
        draw_food_card(food, rank_icons[idx], f"top5_{idx}")
        
    # 그 외 메뉴 개수 합산
    if len(sorted_foods) > 5:
        other_menu_count = len(sorted_foods) - 5
        other_votes_count = sum(score for _, score in sorted_foods[5:])
        st.markdown(f"""
        <div class="other-box">
            🔹 1~5등 외에도 <b>{other_menu_count}개</b>의 다양한 메뉴가 더 적혔어요! (그 외 총 {other_votes_count}점)
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("💡 아직 등록된 메뉴가 없습니다. 아래에서 첫 번째 메뉴를 추천해 보세요!")

# [화면 중앙 2] 최근 등록된 먹킷리스트 5개
st.write("---")
st.markdown("### 🕒 최근 등록된 메뉴 (최신 5개)")

if db["food_history"]:
    # 최근 등록 순으로 중복 제거하여 5개 추출
    recent_unique = []
    for f in reversed(db["food_history"]):
        if f not in recent_unique:
            recent_unique.append(f)
        if len(recent_unique) >= 5:
            break
            
    for idx, food in enumerate(recent_unique):
        draw_food_card(food, "🆕", f"recent_{idx}")
else:
    st.caption("최근 등록된 메뉴가 없습니다.")

st.write("---")

# 8. 입력 및 기능 제어 영역
remaining_chances = 3 - st.session_state.submit_count

with st.form(key="food_form", clear_on_submit=True):
    st.markdown(f"✍️ **음식 추천하기** (오늘 남은 추천 기회: **{remaining_chances} / 3**회)")
    user_food = st.text_input(
        "먹고 싶은 음식을 적어주세요! (🚨 하루에 딱 3개의 메뉴만 추천 가능합니다)", 
        placeholder="예: 치킨, 떡볶이, 마라탕 등",
        disabled=(remaining_chances <= 0)
    )
    submit_button = st.form_submit_button("먹킷리스트에 등록 🚀", disabled=(remaining_chances <= 0))

if submit_button:
    if st.session_state.submit_count >= 3:
        st.error("🚫 오늘은 이미 3번의 추천을 모두 완료했습니다!")
    elif not user_food.strip():
        st.warning("음식 이름을 입력한 후 등록 버튼을 눌러주세요!")
    else:
        with st.spinner("AI가 메뉴를 분석하고 분류하는 중..."):
            ai_res = analyze_food_with_ai(user_food)
            
            if ai_res.get("is_dessert", False):
                st.session_state.warning_msg = f"⚠️ '{user_food}'은(는) 디저트네요! 여기는 든든한 주식만 받습니다."
                st.session_state.ai_feedback = None
            else:
                standard_name = ai_res.get("standard_name", "").strip()
                if standard_name:
                    db["food_history"].append(standard_name) 
                    st.session_state.submit_count += 1
                    st.session_state.ai_feedback = f"🤖 AI 분석 결과: '{standard_name}' 추가 완료! (남은 추천 기회: {3 - st.session_state.submit_count}회)\n\n💬 {ai_res.get('comment', '')}"
                    st.session_state.warning_msg = None
                else:
                    st.session_state.warning_msg = "🤔 식사류 음식을 인식하지 못했습니다. 다시 입력해 주세요."
                    st.session_state.ai_feedback = None
        st.rerun()

if st.session_state.warning_msg:
    st.markdown(f'<div class="dessert-warning">{st.session_state.warning_msg}</div>', unsafe_allow_html=True)
if st.session_state.ai_feedback:
    st.success(st.session_state.ai_feedback)

# 9. 관리자 도구
st.write(" ")
st.write(" ")
with st.expander("⚙️ 앱 테스트 및 관리자 도구"):
    if st.session_state.admin_lock_date == current_date_str:
        st.error("🚫 비밀번호 3회 오류로 인해 오늘 하루 동안 관리자 기능이 차단되었습니다.")
    else:
        admin_password = st.text_input("관리자 비밀번호를 입력하고 Enter를 누르세요", type="password")
        
        if admin_password:
            if admin_password == "qpal":
                st.success("🔓 관리자 인증 성공!")
                st.session_state.admin_fail_count = 0
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("📊 샘플 추가 (테스트)"):
                        sample_data = ["치킨", "치킨", "떡볶이", "마라탕", "피자", "짜장면"]
                        db["food_history"].extend(sample_data)
                        db["likes"]["치킨"] = 3
                        st.success("샘플 주입 완료!")
                        st.rerun()
                with col2:
                    if st.button("🔄 내 기회 & 좋아요 리셋"):
                        st.session_state.submit_count = 0
                        st.session_state.liked_foods = set()
                        st.success("내 추천/좋아요 기록이 초기화되었습니다!")
                        st.rerun()
                with col3:
                    if st.button("🗑️ 전체 데이터 완전 리셋"):
                        db["food_history"] = []
                        db["likes"] = {}
                        st.session_state.liked_foods = set()
                        st.session_state.ai_feedback = None
                        st.session_state.warning_msg = None
                        st.success("전체 초기화 완료!")
                        st.rerun()
            else:
                if "last_checked_pass" not in st.session_state or st.session_state.last_checked_pass != admin_password:
                    st.session_state.admin_fail_count += 1
                    st.session_state.last_checked_pass = admin_password
                    
                    if st.session_state.admin_fail_count >= 3:
                        st.session_state.admin_lock_date = current_date_str
                        st.error("🚫 비밀번호를 3회 틀렸습니다! 오늘 하루 동안 차단됩니다.")
                        st.rerun()
                st.error(f"🔒 비밀번호가 틀렸습니다. (틀린 횟수: {st.session_state.admin_fail_count} / 3회)")
