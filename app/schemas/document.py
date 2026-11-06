from pydantic import BaseModel
from typing import Optional, Union


class Document(BaseModel):
    id: Optional[str] = None
    text: Optional[str] = None
    doc_code: Optional[str] = None
    doc_name: Optional[str] = None
    section: Optional[str] = None
    sub_section: Optional[str] = None
    part: Optional[Union[int,str]] = None
    page: Optional[Union[int,str]] = None

    def to_dict(self) -> dict:
        return self.model_dump()

    def to_rag_format(self) -> dict:
        return {
            "page_content": self.text,
            "metadata": {
                "id": self.id,
                "doc_code": self.doc_code,
                "doc_name": self.doc_name,
                "section": self.section,
                "sub_section": self.sub_section,
                "part": self.part,
                "page": self.page,
            }
        }
