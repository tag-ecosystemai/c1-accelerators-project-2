from unittest.mock import patch

import httpx
import pytest

from llm.client import (
    GroqLLMClient,
    MockLLMClient,
)


def test_mock_llm_client_returns_deterministic_explanation():
    client = MockLLMClient()

    result = client.generate(
        "Explain this candidate result."
    )

    assert isinstance(result, str)
    assert result
    assert "deterministic matching results" in result
    assert "recruiter decision" in result


def test_groq_client_requires_api_key(monkeypatch):
    monkeypatch.delenv(
        "GROQ_API_KEY",
        raising=False,
    )

    with pytest.raises(
        RuntimeError,
        match="GROQ_API_KEY is not configured",
    ):
        GroqLLMClient()


def test_groq_client_uses_configured_model(monkeypatch):
    monkeypatch.setenv(
        "GROQ_API_KEY",
        "test-key",
    )
    monkeypatch.setenv(
        "GROQ_MODEL",
        "openai/gpt-oss-20b",
    )

    client = GroqLLMClient()

    assert client.model == "openai/gpt-oss-20b"


def test_groq_client_parses_completion(monkeypatch):
    monkeypatch.setenv(
        "GROQ_API_KEY",
        "test-key",
    )

    response = httpx.Response(
        status_code=200,
        json={
            "choices": [
                {
                    "message": {
                        "content": "Grounded explanation."
                    }
                }
            ]
        },
        request=httpx.Request(
            "POST",
            "https://api.groq.com/openai/v1/chat/completions",
        ),
    )

    with patch(
        "llm.client.httpx.post",
        return_value=response,
    ) as mock_post:
        client = GroqLLMClient()

        result = client.generate(
            "Explain the supplied result."
        )

    assert result == "Grounded explanation."

    mock_post.assert_called_once()

    call = mock_post.call_args

    assert call.kwargs["headers"][
        "Authorization"
    ] == "Bearer test-key"

    assert (
        call.kwargs["json"]["model"]
        == "openai/gpt-oss-20b"
    )