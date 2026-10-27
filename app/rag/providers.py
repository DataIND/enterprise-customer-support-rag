"""LLM and embedding provider abstractions (OpenAI-compatible)."""

from abc import ABC, abstractmethod

import httpx

from app.core.config import settings


class EmbeddingProvider(ABC):
    """Interface for embedding models."""

    @abstractmethod
    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Return embedding vectors for the given texts."""


class LLMProvider(ABC):
    """Interface for chat / completion models."""

    @abstractmethod
    async def complete(self, *, system: str, user: str) -> str:
        """Return a model completion for the given messages."""


class OpenAICompatibleEmbeddings(EmbeddingProvider):
    """OpenAI-compatible embeddings client."""

    def __init__(
        self,
        *,
        base_url: str | None = None,
        api_key: str | None = None,
        model: str | None = None,
    ) -> None:
        self.base_url = (base_url or settings.LLM_PROVIDER_BASE_URL).rstrip("/")
        self.api_key = api_key if api_key is not None else settings.LLM_API_KEY
        self.model = model or settings.EMBEDDING_MODEL

    async def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {"model": self.model, "input": texts}
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/embeddings",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()["data"]
            data_sorted = sorted(data, key=lambda item: item["index"])
            return [item["embedding"] for item in data_sorted]


class OpenAICompatibleLLM(LLMProvider):
    """OpenAI-compatible chat completions client."""

    def __init__(
        self,
        *,
        base_url: str | None = None,
        api_key: str | None = None,
        model: str | None = None,
    ) -> None:
        self.base_url = (base_url or settings.LLM_PROVIDER_BASE_URL).rstrip("/")
        self.api_key = api_key if api_key is not None else settings.LLM_API_KEY
        self.model = model or settings.LLM_MODEL

    async def complete(self, *, system: str, user: str) -> str:
        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0.2,
        }
        async with httpx.AsyncClient(timeout=90.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]


def get_embedding_provider() -> EmbeddingProvider:
    """Factory for the configured embedding provider."""
    return OpenAICompatibleEmbeddings()


def get_llm_provider() -> LLMProvider:
    """Factory for the configured LLM provider."""
    return OpenAICompatibleLLM()
