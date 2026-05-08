from pydantic_settings import BaseSettings, SettingsConfigDict


class AuthSettings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7


class DatabaseSettings(AuthSettings):
    DB_SCHEME: str
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    DB_PORT: int
    DB_HOST: str

    @property
    def database_url(self) -> str:
        return (
            f'{self.DB_SCHEME}://{self.DB_USER}:{self.DB_PASSWORD}@'
            f'{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'
        )


class Settings(DatabaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore',
    )


settings = Settings()  # type: ignore
