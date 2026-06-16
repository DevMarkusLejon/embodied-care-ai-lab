from __future__ import annotations

from typing import Protocol


class ModelAdapter(Protocol):
    """Minimal interface for model adapters."""

    name: str

    def generate(self, prompt: str) -> str:
        """Generate a response for a benchmark prompt."""
