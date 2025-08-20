import chainlit as cl

from src.models.chat import ChatMessage
from src.settings.services import webui_settings
from src.utils.assistant_client import AssistantClient


@cl.on_chat_start
async def on_chat_start():
    client = AssistantClient(
        base_url=webui_settings.assistant_base_url,
        invoke_endpoint=webui_settings.assistant_chat_invoke_endpoint,
        stream_endpoint=webui_settings.assistant_chat_stream_endpoint,
    )
    cl.user_session.set("client", client)
    cl.user_session.set("conversation_history", [])


async def _display_step(message: ChatMessage):
    step_name = message.role
    if message.role == "tool":
        step_name += " " + message.additional_kwargs.get("name", "")
    async with cl.Step(name=step_name) as step:
        step.input = message.pretty_content()


@cl.on_message
async def main(message: cl.Message):
    conversation_history = cl.user_session.get("conversation_history")
    client = cl.user_session.get("client")

    user_message = ChatMessage(
        role="user",
        content=message.content,
    )
    conversation_history.append(user_message)

    final_message = None
    async with client:
        async for response_message in client.async_stream_chat(
            conversation_history=conversation_history,
        ):
            await _display_step(response_message)
            final_message = response_message
            conversation_history.append(response_message)
    cl.user_session.set("conversation_history", conversation_history)

    await cl.Message(content=final_message.content).send()
