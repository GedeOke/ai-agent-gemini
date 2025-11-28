import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app import dependencies
from app.db import get_session
from app.models.schemas import TenantSettings
from app.utils.security import ApiKeyDep

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/{tenant_id}/settings", response_model=TenantSettings)
async def get_settings(
    tenant_id: str,
    tenant_key: ApiKeyDep,
    session: AsyncSession = Depends(get_session),
) -> TenantSettings:
    if tenant_key not in ("global", "open") and tenant_id != tenant_key:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="tenant mismatch")
    existing = await dependencies.tenant_service.get(session, tenant_id)
    return existing or TenantSettings(tenant_id=tenant_id)


@router.put("/{tenant_id}/settings", response_model=TenantSettings)
async def update_settings(
    tenant_id: str,
    payload: TenantSettings,
    tenant_key: ApiKeyDep,
    session: AsyncSession = Depends(get_session),
) -> TenantSettings:
    if payload.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="tenant_id mismatch",
        )
    if tenant_key not in ("global", "open") and tenant_id != tenant_key:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="tenant mismatch")
    try:
        updated = await dependencies.tenant_service.upsert(session, payload)
        return updated
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Failed to update tenant settings")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update tenant settings",
        ) from exc
