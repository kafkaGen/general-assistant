import argparse
import asyncio

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, ToolMessage
from langsmith import aevaluate

from src.core.workflows import WorkflowFactory
from src.evaluation.evaluators import EvaluatorFactory


async def run_assistant(inputs: dict) -> dict:
    general_assistant = WorkflowFactory.create_general_assistant()
    messages = [
        HumanMessage(content=inputs["question"]),
    ]

    response = await general_assistant.ainvoke(messages=messages)

    answer = response["final_answer"]
    trajectory = "\n\n".join(
        [
            mess.pretty_repr()
            for mess in response["output_messages"]
            if not isinstance(mess, ToolMessage)
        ]
    )

    return {
        "answer": answer,
        "trajectory": trajectory,
    }


async def main(
    dataset_name: str,
    experiment_name: str,
    num_repetitions: int,
    max_concurrency: int,
) -> None:
    await aevaluate(
        run_assistant,
        data=dataset_name,
        evaluators=[
            EvaluatorFactory.create_success_rate_evaluator(),
            EvaluatorFactory.create_trajectory_evaluator(),
        ],
        experiment_prefix=experiment_name,
        num_repetitions=num_repetitions,
        max_concurrency=max_concurrency,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-name", type=str, default="gaia-level-1-no-files")
    parser.add_argument("--experiment-name", type=str, default="perfomance-test")
    parser.add_argument("--num-repetitions", type=int, default=1)
    parser.add_argument("--max-concurrency", type=int, default=5)
    args = parser.parse_args()

    load_dotenv()

    asyncio.run(
        main(
            args.dataset_name,
            args.experiment_name,
            args.num_repetitions,
            args.max_concurrency,
        )
    )
