from src.core.llms import ChatLLM
from src.evaluation.evaluators.success_rate_evaluator import SuccessRateEvaluator
from src.evaluation.evaluators.trajectory_evaluator import TrajectoryEvaluator
from src.models.structured_output import (
    SuccessRateEvaluatorOutput,
    TrajectoryEvaluatorOutput,
)
from src.settings.llms import ChatLLMSettings


class EvaluatorFactory:
    @classmethod
    def create_success_rate_evaluator(cls) -> SuccessRateEvaluator:
        llm_judger = ChatLLM(
            settings=ChatLLMSettings(
                name="success-rate-evaluator-llm",
                prompt_id="success-rate-evaluator-prompt",
                structured_output=SuccessRateEvaluatorOutput,
            )
        )
        evaluator = SuccessRateEvaluator(
            llm_judger=llm_judger,
        )

        return evaluator

    @classmethod
    def create_trajectory_evaluator(cls) -> TrajectoryEvaluator:
        llm_judger = ChatLLM(
            settings=ChatLLMSettings(
                name="trajectory-evaluator-llm",
                prompt_id="trajectory-evaluator-prompt",
                structured_output=TrajectoryEvaluatorOutput,
            )
        )
        evaluator = TrajectoryEvaluator(
            llm_judger=llm_judger,
        )

        return evaluator
