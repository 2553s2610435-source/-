import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# 1. 페이지 설정 및 디자인
st.set_page_config(page_title="EduScan | 수행평가 비서", page_icon="📅", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 10px; background-color: #4A90E2; color: white; font-weight: bold; }
    .result-card { padding: 20px; border-radius: 15px; background-color: white; border: 1px solid #e0e0e0; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# 2. 세션 상태 초기화 (페이지 이동 시 데이터 유지)
if "eval_result" not in st.session_state:
    st.session_state.eval_result = None
if "img_data" not in st.session_state:
    st.session_state.img_data = None

# 3. API 키 설정 (Secrets 보안 연결)
try:
    # Streamlit Cloud의 Secrets에서 GEMINI_API_KEY를 가져옵니다.
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
except Exception:
    st.error("⚠️ Secrets 설정에서 'GEMINI_API_KEY'를 등록해주세요.")
    st.stop()

# 4. 사이드바 메뉴 (간단하고 안전한 페이지 전환)
st.sidebar.title("🚀 EduScan")
page = st.sidebar.radio("메뉴", ["📸 사진 분석하기", "📊 정리된 내용 보기"])

# --- [페이지 1] 사진 분석하기 ---
if page == "📸 사진 분석하기":
    st.title("📸 수행평가 안내문 분석")
    st.write("안내문 사진을 올리면 AI가 핵심 내용을 표와 리스트로 정리합니다.")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("1. 사진 업로드")
        uploaded_file = st.file_uploader("수행평가 이미지 선택", type=["jpg", "jpeg", "png"])
        if uploaded_file:
            st.session_state.img_data = uploaded_file.read()
            st.image(st.session_state.img_data, caption="업로드 완료", use_container_width=True)

    with col2:
        st.subheader("2. AI 스캔")
        if st.session_state.img_data:
            if st.button("🪄 분석 시작 (Gemini 2.5 Flash)"):
                with st.spinner("이미지를 읽고 정리 중..."):
                    try:
                        # 이미지 처리
                        img = Image.open(io.BytesIO(st.session_state.img_data))
                        model = genai.GenerativeModel('gemini-2.5-flash-lite')
                        
                        # 프롬프트 설정
                        prompt = "이 사진에서 수행평가 정보를 추출해서 1.과목/평가명, 2.제출 기한, 3.주요 과제 내용, 4.주의사항(감점요인), 5.점수 비중을 나누어 아주 깔끔한 마크다운 형식으로 정리해줘."
                        
                        response = model.generate_content([prompt, img])
                        st.session_state.eval_result = response.text
                        st.success("✅ 분석 완료! '정리된 내용 보기' 메뉴로 이동해 보세요.")
                        st.markdown(st.session_state.eval_result)
                    except Exception as e:
                        st.error(f"분석 중 오류 발생: {e}")
        else:
            st.info("왼쪽에서 사진을 먼저 업로드해 주세요.")

# --- [페이지 2] 정리된 내용 보기 ---
elif page == "📊 정리된 내용 보기":
    st.title("📊 수행평가 요약 리포트")

    if st.session_state.eval_result:
        st.info("💡 아래 내용은 마우스로 드래그하여 복사할 수 있습니다.")
        
        # 가독성을 위한 레이아웃
        res_col, img_col = st.columns([1.2, 0.8])
        
        with res_col:
            st.markdown("### 📝 정리 결과")
            # 결과창을 카드 형태로 출력
            st.markdown(f'<div class="result-card">{st.session_state.eval_result}</div>', unsafe_allow_html=True)
            
            if st.button("🔄 다시 분석하러 가기"):
                st.session_state.eval_result = None
                st.rerun()

        with img_col:
            st.markdown("### 🖼️ 원본 확인")
            if st.session_state.img_data:
                st.image(st.session_state.img_data, use_container_width=True)
    else:
        st.warning("아직 분석된 내용이 없습니다. '📸 사진 분석하기' 메뉴에서 사진을 먼저 올려주세요.")
