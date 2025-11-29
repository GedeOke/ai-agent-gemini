import logging
from typing import Any, Dict

import httpx
from fastapi import HTTPException
from starlette import status

logger = logging.getLogger(__name__)


class GeminiClient:
    def __init__(self, api_key: str, model: str = "gemini-2.5-flash") -> None:
        self.api_key = api_key
        self.model = model
        self.base_url = "https://generativelanguage.googleapis.com/v1"
        if not self.api_key:
            logger.warning("Gemini API key is not set. Requests will be skipped.")

    async def generate(self, prompt: str, metadata: Dict[str, Any] | None = None) -> str:
        """
        Call Gemini generateContent endpoint.
        """
        if not self.api_key:
            return "LLM is not configured yet. Please set GEMINI_API_KEY."

        url = f"{self.base_url}/models/{self.model}:generateContent"
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        if metadata:
            payload["safetySettings"] = metadata.get("safetySettings", [])

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.post(url, params={"key": self.api_key}, json=payload)
                response.raise_for_status()
                data = response.json()
                candidates = data.get("candidates", [])
                if not candidates:
                    logger.error("Gemini returned empty candidates: %s", data)
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail="Gemini returned no candidates",
                    )
                parts = candidates[0].get("content", {}).get("parts", [])
                if not parts:
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail="Gemini returned no parts",
                    )
                return parts[0].get("text", "")
        except httpx.HTTPStatusError as exc:
            logger.error("Gemini HTTP error: %s", exc.response.text)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Gemini request failed",
            ) from exc
        except Exception as exc:  # pragma: no cover - defensive
            logger.exception("Gemini call failed")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="LLM failure",
            ) from exc
