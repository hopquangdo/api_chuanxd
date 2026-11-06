import random
from typing import AsyncGenerator, Dict, Any, List

from langchain_core.prompts import ChatPromptTemplate
import asyncio
from app.config.llm import get_llm
from app.constants.chat_events import ChatEventType, ChatStep

from app.prompts.prompts import ANSWER_PROMPT
from app.retrieval.vector_db import VectorDB
from app.schemas import ChatEvent, ChatRequest

from app.schemas.document import Document
from app.config.logger import setup_logger
from app.utils.utils import extract_cited_documents

logger = setup_logger("CHAT_SERVICE")


class ChatService:
    def __init__(self, retrieval: VectorDB):
        self.retrieval = retrieval
        self.llm = get_llm()

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", ANSWER_PROMPT)
        ])

        logger.info("✅ ChatService initialized")

    # ===================== helpers =====================

    @staticmethod
    def _status(step: ChatStep, message: str) -> Dict[str, Any]:
        return ChatEvent(
            type=ChatEventType.STATUS,
            data={
                "step": step,
                "message": message
            }
        ).model_dump()

    def _build_prompt(
        self,
        query: str,
        documents: List[Document]
    ) -> ChatPromptTemplate:
        ctx_blocks = []

        for i, doc in enumerate(documents, 1):
            ctx_blocks.append(
                f"<ctx id='{i}' doc='{doc.doc_code}' sec='{doc.section}' page='{doc.page}'>\n"
                f"{doc.text}\n"
                f"</ctx>"
            )

        return self.prompt.partial(
            context="\n\n".join(ctx_blocks),
            question=query
        )

    @staticmethod
    async def _delay(min_s: float = 0.3, max_s: float = 2):
        await asyncio.sleep(random.uniform(min_s, max_s))

    # ===================== main =====================
    async def ask(
        self,
        req: ChatRequest
    ) -> AsyncGenerator[Dict[str, Any], None]:

        logger.info(
            f"💬 New chat | query='{req.query}' | "
            f"document_codes={req.document_codes}"
        )

        try:
            # 1️⃣ Parse query
            yield self._status(
                ChatStep.PARSE_QUERY,
                "Đang phân tích câu hỏi..."
            )
            await self._delay()

            # 2️⃣ Detect intent
            yield self._status(
                ChatStep.DETECT_INTENT,
                "Xác định mục đích tra cứu và yêu cầu pháp lý..."
            )
            await self._delay()

            # 3️⃣ Extract scope
            yield self._status(
                ChatStep.EXTRACT_SCOPE,
                "Xác định phạm vi áp dụng tiêu chuẩn..."
            )
            await self._delay()

            # 4️⃣ Retrieve documents
            yield self._status(
                ChatStep.RETRIEVE_STANDARD,
                "Tra cứu trong hệ thống QCVN / TCVN..."
                if not req.document_codes
                else f"Tra cứu trong ({', '.join(req.document_codes)})..."
            )

            documents = self.retrieval.query(
                query_text=req.query,
                document_codes=req.document_codes,
                top_k=10
            )

            logger.info(f"📚 Retrieved {len(documents)} documents")

            if not documents:
                yield ChatEvent(
                    type=ChatEventType.DONE,
                    data={"text": "Không tìm thấy thông tin phù hợp trong hệ thống."}
                ).model_dump()
                return

            # 5️⃣ Filter
            yield self._status(
                ChatStep.FILTER_DOCUMENT,
                "Lọc các điều khoản liên quan..."

            )
            await self._delay()

            # 6️⃣ Cross check
            yield self._status(
                ChatStep.CROSS_CHECK,
                "Đối chiếu và so sánh các quy chuẩn..."
            )
            await self._delay()

            # 7️⃣ Synthesize
            yield self._status(
                ChatStep.SYNTHESIZE_ANSWER,
                "Tổng hợp và diễn giải kết quả..."
            )

            prompt = self._build_prompt(req.query, documents)

            final_answer_parts: List[str] = []

            logger.info("🤖 LLM streaming started")

            for chunk in self.llm.stream(prompt.format_prompt()):
                if not chunk.content:
                    continue

                final_answer_parts.append(chunk.content)

                yield ChatEvent(
                    type=ChatEventType.ANSWER,
                    data={"delta": chunk.content}
                ).model_dump()

            final_answer = "".join(final_answer_parts)

            logger.info("🤖 LLM streaming completed")

            # 8️⃣ Cite
            yield self._status(
                ChatStep.CITE_SOURCE,
                "Xác định và gắn trích dẫn tiêu chuẩn..."
            )

            cited_docs = extract_cited_documents(
                final_answer,
                documents
            )

            yield ChatEvent(
                type=ChatEventType.DONE,
                data={
                    "text": final_answer,
                    "citations": [
                        {
                            "doc_code": d.doc_code,
                            "section": d.section,
                            "page": d.page
                        }
                        for d in cited_docs
                    ]
                }
            ).model_dump()

        except Exception:
            logger.exception("❌ ChatService error")

            yield ChatEvent(
                type=ChatEventType.ERROR,
                data={"message": "Hệ thống gặp lỗi. Vui lòng thử lại."}
            ).model_dump()
