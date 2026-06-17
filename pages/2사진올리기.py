import streamlit as st
import google.generativeai as genai
import io

# 1. 페이지 및 스타일 설정
st.set_page_config(page_title="EduScan | 수행평가 비서", page_icon="📅", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #4A90E2; color: white; }
    .status-box { padding: 20px; border-radius: 10px; background-color: #ffffff; border: 1px solid #e0e0e0; }
    </style>
    """, unsafe_allow_html=True)

# 2. 세션 상태 초기화 (페이지 간 데이터 유지)
if "eval_data" not in st.session_state:
    st.session_state.eval_data = None
if "uploaded_img_bytes" not in st.session_state:
    st.session_state.uploaded_img_bytes = None

# 3. API 설정 (Secrets 안전하게 가져오기)
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
except Exception:
    st.error("🔑 Streamlit Cloud 설정에서 GEMINI_API_KEY를 입력해주세요!")
    st.stop()

# 4. 사이드바 메뉴 전환
st.sidebar.title("🚀 EduScan")
menu = st.sidebar.selectbox("메뉴 선택", ["📸 사진 업로드 및 분석", "📊 정리된 대시보드"])

# --- 페이지 1: 업로드 및 분석 ---
if menu == "📸 사진 업로드 및 분석":
    st.title("📸 수행평가 안내문 스캔")
    st.write("안내문 사진을 올리면 AI가 일정을 정리해 드립니다.")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        uploaded_file = st.file_uploader("수행평가 사진 업로드", type=["jpg", "jpeg", "png"])
        if uploaded_file:
            # 바이트 데이터로 읽어서 세션에 보관
            st.session_state.uploaded_img_bytes = uploaded_file.read()
            st.image(st.session_state.uploaded_img_bytes, caption="업로드된 안내문", use_container_width=True)

    with col2:
        if st.session_state.uploaded_img_bytes:
            if st.button("🪄 AI 분석 시작"):
                with st.spinner("이미지를 분석하고 있습니다..."):
                    try:
                        # 이미지를 Gemini가 인식할 수 있는 형태로 변환
                        from PIL import Image
                        image = Image.open(io.BytesIO(st.session_state.uploaded_img_bytes))
                        
                        # gemini-2.5-flash-lite 모델 호출
                        model = genai.GenerativeModel('gemini-2.5-flash-lite')
                        
                        prompt = "이 수행평가 안내문을 분석해서 '1.과목명/평가명, 2.마감 기한, 3.주요 평가 내용, 4.감점 주의사항, 5.배점 비중' 항목으로 나누어 아주 깔끔하게 정리해줘."
                        response = model.generate_content([prompt, image])
                        
                        # 결과를 세션에 저장
                        st.session_state.eval_data = response.text
                        st.success("✅ 분석 완료! '정리된 대시보드' 페이지에서 확인하세요.")
                        st.markdown(st.session_state.eval_data)
                    except Exception as e:
                        st.error(f"분석 중 오류 발생: {e}")
        else:
            st.warning("먼저 사진을 업로드해 주세요.")

# --- 페이지 2: 대시보드 ---
elif menu == "📊 정리된 대시보드":
    st.title("📊 수행평가 요약 대시보드")
    
    if st.session_state.eval_data:
        col_a, col_b = st.columns([1, 1])
        
        with col_a:
            st.subheader("📝 정리된 내용")
            st.markdown(f'<div class="status-box">{st.session_state.eval_data}</div>', unsafe_allow_html=True)
            st.caption("💡 텍스트를 마우스로 드래그하여 복사할 수 있습니다.")
        
        with col_b:
            st.subheader("🖼️ 원본 안내문")
            if st.session_state.uploaded_img_bytes:
                st.image(st.session_state.uploaded_img_bytes, use_container_width=True)
    else:
        st.info("아직 분석된 데이터가 없습니다. '📸 사진 업로드 및 분석' 페이지에서 먼저 분석을 진행해 주세요.")
