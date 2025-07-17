from collections.abc import AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from langchain_core.messages import AnyMessage

from src.general_assistant.api.dependency import get_workflow
from src.general_assistant.api.schemas.chat_schemas import (
    ChatInput,
    ChatInvokeOutput,
    ChatMessage,
)
from src.general_assistant.config.logger import create_logger
from src.general_assistant.config.settings import settings
from src.general_assistant.core.workflows import GeneralAssistantWorkflow

logger = create_logger("chat_api", settings.api.log_level)

router = APIRouter(
    prefix=f"/{settings.api.api_version}/chat",
    tags=["Chat"],
    responses={
        400: {"description": "Bad Request - Invalid input"},
        422: {"description": "Validation Error"},
        500: {"description": "Internal Server Error"},
    },
)


@router.post(
    "/chat_invoke",
    response_model=ChatInvokeOutput,
    summary="Invoke chat",
    description="Invoke chat with the AI assistant",
    status_code=status.HTTP_200_OK,
)
async def chat_invoke(
    chat_input: ChatInput,
    workflow: GeneralAssistantWorkflow = Depends(get_workflow),
) -> ChatInvokeOutput:
    """
    Invoke a chat with the AI assistant.

    This endpoint processes a chat input and generates an appropriate
    response from the AI assistant.

    Args:
        chat_input: Chat input containing messages

    Returns:
        ChatInvokeOutput: The assistant's response messages
    """

    try:
        messages = chat_input.to_langchain_messages()
        response_messages = await workflow.invoke(messages=messages)

        return ChatInvokeOutput.from_langchain_messages(response_messages)

    except HTTPException:
        raise
    except Exception as e:
        error_type = type(e).__name__
        logger.error(
            f"Unexpected error processing chat request: {str(e)}",
            error_type=error_type,
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "An unexpected internal error occurred while processing your request. "
                f"Type: {error_type}, details: {str(e)}. Please try again later or "
                "contact support."
            ),
        ) from e


@router.post("/chat_stream")
async def chat_stream(
    chat_input: ChatInput,
    workflow: GeneralAssistantWorkflow = Depends(get_workflow),
) -> StreamingResponse:
    """
    Stream chat responses with real-time updates and final structured output.

    This endpoint streams intermediate results (tool calls, partial responses)
    and ends with a structured final result containing the complete response.
    """

    async def jsonl_workflow_stream(
        messages: list[AnyMessage],
    ) -> AsyncGenerator[str, None]:
        try:
            async for message in workflow.stream(messages=messages):
                try:
                    msg = ChatMessage.from_langchain_message(message)
                    yield f"{msg.model_dump()}\n"
                except Exception as msg_error:
                    logger.warning(
                        f"Error processing message in stream: {str(msg_error)}",
                        error_type=type(msg_error).__name__,
                    )
                    error_msg = ChatMessage(
                        role="assistant",
                        content=(
                            f"[Error processing message: {type(msg_error).__name__}, "
                            f"details: {str(msg_error)}]"
                        ),
                    )
                    yield f"{error_msg.model_dump()}\n"

        except Exception as workflow_error:
            error_type = type(workflow_error).__name__
            logger.error(
                f"Workflow execution failed for streaming request. "
                f"Error Type: {error_type}, Details: {str(workflow_error)}",
                error_type=error_type,
                exc_info=True,
            )
            error_msg = ChatMessage(
                role="assistant",
                content=(
                    f"An error occurred while processing your request. "
                    f"Type: {error_type}, details: {str(workflow_error)}. Please try "
                    "again later or contact support if the issue persists."
                ),
            )
            yield f"{error_msg.model_dump()}\n"

    try:
        messages = chat_input.to_langchain_messages()

        return StreamingResponse(
            jsonl_workflow_stream(messages=messages),
            media_type="application/json",
            headers={
                "X-Accel-Buffering": "no",
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        error_type = type(e).__name__
        logger.error(
            f"Unexpected error in streaming chat request: {str(e)}",
            error_type=error_type,
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "An unexpected internal error occurred while setting up your streaming "
                f"request. Type: {error_type}, details: {str(e)}. Please try again "
                "later or contact support."
            ),
        ) from e
