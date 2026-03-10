from google.adk.agents import LlmAgent
from tools import save_strategic_report, load_memory, save_memory, send_report_email

delivery_agent = LlmAgent(
    model='gemini-2.5-flash',
    name='delivery_agent',
    tools=[save_strategic_report, load_memory, save_memory, send_report_email],
    instruction="""
    당신은 보고서 전달 전문가입니다.
    1. 'load_memory' 도구로 이전 기록을 확인하십시오.
    2. 'save_strategic_report' 도구로 보고서를 파일로 저장하십시오.
    3. 'save_memory' 도구로 핵심 내용을 메모리에 저장하십시오.
    4. 'send_report_email' 도구로 이메일을 발송하십시오.
    5. 모든 답변은 한국어로 작성하십시오.
    """
)