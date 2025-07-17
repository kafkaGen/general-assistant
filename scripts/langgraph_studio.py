from langgraph.graph.state import CompiledStateGraph

from src.general_assistant.config.settings import settings
from src.general_assistant.core.workflows import GeneralAssistantWorkflow


def get_general_assistant_workflow_graph() -> CompiledStateGraph:
    workflow = GeneralAssistantWorkflow(
        settings=settings.workflows,
    )
    return workflow.graph


graph = get_general_assistant_workflow_graph()
