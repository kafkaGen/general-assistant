import operator
from typing import Annotated, TypedDict

from langchain_core.messages import AnyMessage, HumanMessage
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

    async def prep_user_input(self, state: WorkflowState) -> dict:
        # TODO: add the user preprocessing here
        return {}

    async def invoke_general_agent(self, state: WorkflowState) -> dict:
        messages = state["messages"]
        response = await self.general_agent.ainvoke({"messages": messages})

        new_messages = response["messages"][len(messages) :]

        return {"messages": new_messages}

    def _build_graph(self) -> CompiledStateGraph:
        graph = StateGraph(WorkflowState)

        graph.add_node("prep_user_input", self.prep_user_input)
        graph.add_node("general_agent", self.invoke_general_agent)

        graph.add_edge(START, "prep_user_input")
        graph.add_edge("prep_user_input", "general_agent")
        graph.add_edge("general_agent", END)

        return graph.compile()

    async def run(self, messages: list[AnyMessage]) -> str:
        final_state = await self.graph.ainvoke({"messages": messages})

        for message in final_state["messages"]:
            message.pretty_print()

        last_message = final_state["messages"][-1]
        return last_message.content

    async def stream(self, messages: list[AnyMessage]) -> str:
        stream_response = self.graph.astream({"messages": messages})
        last_messages = []

        async for event in stream_response:
            for event_value in event.values():
                if event_value:
                    for message in event_value.get("messages", []):
                        message.pretty_print()
                        last_messages = event_value.get("messages", [])

        return last_messages[-1].content if last_messages else ""


# TODO: remove
if __name__ == "__main__":
    import asyncio

    from src.general_assistant.config.settings import AppSettings

    async def main():
        workflow = GeneralAssistantWorkflow(settings=AppSettings().workflows)
        messages: list[AnyMessage] = [
            HumanMessage(
                content=(
                    "Which place did NAVI team take in PGL Valahia season 5 "
                    "dota tournament?"
                ),
            ),
        ]
        # response = await workflow.run(messages=messages)
        response = await workflow.stream(messages=messages)
        print(f"Final response: {response}")

    asyncio.run(main())
