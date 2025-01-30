from pydantic import Field
from pydantic_settings import BaseSettings


class RedisSettings(BaseSettings):
    HOST: str = Field(default="redis-service")
    PORT: int = Field(default=6379)
    SSL: bool = Field()
    PASSWORD: str = Field()


class DatabaseSettings(BaseSettings):
    URL: str = Field(default="sqlite:///test.db")


class ApplicationSettings(BaseSettings):
    REDIS: RedisSettings
    DATABASE: DatabaseSettings

    ENV: str = Field(default="development")
    LOG_LEVEL: str = Field(default="INFO")

    DEFAULT_LRU_TTL: int = Field(default=31 * 60)  # 30 mins
    LOKI_ENDPOINT: str = Field(
        default="http://loki-service:3100/loki/api/v1/push",
    )
    TEMPO_ENDPOINT: str = Field(default="http://tempo-service:4317")

    DEFAULT_TASK_TIMEOUT: int = Field(default=10)  # 10 seconds

    class Config:
        env_file = ".env"
        env_nested_delimiter = "__"
        case_sensitive = True
        extra = "allow"


settings = ApplicationSettings()
