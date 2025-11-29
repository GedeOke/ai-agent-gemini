from app.adapters.llm_gemini import GeminiClient
from app.config import settings
from app.db import get_session
from app.db import SessionLocal
from app.services.embeddings import EmbeddingClient
from app.services.followup import FollowUpService
from app.services.ingest import IngestService
from app.services.orchestrator import Orchestrator
from app.services.post_processing import PostProcessor
from app.services.prompt import PromptBuilder
from app.services.rag import RAGService
from app.services.scheduler import FollowUpScheduler
from app.services.tenant import TenantService
from app.services.contacts import ContactService

# Shared singletons for now; swap with DI container later.
embedding_client = EmbeddingClient(
    api_key=settings.gemini_api_key,
    model=settings.embedding_model_name,
    provider=settings.embedding_provider,
)
rag_service = RAGService(embedding_client)
post_processor = PostProcessor()
prompt_builder = PromptBuilder()
llm_client = GeminiClient(settings.gemini_api_key)
followup_service = FollowUpService()
tenant_service = TenantService()
orchestrator = Orchestrator(llm_client, rag_service, prompt_builder, post_processor)
scheduler = FollowUpScheduler(poll_interval_seconds=settings.followup_poll_interval_seconds)
ingest_service = IngestService()
contact_service = ContactService()

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
    "SessionLocal",
    "scheduler",
    "ingest_service",
    "contact_service",
]
