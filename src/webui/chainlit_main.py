import chainlit as cl
from pydantic import ValidationError

from src.general_assistant.api.schemas.chat_schemas import ChatMessage
from src.general_assistant.config.settings import settings
from src.general_assistant.utils.assistant_client import AssistantClient


@cl.on_chat_start
async def on_chat_start():
    client = AssistantClient(
        base_url=settings.webui.assistant_base_url,
        invoke_endpoint=settings.webui.assistant_chat_invoke_endpoint,
        stream_endpoint=settings.webui.assistant_chat_stream_endpoint,
    )
    cl.user_session.set("client", client)
    cl.user_session.set("conversation_history", [])


async def create_user_message(message: cl.Message) -> tuple[ChatMessage | None, bool]:
    user_message, is_error = None, False

    try:
        user_message = ChatMessage(
            role="user",
            content=message.content,
        )
    except ValidationError as err:
        await cl.Message(
            content=(
                "❌ Error: There was an issue with your message "
                f"format - {err.errors()[0]['msg']}"
            ),
            author="System",
        ).send()
        is_error = True

    return user_message, is_error


async def plot_step(message: ChatMessage):
    step_name = message.role
    if message.role == "tool":
        step_name += " " + message.additional_kwargs.get("name", "")
    async with cl.Step(name=step_name) as step:
        step.input = message.content


@cl.on_message
async def main(message: cl.Message):
    conversation_history = cl.user_session.get("conversation_history")
    client = cl.user_session.get("client")

    user_message, is_error = await create_user_message(message)
    if is_error:
        return

    conversation_history.append(user_message)

    final_message = None
    async with client:
        async for response_message in client.async_stream_chat(
            conversation_history=conversation_history,
        ):
            await plot_step(response_message)
            final_message = response_message
            conversation_history.append(response_message)

    if final_message:
        await cl.Message(content=final_message.content).send()
    cl.user_session.set("conversation_history", conversation_history)
