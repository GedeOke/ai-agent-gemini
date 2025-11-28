import logging

from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from app import dependencies
from app.models.schemas import ChatRequest, ChatResponse, TenantSettings
from app.utils.security import ApiKeyDep
from app.db import get_session
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()
logger = logging.getLogger(__name__)


def _get_tenant_settings(tenant_id: str) -> TenantSettings:
    # Fallback placeholder; real fetch handled via tenant service
    return TenantSettings(tenant_id=tenant_id)


@router.post("", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    tenant_key: ApiKeyDep,
    session: AsyncSession = Depends(get_session),
) -> ChatResponse:
    if tenant_key not in ("global", "open") and payload.tenant_id != tenant_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="tenant mismatch",
        )
    tenant_settings = await dependencies.tenant_service.get(session, payload.tenant_id)
    if not tenant_settings:
        tenant_settings = _get_tenant_settings(payload.tenant_id)
    try:
        return await dependencies.orchestrator.handle_chat(session, payload, tenant_settings)
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Chat endpoint failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Chat processing failed",
        ) from exc
