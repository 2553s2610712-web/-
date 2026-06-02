import streamlit as st
from google import genai
from google.genai import types
from google.genai.errors import APIError

# 페이지 설정
st.set_set_page_config = st.set_page_config(page_title="신비한 AI 타로 소품숍", page_icon="🔮")
st.title("🔮 신비한 AI 타로 마스터")
st.caption("마음을 차분히 가라앉히고, 당신의 고민을 이야기해 주세요. 타로 카드가 길을 보여줄 것입니다.")

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
if prompt := st.chat_input("예시: '올해 취업 운세가 궁금해요', '그 사람과 다시 잘 될 수 있을까요?'"):
    # 사용자 메시지 화면에 표시 및 세션 저장
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 5. Gemini 챗봇 답변 생성
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        # 타로 마스터 페르소나 및 출력 형식을 정의하는 시스템 프롬프트
        system_instruction = (
            "당신은 신비롭고 통찰력 있는 베테랑 타로 마스터입니다. "
            "사용자가 고민을 이야기하면, 메이저 아르카나 카드 중에서 무작위로 3장의 카드(과거, 현재, 미래)를 뽑았다고 가정하고 이를 해석해 주어야 합니다.\n\n"
            "답변은 반드시 아래 형식을 지켜서 가독성 있게 출력해 주세요:\n"
            "1. **복채(인사말)**: 사용자의 고민에 공감하는 신비로운 인사말\n"
            "2. **타로 카드 스프레드 결과**:\n"
            "   * **과거**: [카드 이름] (정방향/역방향 표시) - 해석\n"
            "   * **현재**: [카드 이름] (정방향/역방향 표시) - 해석\n"
            "   * **미래**: [카드 이름] (정방향/역방향 표시) - 해석\n"
            "3. **종합 조언**: 3장의 카드를 종합하여 사용자의 고민에 대한 따뜻하고 현실적인 조언과 격려"
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
                    temperature=0.8, # 타로 특유의 창의적이고 풍부한 리딩을 위해 온도를 약간 올림
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
