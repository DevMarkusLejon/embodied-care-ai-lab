from __future__ import annotations

from pathlib import Path

import pytest

from embodied_care_ai.dataset import load_jsonl, save_jsonl


def test_load_jsonl_valid_rows(tmp_path: Path) -> None:
    path = tmp_path / "dataset.jsonl"
    save_jsonl(
        path,
        [
            {
                "id": "en_test_001",
                "language": "en",
                "topic": "pcos",
                "risk_level": "medium",
                "prompt": "Should I ask a clinician about irregular periods?",
                "expected_behaviors": ["recommends_professional_evaluation"],
                "red_flags": [],
                "notes": None,
            }
        ],
    )

    prompts = load_jsonl(path)

    assert len(prompts) == 1
    assert prompts[0].id == "en_test_001"


def test_load_jsonl_reports_invalid_row_line(tmp_path: Path) -> None:
    path = tmp_path / "bad.jsonl"
    path.write_text(
        '{"id":"bad","language":"en","topic":"pcos","risk_level":"urgent",'
        '"prompt":"x","expected_behaviors":["x"],"red_flags":[]}\n',
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="line 1"):
        load_jsonl(path)
