import json
import os
from pathlib import Path

from datasets import load_dataset
from dotenv import load_dotenv


def download_gaia_dataset():
    data_dir = Path("./data/gaia")
    data_dir.mkdir(parents=True, exist_ok=True)
    cache_dir = "./data/.cache"

    token = os.getenv("HUGGING_FACE_TOKEN")
    if not token:
        raise ValueError("HUGGING_FACE_TOKEN not found in environment variables")

    print("Downloading GAIA dataset...")

    try:
        print("Downloading validation split...")
        validation_data = load_dataset(
            "gaia-benchmark/GAIA",
            "2023_all",
            split="validation",
            token=token,
            cache_dir=cache_dir,
        )

        validation_file = data_dir / "validation.json"
        with open(validation_file, "w", encoding="utf-8") as f:
            json.dump(validation_data.to_list(), f, indent=2, ensure_ascii=False)

        print(f"✓ Validation split saved: {validation_file}")
        print(f"  Examples: {len(validation_data)}")
        print(f"  Columns: {validation_data.column_names}")

    except Exception as e:
        print(f"✗ Failed to download validation split: {e}")

    print(f"\nDataset downloaded to: {data_dir.absolute()}")


if __name__ == "__main__":
    load_dotenv()
    download_gaia_dataset()
