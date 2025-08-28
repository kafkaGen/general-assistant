from typing import Any

from langchain.chat_models import init_chat_model
from langchain.prompts.chat import ChatPromptValue
from langchain_core.messages import AIMessage
from langsmith import Client as LangSmithClient
from pydantic import BaseModel

from src.settings.llms import ChatLLMSettings


class ChatLLM:
    def __init__(self, settings: ChatLLMSettings) -> None:
        self.settings = settings

        langsmith_client = LangSmithClient()
        self._chat_template = langsmith_client.pull_prompt(settings.prompt_id)

        self._default_llm = init_chat_model(
            model_provider=settings.model_provider,
            model=settings.model_name,
            temperature=settings.temperature,
        )
        if settings.structured_output:
            if settings.model_provider == "openai":
                self._llm = self._default_llm.with_structured_output(
                    settings.structured_output,
                    method="json_schema",
                    strict=True,
                    include_raw=True,
                )
            else:
                self._llm = self._default_llm.with_structured_output(
                    settings.structured_output,
                    include_raw=True,
                )
        elif settings.tools:
            if settings.model_provider == "openai":
                self._llm = self._default_llm.bind_tools(
                    settings.tools,
                    strict=True,
                )
            else:
                self._llm = self._default_llm.bind_tools(
                    settings.tools,
                )
        else:
            self._llm = self._default_llm

        self._chain = self._chat_template | self._llm

    def _build_chat_prompt(
        self,
        input: dict[str, Any] | None = None,
    ) -> ChatPromptValue:
        input = input or {}

        if set(input.keys()) != set(self._chat_template.input_variables):
            raise ValueError(
                f"Inputs for chat template {self.settings.prompt_id} must contain the "
                f"following variables: {self._chat_template.input_variables}. "
                f"Got: {set(input.keys())}"
            )
        chat_prompt = self._chat_template.invoke(input)

        return chat_prompt

    def invoke(
        self,
        input: dict[str, Any] | None = None,
    ) -> AIMessage | BaseModel:
        chat_prompt = self._build_chat_prompt(input)

        return self._llm.invoke(chat_prompt)

    async def ainvoke(
        self,
        input: dict[str, Any] | None = None,
    ) -> AIMessage | BaseModel:
        chat_prompt = self._build_chat_prompt(input)

        return await self._llm.ainvoke(chat_prompt)
