import configparser

config = configparser.ConfigParser()
config.read("./config.ini", encoding='utf-8')

print(config.get("fastapi_config", 'debug'))

# 使用pydantic .env 读取配置

from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import Optional
from pydantic import validator
from functools import lru_cache


class Settings(BaseSettings):
    debug: bool = False
    title: str

    class Config:
        env_file = "config.env"
        env_file_encoding = "utf-8"

    @classmethod
    @field_validator("title", mode="before")
    def title_len_check(cls, v: str) -> Optional[str]:
        print("调用validator")
        if v and len(v) > 2:
            return None
        return v


settings = Settings(title="12312312123")
# settings = Settings(_env_file="config.env", _env_file_encoding="utf-8")
print(settings.title)

@lru_cache()
def get_settings():
    return Settings()

title = get_settings().title
print(f"cache: {title}")

