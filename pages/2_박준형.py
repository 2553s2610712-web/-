import streamlit as st
import google.genai as genai
from google.genai import types
import json
import pandas as pd

# 1. 페이지 기본 설정 및 디자인
st.set_page_config(
    page_title="AI 영양사 - 맞춤형 학교 급식 식단 생성기",
    page_icon="🍱",
    layout="wide"
)

# 커스텀 스타일 적용 (깔끔한 급식표 스타일)
st.markdown("""
    <style>
    .main-title { font-size: 2.5rem; font-weight: bold; color: #2C3E50; text-align: center; margin-bottom: 5px; }
    .sub-title { font-size: 1.1rem; color: #7F8C8D; text-align: center; margin-bottom: 30px; }
    .menu-box { background-color: #F8F9FA; padding: 15px; border-radius: 10px; border-left: 5px solid #3498DB; }
    </style>
""", unsafe_index=True)

st.markdown('<div class="main-title">🍱 AI 영양사쌤의 맞춤형 급식 식단 생성기</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">학생들의 선호도와 영양 균형을 모두 잡은 일주일 급식표를 만들어 드립니다.</div>', unsafe_allow_html=True)

# 2. API 키 검증 및 client 초기화
if "GEMINI_API_KEY" not in st.secrets:
    st.error("🚨 Streamlit Secrets에 'GEMINI_API_KEY'가 설정되지 않았습니다. 대시보드에서 설정해 주세요.")
    st.stop()

# 최신 2026년 규격 google-genai 라이브러리 클라이언트 초기화
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# 3. 사이드바 - 학생 선호 메뉴 설정 (등수 리스트)
with st.sidebar:
    st.header("✍️ 학생 선호도 및 조건 설정")
    st.write("학생들이 먹고 싶어 하는 메뉴를 순위별로 적어주세요. AI가 이를 반영하여 식단을 구성합니다.")
    
    # 기본 샘플 제공
    rank_1 = st.text_input("1위 메뉴 (가장 원하는 음식)", "마라탕")
    rank_2 = st.text_input("2위 메뉴", "돈가스")
    rank_3 = st.text_input("3위 메뉴", "치킨 마요 덮밥")
    rank_4 = st.text_input("4위 메뉴", "떡볶이")
    rank_5 = st.text_input("5위 메뉴", "짜장면")
    
    st.markdown("---")
    st.markdown("**📌 필수 규칙 자동 적용:**\n- 모든 식단에 **밥, 국, 김치** 필수 포함\n- 영양 불균형 해소를 위한 사이드 메뉴 AI 자동 조합")

# 4. 메인 화면 구성 및 안내
st.markdown("### 📋 현재 설정된 학생 선호 메뉴")
cols = st.columns(5)
user_ranks = [rank_1, rank_2, rank_3, rank_4, rank_5]
for i, col in enumerate(cols):
    with col:
        st.markdown(f"<div class='menu-box'><b>{i+1}등</b><br>{user_ranks[i]}</div>", unsafe_allow_html=True)

st.write("")

# 급식 생성 버튼
if st.button("✨ 영양 맞춤 일주일 급식표 생성하기", type="primary", use_container_width=True):
    
    # 프롬프트 설계 (요구사항 엄격 지정 및 JSON 구조화 요청)
    prompt = f"""
    당신은 대한민국의 베테랑 학교 영양사입니다. 
    학생들이 원하는 선호 음식 리스트를 바탕으로, 영양 균형이 잡힌 월요일부터 금요일까지의 5일치 점심 급식표를 작성해 주세요.

    [학생 선호 음식 리스트 (1위~5위)]
    1위: {rank_1}
    2위: {rank_2}
    3위: {rank_3}
    4위: {rank_4}
    5위: {rank_5}

    [필수 규칙]
    1. 모든 요일의 식단에는 반드시 한국식 '밥(주식)', '국(찌개류)', '김치류'가 확정적으로 포함되어야 합니다.
    2. 학생들이 원하는 선호 음식(마라탕, 떡볶이 등)이 들어가는 날에는 영양이 치우치지 않도록 채소류나 단백질 반찬을 적절히 조합하세요. (예: 마라탕이 나오면 꿔바로우 대신 신선한 샐러드나 나물, 과일 유제품 등을 매칭)
    3. 5일 동안 탄수화물, 단백질, 지방, 비타민이 골고루 섭취되도록 구성해 주세요.
    4. 각 요일별 식단의 영양적 특징과 조화 이유를 '영양사 코멘트'에 간략히 설명해 주세요.

    정확한 데이터 처리를 위해 반드시 아래의 JSON 포맷으로만 답변하세요. 다른 텍스트는 절대 포함하지 마세요.

    {{
      "식단": [
        {{
          "요일": "월요일",
          "밥": "핵심 주식 이름",
          "국": "국/찌개 이름",
          "김치": "김치 종류",
          "주반찬": "메인 반찬",
          "부반찬": "서브 반찬/샐러드/디저트",
          "영양사코멘트": "이 식단의 영양적 조화 설명"
        }},
        ... (금요일까지 반복)
      ]
    }}
    """
    
    with st.spinner("AI 영양사 선생님이 영양소를 계산하여 식단을 짜고 있습니다. 잠시만 기다려주세요..."):
        try:
            # gemini-2.5-flash-lite 모델 호출 및 JSON 응답 강제
            response = client.models.generate_content(
                model='gemini-2.5-flash-lite',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.7
                )
            )
            
            # 결과 파싱
            result_json = json.loads(response.text)
            menu_list = result_json.get("식단", [])
            
            if menu_list:
                st.success("🎉 영양 만점 일주일 급식표가 완성되었습니다!")
                
                # 시각적인 요일별 카드 배치
                for day_data in menu_list:
                    with st.expander(f"📅 {day_data['요일']} 식단 보기", expanded=True):
                        c1, c2, c3, c4, c5 = st.columns(5)
                        c1.metric("🍚 주식", day_data['밥'])
                        c2.metric("🥣 국물", day_data['국'])
                        c3.metric("🥢 김치", day_data['김치'])
                        c4.metric("🍗 주반찬", day_data['주반찬'])
                        c5.metric("🥗 부반찬/후식", day_data['부반찬'])
                        
                        st.info(f"💡 **영양사 쌤의 한마디:** {day_data['영양사코멘트']}")
                
                # 전체 표 데이터프레임으로 깔끔하게 정리 및 다운로드 기능 제공
                st.markdown("### 📊 한눈에 보는 급식표 요약")
                df = pd.DataFrame(menu_list)
                # 열 순서 예쁘게 변경
                df = df[["요일", "밥", "국", "김치", "주반찬", "부반찬", "영양사코멘트"]]
                st.dataframe(df, use_container_width=True, hide_index=True)
                
                # CSV 다운로드 버튼
                csv = df.to_csv(index=False).encode('utf-8-sig')
                st.download_button(
                    label="📥 급식표 CSV 파일로 다운로드",
                    data=csv,
                    file_name="ai_school_meal_plan.csv",
                    mime="text/csv"
                )
            else:
                st.error("식단 데이터를 가져오지 못했습니다. 다시 시도해 주세요.")
                
        except json.JSONDecodeError:
            st.error("🚨 AI가 생성한 데이터 형식이 올바르지 않습니다. 다시 한 번 버튼을 눌러주세요.")
        except Exception as e:
            st.error(f"🚨 오류가 발생했습니다: {str(e)}\nAPI 키 설정이나 네트워크 상태를 확인해 주세요.")
        
