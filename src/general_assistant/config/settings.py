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


class WebUISettings(BaseSettings):
    """
    Web UI settings, loaded from environment variables and .env files.
    """

    assistant_base_url: str = Field(
        "http://127.0.0.1:8000",
        description="The base URL of the assistant service.",
    )
    assistant_chat_endpoint: str = Field(
        "/v0.1.0/chat/chat_completions",
        description="The chat endpoint path.",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class AssistantClientSettings(BaseSettings):
    """
    Assistant client settings, loaded from environment variables and .env files.
    """

    retry_attempts: int = Field(3, description="Number of retry attempts.")
    retry_min_delay: int = Field(1, description="Minimum delay between retries.")
    retry_max_delay: int = Field(10, description="Maximum delay between retries.")
    timeout: int = Field(90, description="Request timeout in seconds.")

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
    webui: WebUISettings = WebUISettings()
    assistant_client: AssistantClientSettings = AssistantClientSettings()

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = AppSettings()
