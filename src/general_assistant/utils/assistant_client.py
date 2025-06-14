import asyncio
from typing import Any

import httpx
from pydantic import ValidationError
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
)

from src.general_assistant.api.schemas.chat_schemas import (
    AssistantChatInput,
    AssistantChatOutput,
    ChatMessageSchema,
)
from src.general_assistant.config.logger import create_logger
from src.general_assistant.config.settings import settings


class AssistantClient:
    """
    Assistant client that works as both sync and async context manager.
    Handles HTTP client lifecycle, resource management, and robust error handling.
    """

    logger = create_logger("assistant_client", console_level="INFO")

    def __init__(
        self,
        base_url: str,
        chat_endpoint: str,
        timeout: float | None = None,
    ) -> None:
        """
        Initialize AssistantClient.

        Args:
            base_url: Base URL of the assistant service
            chat_endpoint: Chat endpoint path
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.chat_endpoint = chat_endpoint.strip("/")
        self.chat_url = f"{self.base_url}/{self.chat_endpoint}"
        self.timeout = timeout or settings.assistant_client.timeout

        # HTTP clients (will be initialized in context managers)
        self._sync_client: httpx.Client | None = None
        self._async_client: httpx.AsyncClient | None = None

    def __enter__(self) -> "AssistantClient":
        """Enter sync context manager - initialize sync HTTP client."""

        self._sync_client = httpx.Client(timeout=self.timeout)
        return self

    def __exit__(
        self, exc_type: type | None, exc_val: Exception | None, exc_tb: Any | None
    ) -> None:
        """Exit sync context manager - cleanup sync HTTP client."""

        if self._sync_client:
            self._sync_client.close()
            self._sync_client = None

    async def __aenter__(self) -> "AssistantClient":
        """Enter async context manager - initialize async HTTP client."""

        self._async_client = httpx.AsyncClient(timeout=self.timeout)
        return self

    async def __aexit__(
        self, exc_type: type | None, exc_val: Exception | None, exc_tb: Any | None
    ) -> None:
        """Exit async context manager - cleanup async HTTP client."""

        if self._async_client:
            await self._async_client.aclose()
            self._async_client = None

    def _prepare_chat_input(
        self, message: str, conversation_history: list[ChatMessageSchema]
    ) -> tuple[AssistantChatInput, None] | tuple[None, AssistantChatOutput]:
        """
        Validates the user message and prepares the chat input object.

        This method does NOT mutate the original conversation_history.

        Returns:
            A tuple of (AssistantChatInput, None) on success,
            or (None, AssistantChatOutput) on validation failure.
        """
        error_response = None
        chat_input = None

        try:
            # Create a new history list to avoid mutating the original
            new_history = conversation_history + [
                ChatMessageSchema(role="user", content=message)
            ]
            chat_input = AssistantChatInput(
                conversation_history=new_history,
            )
        except ValidationError as err:
            self.logger.error(f"Validation error preparing chat input: {err}")
            error_response = AssistantChatOutput(
                assistant_message=(
                    "ERROR. There was an issue with your message "
                    f"format: {err.errors()[0]['msg']}"
                )
            )
        except Exception as err:
            self.logger.error(f"Unexpected error preparing chat input: {err}")
            error_response = AssistantChatOutput(
                assistant_message=(
                    "An unexpected error occurred while processing your message. "
                    "Please try again. If the issue continues, please report it."
                )
            )

        return chat_input, error_response

    def _handle_chat_request_error(self, err: Exception) -> AssistantChatOutput:
        if isinstance(err, httpx.TimeoutException):
            self.logger.error(f"TimeoutException from assistant API: {err}")
            error_msg = (
                "I'm sorry, but there was an issue communicating with the assistant "
                f"(Timeout after {self.timeout}s). Please try again later. If the "
                "problem persists, please contact support."
            )
            response = AssistantChatOutput(assistant_message=error_msg)
        elif isinstance(err, httpx.HTTPStatusError):
            self.logger.error(
                f"HTTPStatusError from assistant API: {err.response.status_code} - "
                f"Response: {err.response.text}"
            )
            error_msg = (
                "I'm sorry, but there was an issue communicating with the assistant "
                f"(HTTP {err.response.status_code}). Please try again later. If the "
                "problem persists, please contact support."
            )
            response = AssistantChatOutput(assistant_message=error_msg)
        elif isinstance(err, httpx.RequestError):
            self.logger.error(
                f"RequestError connecting to assistant API: {err}",
            )
            error_msg = (
                "I'm sorry, but I couldn't connect to the assistant service. "
                "Please check your network connection and try again. If the "
                "problem persists, please contact support."
            )
            response = AssistantChatOutput(assistant_message=error_msg)
        elif isinstance(err, Exception):
            self.logger.exception("Unexpected error in get_assistant_response.")
            error_msg = (
                "An unexpected error occurred while trying to get a response. "
                "Please try again. If the issue continues, please report it."
            )
            response = AssistantChatOutput(assistant_message=error_msg)

        return response

    @retry(
        stop=stop_after_attempt(settings.assistant_client.retry_attempts),
        wait=wait_exponential(
            multiplier=1,
            min=settings.assistant_client.retry_min_delay,
            max=settings.assistant_client.retry_max_delay,
        ),
        reraise=True,
    )
    def _core_sync_chat_request(
        self,
        chat_input: AssistantChatInput,
    ) -> AssistantChatOutput:
        response = self._sync_client.post(
            self.chat_url,
            json=chat_input.model_dump(),
        )
        response.raise_for_status()
        response = AssistantChatOutput.model_validate(response.json())

        return response

    def request_chat(
        self,
        user_message: str,
        conversation_history: list[ChatMessageSchema],
    ) -> tuple[AssistantChatOutput, list[ChatMessageSchema]]:
        """
        Synchronous chat request method with retry logic.
        Must be used within sync context manager.

        Args:
            user_message: User message
            conversation_history: Conversation history

        Returns:
            Tuple of AssistantChatOutput with assistant response text or error
            message and updated conversation history.
        """

        if not self._sync_client:
            raise RuntimeError(
                "Must use AssistantClient within 'with' statement for sync requests."
            )

        chat_input, error_response = self._prepare_chat_input(
            user_message,
            conversation_history,
        )
        if error_response:
            # Return original history, as it was not modified
            return error_response, conversation_history

        try:
            response = self._core_sync_chat_request(chat_input)
        except Exception as err:
            response = self._handle_chat_request_error(err)
        else:
            conversation_history.extend(
                [
                    ChatMessageSchema(role="user", content=user_message),
                    ChatMessageSchema(
                        role="assistant", content=response.assistant_message
                    ),
                ]
            )

        return response, conversation_history

    @retry(
        stop=stop_after_attempt(settings.assistant_client.retry_attempts),
        wait=wait_exponential(
            multiplier=1,
            min=settings.assistant_client.retry_min_delay,
            max=settings.assistant_client.retry_max_delay,
        ),
        reraise=True,
    )
    async def _core_async_chat_request(
        self,
        chat_input: AssistantChatInput,
    ) -> AssistantChatOutput:
        response = await self._async_client.post(
            self.chat_url,
            json=chat_input.model_dump(),
        )
        response.raise_for_status()
        response = AssistantChatOutput.model_validate(response.json())

        return response

    async def async_request_chat(
        self,
        user_message: str,
        conversation_history: list[ChatMessageSchema],
    ) -> tuple[AssistantChatOutput, list[ChatMessageSchema]]:
        """
        Asynchronous chat request method with retry logic.
        Must be used within async context manager.

        Args:
            user_message: Message to send to the assistant
            conversation_history: Conversation history

        Returns:
            Tuple of AssistantChatOutput with assistant response text or error
            message and updated conversation history.
        """

        if not self._async_client:
            raise RuntimeError(
                "Must use AssistantClient within 'async with' statement "
                "for async requests."
            )

        chat_input, error_response = self._prepare_chat_input(
            user_message,
            conversation_history,
        )
        if error_response:
            # Return original history, as it was not modified
            return error_response, conversation_history

        try:
            response = await self._core_async_chat_request(chat_input)
        except Exception as err:
            response = self._handle_chat_request_error(err)
        else:
            conversation_history.extend(
                [
                    ChatMessageSchema(role="user", content=user_message),
                    ChatMessageSchema(
                        role="assistant", content=response.assistant_message
                    ),
                ]
            )

        return response, conversation_history

    def batch_request_chat(
        self,
        messages: list[str],
        conversation_histories: list[list[ChatMessageSchema]],
    ) -> list[tuple[AssistantChatOutput, list[ChatMessageSchema]] | None]:
        """
        Synchronously processes a batch of chat requests.

        Each message is processed sequentially. If an error occurs for a specific
        message, its corresponding entry in the returned list will be None, and
        the error will be logged.

        Args:
            messages: A list of user message strings.
            conversation_histories: A list of conversation histories. Each history
                is a list of ChatMessageSchema objects. The length of this list
                must match the length of the `messages` list.

        Returns:
            A list where each element is either:
            - A tuple containing (AssistantChatOutput, updated_conversation_history)
              if the request was successful.
            - None if an error occurred for that specific request.
            The order of results corresponds to the order of input messages.
        """

        if not self._sync_client:
            raise RuntimeError(
                "Must use AssistantClient within 'with' statement for "
                "sync batch requests."
            )

        # Validate conversation_histories length if provided
        if len(conversation_histories) != len(messages):
            raise ValueError(
                f"Mismatch in lengths: 'messages' has length {len(messages)}, "
                "but 'conversation_histories' has length "
                f"{len(conversation_histories)}. Both lists must have the same "
                "number of elements."
            )

        responses = []
        for message, conversation_history in zip(
            messages, conversation_histories, strict=True
        ):
            try:
                response, conversation_history = self.request_chat(
                    message, conversation_history
                )
                responses.append((response, conversation_history))
            except Exception as e:
                self.logger.error(f"Error processing batch message {message}: {str(e)}")
                responses.append(None)

        return responses

    async def async_batch_request_chat(
        self,
        messages: list[str],
        conversation_histories: list[list[ChatMessageSchema]],
    ) -> list[tuple[AssistantChatOutput, list[ChatMessageSchema]] | None]:
        """
        Asynchronously processes a batch of chat requests.

        All messages are processed concurrently. If an error occurs for a specific
        message, its corresponding entry in the returned list will be None, and
        the error will be logged.

        Args:
            messages: A list of user message strings.
            conversation_histories: A list of conversation histories. Each history
                is a list of ChatMessageSchema objects. The length of this list
                must match the length of the `messages` list.

        Returns:
            A list where each element is either:
            - A tuple containing (AssistantChatOutput, updated_conversation_history)
              if the request was successful.
            - None if an error occurred for that specific request.
            The order of results corresponds to the order of input messages.
        """

        if not self._async_client:
            raise RuntimeError(
                "Must use AssistantClient within 'async with' statement "
                "for async batch requests."
            )

        # Validate conversation_histories length if provided
        if len(conversation_histories) != len(messages):
            raise ValueError(
                f"Mismatch in lengths: 'messages' has length {len(messages)}, "
                "but 'conversation_histories' has length "
                f"{len(conversation_histories)}. Both lists must have the same "
                "number of elements."
            )

        # Create concurrent tasks for all requests
        tasks = []
        for message, conversation_history in zip(
            messages, conversation_histories, strict=True
        ):
            task = self.async_request_chat(message, conversation_history)
            tasks.append(task)

        # Execute all tasks concurrently and handle exceptions
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        # Convert exceptions to None and log errors
        processed_responses = []
        for i, resp in enumerate(responses):
            if isinstance(resp, Exception):
                self.logger.error(
                    f"Error processing async batch message {messages[i]}: {str(resp)}"
                )
                processed_responses.append(None)
            else:
                processed_responses.append(resp)

        return processed_responses
