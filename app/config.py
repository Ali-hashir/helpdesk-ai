# app/config.py
from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Helpdesk-AI API"
    debug: bool = True

    class Config:
        env_file = ".env"

settings = Settings()
