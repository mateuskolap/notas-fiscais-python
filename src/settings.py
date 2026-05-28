from pydantic_settings import BaseSettings, SettingsConfigDict

from src.enums.ai_enum import AiProviderEnum


class AuthSettings(BaseSettings):
    SECRET_KEY: str = ''
    ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7


class DatabaseSettings(BaseSettings):
    DB_SCHEME: str = ''
    DB_USER: str = ''
    DB_PASSWORD: str = ''
    DB_NAME: str = ''
    DB_PORT: int = ''
    DB_HOST: str = ''

    @property
    def database_url(self) -> str:
        return (
            f'{self.DB_SCHEME}://{self.DB_USER}:{self.DB_PASSWORD}@'
            f'{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'
        )


class AiSettings(BaseSettings):
    AI_PROVIDER: AiProviderEnum = AiProviderEnum.GEMINI
    AI_MODEL: str = 'gemini-2.5-flash'
    AI_API_KEY: str = ''
    AI_MAX_TOKENS: int = 1024
    AI_TEMPERATURE: float = 0.0


class Settings(AuthSettings, DatabaseSettings, AiSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore',
    )


settings = Settings()
