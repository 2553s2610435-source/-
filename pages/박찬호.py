import streamlit as st
from PIL import Image
import openai
import os
import base64

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="수행평가 가이드 & 분석기",
    page_icon="📝",
    layout="centered"
)

# 2. OpenAI API 키 설정
if "OPENAI_API_KEY" in st.secrets:
    openai.api_key = st.secrets["OPENAI_API_KEY"]
elif os.getenv("OPENAI_API_KEY"):
    openai.api_key = os.getenv("OPENAI_API_KEY")
else:
    st.sidebar.warning("⚠️ OpenAI API 키가 설정되지 않았습니다. 사이드바에 입력하거나 Streamlit Secrets를 설정해주세요.")
    user_api_key = st.sidebar.text_input("OpenAI API Key 입력:", type="password")
    if user_api_key:
        openai.api_key = user_api_key

# 3. 앱 타이틀 및 소개
st.title("📝 수행평가 안내 & 사진 분석기")
st.markdown("""
이 앱은 학교 수행평가 안내문을 확인하고, **수행평가 지침이나 조건이 담긴 사진을 업로드하면 AI가 핵심 내용을 분석**해주는 서비스입니다.
""")

# Streamlit 내에서 화면 구분선을 그을 때는 이렇게 함수를 써야 합니다.
st.divider()

# 4. 탭 구성 (안내문 vs 사진 분석)
tab1, tab2 = st.tabs(["📢 수행평가 기본 안내", "🔍 안내문 사진 분석하기"])

with tab1:
    st.header("📌 이번 학기 수행평가 핵심 요약")
    
    st.markdown("""
    ### 1. 국어과 - 독서 논술 평가
    * **일정:** 14주차 (자세한 날짜는 추후 공지)
    * **배점:** 20%
    * **준비물:** 지정 도서 (*자기만의 방*), 필기구
    
    ### 2. 수학과 - 문제 풀이 및 개념 설명
    * **일정:** 10주차 수업 시간 중
    * **배점:** 15%
    * **평가 요소:** 조건에 맞는 풀이 과정 기술 및 오류 수정 능력
    """)
    
    st.info("💡 세부 일정 및 평가 기준은 학교 사정에 따라 변경될 수 있으니 반드시 교과 선생님 공지를 우선으로 확인하세요.")

with tab2:
    st.header("📸 수행평가 사진 분석")
    st.write("선생님이 나눠주신 수행평가 평가지나 칠판의 안내문 사진을 업로드해보세요. AI가 핵심 조건과 일정을 정리해 드립니다.")
    
    uploaded_file = st.file_uploader("수행평가 안내 이미지 업로드 (jpg, jpeg, png)", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption='업로드된 수행평가 안내문', use_column_width=True)
        
        if st.button("🚀 사진 분석 시작"):
            if not openai.api_key:
                st.error("OpenAI API 키가 필요합니다. 사이드바를 확인해주세요.")
            else:
                with st.spinner("AI가 수행평가 안내문을 분석하고 있습니다... 잠시만 기다려주세요."):
                    try:
                        uploaded_file.seek(0)
                        encoded_image = base64.b64encode(uploaded_file.read()).decode('utf-8')
                        
                        client = openai.OpenAI(api_key=openai.api_key)
                        response = client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[
                                {
                                    "role": "user",
                                    "content": [
                                        {
                                            "type": "text", 
                                            "text": (
                                                "너는 학생들의 수행평가 준비를 돕는 친절한 AI 매니저야. "
                                                "제공된 수행평가 안내문 사진을 분석해서 아래 템플릿에 맞춰 한국어로 깔끔하게 정리해줘.\n\n"
                                                "1. **수행평가 제목 및 과목**:\n"
                                                "2. **중요 일정 및 마감 기한**:\n"
                                                "3. **핵심 평가 조건/감점 요인 (리스트 형태로)**:\n"
                                                "4. **학생들이 놓치기 쉬운 꿀팁/준비사항**:"
                                            )
                                        },
                                        {
                                            "type": "image_url",
                                            "image_url": {
                                                "url": f"data:image/jpeg;base64,{encoded_image}"
                                            }
                                        }
                                    ]
                                }
                            ],
                            max_tokens=1000
                        )
                        
                        analysis_result = response.choices[0].message.content
                        st.success("✨ 분석이 완료되었습니다!")
                        st.divider()
                        st.markdown(analysis_result)
                        
                    except Exception as e:
                        st.error(f"분석 중 오류가 발생했습니다: {e}")
