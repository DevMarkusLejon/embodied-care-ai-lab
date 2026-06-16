#!/usr/bin/env bash
set -euo pipefail

uv run embodied-care benchmark validate --dataset data/benchmark_prompts/womens_health_sv.jsonl
uv run embodied-care benchmark run \
  --dataset data/benchmark_prompts/womens_health_sv.jsonl \
  --adapter mock-safe \
  --output reports/mock_sv_report.md
