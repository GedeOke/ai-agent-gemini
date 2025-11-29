import logging
from typing import Iterable, List

import httpx

logger = logging.getLogger(__name__)


class EmbeddingClient:
    """
    Simple Gemini embeddings client. Replace model/version if needed.
    """

    def __init__(self, api_key: str, model: str = "models/embedding-001") -> None:
        self.api_key = api_key
        self.model = model
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        if not api_key:
            logger.warning("Gemini API key missing; embeddings will return zeros.")

    async def embed(self, texts: Iterable[str]) -> List[List[float]]:
        texts_list = list(texts)
        if not self.api_key:
            # return zero vectors placeholder
            return [[0.0] * 32 for _ in texts_list]
        url = f"{self.base_url}/models/embedding-001:batchEmbedContents"
        payload = {
            "requests": [
                {
                    "model": self.model,
                    "content": {"parts": [{"text": text}]},
                }
                for text in texts_list
            ]
        }
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                res = await client.post(url, params={"key": self.api_key}, json=payload)
                res.raise_for_status()
                data = res.json()
                embeddings = []
                for item in data.get("embeddings", []):
                    embeddings.append(item.get("values", []))
                if len(embeddings) != len(texts_list):
                    logger.warning("Embeddings count mismatch; expected %s got %s", len(texts_list), len(embeddings))
                return embeddings
        except Exception as exc:  # pragma: no cover - defensive
            logger.exception("Embedding request failed")
            # fallback zeros to avoid crashing the flow
            return [[0.0] * 32 for _ in texts_list]
