import time
import uuid

from fastapi import APIRouter, Depends, HTTPException, status

from src.general_assistant.api.dependency import get_workflow
from src.general_assistant.api.schemas.chat_schemas import (
    AssistantChatInput,
    AssistantChatOutput,
    ChatMessageSchema,
    SimpleAssistantChatInput,
)
from src.general_assistant.config.logger import create_logger
from src.general_assistant.config.settings import settings
from src.general_assistant.core.workflow import GeneralAssistantWorkflow

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
    "/chat_completions",
    response_model=AssistantChatOutput,
    summary="Create chat completion",
    description="Generate AI assistant response based on conversation history",
    status_code=status.HTTP_200_OK,
)
async def create_chat_completion(
    chat_input: AssistantChatInput,
    workflow: GeneralAssistantWorkflow = Depends(get_workflow),
) -> AssistantChatOutput:
    """
    Create a chat completion with the AI assistant.

    This endpoint processes a conversation history and generates an appropriate
    response from the AI assistant. The conversation history should include
    all previous messages in the conversation.

    Args:
        chat_input: Chat input containing conversation history

    Returns:
        AssistantChatOutput: The assistant's response

    Raises:
        HTTPException: For various error conditions
    """
    start_time = time.time()
    request_id = f"chat_{uuid.uuid4()}"

    try:
        logger.info(
            f"Processing chat completion request {request_id}",
            request_id=request_id,
            message_count=len(chat_input.conversation_history),
            user_message=(
                chat_input.get_current_user_message()[:100] + "..."
                if len(chat_input.get_current_user_message()) > 100
                else chat_input.get_current_user_message()
            ),
        )

        conversation_history = chat_input.get_llama_index_messages()

        try:
            output = await workflow.run(conversation_history=conversation_history)
        except Exception as workflow_error:
            error_type = type(workflow_error).__name__
            log_message = (
                f"Workflow execution failed for request {request_id}. "
                f"Error Type: {error_type}, Details: {str(workflow_error)}"
            )
            logger.error(log_message, exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=(
                    f"An error occurred while processing your chat request (ID: "
                    f"{request_id}). Type: {error_type}. Please try again later "
                    "or contact support if the issue persists."
                ),
            ) from workflow_error

        if not output or not isinstance(output, str):
            output_type = type(output).__name__
            log_message = (
                f"Invalid workflow output for request {request_id}. "
                f"Expected str, got {output_type}. Output: {str(output)[:200]}"
            )
            logger.error(log_message)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=(
                    f"The assistant generated an unexpected response format for your "
                    f"request (ID: {request_id})."
                ),
            )

        response = AssistantChatOutput(assistant_message=output)

        processing_time = time.time() - start_time
        logger.info(
            f"Chat completion successful for request {request_id}",
            request_id=request_id,
            processing_time_ms=int(processing_time * 1000),
            response_length=len(output),
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        error_type = type(e).__name__
        logger.error(
            f"Unexpected error processing chat request {request_id}: {str(e)}",
            request_id=request_id,
            error_type=error_type,
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                f"An unexpected internal error occurred while processing your request "
                f"(ID: {request_id}). Please try again later or contact support."
            ),
        ) from e


@router.post(
    "/simple_completion",
    response_model=AssistantChatOutput,
    summary="Simple one chat message",
    description="Send a single message to the assistant (convenience endpoint)",
    status_code=status.HTTP_200_OK,
)
async def send_simple_message(
    chat_input: SimpleAssistantChatInput,
    workflow: GeneralAssistantWorkflow = Depends(get_workflow),
) -> AssistantChatOutput:
    """
    Convenience endpoint for sending a single message without conversation history.

    Args:
        message: The user's message

    Returns:
        AssistantChatOutput: The assistant's response
    """
    chat_input = AssistantChatInput(
        conversation_history=[
            ChatMessageSchema(role="user", content=chat_input.message)
        ]
    )

    return await create_chat_completion(chat_input, workflow)
