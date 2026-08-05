from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    APP_NAME: str = "Global Intelligence Platform"

    ENV: str = "development"

    DATABASE_URL: str

    SECRET_KEY: str

    GOOGLE_CLOUD_PROJECT: str

    GOOGLE_CLOUD_LOCATION: str

    GOOGLE_APPLICATION_CREDENTIALS: str

    VERTEX_MODEL: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()