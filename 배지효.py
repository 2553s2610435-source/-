
import streamlit as st
import pandas as pd
from datetime import datetime, date
import google.generativeai as genai

# 1. 페이지 설정
st.set_page_config(
    page_title="스마트 수행평가 알리미",
    page_icon="📅",
    layout="wide"
)

# 2. 데이터 초기화 (Session State 활용)
if "evaluations" not in st.session_state:
    # 초보자가 앱을 켰을 때 바로 확인해볼 수 있도록 예시 데이터 탑재
    st.session_state.evaluations = [
        {"subject": "국어", "title": "현대시 분석 및 비평문 쓰기", "due_date": date(2026, 6, 25), "type": "서술형 작성", "memo": "교과서 3단원 작품 위주"},
        {"subject": "수학", "title": "미적분 실생활 활용 사례 발표", "due_date": date(2026, 6, 20), "type": "발표/PPT", "memo": "PPT 5장 내외로 준비"},
        {"subject": "영어", "title": "영작문 및 에세이 제출", "due_date": date(2026, 7, 2), "type": "보고서 제출", "memo": "단어 수 300자 이상"}
    ]

# 3. Gemini AI API 설정
api_key = st.secrets.get("GEMINI_API_KEY") or st.sidebar.text_input("Gemini API Key (선택)", type="password")
ai_available = False

if api_key:
    try:
        genai.configure(api_key=api_key)
        ai_available = True
    except Exception:
        st.sidebar.error("⚠️ API Key 인증에 실패했습니다.")

# 4. 사이드바 - 대시보드 요약
st.sidebar.title("🎒 알리미 대시보드")
today = date.today()
st.sidebar.info(f"📆 오늘은 **{today.strftime('%Y년 %m월 %d일')}** 입니다.")

# 남은 수행평가 계산
total_count = len(st.session_state.evaluations)
st.sidebar.metric(label="총 남은 수행평가", value=f"{total_count}개")

if not st.secrets.get("GEMINI_API_KEY") and not api_key:
    st.sidebar.warning("💡 AI 가이드 기능을 쓰려면 사이드바나 Secrets에 GEMINI_API_KEY를 등록하세요.")

# 5. 메인 화면 타이틀
st.title("📅 학업 치트키: 스마트 수행평가 알리미")
st.write("수행평가 일정을 기록하고, AI 가이드를 받아 철저하게 대비해 보세요!")
st.markdown("---")

# 탭 구성으로 화면 분할 (깔끔한 UI 제공)
tab1, tab2, tab3 = st.tabs(["🔍 일정 및 D-Day 확인", "➕ 새 수행평가 등록", "🤖 AI 고득점 가이드"])

# ----------------- 탭 1: 일정 및 D-Day 확인 -----------------
with tab1:
    st.subheader("📋 내 수행평가 마감 일정")
    
    if total_count == 0:
        st.info("🎉 등록된 수행평가가 없습니다! 여유로운 학기를 즐기세요.")
    else:
        # 데이터 정렬 및 D-Day 계산을 위한 가공
        processed_data = []
        for item in st.session_state.evaluations:
            d_day = (item["due_date"] - today).days
            if d_day < 0:
                d_day_str = f"종료 (D+{abs(d_day)})"
                status = "⚪ 완료/만료"
            elif d_day == 0:
                d_day_str = "🚨 D-Day"
                status = "🔴 당일 마감!"
            else:
                d_day_str = f"D-{d_day}"
                status = "🟡 진행중" if d_day <= 3 else "🟢 여유"
                
            processed_data.append({
                "상태": status,
                "남은 기한": d_day_str,
                "마감일": item["due_date"].strftime("%Y-%m-%d"),
                "과목": item["subject"],
                "수행평가명": item["title"],
                "유형": item["type"],
                "메모": item["memo"],
                "days_left": d_day # 정렬용 임시 필드
            })
            
        # D-Day 임박 순서로 정렬
        df = pd.DataFrame(processed_data).sort_values(by="days_left", ascending=True)
        # 정렬용 임시 필드 삭제
        df = df.drop(columns=["days_left"])
        
        # 표 형태로 시각화
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # 삭제 기능 제공
        st.markdown("### 🛠️ 완료한 일정 삭제")
        titles = [f"[{item['subject']}] {item['title']}" for item in st.session_state.evaluations]
        delete_target = st.selectbox("삭제할 수행평가를 선택하세요", titles)
        if st.button("선택한 일정 삭제하기"):
            target_idx = titles.index(delete_target)
            st.session_state.evaluations.pop(target_idx)
            st.success("일정이 성공적으로 삭제되었습니다.")
            st.rerun()

