import logging

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.adapters.llm_gemini import GeminiClient
from app.models.schemas import ChatRequest, ChatResponse, TenantSettings
from app.services.post_processing import PostProcessor
from app.services.prompt import PromptBuilder
from app.services.rag import RAGService
from app.services.sop import SopStateService

logger = logging.getLogger(__name__)


class Orchestrator:
    def __init__(
        self,
        llm_client: GeminiClient,
        rag_service: RAGService,
        prompt_builder: PromptBuilder,
        post_processor: PostProcessor,
        sop_state_service: SopStateService | None = None,
    ) -> None:
        self.llm_client = llm_client
        self.rag_service = rag_service
        self.prompt_builder = prompt_builder
        self.post_processor = post_processor
        self.sop_state_service = sop_state_service

    async def handle_chat(
        self, session: AsyncSession, payload: ChatRequest, tenant_settings: TenantSettings
    ) -> ChatResponse:
        try:
            retrieved_context = await self.rag_service.retrieve(session, payload)
        except Exception:  # pragma: no cover - defensive
            logger.exception("Context retrieval failed, continuing without context")
            retrieved_context = []

        sop_current = None
        if self.sop_state_service:
            sop_state = await self.sop_state_service.update_from_history(session, tenant_settings.sop, payload)
            sop_current = sop_state.current_step

        prompt = self.prompt_builder.build_chat_prompt(payload, retrieved_context, tenant_settings, sop_current)

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
