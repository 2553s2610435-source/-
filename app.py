import streamlit as cls
import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
import io

# 1. 페이지 설정 및 API 키 초기화
st.set_page_config(page_title="수행평가 가이드 챗봇", page_icon="📝", layout="centered")
st.title("📝 수행평가 안내 로봇")
st.caption("수행평가 안내 사진을 업로드하면 일정, 내용, 안내사항을 깔끔하게 정리해 드립니다!")

# 제공해주신 API 키 설정
GEMINI_API_KEY = "AIzaSyDEIuvWZ9nMxng6o62qY45rbAAZcs0eezw"

try:
    # Google GenAI SDK 클라이언트 초기화
    client = genai.Client(api_key=GEMINI_API_KEY)
except Exception as e:
    st.error(f"API 클라이언트 초기화 중 오류가 발생했습니다: {e}")

# 2. 세션 상태(Session State) 초기화 (채팅 기록 및 업로드 이미지 유지)
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "안녕하세요! 수행평가 안내문 사진을 업로드하신 뒤 필요한 내용을 물어보세요."}
    ]

if "uploaded_image_bytes" not in st.session_state:
    st.session_state.uploaded_image_bytes = None

# 3. 사이드바 - 이미지 업로드 처리
with st.sidebar:
    st.header("📸 이미지 업로드")
    uploaded_file = st.file_uploader("수행평가 안내 사진을 선택하세요", type=["png", "jpg", "jpeg"])
    
    if uploaded_file is not None:
        # 이미지를 바이트 데이터로 읽어서 세션에 저장
        img_bytes = uploaded_file.read()
        st.session_state.uploaded_image_bytes = img_bytes
        
        # 사이드바에 미리보기 표시
        image = Image.open(io.BytesIO(img_bytes))
        st.image(image, caption="업로드된 수행평가 안내문", use_container_width=True)
        st.success("이미지가 성공적으로 로드되었습니다! 이제 채팅창에 질문을 입력하세요.")
    else:
        # 파일이 비워지면 세션 데이터도 초기화
        st.session_state.uploaded_image_bytes = None

# 4. 기존 채팅 기록 출력
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. 사용자 입력 및 챗봇 답변 처리
if user_input := st.chat_input("예: 이 수행평가의 일정과 주요 내용을 요약해줘."):
    
    # 사용자 메시지 화면 표시 및 저장
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # 챗봇 응답 생성
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("🔍 이미지를 분석하고 답변을 생성하는 중입니다...")
        
        try:
            # 기본 프롬프트 설정 (수행평가 분석에 최적화)
            system_instruction = (
                "당신은 학생들의 수행평가 안내문을 분석하고 정리해주는 스마트한 AI 조수입니다. "
                "사용자가 사진을 제공하면, 해당 사진에서 '일정(기한)', '평가 내용', '주의사항/안내사항'을 "
                "구분하여 가독성 좋고 깔끔하게 정리해 주어야 합니다."
            )
            
            # API 요청 콘텐츠 준비
            contents = []
            
            # 업로드된 이미지가 있으면 콘텐츠에 포함 (멀티모달)
            if st.session_state.uploaded_image_bytes:
                contents.append(
                    types.Part.from_bytes(
                        data=st.session_state.uploaded_image_bytes,
                        mime_type="image/jpeg"
                    )
                )
            
            # 사용자의 질문 추가
            contents.append(user_input)
            
            # gemini-2.5-flash-lite 모델 호출
            response = client.models.generate_content(
                model="gemini-2.5-flash-lite",
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.3, # 답변의 일관성을 위해 다소 낮게 설정
                )
            )
            
            # 결과 출력 및 저장
            ai_response = response.text
            message_placeholder.markdown(ai_response)
            st.session_state.messages.append({"role": "assistant", "content": ai_response})
            
        except Exception as e:
            # 상세한 오류 처리
            error_msg = f"❌ 답변을 생성하는 동안 오류가 발생했습니다.\n\n**오류 내용:** {str(e)}"
            message_placeholder.markdown(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
