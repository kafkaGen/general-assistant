from langchain.chat_models import init_chat_model
from langgraph.prebuilt import create_react_agent
from langsmith import Client as LangSmithClient

from src.general_assistant.config.settings import WorkflowsSettings
from src.general_assistant.core.agent.tools import (
    PythonExecutorTool,
    WebSearchTool,
)


class AgentFactory:
    """Factory for creating agents."""

    def __init__(self, settings: WorkflowsSettings):
        self._settings = settings
        self._langsmith_client = LangSmithClient()

    def get_general_agent(self):
        llm = init_chat_model(
            model_provider=self._settings.models.general_agent.provider,
            model=self._settings.models.general_agent.model_name,
            # TODO: solve the issue with overload error
            # temperature=self._settings.models.general_agent.temperature,
            # max_tokens=self._settings.models.general_agent.max_tokens,
        )
        prompt_template = self._langsmith_client.pull_prompt(
            self._settings.models.general_agent.prompt_id
        )
        prompt = prompt_template.format_messages()[0]

        tools = []
        tools.extend(
            WebSearchTool(settings=self._settings.tools.web_search_tool).get_tools()
        )
        tools.extend(PythonExecutorTool().get_tools())

        agent_executor = create_react_agent(
            llm,
            tools,
            name="general_agent",
            prompt=prompt,
        )

        return agent_executor
