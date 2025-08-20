import json
from typing import Any, Literal

from langchain_core.messages import (
    AIMessage,
    AnyMessage,
    HumanMessage,
    ToolMessage,
)
from pydantic import BaseModel, ConfigDict, Field


class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "tool"] = Field(
        ...,
        description="The role of the message sender",
    )
    content: str = Field(
        ...,
        description="The content of the message",
    )
    additional_kwargs: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional kwargs of the message",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "role": "user",
                "content": "Hello, how can you help me today?",
            },
        }
    )

    def to_langchain_message(self) -> AnyMessage:
        if self.role == "user":
            return HumanMessage(content=self.content)
        elif self.role == "assistant":
            return AIMessage(
                content=self.content,
                **self.additional_kwargs,
            )
        elif self.role == "tool":
            return ToolMessage(
                content=self.content,
                **self.additional_kwargs,
            )
        else:
            raise ValueError(f"Invalid role: {self.role}")

    @classmethod
    def from_langchain_message(cls, message: AnyMessage) -> "ChatMessage":
        if isinstance(message, HumanMessage):
            return cls(role="user", content=message.content)
        elif isinstance(message, AIMessage):
            additional_kwargs = (
                {"tool_calls": message.tool_calls} if message.tool_calls else {}
            )
            return cls(
                role="assistant",
                content=message.content,
                additional_kwargs=additional_kwargs,
            )
        elif isinstance(message, ToolMessage):
            return cls(
                role="tool",
                content=message.content,
                additional_kwargs={
                    "tool_call_id": message.tool_call_id,
                    "name": message.name,
                    "args": message.args,
                },
            )
        else:
            raise ValueError(f"Invalid message type: {type(message)}")

    def pretty_content(self) -> str:
        content = self.content

        tool_name, tool_args, tool_call_id = (
            self.additional_kwargs.get("name"),
            self.additional_kwargs.get("args"),
            self.additional_kwargs.get("tool_call_id"),
        )
        tool_calls = self.additional_kwargs.get("tool_calls")

        if tool_name:
            content = (
                f"Tool output {tool_name} (id: {tool_call_id})\n"
                f"Args: {json.dumps(tool_args, indent=4)}\n\n" + content
            )
        elif tool_calls:
            tool_calls_str = "\n\n".join(
                f"Tool call {tool_call['name']} (id: {tool_call['id']})\n"
                f"Args: {json.dumps(tool_call['args'], indent=4)}"
                for tool_call in tool_calls
            )
            content += f"\n\n{tool_calls_str}"

        return content.strip()
