from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

### GENERAL SETTINGS ###


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


### MODELS SETTINGS ###


class GeneralAgentModelSettings(BaseSettings):
    """
    General agent model settings, loaded from environment variables and .env files.
    """

    provider: str = Field(
        # "anthropic",
        "openai",
        description="The provider of the model.",
        alias="GENERAL_AGENT_MODEL_PROVIDER",
    )
    model_name: str = Field(
        # "claude-3-5-sonnet-latest",
        "gpt-4o-mini",
        description="The name of the model.",
        alias="GENERAL_AGENT_MODEL_NAME",
    )
    temperature: float = Field(
        0.3,
        description="The temperature of the model.",
        alias="GENERAL_AGENT_MODEL_TEMPERATURE",
    )
    max_tokens: int = Field(
        2048,
        description="The maximum number of tokens to generate.",
        alias="GENERAL_AGENT_MODEL_MAX_TOKENS",
    )
    prompt_id: str = Field(
        "general-agent",
        description="The ID of the general agent prompt.",
        alias="GENERAL_AGENT_PROMPT_ID",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class ModelsSettings(BaseSettings):
    """
    Models settings, loaded from environment variables and .env files.
    """

    general_agent: GeneralAgentModelSettings = GeneralAgentModelSettings()


### TOOLS SETTINGS ###


class WebSearchToolSettings(BaseSettings):
    """
    Web search tool settings, loaded from environment variables and .env files.
    """

    api_key: str = Field(
        ..., description="The API key for the web search tool.", alias="TAVILY_API_KEY"
    )
    max_results: int = Field(2, description="Maximum number of search results.")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class ToolsSettings(BaseSettings):
    """
    Tools settings, loaded from environment variables and .env files.
    """

    web_search_tool: WebSearchToolSettings = WebSearchToolSettings()


### WORKFLOWS SETTINGS ###


class WorkflowsSettings(BaseSettings):
    """
    Workflows settings, loaded from environment variables and .env files.
    """

    models: ModelsSettings = ModelsSettings()
    tools: ToolsSettings = ToolsSettings()


### AGGREGATOR SETTINGS ###


class AppSettings(BaseSettings):
    """
    The main application settings, which composes all component-specific settings.
    """

    api: ApiSettings = ApiSettings()
    webui: WebUISettings = WebUISettings()
    assistant_client: AssistantClientSettings = AssistantClientSettings()
    workflows: WorkflowsSettings = WorkflowsSettings()


settings = AppSettings()
