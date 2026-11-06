from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from app.constants.chat_events import ChatEventType


class ChatRequest(BaseModel):
    query: str
    document_codes: Optional[List[str]] = None






class ChatEvent(BaseModel):
    type: ChatEventType
    data: Dict[str, Any]