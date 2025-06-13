from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ApiSettings(BaseSettings):
    """
    API settings, loaded from environment variables and .env files.
    """

    api_name: str = Field(
        "General Assistant API", description="The name of the application."
    )
    api_version: str = Field("v0.1.0", description="The version of the application.")
    api_description: str = Field(
        "API for the General Assistant application",
        description="A brief description of the application.",
    )
    cors_allowed_origins: list[str] = Field(
        default=["*"],  # WARNING: For development only. Restrict in production.
        description="List of allowed CORS origins.",
    )
    log_level: str = Field("INFO", description="The logging level.")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class AppSettings(BaseSettings):
    """
    The main application settings, which composes all component-specific settings.
    """

    api: ApiSettings = ApiSettings()

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = AppSettings()
