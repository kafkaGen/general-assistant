import json
from typing import Literal

from langchain_core.messages import (
    AIMessage,
    AnyMessage,
    HumanMessage,
    ToolMessage,
)
from pydantic import BaseModel, ConfigDict, Field, field_validator


class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "tool"] = Field(
        ...,
        description="The role of the message sender",
    )
    content: str = Field(
        ...,
        min_length=1,
        description="The content of the message",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "role": "user",
                "content": "Hello, how can you help me today?",
            },
        }
    )

    @field_validator("content")
    @classmethod
    def content_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Content cannot be empty or whitespace only")
        return v.strip()

    def to_langchain_message(self) -> AnyMessage:
        if self.role == "user":
            return HumanMessage(content=self.content)
        elif self.role == "assistant":
            return AIMessage(content=self.content)
        elif self.role == "tool":
            return ToolMessage(content=self.content)
        else:
            raise ValueError(f"Invalid role: {self.role}")

    @classmethod
    def from_langchain_message(cls, message: AnyMessage) -> "ChatMessage":
        if isinstance(message, HumanMessage):
            return cls(role="user", content=message.content)
        elif isinstance(message, AIMessage):
            content = (message.content + "\n\n").strip()
            if message.tool_calls:
                tool_calls = [
                    f"{tool_call['name']}\n\n{json.dumps(tool_call['args'], indent=4)}"
                    for tool_call in message.tool_calls
                ]
                content += "\n\n".join(tool_calls)
            return cls(role="assistant", content=content)
        elif isinstance(message, ToolMessage):
            content = message.content
            try:
                if content[0] == "{" and content[-1] == "}":
                    content = json.dumps(json.loads(content), indent=4)
            except json.JSONDecodeError:
                pass
            return cls(role="tool", content=content)
        else:
            raise ValueError(f"Invalid message type: {type(message)}")


class ChatInput(BaseModel):
    """Input schema for chat requests."""

    messages: list[ChatMessage] = Field(
        default_factory=list,
        description="The messages in the conversation",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "messages": [
                    {
                        "role": "user",
                        "content": "Hello, how can you help me today?",
                    },
                ],
            }
        }
    )

    @field_validator("messages")
    @classmethod
    def validate_messages(cls, v: list[ChatMessage]) -> list[ChatMessage]:
        if not v:
            raise ValueError("Messages cannot be empty")

        if len(v) > 100:
            raise ValueError("Messages cannot be longer than 100 messages")

        return v

    def to_langchain_messages(self) -> list[AnyMessage]:
        return [msg.to_langchain_message() for msg in self.messages]


class ChatInvokeOutput(BaseModel):
    """Output schema for chat responses."""

    messages: list[ChatMessage] = Field(
        ..., description="The messages from the assistant"
    )

    @field_validator("messages")
    @classmethod
    def validate_messages(cls, v: list[ChatMessage]) -> list[ChatMessage]:
        if not v:
            raise ValueError("Messages cannot be empty")

        return v

    @classmethod
    def from_langchain_messages(cls, messages: list[AnyMessage]) -> "ChatInvokeOutput":
        return cls(
            messages=[ChatMessage.from_langchain_message(msg) for msg in messages]
        )
