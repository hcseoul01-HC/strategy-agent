import streamlit as st
import os
import sys
import json
import asyncio
from dotenv import load_dotenv

load_dotenv(override=True)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from agent import root_agent

# ── 페이지 설정 ──
st.set_page_config(
    page_title="전략 분석 AI 에이전트",
    page_icon="🤖",
    layout="wide"
)

# ── 커스텀 CSS ──
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #58a6ff, #f0c040);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .report-card {
        background: #1a2740;
        border: 1px solid #2a4060;
        border-left: 4px solid #58a6ff;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 0.8rem 0;
    }
    .report-card h4 { color: #f0c040 !important; font-size: 0.85rem; margin-bottom: 0.5rem; }
    .report-card p { color: #ffffff !important; line-height: 1.7; }
    .memory-card {
        background: #1a2540;
        border-left: 3px solid #58a6ff;
        border-radius: 0 8px 8px 0;
        padding: 0.6rem 0.8rem;
        margin: 0.4rem 0;
        font-size: 0.78rem;
    }
</style>
""", unsafe_allow_html=True)

# ── 사이드바 ──
with st.sidebar:
    st.markdown("### 📁 문서 업로드")
    uploaded_files = st.file_uploader(
        "PDF 파일을 업로드하세요",
        type=['pdf'],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )

    if uploaded_files:
        doc_dir = os.path.join(os.path.dirname(__file__), "documents")
        os.makedirs(doc_dir, exist_ok=True)
        for f in uploaded_files:
            with open(os.path.join(doc_dir, f.name), "wb") as out:
                out.write(f.read())
        st.success(f"✅ {len(uploaded_files)}개 파일 업로드 완료!")
        for f in uploaded_files:
            st.caption(f"📄 {f.name}")

    st.divider()

    # 이전 메모리
    st.markdown("### 🧠 이전 분석 기록")
    memory_file = os.path.join(os.path.dirname(__file__), "agent_memory.json")
    if os.path.exists(memory_file):
        with open(memory_file, 'r', encoding='utf-8') as f:
            memory = json.load(f)
        for m in memory[-3:]:
            st.markdown(f"""
            <div class="memory-card">
                <strong>📌 {m['timestamp']}</strong><br>
                {m['content'][:120]}...
            </div>
            """, unsafe_allow_html=True)
    else:
        st.caption("아직 분석 기록이 없습니다.")

    st.divider()
    st.caption("🤖 멀티 에이전트 시스템 v1.0")
    st.caption("analyst · writer · delivery")

# ── 메인 화면 ──
st.markdown('<div class="main-title">🤖 전략 분석 AI 에이전트</div>', unsafe_allow_html=True)
st.caption("PDF 문서를 업로드하면 멀티 에이전트가 전략 보고서를 자동 작성합니다.")
st.divider()

# 입력 영역
user_input = st.text_area(
    "💬 분석 요청",
    placeholder="예: documents 폴더의 문서를 분석해서 전략 보고서를 작성해줘",
    height=110,
    label_visibility="collapsed"
)

col1, col2, col3 = st.columns([2, 2, 6])
with col1:
    run_btn = st.button("🚀 분석 시작", type="primary", use_container_width=True)
with col2:
    if st.button("🗑️ 기록 초기화", use_container_width=True):
        if os.path.exists(memory_file):
            os.remove(memory_file)
            st.success("기록이 초기화되었습니다.")

# ── 에이전트 실행 ──
if run_btn and user_input:
    with st.spinner("🤖 멀티 에이전트 분석 중... (1~2분 소요)"):
        try:
            async def run_agent():
                session_service = InMemorySessionService()
                runner = Runner(
                    agent=root_agent,
                    app_name="strategy_app",
                    session_service=session_service
                )
                session = await session_service.create_session(
                    app_name="strategy_app",
                    user_id="user"
                )
                message = types.Content(
                    role='user',
                    parts=[types.Part(text=user_input)]
                )
                result_text = ""
                async for event in runner.run_async(
                    user_id="user",
                    session_id=session.id,
                    new_message=message
                ):
                    if hasattr(event, 'content') and event.content:
                        for part in event.content.parts:
                            if hasattr(part, 'text') and part.text:
                                result_text += part.text
                return result_text

            result_text = asyncio.run(run_agent())

            if result_text:
                st.success("✅ 분석 완료! 이메일로도 전송되었습니다.")
                st.divider()

                # 보고서 항목별 카드 표시
                report_sections = {
                    "🔍 hard_truth": "냉혹한 현실 진단",
                    "💼 current_identity": "핵심 가치 & 비즈니스 모델",
                    "⚠️ primary_constraint": "핵심 병목 구간",
                    "⚡ leverage_point": "최대 효과 지점",
                    "🏗️ the_system": "구축해야 할 시스템",
                    "📅 operating_plan_90_day": "90일 실행 계획",
                    "✅ final_assignment": "지금 당장 할 과제"
                }

                st.markdown("### 📊 전략 보고서")

                # JSON 파싱 시도
                try:
                    import re
                    json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
                    if json_match:
                        report_data = json.loads(json_match.group())
                        for key, label in report_sections.items():
                            field = key.split(" ")[1]
                            if field in report_data:
                                st.markdown(f"""
                                <div class="report-card">
                                    <h4>{key} · {label}</h4>
                                    <p>{report_data[field]}</p>
                                </div>
                                """, unsafe_allow_html=True)
                    else:
                        st.markdown(result_text)
                except:
                    st.markdown(result_text)

                st.divider()
                st.download_button(
                    label="📥 보고서 다운로드 (.txt)",
                    data=result_text.encode('utf-8'),
                    file_name="strategy_report.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            else:
                st.warning("결과를 가져오지 못했습니다. 다시 시도해주세요.")

        except Exception as e:
            st.error(f"오류 발생: {e}")

elif run_btn and not user_input:
    st.warning("⚠️ 분석 요청을 입력해주세요.")