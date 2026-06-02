import streamlit as tf
import streamlit as st
from google import genai
from google.genai import types
from google.genai.errors import APIError

# 페이지 설정
st.set_page_config(page_title="달콤살벌 연애상담소", page_icon="💖")
st.title("💖 달콤살벌 연애상담소")
st.caption("연애 고민이 있나요? Gemini가 진심 어린 조언을 해드릴게요.")

# 1. Streamlit Secrets에서 API 키 가져오기 및 클라이언트 초기화
try:
    # Streamlit Cloud 환경에서는 st.secrets["GEMINI_API_KEY"]로 관리됩니다.
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
if prompt := st.chat_input("연애 고민을 이야기해보세요... (예: 짝사랑하는 사람이 생겼어요)"):
    # 사용자 메시지 화면에 표시 및 세션 저장
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 5. Gemini 챗봇 답변 생성
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        # 이전 대화 맥락을 시스템 프롬프트와 함께 구성
        # (원하는 다른 주제가 있다면 이 system_instruction 부분을 수정하시면 됩니다!)
        system_instruction = (
            "당신은 공감 능력이 뛰어나고 때로는 현실적인 조언을 아끼지 않는 전문 연애 상담사입니다. "
            "친근하고 다정한 말투로 대답하되, 사용자의 고민을 진지하게 듣고 해결책을 제시해주세요."
        )
        
        # 모델에 전달할 메시지 리스트 구축
        contents = []
        for msg in st.session_state.messages:
            role = "user" if msg["role"] == "user" else "model"
            contents.append(types.Content(
                role=role,
                parts=[types.Part.from_text(text=msg["content"])]
            ))
            
        try:
            # API 호출
            response = client.models.generate_content(
                model='gemini-2.5-flash-lite',
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.7,
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
