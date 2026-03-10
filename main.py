import asyncio
import os
from google.adk.agents.llm_agent import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part
from google.genai import types 
# 1. 플래너 부품 가져오기 [cite: 539, 810]
from google.adk.planners import BuiltInPlanner 

os.environ["GOOGLE_API_KEY"] = "AIzaSyCUfkhdVi_TNsV_PCazCRQrKLlbNx-B2aI"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "0"

# 2. 에이전트 설정: BuiltInPlanner 장착 [cite: 540-541, 812]
alpha_hui_thinker = Agent(
    model='gemini-2.5-flash',
    name='strategic_solar_expert',
    description='복합적인 추론과 계획을 통해 최적의 태양광 솔루션을 제시합니다.',
    instruction="""당신은 전략적 에너지 솔루션 전문가입니다. 
    복잡한 질문을 받으면 문제를 분석하고, 대안을 검토한 뒤, 체계적인 로드맵을 제시하세요.""",
    
    # [핵심] 플래너 설정: 사고 과정을 보여주고 1024 토큰의 예산을 할당합니다. [cite: 542-544, 828-831]
    planner=BuiltInPlanner(
        thinking_config=types.ThinkingConfig(
            include_thoughts=True,  # 에이전트의 머릿속(사고 과정)을 출력합니다. [cite: 543, 829]
            thinking_budget=1024    # 깊이 있는 사고를 위해 토큰 예산을 잡습니다. [cite: 544, 829]
        )
    )
)

async def run_planning_app():
    session_service = InMemorySessionService()
    runner = Runner(agent=alpha_hui_thinker, app_name="solar_planning_app", session_service=session_service)
    
    USER_ID = "choi_hui"
    SESSION_ID = "plan_test_01"
    await session_service.create_session(app_name="solar_planning_app", user_id=USER_ID, session_id=SESSION_ID)
    
    # 3. 테스트용 복합 질문 [cite: 485-488]
    user_query = "남양주시에 위치한 60평 단독주택인데, 태양광 설치비용을 2년 안에 회수하려면 어떤 전략을 세워야 할까?"
    print(f"\n[나]: {user_query}")
    
    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=SESSION_ID,
        new_message=Content(role="user", parts=[Part(text=user_query)])
    ):
        if event.is_final_response() and event.content:
            # 4. 결과 출력 (사고 과정이 먼저 나오고 최종 답변이 나옵니다) [cite: 588, 794-797]
            print(f"\n[알파 휘의 사고 및 답변]:\n{event.content.parts[0].text}")

if __name__ == "__main__":
    asyncio.run(run_planning_app())