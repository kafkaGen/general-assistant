from pydantic_settings import BaseSettings, SettingsConfigDict

from src.utils.logger import create_logger

settings_logger = create_logger("settings")


class BaseNamedSettings(BaseSettings):
    name: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    def __init__(self, **data):
        # Dynamically set the environment variable prefix before validation
        name = data.get("name", "default_name")
        env_prefix = f"{name.upper().replace('-', '_')}_"

        super().__init__(_env_prefix=env_prefix, **data)
