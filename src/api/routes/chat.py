import json
from collections.abc import AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from langchain_core.messages import AnyMessage

from src.api.dependency import get_general_assistant, get_logger
from src.api.schemas.chat import ChatInvokeResponse, ChatRequest
from src.core.workflows import GeneralAssistant
from src.models.chat import ChatMessage
from src.settings.services import api_settings
from src.utils.logger import Logger

router = APIRouter(
    prefix=f"/{api_settings.api_version}/chat",
    tags=["Chat"],
    responses={
        400: {"description": "Bad Request - Invalid input"},
        422: {"description": "Validation Error"},
        500: {"description": "Internal Server Error"},
    },
)


@router.post(
    "/chat_invoke",
    response_model=ChatInvokeResponse,
    summary="Invoke chat",
    description="Invoke chat with the AI assistant",
    status_code=status.HTTP_200_OK,
)
async def chat_invoke(
    chat_request: ChatRequest,
    general_assistant: GeneralAssistant = Depends(get_general_assistant),
    logger: Logger = Depends(get_logger),
) -> ChatInvokeResponse:
    """
    Invoke a chat with the AI assistant.

    This endpoint processes a chat input and generates an appropriate
    response from the AI assistant.

    Args:
        chat_request: Chat request containing messages

    Returns:
        ChatInvokeResponse: The assistant's response messages
    """

    try:
        messages = chat_request.to_langchain_messages()
        response = await general_assistant.ainvoke(messages=messages)
        response_messages = response["output_messages"]

        return ChatInvokeResponse.from_langchain_messages(response_messages)

    except Exception as e:
        error_type = type(e).__name__
        error_details = str(e)
        logger.error(
            f"Unexpected error processing chat invoke: {error_details}",
            error_type=error_type,
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": (
                    "An unexpected internal error occurred during chat invoke. "
                    "Please contact support."
                ),
                "error_type": error_type,
                "error_details": error_details,
            },
        ) from e


@router.post("/chat_stream")
async def chat_stream(
    chat_request: ChatRequest,
    general_assistant: GeneralAssistant = Depends(get_general_assistant),
    logger: Logger = Depends(get_logger),
) -> StreamingResponse:
    """
    Stream chat responses with real-time updates and final structured output.

    This endpoint streams intermediate results (tool calls, partial responses)
    and ends with a structured final result containing the complete response.
    """

    async def jsonl_stream_generator(
        messages: list[AnyMessage],
    ) -> AsyncGenerator[str, None]:
        try:
            async for message in general_assistant.astream(messages=messages):
                msg = ChatMessage.from_langchain_message(message)
                yield f"{msg.model_dump_json()}\n"

        except Exception as e:
            error_type = type(e).__name__
            error_details = str(e)
            logger.error(
                f"Unexpected error processing chat stream: {error_details}",
                error_type=error_type,
                exc_info=True,
            )
            error_dict = {
                "message": (
                    "An unexpected internal error occurred. Please contact support."
                ),
                "error_type": error_type,
                "error_details": error_details,
            }

            yield f"{json.dumps(error_dict)}\n"

    try:
        messages = chat_request.to_langchain_messages()

        return StreamingResponse(
            jsonl_stream_generator(messages=messages),
            media_type="application/x-ndjson",
            headers={
                "X-Accel-Buffering": "no",
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            },
        )

    except Exception as e:
        error_type = type(e).__name__
        error_details = str(e)
        logger.error(
            f"Unexpected error setting up streaming chat: {error_details}",
            error_type=error_type,
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": (
                    "An unexpected internal error occurred. Please contact support."
                ),
                "error_type": error_type,
                "error_details": error_details,
            },
        ) from e
