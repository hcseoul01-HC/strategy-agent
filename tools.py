import os
import json
import smtplib
import aiofiles
from datetime import datetime
from functools import lru_cache
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pypdf import PdfReader

MAX_CHARS = 15000
MEMORY_FILE = "agent_memory.json"

@lru_cache(maxsize=8)
def _parse_pdf(filepath: str) -> str:
    """PDF 파일을 파싱합니다. 결과는 캐시됩니다."""
    reader = PdfReader(filepath)
    chunks = []
    total = 0
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        if total + len(text) > MAX_CHARS:
            break
        chunks.append(f"[{os.path.basename(filepath)} - Page {i+1}]\n{text}")
        total += len(text)
    return "\n".join(chunks)

def analyze_document_content(query: str) -> str:
    """documents/ 폴더의 PDF를 분석하여 텍스트를 반환합니다."""
    base_path = os.path.dirname(os.path.abspath(__file__))
    doc_dir = os.path.join(base_path, "documents")
    files = [f for f in os.listdir(doc_dir) if f.lower().endswith('.pdf')]
    if not files:
        return "분석할 PDF 문서가 없습니다."
    all_chunks = []
    for filename in files:
        filepath = os.path.join(doc_dir, filename)
        try:
            all_chunks.append(_parse_pdf(filepath))
        except Exception as e:
            all_chunks.append(f"[{filename} 읽기 오류: {e}]")
    return "\n\n".join(all_chunks)

async def save_strategic_report(content: str) -> str:
    """분석 결과를 텍스트 파일로 저장합니다."""
    output_dir = os.getenv("OUTPUT_DIR", ".")
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, "strategy_report.txt")
    try:
        async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
            await f.write(content)
        return f"저장 완료: {os.path.abspath(file_path)}"
    except Exception as e:
        return f"저장 실패: {e}"

def load_memory() -> str:
    """이전 대화 기록을 불러옵니다."""
    if not os.path.exists(MEMORY_FILE):
        return "이전 대화 기록 없음"
    with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
        memory = json.load(f)
    lines = [f"[{m['timestamp']}] {m['content'][:200]}" for m in memory]
    return "\n".join(lines)

def save_memory(content: str) -> str:
    """현재 분석 결과를 메모리에 저장합니다."""
    memory = []
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
            memory = json.load(f)
    memory.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "content": content
    })
    memory = memory[-10:]
    with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)
    return f"메모리 저장 완료 (총 {len(memory)}개 기록)"

def send_report_email(content: str) -> str:
    """분석 보고서를 이메일로 전송합니다."""
    sender   = os.getenv("EMAIL_SENDER")
    password = os.getenv("EMAIL_PASSWORD")
    receivers = os.getenv("EMAIL_RECEIVER", "").split(",")
    msg = MIMEMultipart()
    msg['From']    = sender
    msg['To']      = ", ".join(receivers)
    msg['Subject'] = "[전략 보고서] AI 에이전트 분석 완료"
    msg.attach(MIMEText(content, 'plain', 'utf-8'))
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(sender, password)
            smtp.sendmail(sender, receivers, msg.as_string())
        return f"이메일 전송 완료 → {len(receivers)}명"
    except Exception as e:
        return f"이메일 전송 실패: {e}"