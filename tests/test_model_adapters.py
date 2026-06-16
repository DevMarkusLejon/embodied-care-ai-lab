from __future__ import annotations

from embodied_care_ai.model_adapters.mock import MockModelAdapter


def test_mock_adapter_output_is_deterministic() -> None:
    adapter = MockModelAdapter(mode="safe")
    prompt = "I have chest pressure and nausea."

    assert adapter.generate(prompt) == adapter.generate(prompt)
    assert adapter.name == "mock-safe"


def test_mock_adapter_supports_swedish() -> None:
    adapter = MockModelAdapter(mode="safe")

    response = adapter.generate("Jag har ont och känner mig yr.")

    assert "Kontakta vården" in response
