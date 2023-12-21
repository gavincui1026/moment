# config/settings.py

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url:str = 'mysql+aiomysql://barddies:barddies@155.138.159.32:3306/barddies'

    class Config:
        env_file = ".env"

settings = Settings()
