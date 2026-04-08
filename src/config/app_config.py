from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_base_url: str = "https://insta.dmcc.az"
    redirect_uri: str = "https://insta.dmcc.az/auth/callback"

    INSTAGRAM_APP_ID: str = os.getenv("INSTAGRAM_APP_ID", "") 
    INSTAGRAM_APP_SECRET: str = os.getenv("INSTAGRAM_APP_SECRET", "")
    VERIFY_TOKEN: str = "SALAM_MARKER_CONFIRMED"

    database_url: str = "postgresql+asyncpg://instagram_user:Orxan20052004!@localhost:5454/instagram"

    default_system_prompt: str = (
        "Ты AI-ассистент компании в Instagram Direct. "
        "Отвечай коротко, дружелюбно и по делу. "
        "Если вопрос непонятен — задай уточняющий вопрос."
    )


settings = Settings()