from __future__ import annotations

from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel, Field


class CatalogEntry(BaseModel):
    id: str
    name: str
    version: str
    description: Optional[str] = None
    license: Optional[str] = None
    tags: list[str] = Field(default_factory=list)
    # One of these should be provided
    local_path: Optional[Path] = None
    hf_repo: Optional[str] = None


class Catalog(BaseModel):
    entries: list[CatalogEntry]

    def get(self, entry_id: str) -> CatalogEntry:
        for e in self.entries:
            if e.id == entry_id:
                return e
        raise KeyError(f"Catalog entry not found: {entry_id}")


def load_catalog(path: Path) -> Catalog:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and "entries" in data:
        return Catalog.model_validate(data)
    # Support bare list format
    return Catalog(entries=[CatalogEntry.model_validate(x) for x in data])


def make_dataset_card(entry: CatalogEntry) -> str:
    tags = "\n".join(f"- {t}" for t in entry.tags)
    body = f"""
---
language: en
license: {entry.license or "other"}
tags:
{tags}
---

# {entry.name} (v{entry.version})

{entry.description or ""}

This dataset is part of the Agentic Datasets pipeline. See repository for pipeline config and provenance.
""".strip()
    return body
