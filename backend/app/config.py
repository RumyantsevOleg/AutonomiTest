from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/fakenews"
    REDIS_URL: str = "redis://localhost:6379/0"
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str | None = None

    model_config = {"env_file": ".env"}


settings = Settings()
