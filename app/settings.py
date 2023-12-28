from functools import lru_cache

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    rabbitmq_host: str
    rabbitmq_user: str
    rabbitmq_password: str
    rabbitmq_image_processing_queue: str
    rabbitmq_connection_pool_size: int = 100
    timeout_seconds: int = 5

@lru_cache
def get_settings() -> Settings:
    return Settings()
