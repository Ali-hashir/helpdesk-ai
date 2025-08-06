# # app/config.py
# from pydantic import Field
# from pydantic_settings import BaseSettings
# from pydantic import PostgresDsn

# class Settings(BaseSettings):
#     app_name: str = "Helpdesk-AI API"
#     debug: bool = Field(False, env="DEBUG")
    
#     # Postgres settings (individual components)
#     postgres_user: str = Field(..., env="POSTGRES_USER")
#     postgres_password: str = Field(..., env="POSTGRES_PASSWORD")
#     postgres_db: str = Field(..., env="POSTGRES_DB")

#     class Config:
#         env_file = ".env"

# settings = Settings()

# app/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Helpdesk-AI API"
    debug: bool = True
    database_url: str                        # plain str


    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

settings = Settings()
