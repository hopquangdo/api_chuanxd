import re
from typing import List
from app.schemas.document import Document

CITE_PATTERN = re.compile(
    r'<cite\s+doc="([^"]+)"\s+section="([^"]+)"\s+page="([^"]+)"\s*/?>',
    re.IGNORECASE
)

def extract_cited_documents(
    answer: str,
    documents: List[Document]
) -> List[Document]:
    cited_docs: list[Document] = []
    seen = set()

    doc_map = {
        (d.doc_code, d.section, str(d.page)): d
        for d in documents
    }

    for doc_code, section, page in CITE_PATTERN.findall(answer):
        key = (doc_code, section, page)

        doc = doc_map.get(key)
        if not doc:
            continue

        if key in seen:
            continue

        seen.add(key)
        cited_docs.append(doc)

    return cited_docs
