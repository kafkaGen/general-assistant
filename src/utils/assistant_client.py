import asyncio
import json
from collections.abc import AsyncGenerator, Generator
from typing import Any

import httpx
from pydantic import ValidationError
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
)

from src.api.schemas.chat import ChatInvokeResponse, ChatRequest
from src.models.chat import ChatMessage
from src.settings.services import assistant_client_settings
from src.utils.logger import create_logger


class AssistantClient:
    """
    HTTP client for the General Assistant API with sync and async support.

    This client handles HTTP communication with the General Assistant API endpoints,
    providing both invoke (request-response) and streaming modes. Conversation
    management is handled client-side - you must provide complete conversation
    history as ChatMessage objects.

    Architecture:
    - Pure HTTP client - no conversation state management
    - Client-side conversation building with ChatMessage objects
    - Comprehensive error handling and retry logic
    - Support for both sync and async operations
    - Streaming and non-streaming modes

    Features:
    - Sync and async context management
    - Invoke mode: Traditional request-response chat
    - Streaming mode: Real-time message streaming (sync and async)
    - Automatic retry logic with exponential backoff
    - Comprehensive error handling and logging
    - Batch request processing (sync and async)
    - Input validation and sanitization

    Usage:
        # Sync invoke
        with AssistantClient(base_url, invoke_endpoint, stream_endpoint) as client:
            messages = [ChatMessage(role="user", content="Hello")]
            response = client.invoke_chat(messages)

        # Async streaming
        async with AssistantClient(
            base_url,
            invoke_endpoint,
            stream_endpoint,
        ) as client:
            messages = [ChatMessage(role="user", content="Hello")]
            async for message in client.async_stream_chat(messages):
                print(message.content)
    """

    logger = create_logger(
        "assistant_client",
        console_level=assistant_client_settings.console_log_level,
        file_level=assistant_client_settings.file_log_level,
    )

    def __init__(
        self,
        base_url: str,
        invoke_endpoint: str,
        stream_endpoint: str,
        timeout: float = assistant_client_settings.timeout,
    ) -> None:
        """
        Initialize AssistantClient.

        Args:
            base_url: Base URL of the assistant service
            invoke_endpoint: Chat invoke endpoint path
            stream_endpoint: Chat stream endpoint path
            timeout: Request timeout in seconds
        """
        self.invoke_url = self._prepare_url(base_url, invoke_endpoint)
        self.stream_url = self._prepare_url(base_url, stream_endpoint)
        self.timeout = timeout

        # HTTP clients (will be initialized in context managers)
        self._sync_client: httpx.Client | None = None
        self._async_client: httpx.AsyncClient | None = None

    def _prepare_url(self, base_url: str, endpoint: str) -> str:
        return f"{base_url.rstrip('/')}/{endpoint.strip('/')}"

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

    def _handle_chat_request_error(self, err: Exception) -> ChatMessage:
        """
        Handle errors from chat requests and return appropriate error response.

        Args:
            err: The exception that occurred during the request

        Returns:
            ChatMessage containing an error message
        """

        if isinstance(err, httpx.TimeoutException | httpx.RequestError):
            self.logger.error(f"Network error connecting to assistant API: {err}")
            error_msg = ChatMessage(
                role="assistant",
                content=(
                    "I'm sorry, but I couldn't connect to the assistant service. "
                    "This could be a network issue or a timeout. Please check your "
                    "connection and try again."
                ),
            )
        elif isinstance(err, httpx.HTTPStatusError):
            try:
                response_json = err.response.json()
                detail = response_json.get("detail", {})

                if isinstance(detail, dict):
                    error_type = detail.get("error_type", "Unknown")
                    error_details = detail.get("error_details", "No details provided.")
                    message = detail.get("message", "No message provided.")

                    content = (
                        f"{message} (Error: {error_type}). Details: {error_details}."
                    )
                else:
                    # Fallback for unexpected or string-based error details
                    content = f"The assistant returned an unexpected error: {detail}"

                log_message = (
                    "HTTPStatusError from assistant API: "
                    f"{err.response.status_code} - Detail: {detail}"
                )
            except json.JSONDecodeError:
                content = (
                    f"The assistant service returned an unreadable error "
                    f"(HTTP {err.response.status_code})."
                )
                log_message = (
                    f"HTTPStatusError from assistant API: "
                    f"{err.response.status_code} - Response: {err.response.text}"
                )

            self.logger.error(log_message)
            error_msg = ChatMessage(role="assistant", content=content)
        else:
            self.logger.exception(
                f"Unexpected error in assistant API: {err.__class__.__name__}: {err}",
            )
            error_msg = ChatMessage(
                role="assistant",
                content=(
                    "An unexpected error occurred while trying to get a response. "
                    "Please try again. If the issue continues, please report it."
                ),
            )

        return error_msg

    def _validate_conversation_history(
        self, conversation_history: list[ChatMessage]
    ) -> None:
        """
        Validate conversation history before processing.

        Args:
            conversation_history: List of ChatMessage objects to validate

        Raises:
            ValueError: If conversation history is invalid
        """
        if not conversation_history:
            raise ValueError(
                "Conversation history cannot be empty. Please provide at least "
                "one message."
            )

        # Additional validation could be added here if needed
        # e.g., checking for alternating roles, valid message types, etc.

    def _parse_stream_chunk(self, chunk: str) -> ChatMessage:
        """
        Parse a streaming chunk into a ChatMessage with robust error handling.

        Args:
            chunk: Raw JSON string data from the stream.

        Returns:
            ChatMessage with parsed content or an error message if parsing failed.
        """
        try:
            data = json.loads(chunk)

            if isinstance(data, dict) and "error_type" in data:
                error_type = data.get("error_type", "Unknown")
                error_details = data.get("error_details", "No details provided.")
                return ChatMessage(
                    role="assistant",
                    content=f"[STREAM ERROR: {error_type}] | {error_details}",
                )

            return ChatMessage.model_validate(data)

        except (json.JSONDecodeError, ValidationError) as e:
            self.logger.warning(
                f"Failed to parse stream chunk. Error: {e}. Chunk: '{chunk[:100]}...'"
            )
            return ChatMessage(
                role="assistant",
                content=(
                    "[CLIENT PARSING ERROR: Could not process an incoming "
                    f"message. Raw data: {chunk[:100]}...]"
                ),
            )

    @retry(
        stop=stop_after_attempt(assistant_client_settings.retry_attempts),
        wait=wait_exponential(
            multiplier=1,
            min=assistant_client_settings.retry_min_delay,
            max=assistant_client_settings.retry_max_delay,
        ),
        reraise=True,
    )
    def _core_sync_chat_invoke(
        self,
        chat_request: ChatRequest,
    ) -> ChatInvokeResponse:
        """
        Core synchronous chat request with retry logic.

        Args:
            chat_request: Validated chat input object

        Returns:
            ChatInvokeResponse from the API response
        """
        response = self._sync_client.post(
            self.invoke_url,
            json=chat_request.model_dump(),
        )
        response.raise_for_status()
        response = ChatInvokeResponse.model_validate(response.json())

        return response

    def invoke_chat(
        self,
        conversation_history: list[ChatMessage],
    ) -> ChatInvokeResponse:
        """
        Synchronous chat request method with retry logic.
        Must be used within sync context manager.

        Args:
            conversation_history: List of ChatMessage objects representing the
                complete conversation history including the user's latest message

        Returns:
            ChatInvokeResponse with assistant response messages
        """

        if not self._sync_client:
            raise RuntimeError(
                "Must use AssistantClient within 'with' statement for sync requests."
            )

        self._validate_conversation_history(conversation_history)

        try:
            chat_request = ChatRequest(messages=conversation_history)
            response = self._core_sync_chat_invoke(chat_request)
        except Exception as err:
            err_msg = self._handle_chat_request_error(err)
            return ChatInvokeResponse(messages=[err_msg])

        return response

    @retry(
        stop=stop_after_attempt(assistant_client_settings.retry_attempts),
        wait=wait_exponential(
            multiplier=1,
            min=assistant_client_settings.retry_min_delay,
            max=assistant_client_settings.retry_max_delay,
        ),
        reraise=True,
    )
    async def _core_async_chat_invoke(
        self,
        chat_request: ChatRequest,
    ) -> ChatInvokeResponse:
        """
        Core asynchronous chat request with retry logic.

        Args:
            chat_request: Validated chat input object

        Returns:
            ChatInvokeResponse from the API response
        """
        response = await self._async_client.post(
            self.invoke_url,
            json=chat_request.model_dump(),
        )
        response.raise_for_status()
        response = ChatInvokeResponse.model_validate(response.json())

        return response

    async def async_invoke_chat(
        self,
        conversation_history: list[ChatMessage],
    ) -> ChatInvokeResponse:
        """
        Asynchronous chat request method with retry logic.
        Must be used within async context manager.

        Args:
            conversation_history: List of ChatMessage objects representing the
                complete conversation history including the user's latest message

        Returns:
            ChatInvokeResponse with assistant response messages
        """

        if not self._async_client:
            raise RuntimeError(
                "Must use AssistantClient within 'async with' statement "
                "for async requests."
            )

        self._validate_conversation_history(conversation_history)

        try:
            chat_request = ChatRequest(messages=conversation_history)
            response = await self._core_async_chat_invoke(chat_request)
        except Exception as err:
            err_msg = self._handle_chat_request_error(err)
            return ChatInvokeResponse(messages=[err_msg])

        return response

    def stream_chat(
        self,
        conversation_history: list[ChatMessage],
    ) -> Generator[ChatMessage, None]:
        """
        Synchronous chat streaming method.
        Must be used within sync context manager.

        Args:
            conversation_history: List of ChatMessage objects representing the
                complete conversation history including the user's latest message

        Yields:
            ChatMessage objects as they are received from the stream
        """

        if not self._sync_client:
            raise RuntimeError(
                "Must use AssistantClient within 'with' statement for sync streaming."
            )

        self._validate_conversation_history(conversation_history)

        try:
            chat_request = ChatRequest(messages=conversation_history)

            with self._sync_client.stream(
                "POST",
                self.stream_url,
                json=chat_request.model_dump(),
            ) as response:
                response.raise_for_status()

                for chunk in response.iter_lines():
                    message = self._parse_stream_chunk(chunk)
                    yield message

        except Exception as err:
            err_msg = self._handle_chat_request_error(err)
            yield err_msg

    async def async_stream_chat(
        self,
        conversation_history: list[ChatMessage],
    ) -> AsyncGenerator[ChatMessage, None]:
        """
        Asynchronous chat streaming method.
        Must be used within async context manager.

        Args:
            conversation_history: List of ChatMessage objects representing the
                complete conversation history including the user's latest message

        Yields:
            ChatMessage objects as they are received from the stream
        """
        if not self._async_client:
            raise RuntimeError(
                "Must use AssistantClient within 'async with' statement "
                "for async streaming requests."
            )

        self._validate_conversation_history(conversation_history)

        try:
            chat_request = ChatRequest(messages=conversation_history)

            async with self._async_client.stream(
                "POST",
                self.stream_url,
                json=chat_request.model_dump(),
            ) as response:
                response.raise_for_status()

                async for chunk in response.aiter_lines():
                    message = self._parse_stream_chunk(chunk)
                    yield message

        except Exception as err:
            err_msg = self._handle_chat_request_error(err)
            yield err_msg

    def batch_invoke_chat(
        self,
        conversation_histories: list[list[ChatMessage]],
    ) -> list[ChatInvokeResponse | None]:
        """
        Synchronously processes a batch of chat requests.

        Each conversation history is processed sequentially. If an error occurs for
        a specific conversation history, its corresponding entry in the returned list
        will be None, and the error will be logged.

        Args:
            conversation_histories: A list of conversation histories. Each history
                is a list of ChatMessage objects representing a complete conversation.

        Returns:
            A list where each element is either:
            - ChatInvokeResponse if the request was successful
            - None if an error occurred for that specific request
            The order of results corresponds to the order of input conversation
            histories.
        """

        if not self._sync_client:
            raise RuntimeError(
                "Must use AssistantClient within 'with' statement for "
                "sync batch requests."
            )

        responses = []
        for conversation_history in conversation_histories:
            try:
                response = self.invoke_chat(conversation_history)
                responses.append(response)
            except Exception as e:
                self.logger.exception(
                    f"Error processing batch message. Error: {e.__class__.__name__}: "
                    f"{e}"
                )
                responses.append(None)

        return responses

    async def async_batch_invoke_chat(
        self,
        conversation_histories: list[list[ChatMessage]],
    ) -> list[ChatInvokeResponse | None]:
        """
        Asynchronously processes a batch of chat requests.

        All conversation histories are processed concurrently. If an error occurs
        for a specific conversation history, its corresponding entry in the returned
        list will be None, and the error will be logged.

        Args:
            conversation_histories: A list of conversation histories. Each history
                is a list of ChatMessage objects representing a complete conversation.

        Returns:
            A list where each element is either:
            - ChatInvokeResponse if the request was successful
            - None if an error occurred for that specific request
            The order of results corresponds to the order of input conversation
            histories.
        """

        if not self._async_client:
            raise RuntimeError(
                "Must use AssistantClient within 'async with' statement "
                "for async batch requests."
            )

        tasks = []
        for conversation_history in conversation_histories:
            task = self.async_invoke_chat(conversation_history)
            tasks.append(task)
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        processed_responses = []
        for resp in responses:
            if isinstance(resp, Exception):
                self.logger.exception(
                    f"Error processing async batch message. Error: "
                    f"{resp.__class__.__name__}: {resp}"
                )
                processed_responses.append(None)
            else:
                processed_responses.append(resp)

        return processed_responses
