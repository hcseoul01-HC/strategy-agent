from google.adk.agents import LlmAgent
from tools import analyze_document_content

analyst_agent = LlmAgent(
    model='gemini-2.5-flash',
    name='analyst_agent',
    tools=[analyze_document_content],
    instruction="""
    당신은 문서 분석 전문가입니다.
    1. 'analyze_document_content' 도구로 documents/ 폴더의 PDF를 분석하십시오.
    2. 문서의 수치, 날짜, 핵심 데이터를 빠짐없이 추출하십시오.
    3. 분석 결과를 명확하고 구조적으로 정리하여 반환하십시오.
    4. 모든 답변은 한국어로 작성하십시오.
    """
)