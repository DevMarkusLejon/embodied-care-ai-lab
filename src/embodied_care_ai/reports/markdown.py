from __future__ import annotations

from collections import Counter, defaultdict

from embodied_care_ai.schemas import BenchmarkReport, EvaluationResult


def generate_markdown_report(report: BenchmarkReport) -> str:
    """Generate a human-readable Markdown benchmark summary."""

    lines = [
        "# Benchmark Report",
        "",
        f"- Adapter: `{report.adapter_name}`",
        f"- Dataset: `{report.dataset_path}`",
        f"- Generated: `{report.generated_at.isoformat()}`",
        f"- Total prompts: `{report.total_prompts}`",
        f"- Average score: `{report.average_score:.2f}`",
        f"- Full-pass rate: `{_pass_rate(report.results):.0%}`",
        "",
        "This report evaluates model behavior on synthetic prompts. It is not medical advice "
        "or clinical validation.",
        "",
        "## Score Distribution",
        "",
        _score_distribution_table(report.results),
        "",
        "## Results by Risk Level",
        "",
        _summary_table(_group_scores(report.results, "risk_level"), "Risk level"),
        "",
        "## Results by Topic",
        "",
        _summary_table(_group_scores(report.results, "topic"), "Topic"),
        "",
        "## Check Failure Frequency",
        "",
        _failure_table(report.results),
        "",
        "## Prompt-Level Results",
        "",
        _results_table(report.results),
        "",
        "## Failed or Partial Cases",
        "",
    ]

    failed_cases = [result for result in report.results if result.score < 1.0]
    if not failed_cases:
        lines.append("No failed or partial cases.")
    else:
        for result in failed_cases:
            lines.extend(_case_block(result))

    lines.extend(["", "## Example Responses", ""])
    for result in report.results[:3]:
        lines.extend(_case_block(result, include_failures=False))

    return "\n".join(lines).rstrip() + "\n"


def _group_scores(results: list[EvaluationResult], field: str) -> dict[str, tuple[int, float]]:
    grouped: dict[str, list[float]] = defaultdict(list)
    for result in results:
        grouped[str(getattr(result, field))].append(result.score)
    return {
        key: (len(scores), sum(scores) / len(scores))
        for key, scores in sorted(grouped.items(), key=lambda item: item[0])
    }


def _summary_table(grouped: dict[str, tuple[int, float]], label: str) -> str:
    lines = [
        f"| {label} | Count | Average score |",
        "| --- | ---: | ---: |",
    ]
    for key, (count, average_score) in grouped.items():
        lines.append(f"| `{key}` | {count} | {average_score:.2f} |")
    return "\n".join(lines)


def _pass_rate(results: list[EvaluationResult]) -> float:
    if not results:
        return 0.0
    return sum(1 for result in results if result.score == 1.0) / len(results)


def _score_distribution_table(results: list[EvaluationResult]) -> str:
    bands = {
        "1.00": 0,
        "0.75-0.99": 0,
        "0.50-0.74": 0,
        "<0.50": 0,
    }
    for result in results:
        if result.score == 1.0:
            bands["1.00"] += 1
        elif result.score >= 0.75:
            bands["0.75-0.99"] += 1
        elif result.score >= 0.50:
            bands["0.50-0.74"] += 1
        else:
            bands["<0.50"] += 1

    lines = ["| Score band | Count |", "| --- | ---: |"]
    for band, count in bands.items():
        lines.append(f"| `{band}` | {count} |")
    return "\n".join(lines)


def _failure_table(results: list[EvaluationResult]) -> str:
    failures = Counter(check for result in results for check in result.failed_checks)
    if not failures:
        return "No scored check failures."

    lines = ["| Failed check | Count |", "| --- | ---: |"]
    for check, count in failures.most_common():
        lines.append(f"| `{check}` | {count} |")
    return "\n".join(lines)


def _results_table(results: list[EvaluationResult]) -> str:
    lines = [
        "| Prompt | Language | Risk | Topic | Score | Failed scored checks |",
        "| --- | --- | --- | --- | ---: | --- |",
    ]
    for result in results:
        failures = ", ".join(f"`{check}`" for check in result.failed_checks) or "None"
        lines.append(
            "| "
            f"`{result.prompt_id}` | "
            f"`{result.language}` | "
            f"`{result.risk_level}` | "
            f"`{result.topic}` | "
            f"{result.score:.2f} | "
            f"{failures} |"
        )
    return "\n".join(lines)


def _case_block(result: EvaluationResult, include_failures: bool = True) -> list[str]:
    lines = [
        f"### `{result.prompt_id}`",
        "",
        f"- Topic: `{result.topic}`",
        f"- Risk level: `{result.risk_level}`",
        f"- Score: `{result.score:.2f}`",
    ]
    if include_failures:
        failed = ", ".join(f"`{check}`" for check in result.failed_checks) or "None"
        lines.append(f"- Failed checks: {failed}")
    lines.extend(
        [
            "",
            "**Prompt**",
            "",
            result.prompt_text,
            "",
            "**Response**",
            "",
            _truncate(result.response_text),
            "",
        ]
    )
    return lines


def _truncate(text: str, max_length: int = 600) -> str:
    if len(text) <= max_length:
        return text
    return text[: max_length - 3].rstrip() + "..."
