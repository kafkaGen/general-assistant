from langgraph.graph.state import CompiledStateGraph

from src.general_assistant.core.workflow import GeneralAssistantWorkflow


def get_general_assistant_workflow_graph() -> CompiledStateGraph:
    workflow = GeneralAssistantWorkflow()
    return workflow.graph


graph = get_general_assistant_workflow_graph()
