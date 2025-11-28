import logging

from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from app import dependencies
from app.models.schemas import TenantSettings
from app.utils.security import ApiKeyDep

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/{tenant_id}/settings", response_model=TenantSettings)
async def get_settings(tenant_id: str, _: ApiKeyDep) -> TenantSettings:
    return dependencies.tenant_settings_store.get(tenant_id, TenantSettings(tenant_id=tenant_id))


@router.put("/{tenant_id}/settings", response_model=TenantSettings)
async def update_settings(
    tenant_id: str,
    payload: TenantSettings,
    _: ApiKeyDep,
) -> TenantSettings:
    if payload.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="tenant_id mismatch",
        )
    try:
        dependencies.tenant_settings_store[tenant_id] = payload
        logger.info("Tenant settings updated for %s", tenant_id)
        return payload
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Failed to update tenant settings")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update tenant settings",
        ) from exc
