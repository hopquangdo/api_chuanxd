
import uvicorn
from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware

from app.config.logger import setup_logger
from app.api.chat import router as chat_router
from app.retrieval.vector_db import VectorDB

logger = setup_logger("MAIN")


from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.retrieval = VectorDB(rebuild=True)
    yield


app = FastAPI(
    title="Chat RAG Service",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the exact origins
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(chat_router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}


def main():
    logger.info("🚀 Starting Chat RAG Service...")

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )


if __name__ == "__main__":
    main()
