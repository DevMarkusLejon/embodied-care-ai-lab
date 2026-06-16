from __future__ import annotations

from embodied_care_ai.reports.markdown import generate_markdown_report
from embodied_care_ai.schemas import BenchmarkReport, EvaluationResult


def test_markdown_report_generation() -> None:
    report = BenchmarkReport(
        adapter_name="mock-safe",
        dataset_path="dataset.jsonl",
        results=[
            EvaluationResult(
                prompt_id="en_test_001",
                language="en",
                topic="pcos",
                risk_level="medium",
                score=1.0,
                passed_checks=["not_dismissive"],
                failed_checks=[],
                explanation="Passed.",
                prompt_text="Prompt",
                response_text="Response",
            )
        ],
    )

    markdown = generate_markdown_report(report)

    assert "# Benchmark Report" in markdown
    assert "Average score" in markdown
    assert "en_test_001" in markdown
