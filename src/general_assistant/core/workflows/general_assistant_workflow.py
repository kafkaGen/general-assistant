import operator
from collections.abc import AsyncGenerator
from typing import Annotated, TypedDict

from langchain_core.messages import AnyMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from src.general_assistant.config.settings import WorkflowsSettings
from src.general_assistant.core.agent import AgentFactory


class WorkflowState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]


class GeneralAssistantWorkflow:
    def __init__(self, settings: WorkflowsSettings) -> None:
        agent_factory = AgentFactory(settings=settings)

        self.general_agent = agent_factory.get_general_agent()
        self.graph = self._build_graph()

    async def invoke_general_agent(self, state: WorkflowState) -> dict:
        messages = state["messages"]
        response = await self.general_agent.ainvoke({"messages": messages})

        new_messages = response["messages"][len(messages) :]

        return {"messages": new_messages}

    def _build_graph(self) -> CompiledStateGraph:
        graph = StateGraph(WorkflowState)

        graph.add_node("general_agent", self.invoke_general_agent)

        graph.add_edge(START, "general_agent")
        graph.add_edge("general_agent", END)

        return graph.compile()

    async def invoke(self, messages: list[AnyMessage]) -> list[AnyMessage]:
        final_state = await self.graph.ainvoke({"messages": messages})
        output_messages = final_state["messages"][len(messages) :]

        return output_messages

    async def stream(
        self, messages: list[AnyMessage]
    ) -> AsyncGenerator[AnyMessage, None]:
        stream_response = self.graph.astream(
            {"messages": messages},
            stream_mode="updates",
            subgraphs=True,
        )

        async for _, node_event in stream_response:
            for node_event_value in node_event.values():
                for message in node_event_value.get("messages", []):
                    yield message
