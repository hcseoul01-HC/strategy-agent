import os
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from analyst_agent import analyst_agent
from writer_agent import writer_agent
from delivery_agent import delivery_agent

load_dotenv(override=True)

root_agent = LlmAgent(
    model='gemini-2.5-flash',
    name='orchestrator',
    sub_agents=[analyst_agent, writer_agent, delivery_agent],
    instruction="""
    당신은 전략 분석 팀의 총괄 오케스트레이터입니다.
    사용자의 요청을 받으면 아래 순서로 팀을 지휘하십시오.

    1. analyst_agent  → 문서 분석 담당
    2. writer_agent   → 보고서 작성 담당
    3. delivery_agent → 저장 + 메모리 + 이메일 담당

    각 에이전트의 결과를 다음 에이전트에게 전달하며 순서대로 진행하십시오.
    모든 답변은 한국어로 작성하십시오.
    """
)
