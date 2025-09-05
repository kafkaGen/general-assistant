from pydantic import BaseModel


class LLMConfig(BaseModel):
    model: str
    temperature: float | None = None
    max_tokens: int | None = None


class GeneralAgentConfiguration(BaseModel):
    max_agent_steps: int
    agent_llm: LLMConfig
    reflection_llm: LLMConfig


class AgentsConfiguration(BaseModel):
    general_agent: GeneralAgentConfiguration
