# config/settings.py

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = (
        "mysql+aiomysql://barddies:barddies@155.138.159.32:3306/barddies"
    )
    database_url2: str = (
        "mysql+aiomysql://addon:zBrLH5weBNpBwEM2@155.138.159.32:3306/addon"
    )

    class Config:
        env_file = ".env"


settings = Settings()
