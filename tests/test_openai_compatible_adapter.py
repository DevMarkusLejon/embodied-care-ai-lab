from __future__ import annotations

import pytest

from embodied_care_ai.model_adapters.openai_compatible import (
    AdapterConfigurationError,
    OpenAICompatibleConfig,
)


def test_openai_config_requires_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("EMBODIED_CARE_MODEL", "example-model")

    with pytest.raises(AdapterConfigurationError, match="OPENAI_API_KEY"):
        OpenAICompatibleConfig.from_env()


def test_openai_config_uses_env_model_and_base_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("EMBODIED_CARE_MODEL", "example-model")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://example.test/v1/")

    config = OpenAICompatibleConfig.from_env()

    assert config.api_key == "test-key"
    assert config.model == "example-model"
    assert config.base_url == "https://example.test/v1"
