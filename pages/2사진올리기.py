import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# 1. 페이지 제목 및 레이아웃 설정
st.set_page_config(page_title="EduScan | 수행평가 비서", page_icon="📅", layout="wide")

# 2. 가독성을 높이기 위한 화면 디자인(CSS)
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 10px; background-color: #4A90E2; color: white; font-weight: bold; height: 3em; }
    .result-card { padding: 25px; border-radius: 15px; background-color: white; border: 1px solid #e0e0e0; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); font-size: 16px; line-height: 1.6; }
    </style>
    """, unsafe_allow_html=True)

# 3. 세션 상태 초기화 (페이지를 넘나들어도 사진과 분석 결과가 지워지지 않음)
if "eval_result" not in st.session_state:
    st.session_state.eval_result = None
if "img_data" not in st.session_state:
    st.session_state.img_data = None

# 4. API 키 보안 연결 (Streamlit Cloud Secrets)
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
except Exception:
    st.error("⚠️ Streamlit Cloud의 [Settings] -> [Secrets]에서 'GEMINI_API_KEY'를 등록해주세요!")
    st.stop()

# 5. 사이드바 내비게이션 (에러 없는 멀티 페이지 구현)
st.sidebar.title("🚀 EduScan 메뉴")
page = st.sidebar.radio("페이지 이동", ["📸 1. 사진 업로드 및 분석", "📊 2. 정리된 내용 보기"])

# --- [페이지 1] 사진 업로드 및 분석 ---
if page == "📸 1. 사진 업로드 및 분석":
    st.title("📸 수행평가 안내문 분석")
    st.write("학교에서 받은 수행평가 안내문 사진을 올리면 AI가 핵심 내용을 요약해 줍니다.")
    st.divider()

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📋 안내문 사진 올리기")
        uploaded_file = st.file_uploader("이미지 파일 선택 (jpg, jpeg, png)", type=["jpg", "jpeg", "png"])
        if uploaded_file:
            st.session_state.img_data = uploaded_file.read()
            st.image(st.session_state.img_data, caption="업로드된 안내문", use_container_width=True)

    with col2:
        st.subheader("🪄 AI 스캔 실행")
        if st.session_state.img_data:
            if st.button("수행평가 내용 요약하기 (Gemini 2.5 Flash)"):
                with st.spinner("AI가 이미지를 정밀 분석하는 중입니다..."):
                    try:
                        # 바이트 데이터를 이미지 객체로 변환
                        img = Image.open(io.BytesIO(st.session_state.img_data))
                        model = genai.GenerativeModel('gemini-2.5-flash-lite')
                        
                        # 프롬프트 설정
                        prompt = (
                            "이 사진에서 수행평가 정보를 추출해서 "
                            "1. 과목/평가명, 2. 제출 기한, 3. 주요 과제 내용, 4. 주의사항(감점요인), 5. 점수 비중 "
                            "항목을 나누어 가독성이 뛰어난 마크다운 형식으로 보기 좋게 정리해줘."
                        )
                        
                        response = model.generate_content([prompt, img])
                        
                        # 결과를 세션에 저장
                        st.session_state.eval_result = response.text
                        st.success("✅ 분석 성공! 왼쪽 메뉴에서 '📊 2. 정리된 내용 보기'를 누르면 상시 보관됩니다.")
                        st.markdown(st.session_state.eval_result)
                        
                    except Exception as e:
                        st.error(f"분석 중 오류가 발생했습니다: {e}")
        else:
            st.info("💡 왼쪽 화면에서 수행평가 안내 사진을 먼저 업로드해 주세요.")

# --- [페이지 2] 정리된 내용 보기 ---
elif page == "📊 2. 정리된 내용 보기":
    st.title("📊 수행평가 요약 리포트")
    st.write("첫 번째 페이지에서 분석한 결과와 원본 사진이 안전하게 보관되는 페이지입니다.")
    st.divider()

    if st.session_state.eval_result:
        st.info("💡 아래 요약 내용은 마우스로 드래그하여 자유롭게 복사(Ctrl+C)할 수 있습니다.")
        
        res_col, img_col = st.columns([1.2, 0.8])
        
        with res_col:
            st.markdown("### 📝 AI 분석 요약본")
            # 깔끔한 카드 디자인 안에 결과 출력
            st.markdown(f'<div class="result-card">{st.session_state.eval_result}</div>', unsafe_allow_html=True)
            
            if st.button("🔄 처음부터 다시 분석하기"):
                st.session_state.eval_result = None
                st.session_state.img_data = None
                st.rerun()

        with img_col:
            st.markdown("### 🖼️ 원본 안내문 확인")
            if st.session_state.img_data:
                st.image(st.session_state.img_data, use_container_width=True)
    else:
        st.warning("🧐 아직 분석된 내용이 없습니다. '📸 1. 사진 업로드 및 분석' 페이지에서 먼저 분석을 진행해 주세요.")
