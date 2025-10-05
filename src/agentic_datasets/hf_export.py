from __future__ import annotations

from pathlib import Path
from typing import Optional

from datasets import Dataset, load_dataset
from huggingface_hub import create_repo, upload_file


def jsonl_to_dataset(path: Path) -> Dataset:
    return load_dataset("json", data_files=str(path), split="train")


def ensure_repo(repo_id: str, private: bool = False) -> None:
    create_repo(repo_id, repo_type="dataset", private=private, exist_ok=True)


def push_jsonl(
    repo_id: str,
    path: Path,
    *,
    commit_message: str = "Add dataset",
    dataset_card: Optional[str] = None,
    private: bool = False,
) -> None:
    ensure_repo(repo_id, private=private)
    # Upload data file
    upload_file(
        path_or_fileobj=str(path),
        path_in_repo=path.name,
        repo_id=repo_id,
        repo_type="dataset",
        commit_message=commit_message,
    )
    # Optional: upload README.md as dataset card
    if dataset_card:
        upload_file(
            path_or_fileobj=dataset_card.encode("utf-8"),
            path_in_repo="README.md",
            repo_id=repo_id,
            repo_type="dataset",
            commit_message="Update dataset card",
        )
