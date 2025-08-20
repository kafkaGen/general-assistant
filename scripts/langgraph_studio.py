from langgraph.graph.state import CompiledStateGraph

from src.core.workflows import WorkflowFactory


def get_general_assistant_graph() -> CompiledStateGraph:
    workflow = WorkflowFactory.create_general_assistant()
    return workflow._graph


graph = get_general_assistant_graph()
