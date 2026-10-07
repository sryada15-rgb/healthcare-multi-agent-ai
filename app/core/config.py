from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Healthcare Multi-Agent AI"
    postgres_url: str = "postgresql+psycopg://healthcare:healthcare@localhost:5432/healthcare"
    redis_url: str = "redis://localhost:6379/0"
    milvus_uri: str = "http://localhost:19530"
    milvus_collection: str = "healthcare_policies"
    aws_region: str = "us-east-1"
    bedrock_model_id: str = "anthropic.claude-3-5-sonnet-20240620-v1:0"
    use_bedrock: bool = False
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

@lru_cache
def get_settings() -> Settings:
    return Settings()
