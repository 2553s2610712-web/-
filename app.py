import streamlit as st
from google import genai
from google.genai import types
from google.genai.errors import APIError

# 페이지 설정
st.set_page_config(page_title="영양성분 분석 AI", page_icon="🥗")
st.title("🥗 무엇이든 분석하는 영양성분 AI 상담소")
st.caption("궁금한 음식이나 오늘 드신 식단을 입력하시면 영양성분을 상세히 분석해 드립니다.")

# 1. Streamlit Secrets에서 API 키 가져오기 및 클라이언트 초기화
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=api_key)
except KeyError:
    st.error("API 키가 설정되지 않았습니다. Streamlit Secrets에 'GEMINI_API_KEY'를 등록해주세요.")
    st.stop()

# 2. 세션 상태로 채팅 기록 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 3. 기존 대화 기록 화면에 출력
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. 사용자 입력 받기
if prompt := st.chat_input("예시: '제육볶음이랑 공기밥 1그릇 영양소 분석해줘' 또는 '오늘 아침에 사과랑 그릭요거트 먹었어'"):
    # 사용자 메시지 화면에 표시 및 세션 저장
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 5. Gemini 챗봇 답변 생성
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        # 챗봇의 페르소나 및 출력 형식을 정의하는 시스템 프롬프트
        system_instruction = (
            "당신은 친절하고 전문적인 영양사 AI입니다. "
            "사용자가 입력한 음식이나 식단을 분석하여 각 음식별 칼로리, 탄수화물, 단백질, 지방 등 주영양소를 제공해야 합니다. "
            "결과를 보여줄 때는 가독성을 위해 반드시 '마크다운 표(Table)' 형태로 정돈하여 제시해주세요. "
            "표 아래에는 전체 식단에 대한 간단한 총평이나 영양학적 조언(예: 단백질이 부족하니 다음 식사 때 보충하세요 등)을 다정하게 덧붙여주세요."
        )
        
        # 대화 맥락 구축
        contents = []
        for msg in st.session_state.messages:
            role = "user" if msg["role"] == "user" else "model"
            contents.append(types.Content(
                role=role,
                parts=[types.Part.from_text(text=msg["content"])]
            ))
            
        try:
            # API 호출 (gemini-2.5-flash-lite 모델 사용)
            response = client.models.generate_content(
                model='gemini-2.5-flash-lite',
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.4, # 조금 더 정확한 정보 제공을 위해 온도를 낮춤
                )
            )
            
            # 답변 출력 및 세션 저장
            ai_response = response.text
            message_placeholder.markdown(ai_response)
            st.session_state.messages.append({"role": "assistant", "content": ai_response})
            
        except APIError as e:
            st.error(f"Gemini API 오류가 발생했습니다: {e.message}")
        except Exception as e:
            st.error(f"예상치 못한 오류가 발생했습니다: {str(e)}")
