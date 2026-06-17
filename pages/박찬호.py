import streamlit as st
from PIL import Image
import pytesseract
import re

st.set_page_config(
    page_title="수행평가 안내 분석기",
    page_icon="📚",
    layout="wide"
)

st.title("📚 수행평가 안내 분석기")

st.write(
    """
    수행평가 안내문 사진을 업로드하면
    내용을 분석하여 요약 및 체크리스트를 생성합니다.
    """
)

uploaded_file = st.file_uploader(
    "수행평가 안내 사진 업로드",
    type=["png", "jpg", "jpeg"]
)

def extract_info(text):
    result = {
        "과목": "확인 불가",
        "제출일": "확인 불가",
        "제목": "확인 불가"
    }

    date_pattern = r"\d{4}[./-]\d{1,2}[./-]\d{1,2}|\d{1,2}[./-]\d{1,2}"

    date_match = re.search(date_pattern, text)
    if date_match:
        result["제출일"] = date_match.group()

    lines = [line.strip() for line in text.split("\n") if line.strip()]

    if len(lines) > 0:
        result["제목"] = lines[0]

    subjects = [
        "국어", "영어", "수학", "과학",
        "사회", "역사", "정보", "기술가정",
        "음악", "미술"
    ]

    for subject in subjects:
        if subject in text:
            result["과목"] = subject
            break

    return result

if uploaded_file:
    image = Image.open(uploaded_file)

    st.image(
        image,
        caption="업로드한 수행평가 안내",
        use_container_width=True
    )

    with st.spinner("분석 중..."):
        try:
            text = pytesseract.image_to_string(image, lang="kor+eng")

            st.subheader("📄 추출된 텍스트")

            if text.strip():
                st.text_area(
                    "OCR 결과",
                    text,
                    height=250
                )

                info = extract_info(text)

                st.subheader("🔍 분석 결과")

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("과목", info["과목"])

                with col2:
                    st.metric("제출일", info["제출일"])

                with col3:
                    st.metric("제목", info["제목"])

                st.subheader("📝 요약")

                summary = text[:500]

                st.info(summary)

                st.subheader("✅ 해야 할 일")

                checklist = []

                if info["제출일"] != "확인 불가":
                    checklist.append(
                        f"제출일({info['제출일']}) 확인하기"
                    )

                checklist.extend([
                    "수행평가 주제 확인",
                    "준비물 확인",
                    "평가 기준 확인",
                    "제출 방식 확인"
                ])

                for item in checklist:
                    st.checkbox(item)

            else:
                st.warning("텍스트를 인식하지 못했습니다.")

        except Exception as e:
            st.error(f"오류 발생: {e}")
