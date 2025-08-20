from langchain_core.tools import StructuredTool


def pretty_tools_formatting(tools: list[StructuredTool]) -> str:
    return "\n\n".join([f"\t{tool.name}: {tool.description}" for tool in tools])
