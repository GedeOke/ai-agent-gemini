from app.adapters.llm_gemini import GeminiClient
from app.config import settings
from app.models.schemas import TenantSettings
from app.services.followup import FollowUpService
from app.services.orchestrator import Orchestrator
from app.services.post_processing import PostProcessor
from app.services.prompt import PromptBuilder
from app.services.rag import RAGService

# Shared singletons for now; swap with DI container later.
rag_service = RAGService()
post_processor = PostProcessor()
prompt_builder = PromptBuilder()
llm_client = GeminiClient(settings.gemini_api_key)
followup_service = FollowUpService()
orchestrator = Orchestrator(llm_client, rag_service, prompt_builder, post_processor)

tenant_settings_store: dict[str, TenantSettings] = {"default": TenantSettings(tenant_id="default")}
