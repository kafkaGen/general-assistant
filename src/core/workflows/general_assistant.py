import asyncio
import operator
from collections.abc import AsyncGenerator, Generator
from datetime import datetime
from typing import Annotated, Literal, TypedDict

from langchain_core.messages import AnyMessage, ToolMessage
from langchain_core.tools import BaseTool
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from src.core.llms import ChatLLM
from src.settings.workflows import GeneralAssistantSettings
from src.utils.functions import (
    pretty_tools_formatting,
)


class GeneralAssistantState(TypedDict):
    input_messages: Annotated[list[AnyMessage], operator.add]
    output_messages: Annotated[list[AnyMessage], operator.add]
    final_answer: str | None = None


# NOTE: in future i can cash the workflow based on its inputs and
# if client request the workflow check if one with such config
# already exists cached or create one. Make the LRU policy for cache.
# Can do the same for llms and tools.
class GeneralAssistant:
    def __init__(
        self,
        settings: GeneralAssistantSettings,
        planner_llm: ChatLLM,
        executor_llm: ChatLLM,
        tools: dict[str, BaseTool],
    ) -> None:
        self._settings = settings
        self._planner_llm = planner_llm
        self._executor_llm = executor_llm
        self._tools = tools

        self._graph = self._build_graph()

    async def _create_plan_node(self, state: GeneralAssistantState) -> dict:
        output = await self._planner_llm.ainvoke(
            input={
                "current_date": datetime.now().strftime("%Y-%m-%d"),
                "tools": pretty_tools_formatting(self._tools.values()),
                "messages": state["input_messages"] + state["output_messages"],
            },
        )

        return {
            "output_messages": [output],
        }

    async def _execution_node(self, state: GeneralAssistantState) -> dict:
        output = await self._executor_llm.ainvoke(
            input={
                "current_date": datetime.now().strftime("%Y-%m-%d"),
                "messages": state["input_messages"] + state["output_messages"],
            },
        )

        return {
            "output_messages": [output],
        }

    async def _tool_executor_node(self, state: GeneralAssistantState) -> dict:
        async def execute_tool(tool_call: dict) -> dict:
            return await self._tools[tool_call["name"]].ainvoke(tool_call["args"])

        tool_calls = state["output_messages"][-1].tool_calls
        tool_results = await asyncio.gather(
            *[execute_tool(tool_call) for tool_call in tool_calls]
        )

        new_ai_messages = []
        for tool_call, tool_result in zip(tool_calls, tool_results, strict=False):
            new_ai_messages.append(
                ToolMessage(
                    content=str(tool_result),
                    name=tool_call["name"],
                    args=tool_call["args"],
                    tool_call_id=tool_call["id"],
                )
            )

        return {
            "output_messages": new_ai_messages,
        }

    async def _final_answer_node(self, state: GeneralAssistantState) -> dict:
        final_answer = state["output_messages"][-1].content

        return {
            "final_answer": final_answer,
        }

    def _check_for_tool_call_edge(
        self, state: GeneralAssistantState
    ) -> Literal["tool_executor_node", "final_answer_node"]:
        last_message = state["output_messages"][-1]

        if last_message.tool_calls:
            return "tool_executor_node"

        return "final_answer_node"

    def _build_graph(self) -> CompiledStateGraph:
        graph = StateGraph(GeneralAssistantState)

        graph.add_node("create_plan_node", self._create_plan_node)
        graph.add_node("execution_node", self._execution_node)
        graph.add_node("tool_executor_node", self._tool_executor_node)
        graph.add_node("final_answer_node", self._final_answer_node)

        graph.add_edge(START, "create_plan_node")
        graph.add_edge("create_plan_node", "execution_node")
        graph.add_conditional_edges(
            "execution_node",
            self._check_for_tool_call_edge,
            ["tool_executor_node", "final_answer_node"],
        )
        graph.add_edge("tool_executor_node", "execution_node")
        graph.add_edge("final_answer_node", END)

        return graph.compile()

    def invoke(self, messages: list[AnyMessage]) -> dict:
        return asyncio.run(self.ainvoke(messages))

    async def ainvoke(self, messages: list[AnyMessage]) -> dict:
        final_state = await self._graph.ainvoke({"input_messages": messages})

        return final_state

    def stream(
        self,
        messages: list[AnyMessage],
    ) -> Generator[AnyMessage, None, None]:
        async def gen():
            async for message in self.astream(messages):
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
    ) -> AsyncGenerator[AnyMessage, None]:
        stream_response = self._graph.astream(
            {"input_messages": messages},
            stream_mode="updates",
        )

        async for node_event in stream_response:
            for node_output in node_event.values():
                for message in node_output.get("output_messages", []):
                    yield message
