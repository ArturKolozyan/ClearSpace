from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    bot_token: str
    owner_chat_id: int
    fastapi_host: str = "127.0.0.1"
    fastapi_port: int = 8000
    data_dir: str = "backend/data"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
