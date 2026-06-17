import streamlit as st
from datetime import date, datetime

def app():
    st.title("⏳ 수행평가 D-day 알림이")
    st.write("마감일이 얼마 남지 않은 수행평가를 확인하고 미리 준비하세요!")

    # 세션 상태(Session State)를 활용해 등록된 수행평가 데이터 유지
    if 'tasks' not in st.session_state:
        st.session_state.tasks = [
            {"과목/평가명": "기술가정 수행평가", "마감일": date(2026, 7, 5)},
            {"과목/평가명": "수학 문제풀이", "마감일": date(2026, 6, 25)}
        ]

    # --- 1. 새로운 수행평가 등록 양식 ---
    st.subheader("➕ 새로운 수행평가 일정 추가")
    with st.form("task_form", clear_on_submit=True):
        task_name = st.text_input("수행평가 이름 (예: 국어 독서록 제출)")
        due_date = st.date_input("마감일 선택", min_value=date.today())
        submit_button = st.form_submit_button("일정 등록하기")
        
        if submit_button:
            if task_name:
                st.session_state.tasks.append({"과목/평가명": task_name, "마감일": due_date})
                st.success(f"'{task_name}' 일정이 성공적으로 등록되었습니다!")
            else:
                st.warning("수행평가 이름을 입력해 주세요.")

    # --- 2. D-day 목록 출력 ---
    st.subheader("📅 나의 수행평가 D-day 목록")
    
    if not st.session_state.tasks:
        st.info("등록된 수행평가 일정이 없습니다. 위에 새로 추가해 보세요!")
    else:
        today = date.today()
        
        # 마감일 순으로 정렬하기 위한 리스트 생성 및 계산
        processed_tasks = []
        for task in st.session_state.tasks:
            d_day = (task["마감일"] - today).days
            processed_tasks.append({
                "과목/평가명": task["과목/평가명"],  # <- 오타 수정 완료!
                "마감일": task["마감일"],
                "d_day": d_day
            })
            
        # D-day가 적게 남은 순(마감에 임박한 순)으로 정렬
        processed_tasks = sorted(processed_tasks, key=lambda x: x["d_day"])

        # 화면에 예쁘게 출력하기
        for task in processed_tasks:
            d_day_val = task["d_day"]
            
            # D-day 표현 방식 설정
            if d_day_val == 0:
                d_day_str = "🔥 D-Day (오늘 마감!)"
                color_box = "🔴"
            elif d_day_val < 0:
                d_day_str = f"❌ 만료 ({-d_day_val}일 지남)"
                color_box = "⚪"
            else:
                d_day_str = f"⏳ D-{d_day_val}"
                # 3일 이내로 남았으면 경고 표시
                color_box = "🚨" if d_day_val <= 3 else "🟢"

            # 텍스트 박스로 시각화
            st.info(f"{color_box} **[{d_day_str}]** {task['과목/평가명']} (마감일: {task['마감일'].strftime('%Y-%m-%d')})")

# 독립 실행 테스트를 위한 코드
if __name__ == "__main__":
    app()
