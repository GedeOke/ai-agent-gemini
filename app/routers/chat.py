import logging

from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from app import dependencies
from app.models.schemas import ChatRequest, ChatResponse, TenantSettings
from app.utils.security import ApiKeyDep

router = APIRouter()
logger = logging.getLogger(__name__)


def _get_tenant_settings(tenant_id: str) -> TenantSettings:
    return dependencies.tenant_settings_store.get(
        tenant_id,
        TenantSettings(tenant_id=tenant_id),
    )


@router.post("", response_model=ChatResponse)
async def chat(payload: ChatRequest, _: ApiKeyDep) -> ChatResponse:
    tenant_settings = _get_tenant_settings(payload.tenant_id)
    try:
        return await dependencies.orchestrator.handle_chat(payload, tenant_settings)
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Chat endpoint failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Chat processing failed",
        ) from exc
