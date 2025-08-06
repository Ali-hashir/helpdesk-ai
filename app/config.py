# app/config.py
from pydantic import Field
from pydantic_settings import BaseSettings
from pydantic import PostgresDsn

class Settings(BaseSettings):
    app_name: str = "Helpdesk-AI API"
    debug: bool = Field(False, env="DEBUG")
    database_url: PostgresDsn
    
    # Postgres settings (individual components)
    postgres_user: str = Field(..., env="POSTGRES_USER")
    postgres_password: str = Field(..., env="POSTGRES_PASSWORD")
    postgres_db: str = Field(..., env="POSTGRES_DB")

    class Config:
        env_file = ".env"

settings = Settings()
