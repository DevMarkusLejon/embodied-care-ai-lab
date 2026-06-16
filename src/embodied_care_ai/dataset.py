from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from embodied_care_ai.schemas import BenchmarkPrompt


def load_jsonl(path: Path) -> list[BenchmarkPrompt]:
    """Load benchmark prompts from a JSONL file."""

    if not path.exists():
        msg = f"Dataset file does not exist: {path}"
        raise FileNotFoundError(msg)

    prompts: list[BenchmarkPrompt] = []
    with path.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                raw = json.loads(stripped)
            except json.JSONDecodeError as exc:
                msg = f"Invalid JSON in {path} at line {line_number}: {exc.msg}"
                raise ValueError(msg) from exc
            if not isinstance(raw, dict):
                msg = f"Invalid row in {path} at line {line_number}: expected an object"
                raise ValueError(msg)
            try:
                prompts.append(BenchmarkPrompt.model_validate(raw))
            except ValidationError as exc:
                msg = f"Invalid row in {path} at line {line_number}: {exc}"
                raise ValueError(msg) from exc
    return prompts


def save_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    """Save dictionaries to JSONL using UTF-8."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        for row in rows:
            file.write(json.dumps(row, ensure_ascii=False, sort_keys=True))
            file.write("\n")
