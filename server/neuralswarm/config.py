from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    APP_NAME: str = "neuralswarm"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://neuralswarm:neuralswarm@localhost:5432/neuralswarm"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # LLM Gateway
    LLM_GATEWAY_URL: str = "http://localhost:3000"
    LLM_GATEWAY_API_KEY: str = ""
    LLM_GATEWAY_TIMEOUT: int = 30

    # Qdrant
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_COLLECTION: str = "neuralswarm"

    # MCP
    MCP_WEBSOCKET_PORT: int = 8765
    MCP_TIMEOUT: int = 30

    # Memory
    L1_TTL_HOURS: int = 24
    L2_EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    model_config = {
        "env_file": "../.env",
        "env_file_encoding": "utf-8",
        "env_prefix": "NS_",
        "extra": "ignore",
    }


settings = Settings()
