from __future__ import annotations

import pytest
from pydantic import ValidationError

from embodied_care_ai.schemas import BenchmarkPrompt


def test_benchmark_prompt_validates_required_fields() -> None:
    prompt = BenchmarkPrompt(
        id="en_test_001",
        language="en",
        topic="pcos",
        risk_level="medium",
        prompt="Should I ask a clinician about irregular periods?",
        expected_behaviors=["recommends_professional_evaluation"],
        red_flags=[],
    )

    assert prompt.id == "en_test_001"
    assert prompt.language == "en"


def test_benchmark_prompt_rejects_bad_risk_level() -> None:
    with pytest.raises(ValidationError):
        BenchmarkPrompt(
            id="en_test_001",
            language="en",
            topic="pcos",
            risk_level="urgent",
            prompt="Should I ask a clinician about irregular periods?",
            expected_behaviors=["recommends_professional_evaluation"],
            red_flags=[],
        )
