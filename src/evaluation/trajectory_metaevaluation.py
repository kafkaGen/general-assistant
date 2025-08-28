import argparse

from dotenv import load_dotenv
from langsmith import evaluate

from src.evaluation.evaluators import EvaluatorFactory


def run_trajectory_evaluator(inputs: dict) -> dict:
    evaluator = EvaluatorFactory.create_trajectory_evaluator()
    _inputs = {"question": inputs["question"]}
    _outputs = {"trajectory": inputs["agent_trajectory"]}
    _reference_outputs = {
        "trajectory": inputs["reference_trajectory"],
        "tools_used": inputs["reference_tools_used"],
    }
    result = evaluator(_inputs, _outputs, _reference_outputs)

    return result


def trajectory_metaevaluator(
    inputs: dict,
    outputs: dict,
    reference_outputs: dict,
) -> dict:
    mae = abs(reference_outputs["score"] - outputs["score"])

    return {
        "key": "trajectory-alignment",
        "score": 1 - mae,
    }


def main(
    dataset_name: str,
    experiment_name: str,
    num_repetitions: int,
    max_concurrency: int,
) -> None:
    evaluate(
        run_trajectory_evaluator,
        data=dataset_name,
        evaluators=[
            trajectory_metaevaluator,
        ],
        experiment_prefix=experiment_name,
        num_repetitions=num_repetitions,
        max_concurrency=max_concurrency,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dataset-name", type=str, default="trajectory-evaluator-dataset"
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
