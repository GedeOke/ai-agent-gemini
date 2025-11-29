import asyncio
import logging
from typing import Iterable, List

import httpx
import numpy as np

logger = logging.getLogger(__name__)


class EmbeddingClient:
    """
    Embedding client with support for Gemini or local sentence-transformers.
    """

    def __init__(self, api_key: str, model: str = "models/embedding-001", provider: str = "gemini") -> None:
        self.api_key = api_key
        self.model = model
        self.provider = provider
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self._local_model = None
        if provider == "gemini" and not api_key:
            logger.warning("Gemini API key missing; embeddings will return zeros.")
        if provider == "local":
            try:
                from sentence_transformers import SentenceTransformer  # type: ignore

                self._local_model = SentenceTransformer(self.model)
                logger.info("Loaded local embedding model: %s", self.model)
            except Exception as exc:  # pragma: no cover - defensive
                logger.exception("Failed to load local embedding model %s", self.model)
                raise exc

    async def embed(self, texts: Iterable[str]) -> List[List[float]]:
        texts_list = list(texts)
        if self.provider == "local":
            return self._embed_local(texts_list)
        # gemini provider
        if not self.api_key:
            return [[0.0] * 32 for _ in texts_list]
        batch_size = 16
        results: List[List[float]] = []
        for i in range(0, len(texts_list), batch_size):
            chunk = texts_list[i : i + batch_size]
            batch_embeddings = await self._embed_batch_gemini(chunk)
            results.extend(batch_embeddings)
        if len(results) != len(texts_list):
            logger.warning("Embeddings total mismatch; expected %s got %s", len(texts_list), len(results))
            while len(results) < len(texts_list):
                results.append([0.0] * 32)
        return results

    def _embed_local(self, texts_list: List[str]) -> List[List[float]]:
        if not self._local_model:
            logger.error("Local embedding model not initialized")
            return [[0.0] * 32 for _ in texts_list]
        vectors = self._local_model.encode(texts_list, normalize_embeddings=True)
        # ensure python lists
        return [np.asarray(v).tolist() for v in vectors]

    async def _embed_batch_gemini(self, texts_list: List[str]) -> List[List[float]]:
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
        retries = 2
        backoff = 1.0
        for attempt in range(retries + 1):
            try:
                async with httpx.AsyncClient(timeout=20.0) as client:
                    res = await client.post(url, params={"key": self.api_key}, json=payload)
                    if res.status_code == 429 and attempt < retries:
                        retry_after = float(res.headers.get("retry-after", backoff))
                        await asyncio.sleep(retry_after)
                        backoff *= 2
                        continue
                    res.raise_for_status()
                    data = res.json()
                    embeddings = []
                    for item in data.get("embeddings", []):
                        embeddings.append(item.get("values", []))
                    if len(embeddings) != len(texts_list):
                        logger.warning(
                            "Embeddings count mismatch; expected %s got %s",
                            len(texts_list),
                            len(embeddings),
                        )
                    return embeddings
            except httpx.HTTPStatusError as exc:
                body = exc.response.text if exc.response else ""
                logger.error(
                    "Embedding request failed (status %s): %s",
                    exc.response.status_code if exc.response else "?",
                    body,
                )
                if exc.response is not None and exc.response.status_code == 429 and attempt < retries:
                    retry_after = float(exc.response.headers.get("retry-after", backoff))
                    await asyncio.sleep(retry_after)
                    backoff *= 2
                    continue
                break
            except Exception as exc:  # pragma: no cover - defensive
                logger.exception("Embedding request failed")
                break
        return [[0.0] * 32 for _ in texts_list]
