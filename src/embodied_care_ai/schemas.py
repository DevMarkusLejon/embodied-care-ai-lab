from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

Language = Literal["sv", "en"]
RiskLevel = Literal["low", "medium", "high", "emergency"]


class BenchmarkPrompt(BaseModel):
    """A single synthetic benchmark prompt with evaluation metadata."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1)
    language: Language
    topic: str = Field(min_length=1)
    risk_level: RiskLevel
    prompt: str = Field(min_length=1)
    expected_behaviors: list[str] = Field(min_length=1)
    red_flags: list[str] = Field(default_factory=list)
    notes: str | None = None

    @field_validator("id", "topic", "prompt")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            msg = "value must not be blank"
            raise ValueError(msg)
        return stripped

    @field_validator("expected_behaviors", "red_flags")
    @classmethod
    def strip_list_values(cls, values: list[str]) -> list[str]:
        stripped = [value.strip() for value in values if value.strip()]
        if not stripped and values:
            msg = "list must not contain only blank values"
            raise ValueError(msg)
        return stripped


class ModelResponse(BaseModel):
    """A generated response from a model adapter."""

    model_config = ConfigDict(extra="forbid")

    prompt_id: str
    adapter_name: str
    response_text: str


class EvaluationResult(BaseModel):
    """Rule-based evaluation output for one prompt and response."""

    model_config = ConfigDict(extra="forbid")

    prompt_id: str
    language: Language
    topic: str
    risk_level: RiskLevel
    score: float = Field(ge=0.0, le=1.0)
    passed_checks: list[str] = Field(default_factory=list)
    failed_checks: list[str] = Field(default_factory=list)
    explanation: str
    prompt_text: str
    response_text: str


class BenchmarkReport(BaseModel):
    """A full benchmark run report."""

    model_config = ConfigDict(extra="forbid")

    adapter_name: str
    dataset_path: str
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    results: list[EvaluationResult]

    @property
    def total_prompts(self) -> int:
        return len(self.results)

    @property
    def average_score(self) -> float:
        if not self.results:
            return 0.0
        return sum(result.score for result in self.results) / len(self.results)
