import ast
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

from src.general_assistant.api.schemas.chat_schemas import (
    ChatInput,
    ChatInvokeOutput,
    ChatMessage,
)
from src.general_assistant.config.logger import create_logger
from src.general_assistant.config.settings import settings


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

    logger = create_logger("assistant_client", console_level="INFO")

    def __init__(
        self,
        base_url: str,
        invoke_endpoint: str,
        stream_endpoint: str,
        timeout: float = settings.assistant_client.timeout,
    ) -> None:
        """
        Initialize AssistantClient.

        Args:
            base_url: Base URL of the assistant service
            invoke_endpoint: Chat invoke endpoint path
            stream_endpoint: Chat stream endpoint path
            timeout: Request timeout in seconds
        """
        self.invoke_url = f"{base_url.rstrip('/')}/{invoke_endpoint.strip('/')}"
        self.stream_url = f"{base_url.rstrip('/')}/{stream_endpoint.strip('/')}"
        self.timeout = timeout

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

    def _handle_chat_request_error(self, err: Exception) -> ChatMessage:
        """
        Handle errors from chat requests and return appropriate error response.

        Args:
            err: The exception that occurred during the request

        Returns:
            ChatMessage containing an error message
        """
        if isinstance(err, httpx.TimeoutException):
            self.logger.error(f"TimeoutException from assistant API: {err}")
            error_msg = ChatMessage(
                role="assistant",
                content=(
                    "I'm sorry, but there was an issue communicating with the "
                    f"assistant (Timeout after {self.timeout}s). Please try again "
                    "later. If the problem persists, please contact support."
                ),
            )
        elif isinstance(err, httpx.HTTPStatusError):
            # Handle streaming responses that can't be read
            try:
                response_text = err.response.text
            except Exception:
                response_text = "<response body not available>"

            self.logger.error(
                f"HTTPStatusError from assistant API: {err.response.status_code} - "
                f"Response: {response_text}"
            )
            error_msg = ChatMessage(
                role="assistant",
                content=(
                    "I'm sorry, but there was an issue communicating with the "
                    f"assistant (HTTP {err.response.status_code}). Please try "
                    "again later. If the problem persists, please contact "
                    "support."
                ),
            )
        elif isinstance(err, httpx.RequestError):
            self.logger.error(
                f"RequestError connecting to assistant API: {err}",
            )
            error_msg = ChatMessage(
                role="assistant",
                content=(
                    "I'm sorry, but I couldn't connect to the assistant service. "
                    "Please check your network connection and try again. If the "
                    "problem persists, please contact support."
                ),
            )
        else:
            self.logger.exception(
                f"Unexpected error in chat request. {err.__class__.__name__}: {err}"
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
            chunk: Raw chunk data from the stream

        Returns:
            ChatMessage with parsed content or error message if parsing failed
        """
        try:
            chunk = chunk.strip()
            if not chunk:
                # Return empty content message for empty chunks
                return ChatMessage(role="assistant", content="")

            try:
                data = json.loads(chunk)
            except json.JSONDecodeError:
                data = ast.literal_eval(chunk)

            return ChatMessage.model_validate(data)

        except (ValueError, SyntaxError, ValidationError) as e:
            self.logger.warning(f"Failed to parse stream chunk '{chunk[:100]}...': {e}")
            return ChatMessage(
                role="assistant",
                content="[ERROR: Message parsing failed]",
            )

    @retry(
        stop=stop_after_attempt(settings.assistant_client.retry_attempts),
        wait=wait_exponential(
            multiplier=1,
            min=settings.assistant_client.retry_min_delay,
            max=settings.assistant_client.retry_max_delay,
        ),
        reraise=True,
    )
    def _core_sync_chat_invoke(
        self,
        chat_input: ChatInput,
    ) -> ChatInvokeOutput:
        """
        Core synchronous chat request with retry logic.

        Args:
            chat_input: Validated chat input object

        Returns:
            ChatInvokeOutput from the API response
        """
        response = self._sync_client.post(
            self.invoke_url,
            json=chat_input.model_dump(),
        )
        response.raise_for_status()
        response = ChatInvokeOutput.model_validate(response.json())

        return response

    def invoke_chat(
        self,
        conversation_history: list[ChatMessage],
    ) -> ChatInvokeOutput:
        """
        Synchronous chat request method with retry logic.
        Must be used within sync context manager.

        Args:
            conversation_history: List of ChatMessage objects representing the
                complete conversation history including the user's latest message

        Returns:
            ChatInvokeOutput with assistant response messages
        """

        if not self._sync_client:
            raise RuntimeError(
                "Must use AssistantClient within 'with' statement for sync requests."
            )

        self._validate_conversation_history(conversation_history)

        try:
            chat_input = ChatInput(messages=conversation_history)
            response = self._core_sync_chat_invoke(chat_input)
        except Exception as err:
            err_msg = self._handle_chat_request_error(err)
            return ChatInvokeOutput(messages=[err_msg])

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
    async def _core_async_chat_invoke(
        self,
        chat_input: ChatInput,
    ) -> ChatInvokeOutput:
        """
        Core asynchronous chat request with retry logic.

        Args:
            chat_input: Validated chat input object

        Returns:
            ChatInvokeOutput from the API response
        """
        response = await self._async_client.post(
            self.invoke_url,
            json=chat_input.model_dump(),
        )
        response.raise_for_status()
        response = ChatInvokeOutput.model_validate(response.json())

        return response

    async def async_invoke_chat(
        self,
        conversation_history: list[ChatMessage],
    ) -> ChatInvokeOutput:
        """
        Asynchronous chat request method with retry logic.
        Must be used within async context manager.

        Args:
            conversation_history: List of ChatMessage objects representing the
                complete conversation history including the user's latest message

        Returns:
            ChatInvokeOutput with assistant response messages
        """

        if not self._async_client:
            raise RuntimeError(
                "Must use AssistantClient within 'async with' statement "
                "for async requests."
            )

        self._validate_conversation_history(conversation_history)

        try:
            chat_input = ChatInput(messages=conversation_history)
            response = await self._core_async_chat_invoke(chat_input)
        except Exception as err:
            err_msg = self._handle_chat_request_error(err)
            return ChatInvokeOutput(messages=[err_msg])

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
            chat_input = ChatInput(messages=conversation_history)

            with self._sync_client.stream(
                "POST",
                self.stream_url,
                json=chat_input.model_dump(),
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
            chat_input = ChatInput(messages=conversation_history)

            async with self._async_client.stream(
                "POST",
                self.stream_url,
                json=chat_input.model_dump(),
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
    ) -> list[ChatInvokeOutput | None]:
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
            - ChatInvokeOutput if the request was successful
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
                self.logger.exception(f"Error processing batch message: {str(e)}")
                responses.append(None)

        return responses

    async def async_batch_invoke_chat(
        self,
        conversation_histories: list[list[ChatMessage]],
    ) -> list[ChatInvokeOutput | None]:
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
            - ChatInvokeOutput if the request was successful
            - None if an error occurred for that specific request
            The order of results corresponds to the order of input conversation
            histories.
        """

        if not self._async_client:
            raise RuntimeError(
                "Must use AssistantClient within 'async with' statement "
                "for async batch requests."
            )

        # Create concurrent tasks for all requests
        tasks = []
        for conversation_history in conversation_histories:
            task = self.async_invoke_chat(conversation_history)
            tasks.append(task)

        # Execute all tasks concurrently and handle exceptions
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        # Convert exceptions to None and log errors
        processed_responses = []
        for resp in responses:
            if isinstance(resp, Exception):
                self.logger.exception(
                    f"Error processing async batch message: {str(resp)}"
                )
                processed_responses.append(None)
            else:
                processed_responses.append(resp)

        return processed_responses
