from pydantic import Field

from .base_named_settings import BaseNamedSettings


class WebSearchToolSettings(BaseNamedSettings):
    max_results: int = Field(2, description="Maximum number of search results.")
