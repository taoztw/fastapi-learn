from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    ASYNC_DATABASE_URL: str = "sqlite+aiosqlite:///user.db"

@lru_cache()
def get_settings():
    return Settings()