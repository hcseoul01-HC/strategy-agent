from google.adk.agents import LlmAgent
from pydantic import BaseModel, Field

class StrategicReport(BaseModel):
    hard_truth: str = Field(description="데이터에 근거한 가장 냉혹하고 객관적인 현실 진단")
    current_identity: str = Field(description="분석된 계획의 핵심 가치와 비즈니스 모델")
    primary_constraint: str = Field(description="목표 달성을 가로막는 가장 큰 병목 구간")
    leverage_point: str = Field(description="최소의 노력으로 최대 효과를 낼 수 있는 핵심 지점")
    the_system: str = Field(description="지속 가능한 운영을 위해 구축해야 할 시스템")
    operating_plan_90_day: str = Field(description="향후 3개월간의 구체적인 실행 우선순위")
    final_assignment: str = Field(description="의사결정권자가 지금 당장 승인하거나 검토해야 할 과제")

writer_agent = LlmAgent(
    model='gemini-2.5-flash',
    name='writer_agent',
    # output_schema=StrategicReport,
    instruction="""
    당신은 전략 보고서 작성 전문가입니다.
    1. 전달받은 분석 내용을 바탕으로 StrategicReport 형식에 맞게 보고서를 작성하십시오.
    2. 각 항목을 구체적이고 실행 가능한 내용으로 채우십시오.
    3. 모든 답변은 한국어로 작성하십시오.
    """
)