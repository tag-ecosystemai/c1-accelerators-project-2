import os
from abc import ABC, abstractmethod

import httpx


GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_GROQ_MODEL = "openai/gpt-oss-20b"


class LLMClient(ABC):
    """Interface for text-generation providers."""

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Generate text from a prompt."""
        raise NotImplementedError


class MockLLMClient(LLMClient):
    """Deterministic LLM client for local development and tests."""

    model = "mock-llm"

    def generate(self, prompt: str) -> str:
        """Return a deterministic grounded explanation."""

        return (
            "This explanation is generated from the deterministic "
            "matching results and supplied resume evidence. "
            "The matching engine's scores and ranking are preserved. "
            "Review the matched skills, identified gaps, and available "
            "evidence before making a recruiter decision."
        )


class GroqLLMClient(LLMClient):
    """Groq-backed implementation of the LLM client."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
    ) -> None:
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.model = (
            model
            or os.getenv("GROQ_MODEL")
            or DEFAULT_GROQ_MODEL
        )

        if not self.api_key:
            raise RuntimeError(
                "GROQ_API_KEY is not configured."
            )

    def generate(self, prompt: str) -> str:
        """Send a grounded prompt to Groq."""

        response = httpx.post(
            GROQ_URL,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are a grounded recruitment "
                            "analysis assistant. "
                            "Use only the information supplied "
                            "in the prompt."
                        ),
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                "temperature": 0.2,
            },
            timeout=60.0,
        )

        response.raise_for_status()

        data = response.json()

        choices = data.get("choices")

        if not isinstance(choices, list) or not choices:
            raise RuntimeError(
                "Groq returned no completion."
            )

        message = choices[0].get("message")

        if not isinstance(message, dict):
            raise RuntimeError(
                "Groq returned an invalid completion."
            )

        content = message.get("content")

        if not isinstance(content, str) or not content.strip():
            raise RuntimeError(
                "Groq returned an empty explanation."
            )

        return content.strip()