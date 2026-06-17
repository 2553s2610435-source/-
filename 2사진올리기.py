import streamlit as st
from google import genai
from google.genai import types

# 1. 페이지 설정
st.set_page_config(
    page_title="EduScan | 수행평가 비서",
    page_icon="📅",
    layout="wide"
)

# 2. 스타일 설정 (커스텀 CSS)
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #4A90E2; color: white; }
    .status-box { padding: 20px; border-radius: 10px; background-color: #ffffff; border: 1px solid #e0e0e0; }
    </style>
    """, unsafe_allow_html=True)

# 3. 세션 상태 초기화 (데이터 저장소)
if "eval_data" not in st.session_state:
    st.session_state.eval_data = None  # AI 분석 결과 저장
if "uploaded_img" not in st.session_state:
    st.session_state.uploaded_img = None  # 업로드 이미지 저장

# 4. API 설정 (Secrets 사용)
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=API_KEY)
except Exception:
    st.error("🔑 API 키를 설정해주세요. (Secrets에 GEMINI_API_KEY 필요)")
    st.stop()

# 5. 사이드바 내비게이션
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
            st.session_state.uploaded_img = uploaded_file.read()
            st.image(st.session_state.uploaded_img, caption="업로드된 안내문", use_container_width=True)

    with col2:
        if st.session_state.uploaded_img:
            if st.button("🪄 AI 분석 시작"):
                with st.spinner("이미지를 분석하고 있습니다..."):
                    try:
                        # Gemini 2.5 Flash-Lite 호출
                        response = client.models.generate_content(
                            model="gemini-2.5-flash-lite",
                            contents=[
                                types.Part.from_bytes(data=st.session_state.uploaded_img, mime_type="image/jpeg"),
                                "이 수행평가 안내문을 분석해서 '1.과목명/평가명, 2.마감 기한, 3.주요 평가 내용, 4.감점 주의사항, 5.배점 비중' 항목으로 나누어 아주 깔끔하게 정리해줘."
                            ]
                        )
                        st.session_state.eval_data = response.text
                        st.success("✅ 분석 완료! '정리된 대시보드' 페이지에서 확인하세요.")
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
            st.markdown(f"""
            <div class="status-box">
                {st.session_state.eval_data}
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("📋 텍스트 복사하기"):
                st.write("위 텍스트를 드래그하여 복사하세요!")
        
        with col_b:
            st.subheader("🖼️ 원본 안내문")
            if st.session_state.uploaded_img:
                st.image(st.session_state.uploaded_img, use_container_width=True)
    else:
        st.info("아직 분석된 데이터가 없습니다. 첫 번째 페이지에서 사진을 분석해 주세요.")
        if st.button("홈으로 이동"):
            st.query_params["menu"] = "📸 사진 업로드 및 분석" # 쿼리 파라미터는 배포 환경에 따라 다를 수 있음
