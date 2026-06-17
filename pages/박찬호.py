import streamlit as st
from PIL import Image
import google.generativeai as genai
import os

st.set_page_config(page_title="수행평가 사진 분석기", page_icon="🔍")

# 구글 Gemini API 키 설정 확인
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
elif os.getenv("GEMINI_API_KEY"):
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
else:
    st.sidebar.warning("⚠️ GEMINI_API_KEY를 설정해주세요.")
    user_api_key = st.sidebar.text_input("Gemini API Key 입력:", type="password")
    if user_api_key:
        genai.configure(api_key=user_api_key)

st.title("🔍 수행평가 안내문 사진 분석")

uploaded_file = st.file_uploader("수행평가 사진을 올려주세요", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="업로드된 사진", use_container_width=True)
    
    if st.button("🚀 사진 분석 시작"):
        with st.spinner("구글 AI가 분석 중입니다..."):
            try:
                # 텍스트와 이미지 분석에 최적화된 무료 지원 모델
                model = genai.GenerativeModel('gemini-1.5-flash-latest')
                prompt = "제공된 수행평가 사진을 분석해서 제목, 일정, 핵심 평가 조건, 준비사항을 한국어로 깔끔하게 정리해줘."
                
                response = model.generate_content([prompt, image])
                st.success("✅ 분석 완료!")
                st.divider()
                st.markdown(response.text)
            except Exception as e:
                st.error(f"분석 중 오류가 발생했습니다: {e}")
