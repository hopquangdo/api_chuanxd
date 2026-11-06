from langchain_openai import ChatOpenAI

from app.config.env import settings


def get_llm(model_name: str = "gpt-4o-mini", temperature=0, max_tokens: int = 1024):
    return ChatOpenAI(
        model=model_name,
        temperature=temperature,
        max_tokens=max_tokens,
        api_key=settings.OPENAI_API_KEY
    )
