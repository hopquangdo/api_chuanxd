from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    OPENAI_API_KEY: str
    HF_TOKEN: str

    VECTORDB_HOST: str = "qdrant"
    VECTORDB_PORT: int = 6333
    VECTORDB_COLLECTION_NAME: str = "aichuanxd"
    VECTORDB_EMBEDDING_MODEL: str = "dangvantuan/vietnamese-embedding"

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8"
    )


settings = Settings()
