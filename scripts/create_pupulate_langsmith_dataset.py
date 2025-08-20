import json
import os

from langsmith import Client as LangSmithClient

DATASET_PATH = "data/gaia/validation.json"
DATASET_NAME = "gaia_level_1_no_files"
DATASET_DESCRIPTION = "GAIA dataset with level 1 questions and no files on input"
INPUTS_SCHEMA = {
    "type": "object",
    "properties": {
        "question": {
            "type": "string",
            "description": "The question to be answered",
        }
    },
    "required": ["question"],
}
OUTPUTS_SCHEMA = {
    "type": "object",
    "properties": {
        "answer": {
            "type": "string",
            "description": "The answer to the question",
        },
        "tools_used": {
            "type": "string",
            "description": "List of tools used to generate the answer",
        },
        "trajectory": {
            "type": "string",
            "description": (
                "The golden reasoning trajectory of the agent to answer the question"
            ),
        },
    },
    "required": ["answer", "tools_used", "trajectory"],
}


def load_gaia_dataset() -> list[dict]:
    if not os.path.exists(DATASET_PATH):
        raise FileNotFoundError(f"Dataset file {DATASET_PATH} not found")

    with open(DATASET_PATH, encoding="utf-8") as jf:
        gaia_dataset = json.load(jf)

    gaia_dataset = [
        el for el in gaia_dataset if el["Level"] == "1" and not el["file_path"]
    ]
    gaia_dataset_prepared = list(map(prepare_gaia_example, gaia_dataset))

    return gaia_dataset_prepared


def prepare_gaia_example(example: dict) -> dict:
    return {
        "inputs": {
            "question": example["Question"],
        },
        "outputs": {
            "answer": example["Final answer"],
            "tools_used": example["Annotator Metadata"]["Tools"],
            "trajectory": example["Annotator Metadata"]["Steps"],
        },
    }


def main():
    langsmith_client = LangSmithClient()
    datasets = langsmith_client.list_datasets()

    for dataset in datasets:
        if dataset.name == DATASET_NAME:
            print(f"Dataset {DATASET_NAME} already exists.")
            break
    else:
        print(f"Dataset {DATASET_NAME} does not exist, creating it.")
        dataset = langsmith_client.create_dataset(
            dataset_name=DATASET_NAME,
            description=DATASET_DESCRIPTION,
            inputs_schema=INPUTS_SCHEMA,
            outputs_schema=OUTPUTS_SCHEMA,
        )

    gaia_dataset_prepared = load_gaia_dataset()

    langsmith_client.create_examples(
        dataset_id=dataset.id,
        examples=gaia_dataset_prepared,
    )
    print(f"Dataset {DATASET_NAME} populated successfully.")


if __name__ == "__main__":
    main()
