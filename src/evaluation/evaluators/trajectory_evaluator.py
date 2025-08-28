from collections import Counter

from src.core.llms import ChatLLM


class TrajectoryEvaluator:
    def __init__(
        self,
        llm_judger: ChatLLM,
    ):
        self._llm_judger = llm_judger
        self._evaluator_name = "trajectory"

    def __call__(
        self,
        inputs: dict,
        outputs: dict,
        reference_outputs: dict,
    ) -> dict:
        response = self._llm_judger.invoke(
            input={
                "question": inputs["question"],
                "reference_trajectory": reference_outputs["trajectory"],
                "reference_tool_used": reference_outputs["tools_used"],
                "agent_trajectory": outputs["trajectory"],
            },
        )
        step_types = Counter(step.step_type for step in response["parsed"].steps)
        f1_score = (2 * step_types["tp"]) / (
            2 * step_types["tp"] + step_types["fp"] + step_types["fn"]
        )

        return {
            "key": self._evaluator_name,
            "score": f1_score,
            "evaluatorInfo": {
                "evaluated_steps": response["parsed"].steps,
                "tp": step_types.get("tp", 0),
                "fp": step_types.get("fp", 0),
                "fn": step_types.get("fn", 0),
            },
        }
