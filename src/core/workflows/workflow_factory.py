from src.core.llms import ChatLLM
from src.core.tools import WebSearchTool
from src.core.workflows.general_assistant import GeneralAssistant
from src.settings.llms import ChatLLMSettings
from src.settings.tools import WebSearchToolSettings
from src.settings.workflows import GeneralAssistantSettings


class WorkflowFactory:
    @classmethod
    def create_general_assistant(cls) -> GeneralAssistant:
        planner_llm = ChatLLM(
            settings=ChatLLMSettings(
                # NOTE: In future i can pass here the configuration
                # from the user to change some model parameters
                name="general-assistant-planner-llm",
                prompt_id="general-assistant-planner-prompt",
            )
        )

        executor_llm_chain_tools = WebSearchTool(
            settings=WebSearchToolSettings(
                name="general-assistant-web-search-tool",
            ),
        ).get_tools()

        executor_llm = ChatLLM(
            settings=ChatLLMSettings(
                name="general-assistant-executor-llm",
                prompt_id="general-assistant-executor-prompt",
                tools=executor_llm_chain_tools,
            )
        )

        all_tools = {tool.name: tool for tool in executor_llm_chain_tools}

        return GeneralAssistant(
            settings=GeneralAssistantSettings(
                name="general-assistant-workflow",
            ),
            planner_llm=planner_llm,
            executor_llm=executor_llm,
            tools=all_tools,
        )
