from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "RAG 个人网站 API"
    API_VERSION: str = "1.0.0"
    DEBUG: bool = True
    DATABASE_URL: str = "mysql+pymysql://root:123456@localhost:3306/self_website"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()