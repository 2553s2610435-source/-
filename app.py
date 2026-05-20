import streamlit as st

st.title("📚 수행평가 체크 앱")

subject = st.text_input("과목 입력")
done = st.checkbox("수행평가 완료")

if done:
    st.success(f"{subject} 수행평가 완료!")
else:
    st.warning("아직 수행평가를 하지 않았어요.")
