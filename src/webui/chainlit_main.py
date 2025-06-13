import chainlit as cl

from src.general_assistant.config.settings import settings
from src.general_assistant.utils.assistant_client import AssistantClient


@cl.on_chat_start
async def on_chat_start():
    """Initialize the assistant client and conversation history for the user session."""

    client = AssistantClient(
        base_url=settings.webui.assistant_base_url,
        chat_endpoint=settings.webui.assistant_chat_endpoint,
    )
    cl.user_session.set("client", client)
    cl.user_session.set("conversation_history", [])


@cl.on_message
async def main(message: cl.Message):
    conversation_history = cl.user_session.get("conversation_history")
    client = cl.user_session.get("client")

    # Show a "thinking" indicator to the user
    assistant_msg = cl.Message(content="Thinking...")
    await assistant_msg.send()

    async with client:
        response, conversation_history = await client.async_request_chat(
            user_message=message.content,
            conversation_history=conversation_history,
        )

    cl.user_session.set("conversation_history", conversation_history)

    assistant_msg.content = response.assistant_message
    await assistant_msg.update()
