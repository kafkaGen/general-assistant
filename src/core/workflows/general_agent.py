import asyncio
import operator
from collections.abc import AsyncGenerator, Generator
from typing import Annotated, Literal, TypedDict

from langchain.chat_models import init_chat_model
from langchain_core.messages import AnyMessage, ToolMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.runnables.graph_mermaid import draw_mermaid_png
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langsmith import Client as LangSmithClient

from src.core.tools import CalculatorToolSet, ReasoningToolSet, WebSearchToolSet
from src.settings.configuration import AgentsConfiguration
from src.utils.functions import (
    get_date,
)
from src.utils.logger import create_logger


class GeneralAgentState(TypedDict):
    input_messages: Annotated[list[AnyMessage], operator.add]
    output_messages: Annotated[list[AnyMessage], operator.add]


class GeneralAgent:
    logger = create_logger("general_agent")

    def __init__(self) -> None:
        self._config = None
        self._langsmith_client = LangSmithClient()

        self._graph = self._build_graph()

    def _setup_node(
        self,
        state: GeneralAgentState,
        config: RunnableConfig,
    ) -> dict:
        self._config = config["configurable"]["general_agent"]

        agent_tools = [
            *ReasoningToolSet().get_tools(),
            *WebSearchToolSet().get_tools(),
            *CalculatorToolSet().get_tools(),
        ]
        self._agent_tools = {tool.name: tool for tool in agent_tools}
        self._agent_llm = init_chat_model(**self._config["agent_llm"]).bind_tools(
            agent_tools,
            tool_choice="any",
        )
        self._agent_prompt = self._langsmith_client.pull_prompt(
            "general-agent-prompt",
        )

        return {}

    async def _decide_next_step_node(self, state: GeneralAgentState) -> dict:
        prompt = self._agent_prompt.invoke(
            {
                "messages": state["input_messages"] + state["output_messages"],
                "current_date": get_date(),
            }
        )
        output = await self._agent_llm.ainvoke(prompt)

        return {
            "output_messages": [output],
        }

    async def _run_tools_node(self, state: GeneralAgentState) -> dict:
        async def execute_tool(tool_call: dict) -> dict:
            return await self._agent_tools[tool_call["name"]].ainvoke(tool_call["args"])

        tool_calls = state["output_messages"][-1].tool_calls
        tool_results = await asyncio.gather(
            *[execute_tool(tool_call) for tool_call in tool_calls]
        )

        tool_messages = []
        for tool_call, tool_result in zip(tool_calls, tool_results, strict=False):
            tool_messages.append(
                ToolMessage(
                    content=tool_result,
                    name=tool_call["name"],
                    args=tool_call["args"],
                    tool_call_id=tool_call["id"],
                )
            )

        return {
            "output_messages": tool_messages,
        }

    # async def _reflect_node(self, state: GeneralAgentState) -> dict:
    #     pass

    def _route_continue_or_end_edge(
        self, state: GeneralAgentState
    ) -> Literal["decide_next_step_node", END]:
        last_message = state["output_messages"][-1]

        if last_message.name == "final_answer":
            return END

        return "decide_next_step_node"

    # def _route_reflect_or_end_edge(
    #     self,
    #     state: GeneralAgentState,
    # ) -> Literal["reflect_node", END]:
    #     pass

    def _build_graph(self) -> CompiledStateGraph:
        graph = StateGraph(GeneralAgentState, config_schema=AgentsConfiguration)

        graph.add_node("setup_node", self._setup_node)
        graph.add_node("decide_next_step_node", self._decide_next_step_node)
        graph.add_node("run_tools_node", self._run_tools_node)

        graph.add_edge(START, "setup_node")
        graph.add_edge("setup_node", "decide_next_step_node")
        graph.add_edge("decide_next_step_node", "run_tools_node")

        graph.add_conditional_edges(
            "run_tools_node",
            self._route_continue_or_end_edge,
            ["decide_next_step_node", END],
        )

        return graph.compile()

    def invoke(
        self,
        messages: list[AnyMessage],
        config: RunnableConfig,
    ) -> dict:
        return asyncio.run(self.ainvoke(messages, config))

    async def ainvoke(
        self,
        messages: list[AnyMessage],
        config: RunnableConfig,
    ) -> dict:
        final_state = await self._graph.ainvoke(
            {"input_messages": messages},
            config,
        )

        return final_state

    def stream(
        self,
        messages: list[AnyMessage],
        config: RunnableConfig,
    ) -> Generator[AnyMessage, None, None]:
        async def gen():
            async for message in self.astream(messages, config):
                yield message

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            agen = gen().__aiter__()
            while True:
                try:
                    message = loop.run_until_complete(agen.__anext__())
                    yield message
                except StopAsyncIteration:
                    break
        finally:
            loop.close()

    async def astream(
        self,
        messages: list[AnyMessage],
        config: RunnableConfig,
    ) -> AsyncGenerator[AnyMessage, None]:
        stream_response = self._graph.astream(
            {"input_messages": messages},
            config=config,
            stream_mode="updates",
        )

        async for node_event in stream_response:
            for node_output in node_event.values():
                if node_output:
                    for message in node_output.get("output_messages", []):
                        yield message

    def plot_graph(self, image_path: str = "docs/general_agent_graph.png") -> None:
        draw_mermaid_png(
            self._graph.get_graph().draw_mermaid(),
            output_file_path=image_path,
        )
        self.logger.info(
            f"{self.__class__.__name__}: Graph image saved to {image_path}"
        )
