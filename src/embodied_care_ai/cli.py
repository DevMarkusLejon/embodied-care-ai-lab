from __future__ import annotations

from pathlib import Path
from typing import Annotated

import pandas as pd
import typer
from rich.console import Console
from rich.table import Table

from embodied_care_ai.dataset import load_jsonl
from embodied_care_ai.evaluators.scoring import evaluate_response
from embodied_care_ai.model_adapters.base import ModelAdapter
from embodied_care_ai.model_adapters.mock import MockMode, MockModelAdapter
from embodied_care_ai.model_adapters.openai_compatible import (
    AdapterConfigurationError,
    OpenAICompatibleAdapter,
    OpenAICompatibleConfig,
)
from embodied_care_ai.reports.markdown import generate_markdown_report
from embodied_care_ai.schemas import BenchmarkReport

app = typer.Typer(help="Embodied Care AI Lab CLI.")
benchmark_app = typer.Typer(help="Run and validate benchmark datasets.")
app.add_typer(benchmark_app, name="benchmark")

console = Console()


@benchmark_app.command("validate")
def validate_dataset(
    dataset: Annotated[
        Path,
        typer.Option(
            "--dataset",
            "-d",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            help="Path to a JSONL benchmark dataset.",
        ),
    ],
) -> None:
    """Validate a benchmark JSONL dataset."""

    prompts = load_jsonl(dataset)
    console.print(f"Validated [bold]{len(prompts)}[/bold] prompts from {dataset}")


@benchmark_app.command("run")
def run_benchmark(
    dataset: Annotated[
        Path,
        typer.Option(
            "--dataset",
            "-d",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            help="Path to a JSONL benchmark dataset.",
        ),
    ],
    adapter: Annotated[
        str,
        typer.Option(
            "--adapter",
            "-a",
            help=(
                "Adapter name. Supported values: mock-safe, mock-unsafe, mock-mixed, "
                "openai-compatible."
            ),
        ),
    ] = "mock-safe",
    model: Annotated[
        str | None,
        typer.Option("--model", help="Model name for the OpenAI-compatible adapter."),
    ] = None,
    output: Annotated[
        Path | None,
        typer.Option("--output", "-o", help="Path for the Markdown report."),
    ] = None,
    json_output: Annotated[
        Path | None,
        typer.Option("--json-output", help="Path for the JSON report."),
    ] = None,
    csv_output: Annotated[
        Path | None,
        typer.Option("--csv-output", help="Optional path for a CSV result summary."),
    ] = None,
) -> None:
    """Run a benchmark dataset through an adapter and evaluate responses."""

    prompts = load_jsonl(dataset)
    model_adapter = _build_adapter(adapter, model)
    results = [
        evaluate_response(prompt, model_adapter.generate(prompt.prompt)) for prompt in prompts
    ]
    report = BenchmarkReport(
        adapter_name=model_adapter.name,
        dataset_path=str(dataset),
        results=results,
    )

    if output is not None:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(generate_markdown_report(report), encoding="utf-8")

    json_path = json_output or _default_json_output(output)
    if json_path is not None:
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(report.model_dump_json(indent=2), encoding="utf-8")

    if csv_output is not None:
        csv_output.parent.mkdir(parents=True, exist_ok=True)
        _write_csv_summary(report, csv_output)

    _print_run_summary(report, output, json_path, csv_output)


def _build_adapter(adapter: str, model: str | None = None) -> ModelAdapter:
    modes: dict[str, MockMode] = {
        "mock-safe": "safe",
        "mock-unsafe": "unsafe",
        "mock-mixed": "mixed",
    }
    if adapter in modes:
        return MockModelAdapter(mode=modes[adapter])
    if adapter == "openai-compatible":
        try:
            return OpenAICompatibleAdapter(OpenAICompatibleConfig.from_env(model=model))
        except AdapterConfigurationError as exc:
            raise typer.BadParameter(str(exc)) from exc

    supported = [*sorted(modes), "openai-compatible"]
    msg = f"Unsupported adapter '{adapter}'. Choose one of: {', '.join(supported)}."
    raise typer.BadParameter(msg)


def _default_json_output(output: Path | None) -> Path | None:
    if output is None:
        return None
    return output.with_suffix(".json")


def _write_csv_summary(report: BenchmarkReport, csv_output: Path) -> None:
    rows = [
        {
            "prompt_id": result.prompt_id,
            "language": result.language,
            "topic": result.topic,
            "risk_level": result.risk_level,
            "score": result.score,
            "passed_checks": ";".join(result.passed_checks),
            "failed_checks": ";".join(result.failed_checks),
            "explanation": result.explanation,
        }
        for result in report.results
    ]
    pd.DataFrame(rows).to_csv(csv_output, index=False)


def _print_run_summary(
    report: BenchmarkReport,
    markdown_output: Path | None,
    json_output: Path | None,
    csv_output: Path | None,
) -> None:
    table = Table(title="Benchmark complete")
    table.add_column("Metric")
    table.add_column("Value")
    table.add_row("Adapter", report.adapter_name)
    table.add_row("Prompts", str(report.total_prompts))
    table.add_row("Average score", f"{report.average_score:.2f}")
    if markdown_output is not None:
        table.add_row("Markdown report", str(markdown_output))
    if json_output is not None:
        table.add_row("JSON report", str(json_output))
    if csv_output is not None:
        table.add_row("CSV report", str(csv_output))
    console.print(table)


if __name__ == "__main__":
    app()
