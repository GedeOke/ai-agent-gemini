import logging

from fastapi import HTTPException
from starlette import status

from app.adapters.llm_gemini import GeminiClient
from app.models.schemas import ChatRequest, ChatResponse, TenantSettings
from app.services.post_processing import PostProcessor
from app.services.prompt import PromptBuilder
from app.services.rag import RAGService

logger = logging.getLogger(__name__)


class Orchestrator:
    def __init__(
        self,
        llm_client: GeminiClient,
        rag_service: RAGService,
        prompt_builder: PromptBuilder,
        post_processor: PostProcessor,
    ) -> None:
        self.llm_client = llm_client
        self.rag_service = rag_service
        self.prompt_builder = prompt_builder
        self.post_processor = post_processor

    async def handle_chat(self, payload: ChatRequest, tenant_settings: TenantSettings) -> ChatResponse:
        try:
            retrieved_context = await self.rag_service.retrieve(payload)
        except Exception:  # pragma: no cover - defensive
            logger.exception("Context retrieval failed, continuing without context")
            retrieved_context = []

        prompt = self.prompt_builder.build_chat_prompt(payload, retrieved_context, tenant_settings)

        try:
            llm_text = await self.llm_client.generate(prompt, metadata={"tenant_id": payload.tenant_id})
        except HTTPException:
            raise
        except Exception as exc:  # pragma: no cover - defensive
            logger.exception("LLM generation failed")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to generate response"
            ) from exc

        bubbles = self.post_processor.split_bubbles(llm_text)
        return ChatResponse(
            bubbles=bubbles,
            full_text=llm_text,
            metadata={"channel": payload.channel, "locale": payload.locale},
            retrieved_context=retrieved_context,
        )
