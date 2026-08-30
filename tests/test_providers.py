"""Unit tests for the provider factory and GroqProvider's configuration
logic. Mocks the `openai` client entirely — these must never make a real
network call, unlike an actual eval run with PROVIDER=groq/openai."""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from services.providers import get_provider
from services.providers.groq_provider import (
    _DEFAULT_MODEL,
    _DEFAULT_REASONING_EFFORT,
    _GROQ_BASE_URL,
    GroqProvider,
)


def test_groq_provider_requires_api_key(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="GROQ_API_KEY"):
        GroqProvider()


def test_groq_provider_uses_groq_base_url_and_default_model(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "fake-key-for-test")
    monkeypatch.delenv("GROQ_MODEL", raising=False)
    with patch("openai.OpenAI") as mock_openai_cls:
        provider = GroqProvider()
        mock_openai_cls.assert_called_once_with(api_key="fake-key-for-test", base_url=_GROQ_BASE_URL)
    assert provider._model == _DEFAULT_MODEL
    assert provider.name == "groq"


def test_groq_provider_respects_model_override(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "fake-key-for-test")
    monkeypatch.setenv("GROQ_MODEL", "some/other-model")
    with patch("openai.OpenAI"):
        provider = GroqProvider()
    assert provider._model == "some/other-model"

    with patch("openai.OpenAI"):
        provider2 = GroqProvider(model="explicit-arg-wins")
    assert provider2._model == "explicit-arg-wins"


def test_groq_provider_complete_calls_openai_compatible_chat_endpoint(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "fake-key-for-test")
    fake_response = MagicMock()
    fake_response.choices = [MagicMock(message=MagicMock(content="a real answer"))]
    with patch("openai.OpenAI") as mock_openai_cls:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = fake_response
        mock_openai_cls.return_value = mock_client
        provider = GroqProvider()
        result = provider.complete("system prompt", "user prompt")
    assert result == "a real answer"
    mock_client.chat.completions.create.assert_called_once()
    _, kwargs = mock_client.chat.completions.create.call_args
    assert kwargs["messages"][0] == {"role": "system", "content": "system prompt"}
    assert kwargs["messages"][1] == {"role": "user", "content": "user prompt"}


def test_groq_provider_defaults_to_low_reasoning_effort_and_includes_it_in_the_call(monkeypatch):
    """Measured directly (docs/evaluation.md): the API's own default
    reasoning effort burns most of max_tokens on hidden reasoning for this
    project's short, structured completions, truncating answers. "low" was
    verified to produce complete, correct answers using far fewer tokens."""
    monkeypatch.setenv("GROQ_API_KEY", "fake-key-for-test")
    monkeypatch.delenv("GROQ_REASONING_EFFORT", raising=False)
    fake_response = MagicMock()
    fake_response.choices = [MagicMock(message=MagicMock(content="answer"))]
    with patch("openai.OpenAI") as mock_openai_cls:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = fake_response
        mock_openai_cls.return_value = mock_client
        provider = GroqProvider()
        assert provider._reasoning_effort == _DEFAULT_REASONING_EFFORT == "low"
        provider.complete("system", "prompt")
    _, kwargs = mock_client.chat.completions.create.call_args
    assert kwargs["reasoning_effort"] == "low"


def test_groq_provider_reasoning_effort_overridable_and_omittable(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "fake-key-for-test")
    with patch("openai.OpenAI"):
        provider = GroqProvider(reasoning_effort="high")
    assert provider._reasoning_effort == "high"

    # Empty string disables the parameter entirely — for a non-reasoning
    # Groq model that would reject an unrecognized field.
    fake_response = MagicMock()
    fake_response.choices = [MagicMock(message=MagicMock(content="answer"))]
    with patch("openai.OpenAI") as mock_openai_cls:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = fake_response
        mock_openai_cls.return_value = mock_client
        provider = GroqProvider(reasoning_effort="")
        provider.complete("system", "prompt")
    _, kwargs = mock_client.chat.completions.create.call_args
    assert "reasoning_effort" not in kwargs


def test_get_provider_factory_returns_groq_provider(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "fake-key-for-test")
    with patch("openai.OpenAI"):
        provider = get_provider("groq")
    assert provider.name == "groq"


def test_get_provider_factory_rejects_unknown_provider():
    with pytest.raises(ValueError, match="Unknown provider"):
        get_provider("not-a-real-provider")
