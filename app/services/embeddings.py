import logging
import asyncio
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
        # Batch to avoid hitting payload/throughput limits
        batch_size = 16
        results: List[List[float]] = []
        for i in range(0, len(texts_list), batch_size):
            chunk = texts_list[i : i + batch_size]
            batch_embeddings = await self._embed_batch(chunk)
            results.extend(batch_embeddings)
        # Ensure length matches
        if len(results) != len(texts_list):
            logger.warning("Embeddings total mismatch; expected %s got %s", len(texts_list), len(results))
            # pad with zeros
            while len(results) < len(texts_list):
                results.append([0.0] * 32)
        return results

    async def _embed_batch(self, texts_list: List[str]) -> List[List[float]]:
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
                logger.error("Embedding request failed (status %s): %s", exc.response.status_code if exc.response else "?", body)
                if exc.response is not None and exc.response.status_code == 429 and attempt < retries:
                    retry_after = float(exc.response.headers.get("retry-after", backoff))
                    await asyncio.sleep(retry_after)
                    backoff *= 2
                    continue
                break
            except Exception as exc:  # pragma: no cover - defensive
                logger.exception("Embedding request failed")
                break
        # fallback zeros to avoid crashing the flow
        return [[0.0] * 32 for _ in texts_list]
