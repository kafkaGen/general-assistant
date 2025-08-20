from src.core.llms import ChatLLM


class SuccessRateEvaluator:
    def __init__(
        self,
        llm_judger: ChatLLM,
    ):
        self._llm_judger = llm_judger
        self._evaluator_name = "success_rate"

    def __call__(
        self,
        inputs: dict,
        outputs: dict,
        reference_outputs: dict,
    ) -> dict:
        response = self._llm_judger.invoke(
            input={
                "question": inputs["question"],
                "reference_answer": reference_outputs["answer"],
                "agent_answer": outputs["answer"],
            },
        )

        return {
            "key": self._evaluator_name,
            "score": response["parsed"].score,
            "evaluatorInfo": {
                "explanation": response["parsed"].explanation,
            },
        }
