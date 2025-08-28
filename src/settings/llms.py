import os

from langchain_core.tools import BaseTool
from pydantic import BaseModel, model_validator

from .base_named_settings import BaseNamedSettings, settings_logger


class ChatLLMSettings(BaseNamedSettings):
    model_provider: str = "openai"
    model_name: str = "gpt-4o-mini"
    temperature: float = 0.3
    prompt_id: str
    structured_output: type[BaseModel] | None = None
    tools: list[BaseTool] | None = None

    @model_validator(mode="after")
    def validate_bind_options(self):
        """Ensure that structured_output and tools are mutually exclusive."""

        if self.structured_output is not None and self.tools is not None:
            raise ValueError(
                "structured_output and tools are mutually exclusive. "
                "Only one can be set at a time, or both can be None."
            )

        return self

    @model_validator(mode="after")
    def replace_prompt_id_with_env_var(self):
        """
        After initialization, check for prompt_id environment variables and
        override the field value if it exists. Env variable is more important
        than the field value.
        """

        env_var_name = self.model_config["env_prefix"] + "PROMPT_ID"
        env_value = os.getenv(env_var_name)
        if env_value is not None and env_value != self.prompt_id:
            settings_logger.warning(
                f"Overriding prompt_id {self.prompt_id} passed as variable "
                f"in constructor with {env_value} from environment variable "
                f"in {self.__class__.__name__} {self.name} as environment "
                "variable has higher priority."
            )
            self.prompt_id = env_value

        return self
