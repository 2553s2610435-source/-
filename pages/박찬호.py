import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="수행평가 가이드 홈",
    page_icon="📢",
    layout="centered"
)

st.title("📝 우리 반 수행평가 안내소")
st.markdown("""
안녕하세요! 이번 학기 수행평가 일정을 확인하고 준비할 수 있는 공간입니다.
지침을 꼼꼼히 확인하여 좋은 성적을 거두길 바랍니다. 💯
""")

st.divider()

st.header("📌 이번 주 주요 수행평가 요약")

# 예시 데이터입니다. 학교 상황에 맞게 텍스트를 자유롭게 수정하세요.
col1, col2 = st.columns(2)

with col1:
    st.subheader("📚 국어 (독서 논술)")
    st.markdown("""
    * **일정:** 14주차 금요일
    * **배점:** 20%
    * **준비물:** 지정 도서, 필기구
    """)

with col2:
    st.subheader("📐 수학 (개념 설명)")
    st.markdown("""
    * **일정:** 10주차 수업 시간
    * **배점:** 15%
    * **평가 내용:** 조건에 맞는 풀이 과정 기술
    """)

st.info("💡 더 자세한 채점 기준이나 안내문 양식이 있다면 왼쪽 사이드바에서 **[사진 분석하기]** 메뉴로 이동해 사진을 업로드해 보세요!")
