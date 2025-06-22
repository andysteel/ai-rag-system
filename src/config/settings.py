import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class DatabaseConfig:
    url: str = "sqlite:///my_database.db"
    embedding_dimension: int = 768

@dataclass
class EmbeddingConfig:
    model_name: str = "text-embedding-004"
    chunk_size: int = 384
    chunk_overlap: int = 38
    batch_size: int = 5
    rate_limit_delay: int = 65

@dataclass
class AppConfig:
    database: DatabaseConfig
    embedding: EmbeddingConfig
    google_api_key: Optional[str]
    logging_level: str
    gen_ai_model: str

    @classmethod
    def from_env(cls) -> 'AppConfig':
        return cls(
            database=DatabaseConfig(),
            embedding=EmbeddingConfig(),
            google_api_key=os.getenv("GOOGLE_AI_API"),
            logging_level="INFO",
            gen_ai_model="gemini-2.5-flash-preview-05-20"
        )
    
# Global config instance
config = AppConfig.from_env()