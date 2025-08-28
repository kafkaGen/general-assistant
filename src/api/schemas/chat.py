from langchain_core.messages import (
    AnyMessage,
)
from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.models.chat import ChatMessage


class ChatRequest(BaseModel):
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
                        "content": (
                            "Who did the actor who played Ray in the Polish-language "
                            "version of Everybody Loves Raymond play in Magda M.? Give "
                            "only the first name."
                        ),
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


class ChatInvokeResponse(BaseModel):
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
    def from_langchain_messages(
        cls, messages: list[AnyMessage]
    ) -> "ChatInvokeResponse":
        return cls(
            messages=[ChatMessage.from_langchain_message(msg) for msg in messages]
        )
