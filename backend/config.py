from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OPENROUTER_API_KEY: str
    DATABASE_URL: str
    DEFAULT_TIMEOUT_SECONDS: int = 30
    DEFAULT_TIER: str = "default"
    MAX_CONCURRENT_MODELS: int = 10
    
    OPENROUTER_API_URL: str = "https://openrouter.ai/api/v1/chat/completions"
    LOG_FILE: str = "chat_logs.csv"
    
    MODEL_MAP: dict = {
        "mistral": "mistralai/mistral-7b-instruct",
        "llama": "meta-llama/llama-3.1-8b-instruct"
    }

    class Config:
        env_file = ".env"

settings = Settings()
