import argparse

from dotenv import load_dotenv
from langsmith import evaluate

from src.evaluation.evaluators import EvaluatorFactory


def run_success_rate_evaluator(inputs: dict) -> dict:
    evaluator = EvaluatorFactory.create_success_rate_evaluator()
    _inputs = {"question": inputs["question"]}
    _outputs = {"answer": inputs["agent_answer"]}
    _reference_outputs = {"answer": inputs["reference_answer"]}
    result = evaluator(_inputs, _outputs, _reference_outputs)

    return result


def success_rate_metaevaluator(
    inputs: dict,
    outputs: dict,
    reference_outputs: dict,
) -> dict:
    is_correct = False
    if outputs["score"] == reference_outputs["score"]:
        is_correct = True

    return {
        "key": "success-rate-alignment",
        "score": is_correct,
    }


def main(
    dataset_name: str,
    experiment_name: str,
    num_repetitions: int,
    max_concurrency: int,
) -> None:
    evaluate(
        run_success_rate_evaluator,
        data=dataset_name,
        evaluators=[
            success_rate_metaevaluator,
        ],
        experiment_prefix=experiment_name,
        num_repetitions=num_repetitions,
        max_concurrency=max_concurrency,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dataset-name", type=str, default="success-rate-evaluator-dataset"
    )
    parser.add_argument("--experiment-name", type=str, default="regression-test")
    parser.add_argument("--num-repetitions", type=int, default=1)
    parser.add_argument("--max-concurrency", type=int, default=10)
    args = parser.parse_args()

    load_dotenv()

    main(
        args.dataset_name,
        args.experiment_name,
        args.num_repetitions,
        args.max_concurrency,
    )
