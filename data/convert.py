import uuid

import fitz
import re
import json
from tqdm import tqdm
from docx import Document
import re

# =========================
# CONFIG
# =========================
PDF_PATH = "raw/pdf/TCVN5687_2024.pdf"
OUTPUT_JSON = "TCVN_5687_2024.json"

DOC_CODE = "TCVN 5687-2024"
DOC_NAME = "THÔNG GIÓ VÀ ĐIỀU HÒA KHÔNG KHÍ - YÊU CẦU THIẾT KẾ"

MAX_CHARS = 1200

# =========================
# REGEX
# =========================
SECTION_RE = re.compile(r"^(\d+)\.\s+(.+)")          # 4. Quy định chung
SUB_RE     = re.compile(r"^(\d+\.\d+)\.?\s*(.*)")   # 4.1 Nội dung
CHAPTER_RE = re.compile(r"^CHƯƠNG\s+\d+", re.I)

# =========================
# CLEAN TEXT
# =========================
def clean_text(text):
    text = text.replace("\xa0", " ")
    text = re.sub(r"\n{2,}", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()

# =========================
# PDF → LINES (GIỮ PAGE)
# =========================
def pdf_to_lines(pdf_path):
    doc = fitz.open(pdf_path)
    lines = []

    for page_num, page in enumerate(doc, start=1):
        text = clean_text(page.get_text())
        for line in text.split("\n"):
            line = line.strip()
            if line:
                lines.append({
                    "page": page_num,
                    "line": line
                })
    return lines

# =========================
# DOCX → LINES (FAKE PAGE)
# =========================
def docx_to_lines(docx_path):
    doc = Document(docx_path)
    lines = []

    page = 1  # Word không có page thực → giả lập

    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue

        text = re.sub(r"\s+", " ", text)

        lines.append({
            "page": page,
            "line": text
        })

        # heuristic: gặp heading lớn thì coi như sang page
        if text.isupper() and len(text) < 80:
            page += 1

    return lines


# =========================
# MERGE DÒNG BỊ GÃY
# =========================
def merge_broken_lines(items):
    merged = []
    buffer = ""
    buffer_page = None

    def is_new_block(line):
        return (
            SECTION_RE.match(line)
            or SUB_RE.match(line)
            or CHAPTER_RE.match(line)
        )

    for item in items:
        line = item["line"]
        page = item["page"]

        if not buffer:
            buffer = line
            buffer_page = page
            continue

        if is_new_block(line):
            merged.append({
                "page": buffer_page,
                "line": buffer.strip()
            })
            buffer = line
            buffer_page = page
        else:
            if not buffer.endswith((".", ";", ",")):
                buffer += " "
            buffer += line

    if buffer:
        merged.append({
            "page": buffer_page,
            "line": buffer.strip()
        })

    return merged

# =========================
# SPLIT SAFE
# =========================
def split_safe(lines, max_chars):
    chunks = []
    buffer = ""

    for line in lines:
        if len(buffer) + len(line) <= max_chars:
            buffer += " " + line
        else:
            chunks.append(buffer.strip())
            buffer = line

    if buffer.strip():
        chunks.append(buffer.strip())

    return chunks

# =========================
# BUILD CHUNKS
# =========================
def build_chunks(lines):
    results = []
    idx = 1

    current_section = None      # ví dụ: "Quy định chung"
    current_sub = None          # ví dụ: "4.1"
    content_lines = []
    start_page = None

    def flush():
        nonlocal idx, content_lines
        if not current_sub or not content_lines:
            return

        parts = split_safe(content_lines, MAX_CHARS)

        for i, part in enumerate(parts, start=1):
            results.append({
                "id": str(uuid.uuid4()),
                "text": part.strip(),
                "doc_code": DOC_CODE,
                "doc_name": DOC_NAME,
                "section": current_section,      # ✅ KHÔNG SỐ
                "page": start_page
            })
            idx += 1

        content_lines.clear()

    for item in tqdm(lines, desc="Chunking by subsection"):
        line = item["line"]
        page = item["page"]

        # SECTION CHA → bỏ số, chỉ lấy tên
        m_sec = SECTION_RE.match(line)
        if m_sec:
            flush()
            current_section = m_sec.group(2).strip()  # 🔥 BỎ "4."
            current_sub = None
            continue

        # MỤC CON → chunk
        m_sub = SUB_RE.match(line)
        if m_sub:
            flush()
            current_sub = m_sub.group(1)
            start_page = page

            first_content = m_sub.group(2).strip()
            if first_content:
                content_lines.append(first_content)
            continue

        if current_sub:
            content_lines.append(line)

    flush()
    return results

# =========================
# MAIN
# =========================
if __name__ == "__main__":
    raw_lines = pdf_to_lines(PDF_PATH)
    merged_lines = merge_broken_lines(raw_lines)
    chunks = build_chunks(merged_lines)

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)

    print(f"✅ DONE: {len(chunks)} chunks – section không còn số, text thuần content")
