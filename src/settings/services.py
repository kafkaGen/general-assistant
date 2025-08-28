from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ApiSettings(BaseSettings):
    api_name: str = Field(
        "General Assistant API", description="The name of the application."
    )
    api_version: str = Field("v0.2.0", description="The version of the application.")
    api_description: str = Field(
        "API for the General Assistant application",
        description="A brief description of the application.",
    )
    cors_allowed_origins: list[str] = Field(
        default=["*"],  # NOTE: For development only. Restrict in production.
        description="List of allowed CORS origins.",
    )
    console_log_level: str = Field("INFO", description="The console logging level.")
    file_log_level: str = Field("INFO", description="The file logging level.")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="API_",
        extra="ignore",
    )


class WebUISettings(BaseSettings):
    assistant_base_url: str = Field(
        "http://127.0.0.1:8000",
        description="The base URL of the assistant service.",
    )
    assistant_chat_invoke_endpoint: str = Field(
        "/v0.2.0/chat/chat_invoke",
        description="The chat invoke endpoint path.",
    )
    assistant_chat_stream_endpoint: str = Field(
        "/v0.2.0/chat/chat_stream",
        description="The chat stream endpoint path.",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="WEBUI_",
        extra="ignore",
    )


class AssistantClientSettings(BaseSettings):
    retry_attempts: int = Field(3, description="Number of retry attempts.")
    retry_min_delay: int = Field(1, description="Minimum delay between retries.")
    retry_max_delay: int = Field(10, description="Maximum delay between retries.")
    timeout: int = Field(180, description="Request timeout in seconds.")
    console_log_level: str = Field("INFO", description="The console logging level.")
    file_log_level: str = Field("INFO", description="The file logging level.")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="ASSISTANT_CLIENT_",
        extra="ignore",
    )


api_settings = ApiSettings()
webui_settings = WebUISettings()
assistant_client_settings = AssistantClientSettings()