# ----------------- 탭 2: 새 수행평가 등록 -----------------
with tab2:
    st.subheader("📝 수행평가 정보 추가하기")
    
    with st.form("evaluation_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            subject = st.text_input("📚 과목명", placeholder="예: 수학, 영어, 과학")
            title = st.text_input("📌 수행평가 제목", placeholder="예: 세포 분열 실험 보고서 제출")
        with col2:
            due_date = st.date_input("📅 마감일 선택", date.today())
            eval_type = st.selectbox("💡 수행 유형", ["보고서 제출", "발표/PPT", "서술형 작성", "실기/실험", "포트폴리오", "기타"])
            
        memo = st.text_area("✍️ 세부 내용 및 메모", placeholder="예: 준비물 가운 지참, 참고 사이트 주소 등")
        
        submit_btn = st.form_submit_button("📅 일정 추가하기")
        
        if submit_btn:
            if not subject.strip() or not title.strip():
                st.error("❌ 과목명과 수행평가 제목은 필수 입력 사항입니다.")
            else:
                new_item = {
                    "subject": subject.strip(),
                    "title": title.strip(),
                    "due_date": due_date,
                    "type": eval_type,
                    "memo": memo.strip()
                }
                st.session_state.evaluations.append(new_item)
                st.success(f"✅ '{title}' 일정이 성공적으로 등록되었습니다!")
                st.rerun()

# ----------------- 탭 3: AI 고득점 가이드 -----------------
with tab3:
    st.subheader("🤖 AI 수행평가 고득점 전략 가이드")
    st.write("등록된 수행평가를 선택하면 Gemini AI가 맞춤형 준비 팁을 제시합니다.")
    
    if total_count == 0:
        st.info("가이드를 줄 수행평가 일정이 없습니다. 먼저 일정을 등록해 주세요.")
    elif not ai_available:
        st.warning("⚠️ 이 기능을 사용하려면 사이드바 혹은 Secrets에 올바른 `GEMINI_API_KEY`를 설정해야 합니다.")
    else:
        titles = [f"[{item['subject']}] {item['title']}" for item in st.session_state.evaluations]
        selected_eval = st.selectbox("가이드를 받을 수행평가 선택", titles, key="ai_select")
        
        if st.button("🪄 AI 전략 생성하기"):
            target_idx = titles.index(selected_eval)
            target = st.session_state.evaluations[target_idx]
            
            prompt = f"""
            너는 대한민국 고등학교/중학교의 베테랑 교사이자 학업 멘토야. 
            학생이 등록한 아래 수행평가 정보를 보고, 만점을 받기 위한 [고득점 전략 정보]를 친절하고 명확하게 제공해줘.

            - 과목: {target['subject']}
            - 수행평가 주제: {target['title']}
            - 유형: {target['type']}
            - 학생의 메모: {target['memo'] if target['memo'] else '없음'}

            [답변 구조 가이드]
            1. ✨ 이 수행평가에서 가장 중요한 핵심 채점 포인트 (교사가 주로 보는 항목)
            2. 📈 구체적인 단계별 준비 로드맵 (오늘부터 마감일까지 해야 할 일)
            3. 💡 발표나 작성 시 쓰면 좋은 차별화된 꿀팁이나 추천 키워드
            
            친근하고 학생을 격려하는 어조로 이모지를 섞어가며 작성해줘.
            """
            
            with st.spinner("🤖 AI가 평가 기준을 분석하고 전략을 생성하고 있습니다..."):
                try:
                    model = genai.GenerativeModel("gemini-2.5-flash-lite")
                    response = model.generate_content(prompt)
                    
                    st.success("🎉 AI 멘토의 고득점 가이드가 완성되었습니다!")
                    st.markdown("---")
                    st.markdown(response.text)
                except Exception as e:
                    st.error("AI 서버 통신 중 에러가 발생했습니다.")
                    st.caption(f"에러 세부 정보: {str(e)}")
