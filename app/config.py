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

    # Search / research pipeline limits (configurable)
    SEARCH_DISCOVERY_LIMIT: int = 30
    SEARCH_RESEARCH_LIMIT: int = 15
    SEARCH_DEFAULT_LIMIT: int = 10
    RESEARCH_MAX_PAGES: int = 5
    RESEARCH_CONCURRENCY: int = 4
    REQUEST_TIMEOUT: int = 10

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()