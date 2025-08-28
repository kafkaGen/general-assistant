from typing import Literal

from pydantic import BaseModel


class SuccessRateEvaluatorOutput(BaseModel):
    score: Literal[0, 50, 100]
    explanation: str


class TrajectoryStep(BaseModel):
    step_overview: str
    step_type: Literal["tp", "fp", "fn"]


class TrajectoryEvaluatorOutput(BaseModel):
    steps: list[TrajectoryStep]
