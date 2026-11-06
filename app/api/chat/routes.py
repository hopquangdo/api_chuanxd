import json
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from app.chat.service import ChatService
from app.config.logger import setup_logger
from app.retrieval.vector_db import VectorDB
from app.schemas import ChatRequest

logger = setup_logger("CHAT_API")

router = APIRouter(prefix="/api/chat", tags=["Chat"])

@router.post("/stream")
async def chat_stream(
        request: Request,
        req: ChatRequest
):
    logger.info(f"Chat stream request: query={req.query}")
    retrieval = request.app.state.retrieval
    chat_service = ChatService(retrieval=retrieval)

    async def event_generator():
        async for event in chat_service.ask(req=req):
            yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )
