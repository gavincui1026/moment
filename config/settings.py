# config/settings.py

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url:str = 'mysql+aiomysql://root:303816@host:3306/test'

    class Config:
        env_file = ".env"

settings = Settings()
