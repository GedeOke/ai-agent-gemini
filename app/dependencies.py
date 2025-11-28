from app.adapters.llm_gemini import GeminiClient
from app.config import settings
from app.db import get_session
from app.services.embeddings import EmbeddingClient
from app.services.followup import FollowUpService
from app.services.orchestrator import Orchestrator
from app.services.post_processing import PostProcessor
from app.services.prompt import PromptBuilder
from app.services.rag import RAGService
from app.services.tenant import TenantService

# Shared singletons for now; swap with DI container later.
embedding_client = EmbeddingClient(settings.gemini_api_key)
rag_service = RAGService(embedding_client)
post_processor = PostProcessor()
prompt_builder = PromptBuilder()
llm_client = GeminiClient(settings.gemini_api_key)
followup_service = FollowUpService()
tenant_service = TenantService()
orchestrator = Orchestrator(llm_client, rag_service, prompt_builder, post_processor)

__all__ = [
    "rag_service",
    "embedding_client",
    "post_processor",
    "prompt_builder",
    "llm_client",
    "followup_service",
    "tenant_service",
    "orchestrator",
    "get_session",
]
