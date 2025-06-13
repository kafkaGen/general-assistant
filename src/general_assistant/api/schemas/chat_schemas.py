from typing import Literal

from llama_index.core.base.llms.types import ChatMessage
from pydantic import BaseModel, ConfigDict, Field, field_validator


class ChatMessageSchema(BaseModel):
    role: Literal["user", "assistant", "system"] = Field(
        ...,
        description="The role of the message sender",
    )
    content: str = Field(
        ...,
        min_length=1,
        max_length=10000,
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

    def to_llama_index_message(self) -> ChatMessage:
        """Convert to LlamaIndex ChatMessage format."""
        return ChatMessage(role=self.role, content=self.content)


class AssistantChatInput(BaseModel):
    """Input schema for assistant chat requests."""

    conversation_history: list[ChatMessageSchema] = Field(
        default_factory=list,
        max_items=100,  # Prevent extremely long conversations
        description="The conversation history including the current user message",
    )
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "conversation_history": [
                    {
                        "role": "user",
                        "content": "Hello, how can you help me today?",
                    },
                ],
            }
        }
    )

    @field_validator("conversation_history")
    def validate_conversation_history(
        cls, v: list[ChatMessageSchema]
    ) -> list[ChatMessageSchema]:
        if not v:
            raise ValueError("Conversation history cannot be empty")

        # Ensure last message is from user
        if v[-1].role != "user":
            raise ValueError("Last message must be from user")

        return v

    def get_llama_index_messages(self) -> list[ChatMessage]:
        """Convert to LlamaIndex ChatMessage format."""
        return [msg.to_llama_index_message() for msg in self.conversation_history]

    def get_current_user_message(self) -> str:
        """Get the latest user message."""
        for msg in reversed(self.conversation_history):
            if msg.role == "user":
                return msg.content
        raise ValueError("No user message found in conversation history")


class SimpleAssistantChatInput(BaseModel):
    message: str = Field(..., description="The user's message")


class AssistantChatOutput(BaseModel):
    """Output schema for assistant chat responses."""

    assistant_message: str = Field(..., description="The assistant's response message")

    @field_validator("assistant_message")
    @classmethod
    def assistant_message_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Assistant message cannot be empty or whitespace only")
        return v.strip()
